# Standard Library
import re

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.authentication.models import EveCorporationInfo
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger
from esi.exceptions import HTTPNotModified
from esi.helpers import get_token
from esi.models import Token
from esi.openapi_clients import ESIClientProvider

# AA unistudent App
from unistudent.models import Owner, SelectedTitle, Title

logger = get_extension_logger(__name__)

esi = ESIClientProvider(
    compatibility_date="2025-11-28",
    ua_appname="EveUniversity_Student_app",
    ua_version="0.0.1",
    operations=[
        "GetCorporationsCorporationIdTitles",
        "GetCorporationsCorporationIdMembersTitles",
    ],
)


def strip_html(raw: str) -> str:
    if not raw:
        return ""
    cleaned = re.sub(r"<[^>]*>", "", raw)
    return cleaned.strip()


def save_titles_to_db(corporation_id: int, titles: list):
    logger.info(f"Saving titles for corporation {corporation_id}. Count: {len(titles)}")

    try:
        corp = EveCorporationInfo.objects.get(corporation_id=corporation_id)
    except EveCorporationInfo.DoesNotExist:
        return

    deleted_count, _ = Title.objects.filter(corp_id=corporation_id).delete()
    logger.debug(f"Deleted {deleted_count} stale titles for corp {corporation_id}")

    saved_count = 0
    for t in titles:
        if t.name == "":
            continue
        Title.objects.update_or_create(
            corp=corp,
            title_id=t.title_id,
            defaults={"title_name": strip_html(t.name)},
        )
        saved_count += 1

    logger.info(f"Saved {saved_count} titles for corporation {corporation_id}")


def get_corp_titles(user_id, corp_id):
    logger.info(
        f"Fetching corporation titles for corp {corp_id} using user_id {user_id}"
    )
    req_scopes = ["esi-corporations.read_titles.v1"]

    try:
        token = get_token(user_id, req_scopes)
    except Token.DoesNotExist:
        logger.warning(f"No valid token found for user {user_id}")
        Owner.objects.filter(user__id=user_id).update(valid_token=False)
        return False

    owner, _ = Owner.objects.get_or_create(user=token.user)

    op = esi.client.Corporation.GetCorporationsCorporationIdTitles(
        corporation_id=corp_id,
        token=token,
    )
    try:
        data = op.result()
        logger.debug(f"Retrieved {len(data)} titles for corp {corp_id}")

        save_titles_to_db(corp_id, data)

        owner.valid_token = True
        owner.last_pull = timezone.now()
        owner.save()
        logger.info(f"Updated Owner record for user {owner.user_id}: valid_token=True")

        return True

    except HTTPNotModified:
        # Do not modify valid_token, do not update last_pull
        logger.info(f"No title changes for corp {corp_id} (HTTP 304 Not Modified)")
        return False

    except Exception as ex:
        logger.error(f"Error fetching titles for corp {corp_id}: {ex}", exc_info=True)
        owner.valid_token = False
        owner.save()
        return False


def get_title_members(user_id, corp_id):
    logger.info(f"Fetching member titles for corp {corp_id}")

    selected = SelectedTitle.objects.filter(corp__corporation_id=corp_id).first()

    if not selected:
        logger.warning(
            f"No selected title for corp {corp_id} — skipping title member sync"
        )
        return False

    req_scopes = ["esi-corporations.read_titles.v1"]

    try:
        token = get_token(user_id, req_scopes)
    except Token.DoesNotExist:
        logger.warning(f"No valid token found for member sync for user {user_id}")
        Owner.objects.filter(user__id=user_id).update(valid_token=False)
        return False

    owner, _ = Owner.objects.get_or_create(user=token.user)

    op = esi.client.Corporation.GetCorporationsCorporationIdMembersTitles(
        corporation_id=corp_id,
        token=token,
    )

    try:
        data = op.result()
        logger.debug(
            f"Retrieved member-title data for corp {corp_id}. Count: {len(data)}"
        )

        parse_members(corp_id, data)

        owner.valid_token = True
        owner.last_pull = timezone.now()
        owner.save()

        logger.info(f"Owner {owner.user_id} validated from member sync")

        return True

    except HTTPNotModified:
        # Do not modify valid_token, do not update last_pull
        logger.info(f"No member-title changes for corp {corp_id} (304)")

        return False

    except Exception as ex:
        logger.error(f"Error syncing member titles: {ex}", exc_info=True)
        owner.valid_token = False
        owner.save()
        return False


