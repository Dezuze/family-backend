from django.urls import path
from .views import EventsListView, NewsListView, NewsCreateView, NewsDetailView

urlpatterns = [
    path('events/', EventsListView.as_view()),
    path('list/', NewsListView.as_view()),
    path('create/', NewsCreateView.as_view()),
    path('<int:pk>/', NewsDetailView.as_view()),
]
