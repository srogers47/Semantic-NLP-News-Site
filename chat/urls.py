from django.urls import path 
from . import views

urlpatterns = [
        path('', views.index, name='index'), # TODO Change to chatroom after homepage creation
        path('<str:room_name>/', views.room, name='room'),
        ]
