


# questionMGT/urls.py
from django.urls import path
from .views import ask_question
from . import views

urlpatterns = [
    path('ask/', ask_question),
    path("history/", views.chat_history),
]
