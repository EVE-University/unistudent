"""App Configuration"""

# Django
from django.apps import AppConfig

# AA unistudent App
from unistudent import __version__


class UnistudentConfig(AppConfig):
    """App Config"""

    name = "unistudent"
    label = "Unistudent"
    verbose_name = f"Unistudent App v{__version__}"
