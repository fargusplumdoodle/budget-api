import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from api2.constants import (
    ROOT_BUDGET_NAME,
    PAYCHEQUE_TAG_NAME,
    TRANSFER_TAG_NAME,
    INCOME_TAG_NAME,
)
from api2.models import UserInfo, Budget, Tag

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def ensure_user_info(sender, instance: User, **kwargs):
    if not kwargs.get("created"):
        return

    _, created = UserInfo.objects.get_or_create(user=instance)
    if created:
        logger.info("Created user_info for %s", instance.username)


@receiver(post_save, sender=User)
def ensure_root_budget(sender, instance: User, **kwargs):
    if not kwargs.get("created"):
        return

    _, created = Budget.objects.get_or_create(user=instance, name=ROOT_BUDGET_NAME)
    if created:
        logger.info("Created root budget for %s", instance.username)


@receiver(post_save, sender=User)
def ensure_default_tags(sender, instance: User, **kwargs):
    if not kwargs.get("created"):
        return

    default_tags = [INCOME_TAG_NAME, TRANSFER_TAG_NAME, PAYCHEQUE_TAG_NAME]

    for tag_name in default_tags:
        _, created = Tag.objects.get_or_create(user=instance, name=tag_name)
        if created:
            logger.info("Created %s tag for %s", tag_name, instance.username)
