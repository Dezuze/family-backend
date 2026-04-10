from django.urls import path
from .views import GalleryListCreateView, CommitteeListCreateView, CommunityRoleListCreateView

urlpatterns = [
    path('gallery/', GalleryListCreateView.as_view()),
    path('committee/', CommitteeListCreateView.as_view()),
    path('community-roles/', CommunityRoleListCreateView.as_view()),
]
