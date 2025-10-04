from rest_framework import serializers
from app.models.agent import Agent


class AgentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Agent model.

    Converts Agent model instances to/from JSON format for API operations.
    Uses Django REST Framework's ModelSerializer to automatically include all fields.

    Meta:
        model: Agent model class
        fields: All fields from the Agent model are included

    Serialized fields:
        - id (int): Primary key
        - name (str): Agent's name
        - prompt (str): Agent's system prompt
        - created_at (datetime): Creation timestamp
    """

    class Meta:
        model = Agent
        fields = "__all__"
