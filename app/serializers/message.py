from rest_framework import serializers
from app.models.message import Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    Manages serialization of chat messages for API communication.
    Converts Message instances to/from JSON format.

    Meta:
        model: Message model class
        fields: All fields from the Message model are included

    Serialized fields:
        - id (int): Primary key
        - session (int): Foreign key to ChatSession model
        - role (str): Message sender role ('user' or 'agent')
        - content (str): Message content
        - created_at (datetime): Message creation timestamp
    """

    class Meta:
        model = Message
        fields = "__all__"
