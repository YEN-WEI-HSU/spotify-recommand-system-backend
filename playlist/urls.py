



# playlist/urls.py
from django.urls import path
from .views import my_playlist_view  # 假設你已經有這個 view

urlpatterns = [
    path('my/', my_playlist_view),   # /api/playlist/my/
]
