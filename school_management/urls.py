# # school_management/urls.py

# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# # Remove or comment out these imports
# # from django.urls import re_path
# # from rest_framework import permissions
# # from drf_yasg.views import get_schema_view
# # from drf_yasg import openapi

# # If you want to add API documentation later, use this:
# # from rest_framework.documentation import include_docs_urls

# urlpatterns = [
#     path('admin/', admin.site.urls),
    
#     # API Documentation (optional - enable if you want it)
#     # path('api-docs/', include_docs_urls(title='School Management API')),
    
#     # API endpoints
#     path('api/auth/', include('users.urls')),  # This includes activities endpoints
#     path('api/students/', include('students.urls')),
#     path('api/parents/', include('parents.urls')),
#     path('api/staff/', include('staff.urls')),
#     path('api/results/', include('results.urls')),
#     path('api/academic/', include('academic.urls')),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# school_management/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation with drf-spectacular
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/students/', include('students.urls')),
    path('api/parents/', include('parents.urls')),
    path('api/staff/', include('staff.urls')),
    path('api/results/', include('results.urls')),
    path('api/academic/', include('academic.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)