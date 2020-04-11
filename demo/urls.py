from django.contrib import admin
from django.urls import path
from demo import views

urlpatterns = [
    path('<str:session_name>/game-state', views.get_game_state, name="get_game_state"),
    path('<str:session_name>/next-game', views.next_game, name="next_game"),
    path('<str:session_name>/make-guess', views.make_guess, name="make_guess"),
    path('<str:session_name>/end-turn', views.end_turn, name="end_turn"),
    path('<str:session_name>', views.get_playfield, name="get_playfield"),
    path('', views.CreateJoinSession.as_view(), name="join_game"),
]
