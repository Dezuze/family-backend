from django.urls import path
from .views import UserProfileView, FamilyTreeView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('tree/', FamilyTreeView.as_view(), name='family-tree'),
]
