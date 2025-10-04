from django.db import models
from app.models.agent import Agent

class ChatSession(models.Model):
    """
    Represents a conversation session between a user and an AI agent.

    A ChatSession maintains the context and history of a specific conversation.
    It links messages exchanged between the user and the agent.

    Attributes:
        agent (Agent): Foreign key to the Agent model
        created_at (datetime): Timestamp when the session was created

    Relationships:
        - Has one Agent (ForeignKey)
        - Has many Messages (reverse relationship)
    """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="sessions")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id} with {self.agent.name}"