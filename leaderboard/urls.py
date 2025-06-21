# leaderboard/urls.py
from django.urls import path
from .views import register_user, get_top_100, update_score

urlpatterns = [
    path('register/', register_user),
    path('top/', get_top_100),
    path('update-score/', update_score),
]
