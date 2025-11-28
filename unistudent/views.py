"""App Views"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render
from esi.decorators import tokens_required
from unistudent.models import Owner
from django.utils import timezone

@login_required
@permission_required("unistudent.basic_access")
@tokens_required(scopes="esi-corporations.read_titles.v1")
def index(request: WSGIRequest, tokens) -> HttpResponse:
    token = tokens[0]
    Owner.objects.get_or_create(user=token.user)

    owners = Owner.objects.select_related("user").all()

    data = []
    now = timezone.now()

    for owner in owners:
        age = now - owner.created_at
        data.append({
            "username": owner.user.profile.main_character,
            "age_days": age.days,
            "last_pull": owner.last_pull,
            "valid_token": owner.valid_token
        })

    return render(request, "unistudent/index.html", {"owners": data})
