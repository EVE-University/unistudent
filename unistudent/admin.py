"""Admin models"""

# Django
from django.contrib import admin  # noqa: F401
from unistudent.models import Owner, Title, SelectedTitle

# Register your models here.
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_username')

    def user_username(self, obj):
        return obj.user.profile.main_character
    
    user_username.short_description = "Username"
        
@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('corp', 'title_name', 'title_id')


@admin.register(SelectedTitle)
class SelectedTitleAdmin(admin.ModelAdmin):
    list_display = ("corp", "title")
    list_filter = ("corp",)