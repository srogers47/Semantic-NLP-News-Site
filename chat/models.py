from django.db import models
from django.urls import reverse
from django.contrib.auth.models import Group

class ChatGroup(Group):
    """Extend Group model.  Similar to GroupChat"""
    description = models.TextField(blank=True, help_text="Describe the group.")
    mute_notifications = models.BooleanField(defualt=False, help_text="Would you like to mute notifications?")
    icon = models.ImageField(help_text="Icon for Group", blank=True, upload_to="chatgroup_media")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('chat:room', args=[str(self.id)])
