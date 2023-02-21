from django.conf.urls import url 
from survivor_app import views 
 
urlpatterns = [ 
    url(r'^api/login$', views.login),
    url(r'^api/test$', views.test),
    url(r'^api/create_account$', views.create_account),
    url(r'^api/account$', views.account),
    url(r'^api/game$', views.game),
    url(r'^api/game_join$', views.game_join),
    url(r'^api/game_create$', views.game_create),
    url(r'^api/game_rounds$', views.game_rounds),
    url(r'^api/current_player$', views.current_player),
    url(r'^api/game_players$', views.game_players),
    url(r'^api/active_game_players$', views.active_game_players),
    url(r'^api/challenges$', views.challenges),
    url(r'^api/get_challenge_name$', views.challenge_name),
    url(r'^api/name_by_id$', views.name_by_id),
    url(r'^api/start_game$', views.start_game),
    url(r'^api/start_round$', views.start_round),
    url(r'^api/end_game$', views.end_game),
    url(r'^api/transfer_idol$', views.transfer_idol),
    url(r'^api/create_game_tribes$', views.create_tribes),
    url(r'^api/players_to_tribes$', views.tribe_insert),
    url(r'^api/get_games$', views.get_games),
    url(r'^api/get_latest_round$', views.get_latest_round),
    url(r'^api/get_player_from_username$', views.get_player_from_username)
]