def parse_members(corp_id, data):
    logger.info(f"Parsing member-title mappings for corp {corp_id}")

    selected = (
        SelectedTitle.objects.filter(corp__corporation_id=corp_id)
        .select_related("title", "aa_group")
        .first()
    )

    if not selected:
        logger.warning(f"No selected title for corp {corp_id} – skipping group update")
        return

    target_title_id = selected.title.title_id
    group = selected.aa_group

    logger.info(f"Selected title {target_title_id} maps to Group '{group.name}'")

    esi_char_ids = {
        member.character_id for member in data if target_title_id in member.titles
    }

    logger.info(f"{len(esi_char_ids)} characters have selected title")

    characters = EveCharacter.objects.filter(
        character_id__in=esi_char_ids
    ).select_related("character_ownership__user")

    users_to_add = set()
    for char in characters:
        try:
            users_to_add.add(char.character_ownership.user)
        except Exception:
            logger.error(f"Character {char.character_id} missing ownership → skipping")

    logger.info(f"{len(users_to_add)} Users to grant '{group.name}'")

    current_group_users = set(group.user_set.all())

    add_users = users_to_add - current_group_users
    if add_users:
        group.user_set.add(*add_users)
        logger.info(f"Added {len(add_users)} users to '{group.name}'")

    remove_users = current_group_users - users_to_add
    if remove_users:
        group.user_set.remove(*remove_users)
        logger.info(f"Removed {len(remove_users)} users from '{group.name}'")

    logger.info("Group sync completed successfully.")


def sync_all():
    owners = Owner.objects.select_related(
        "user__profile__main_character__character_ownership"
    ).all()

    corp_buckets = {}

    for owner in owners:
        # resolve corp ID via main character (cached relationship)
        try:
            corp_id = owner.user.profile.main_character.corporation_id
        except Exception:
            logger.warning(f"Owner {owner.user} has no corporation — skipping")
            continue

        corp_buckets.setdefault(corp_id, []).append(owner)

    logger.info(f"Found {len(corp_buckets)} corporations to sync")

    for corp_id, corp_owners in corp_buckets.items():
        logger.info(f"--- Syncing corporation {corp_id} ---")

        title_synced = False
        for owner in corp_owners:
            logger.info(f"Attempt get_corp_titles via {owner.user.username}")
            res = get_corp_titles(
                owner.user.profile.main_character.character_id, corp_id
            )
            if res:
                logger.info(f"Title sync success via {owner.user.username}")
                title_synced = True
                break
            else:
                logger.info(
                    f"Title sync failed via {owner.user.username} — trying next"
                )

        if not title_synced:
            logger.warning(f"No valid tokens for corp {corp_id}. Titles NOT synced.")
            continue

        selected = SelectedTitle.objects.filter(corp__corporation_id=corp_id).first()
        if not selected:
            logger.info(f"No selected title for corp {corp_id}. Skipping member sync.")
            continue

        member_synced = False
        for owner in corp_owners:
            logger.info(f"Attempt get_title_members via {owner.user.username}")
            res = get_title_members(
                owner.user.profile.main_character.character_id, corp_id
            )
            if res:
                logger.info(f"Member sync success via {owner.user.username}")
                member_synced = True
                break
            else:
                logger.info(
                    f"Member sync failed via {owner.user.username} — trying next"
                )

        if not member_synced:
            logger.warning(f"No valid token for member sync in corp {corp_id}")

    logger.info("===== UNISTUDENT SYNC COMPLETE =====")
