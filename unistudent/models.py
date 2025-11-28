# Django
from django.contrib.auth.models import Group
from django.db import models

# Alliance Auth
from allianceauth.authentication.models import EveCorporationInfo, User


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        """Meta definitions"""

        managed = False
        default_permissions = ()
        permissions = (("basic_access", "Can access this app"),)


class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_pull = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_token = models.BooleanField(default=True)


class Title(models.Model):
    corp = models.ForeignKey(
        EveCorporationInfo, on_delete=models.CASCADE, related_name="titles"
    )
    title_name = models.TextField(max_length=500)
    title_id = models.IntegerField()

    class Meta:
        unique_together = ("corp", "title_id")

    def __str__(self):
        return f"{self.title_name} ({self.title_id})"


class SelectedTitle(models.Model):
    corp = models.ForeignKey(
        EveCorporationInfo, on_delete=models.CASCADE, related_name="selected_titles"
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    aa_group = models.OneToOneField(
        Group, on_delete=models.CASCADE, related_name="esi_title_mapping"
    )

    class Meta:
        unique_together = ("corp",)

    def __str__(self):
        return f"{self.corp} → {self.title} ({self.aa_group.name})"
