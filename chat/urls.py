from django.urls import path 
from . import views

app_name = 'chat'

urlpatterns = [
        path('', views.index, name='index'), # TODO Change to chatroom after homepage creation or chatroom partial...
        path('history/<str:room_id>/', views.history, name='history'),
        path('unauthorized/', views.unauthorized, name='authorized'), 
        path('<str:group_id>/', views.room, name='room'),
        ]
