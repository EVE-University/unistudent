"""App URLs"""

# Django
from django.urls import path

# AA unistudent App
from unistudent import views

app_name: str = "unistudent"  # pylint: disable=invalid-name

urlpatterns = [
    path("", views.index, name="index"),
]
