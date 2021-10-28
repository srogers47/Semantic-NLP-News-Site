from django.urls import re_path
from . import consumers

websocker_urlpatterns = [
        re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatRoomConsumer),
        ]
