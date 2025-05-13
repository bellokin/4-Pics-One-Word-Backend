# game/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('insertRiddles/', views.generate_and_insert_riddles, name='insertRiddles'), 
    path('fetchAllRiddles/',views.get_all_riddles,name="fetchAllRiddles")
]
