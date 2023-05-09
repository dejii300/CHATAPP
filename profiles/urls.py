from django.urls import path
from .views import *

app_name = 'profiles'

urlpatterns = [
    path('', Index, name='index'),
    path('profiles/', ProfileListView.as_view(), name='all-profiles-view'),
    path('my-invites/', invites_recieved_view, name='my-invites-view'),
    path('to-invite/', invite_profile_list_view, name='invite-profiles-view'),
    path('send-invite/', send_invataion, name='send-invite'),
    path('remove-friend/', remove_from_friends, name='remove-friend'),
    path('my-invites/accept/', accept_invatation, name='accept-invite'),
    path('my-invites/reject/', reject_invatation, name='reject-invite'),
    path("setting/", settingPage, name="setting-page"),
    path('friend-request/', friend_request, name='friend_request'),


    path('sent_msg/<str:pk>', sentMessages, name="sent_msg"),
    path('reci_msg/<str:pk>', receivedMessages, name="reci_msg"),
    path('notification/', chatNotification, name="notification"),
    path('friend/<str:pk>', Detail, name='detail'),
    path('frnd_p/<str:pk>', friend_profile, name='frnd_p'),
    
]