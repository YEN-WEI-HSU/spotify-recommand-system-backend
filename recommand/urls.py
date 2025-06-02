# recommand/urls.py
from django.urls import path
from .views import album_recommendation, track_recommendation

urlpatterns = [
    path('album/', album_recommendation, name='album_recommendation'),
    path('track/', track_recommendation, name='track_recommendation'),
]