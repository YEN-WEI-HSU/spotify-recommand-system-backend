from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test.as_view(), name='test'), 
    path('login', views.AuthenticationaURL.as_view(), name='Spotify-OAuth'),
    path('callback', views.spotify_redirect, name='Spotify-Redirect'),
]
