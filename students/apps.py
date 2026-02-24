"""
App configuration for students app.
"""

from django.apps import AppConfig


class StudentsConfig(AppConfig):
    """Configuration for Students app"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'students'
    verbose_name = 'Student Management'
    
    def ready(self):
        """Import signals when app is ready"""
        import students.signals