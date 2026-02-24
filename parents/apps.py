# parents/apps.py
"""
App configuration for Parents app.
"""

from django.apps import AppConfig


class ParentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'parents'
    verbose_name = 'Parents Management'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        try:
            import parents.signals  # noqa
            print(f"Signals imported for {self.verbose_name}")
        except ImportError as e:
            print(f"Error importing signals for {self.verbose_name}: {e}")