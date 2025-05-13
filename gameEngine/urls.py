# game/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('gameEngine/', views.generate_question, name='generateQuestion'),  # Define a path for the home view
]
