from django.urls import re_path
from django.conf.urls import url 

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/test$', consumers.SurvivorConsumer.as_asgi()),
    re_path(r'ws/connect/game_id=(?P<game_id>\w+)/round_num=(?P<round_num>\w+)/username=(?P<username>\w+)$', consumers.SurvivorConsumer.as_asgi()),
]
