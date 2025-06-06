from django.urls import path
from . import views

urlpatterns = [
    path('login', views.AuthenticationaURL.as_view(), name='Spotify-OAuth'),
    path('callback', views.spotify_redirect, name='Spotify-Redirect'),
    path('get-playlists', views.get_current_user_playlists, name='Get-Playlists'),
]
