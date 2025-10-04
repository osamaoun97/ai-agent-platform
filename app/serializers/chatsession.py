from rest_framework import serializers
from app.models.chatsession import ChatSession


class ChatSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for the ChatSession model.

    Handles serialization of chat sessions for API responses and requests.
    Converts ChatSession instances to/from JSON format.

    Meta:
        model: ChatSession model class
        fields: All fields from the ChatSession model are included

    Serialized fields:
        - id (int): Primary key
        - agent (int): Foreign key to Agent model
        - created_at (datetime): Session creation timestamp
    """

    class Meta:
        model = ChatSession
        fields = "__all__"
