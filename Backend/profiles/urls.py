from django.urls import path
from .views import (
    GalleryListCreateView,
    GalleryDetailView,
    CommunityRoleListCreateView,
    CommunityRoleDetailView,
    CommunityRoleManageFlagView,
)

urlpatterns = [
    path('gallery/', GalleryListCreateView.as_view()),
    path('gallery/<int:pk>/', GalleryDetailView.as_view()),
    path('community-roles/', CommunityRoleListCreateView.as_view()),
    path('community-roles/<int:pk>/', CommunityRoleDetailView.as_view()),
    path('community-roles/<int:pk>/manage/', CommunityRoleManageFlagView.as_view()),
]
