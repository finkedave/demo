from django.contrib import admin
from django.urls import path
from demo import views
from django.views.generic import RedirectView

urlpatterns = [
    path('codenames/<str:session_name>/game-state', views.get_game_state, name="get_game_state"),
    path('codenames/<str:session_name>/next-game', views.next_game, name="next_game"),
    path('codenames/<str:session_name>/make-guess', views.make_guess, name="make_guess"),
    path('codenames/<str:session_name>/end-turn', views.end_turn, name="end_turn"),
    path('codenames/<str:session_name>/end-session', views.end_session, name="end_session"),
    path('codenames/<str:session_name>/update-settings', views.update_settings, name="update_settings"),
    path('codenames/<str:session_name>', views.get_playfield, name="get_playfield"),
    path('codenames', views.CreateJoinSession.as_view(), name="join_game"),

    path('', RedirectView.as_view(pattern_name='join_game', permanent=False)),
]
