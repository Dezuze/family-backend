from django.urls import path
from .views import GalleryListCreateView, CommitteeListCreateView

urlpatterns = [
    path('gallery/', GalleryListCreateView.as_view()),
    path('committee/', CommitteeListCreateView.as_view()),
]
