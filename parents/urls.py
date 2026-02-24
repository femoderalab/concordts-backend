# parents/urls.py
"""
URL configuration for the parents app.
Defines all parent management endpoints.
"""

from django.urls import path
from .views import (
    ParentListView, ParentCreateView, ParentDetailView, ParentUpdateView,
    ParentDashboardView, ParentChildrenView, LinkChildToParentView,
    AcceptDeclarationView, ManagePTAView, ParentStatisticsView,
    ParentSearchView, ParentDeleteView
)

app_name = "parents"

urlpatterns = [
    # =====================
    # PARENT MANAGEMENT
    # =====================
    path('', ParentListView.as_view(), name='parent-list'),
    path('create/', ParentCreateView.as_view(), name='parent-create'),
    path('search/', ParentSearchView.as_view(), name='parent-search'),
    path('statistics/', ParentStatisticsView.as_view(), name='parent-statistics'),
    
    # =====================
    # INDIVIDUAL PARENT OPERATIONS
    # =====================
    path('<int:pk>/', ParentDetailView.as_view(), name='parent-detail'),
    path('<int:pk>/update/', ParentUpdateView.as_view(), name='parent-update'),
    
    # =====================
    # PARENT DASHBOARD
    # =====================
    path('dashboard/', ParentDashboardView.as_view(), name='parent-dashboard'),
    
    # =====================
    # CHILDREN MANAGEMENT
    # =====================
    path('children/', ParentChildrenView.as_view(), name='parent-children'),
    path('link-child/', LinkChildToParentView.as_view(), name='parent-link-child'),
    
    # =====================
    # DECLARATION
    # =====================
    path('accept-declaration/', AcceptDeclarationView.as_view(), name='accept-declaration'),
    path('<int:pk>/accept-declaration/', AcceptDeclarationView.as_view(), name='accept-declaration-for-parent'),
    
    # =====================
    # PTA MANAGEMENT
    # =====================
    path('<int:pk>/manage-pta/', ManagePTAView.as_view(), name='manage-pta'),
    
    # parents/urls.py - ADD THIS LINE
    path('<int:pk>/delete/', ParentDeleteView.as_view(), name='parent-delete'),
]