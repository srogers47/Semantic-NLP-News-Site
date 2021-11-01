from tortoise import fields
from tortoise.models import Model

class ChatMessage(Model): 
    """
    This Model will use Tortoise-ORM for async storage of chat messages.
    Seperate from models.py, solely for messages/chat history.
    """
    id = fields.IntField(pd=True)
    room_id = fields.IntField(null=True)
    username = fields.CharField(max_length=50, null=True)
    message = fields.TextField()
    message_type = fields.CharField(max_length=50, null=True)
    image_caption = fields.CharField(max_length=50, null=True)
    date_created = fields.DatetimeField(null=True, auto_now_add=True)

    class Meta:
        table='chat_chatmessage'

    def __str__(self):
        return self.message
