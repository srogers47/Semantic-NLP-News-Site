from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from asgiref.sync import sync_to_async
from tortoise import Tortoise
from django.conf import settings

from .models import ChatGroup
from .tortoise_models import ChatMessage

@login_required
def index(request):
    return render(request, 'chat/index.html', {})

def get_participants(group_id=None, group_obj=None, user=None):
    """Aggregate all users pertaining to a specific group"""
    if group_id:
        chatgroup=ChatGroup.objecttst.get(id=id)
    else:
        chatgroup = group_obj

    temp_participants = []
    for participants in chatgroup.user_set.values_list('username', flat=True): 
        if participants != user:
            temp_participants.append(participants.title())
    temp_participants.append('You')  # Could also say 'Me' if it looks cleaner
    return ', '.join(temp_participants)

@login_required 
def room(request, group_id):
    if request.user.groups.filter(id=group_id).exists():
        chatgroup = ChatGroup.objects.get(id=group_id)
        assigned_groups= list(request.user.groups.values_list('id', flat=True))
        groups_participated = ChatGroup.objects.filter(id__in=assigned_groups)
        return render(requests, 'chat/room.html', {
            'chatgroup': chatgroup,
            'participants': get_participants(group_obj=chatgroup, user=request.user.username), 
            'groups_participated': groups_participated
            })
    else: 
        return HttpResponseRedirect(reverse("chat:unauthorized"))

@login_required
def unauthorized(request):
    return render(request, 'chat/unauthorized.html', {})

async def history(request, room_id):
    await Tortoise.init(**settings.TORTOISE_INIT)
    chat_message = await ChatMessage.filter(room_id=room_id).order_by('date_created').values()
    await Tortoise.close_connections()
    return await sync_to_async(JsonResponse)(chat_message, safe=False) # Does this work? 


