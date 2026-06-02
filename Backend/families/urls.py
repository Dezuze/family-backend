from django.urls import path
from .views import (
    UserProfileView, FamilyTreeView,
    ManagedMembersView, ManagedMemberDetailView,
    FamilyMemberContextView, FamilyMemberSearchView,
    FamilyTreeAddRelativeView, FamilyTreeLinkExistingMemberView, FamilyTreeRemoveMemberView,
    FamilyTreeUnlinkExistingMemberView,
    FamilyCommitteeMemberListCreateView, FamilyCommitteeMemberDetailView,
)

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('tree/', FamilyTreeView.as_view(), name='family-tree'),
    path('committee-members/', FamilyCommitteeMemberListCreateView.as_view(), name='committee-member-list'),
    path('committee-members/<int:pk>/', FamilyCommitteeMemberDetailView.as_view(), name='committee-member-detail'),
    path('managed/', ManagedMembersView.as_view(), name='managed-members'),
    path('managed/<int:pk>/', ManagedMemberDetailView.as_view(), name='managed-member-detail'),
    path('member-context/<int:pk>/', FamilyMemberContextView.as_view(), name='member-context'),
    path('member-search/', FamilyMemberSearchView.as_view(), name='member-search'),
    path('tree-edit/<int:pk>/add-relative/', FamilyTreeAddRelativeView.as_view(), name='tree-edit-add-relative'),
    path('tree-edit/<int:pk>/link-existing/', FamilyTreeLinkExistingMemberView.as_view(), name='tree-edit-link-existing'),
    path('tree-edit/<int:pk>/unlink-existing/', FamilyTreeUnlinkExistingMemberView.as_view(), name='tree-edit-unlink-existing'),
    path('tree-edit/<int:pk>/remove/', FamilyTreeRemoveMemberView.as_view(), name='tree-edit-remove-member'),
]
