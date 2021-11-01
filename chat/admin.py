from django.contrib import admin
from .models import ChatGroup

class ChatGroupAdmin(admin.ModelAdmin):
    """Enable Chat Group admin actions"""
    list_display = ('id', 'name', 'description', 'icon', 'mute_notifications', 'date_created', 'date_modified')
    list_filter = ('id', 'name', 'description', 'icon', 'mute_notifications', 'date_created', 'date_modified')
    list_display_links = ('name',)

admin.site.register(ChatGroup, ChatGroupAdmin)
