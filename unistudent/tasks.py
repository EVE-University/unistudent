"""App Tasks"""

# Standard Library
import logging

# Third Party
from celery import shared_task

logger = logging.getLogger(__name__)

# Create your tasks here


@shared_task
def pull_all_titles():
    """Task to pull all titles for corp"""

    print("pulled")

    pass
