from django.urls import path
from .views import (
    my_profile_view,
    invites_recieved_view, 
    profile_list_view, 
    invite_profile_list_view,
    ProfileDetailView,
    ProfileListView,
    send_invitation,
    remove_from_friends,
    accept_invitations,
    reject_invitations,
   
)


app_name = 'profiles'

urlpatterns = [
    path('', ProfileListView.as_view(), name='all-profiles-view'),
    path('myprofile/', my_profile_view, name='my-profile-view'),
    path('myinvites/', invites_recieved_view, name='my-invites-view'),
    path('inviteprofile', invite_profile_list_view, name='invite-profiles-view'),
    path('send-invite/', send_invitation, name='send-invite'),
    path('<slug>/', ProfileDetailView.as_view(), name='profile-detail-view'),
    path('remove-friend/', remove_from_friends, name='remove-friend'),
    path('myinvites/accept/', accept_invitations, name='accept-invite'),
    path('myinvites/reject/', reject_invitations, name='reject-invite'),
    
]