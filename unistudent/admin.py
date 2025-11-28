"""Admin models"""

# Django
from django.contrib import admin

# AA unistudent App
from unistudent.models import Owner, SelectedTitle, Title


# Register your models here.
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("user", "user_username")

    @admin.display(description="Username")
    def user_username(self, obj):
        return obj.user.profile.main_character


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ("corp", "title_name", "title_id")


@admin.register(SelectedTitle)
class SelectedTitleAdmin(admin.ModelAdmin):
    list_display = ("corp", "title")
    list_filter = ("corp",)
