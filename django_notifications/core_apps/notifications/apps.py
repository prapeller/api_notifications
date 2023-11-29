from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# from core_apps.notifications.models import PeriodicTaskModel


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_apps.notifications'
    verbose_name = _('notifications')
