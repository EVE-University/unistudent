"""App Tasks"""

# Standard Library
import logging

# Third Party
from celery import shared_task
from providers import sync_all_provider

logger = logging.getLogger(__name__)

# Create your tasks here


@shared_task
def sync_all():
    """Task to pull all titles for corp"""
    sync_all_provider()
