# academic/apps.py
"""
App configuration for Academic app.
"""

from django.apps import AppConfig


class AcademicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academic'
    verbose_name = 'Academic Management'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        try:
            import academic.signals  # noqa
            print(f"Signals imported for {self.verbose_name}")
        except ImportError as e:
            print(f"Error importing signals for {self.verbose_name}: {e}")