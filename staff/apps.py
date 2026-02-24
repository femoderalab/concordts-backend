"""
Staff app configuration.
"""

from django.apps import AppConfig


class StaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff'

    def ready(self):
        """
        Import signals when app is ready.
        This ensures signals are registered when the app loads.
        """
        import staff.signals  # noqa