from django.db import models
from app.models.chatsession import ChatSession

class Message(models.Model):
    """
    Represents a single message in a chat session.

    Messages can be either from the user or the AI agent, determined by the role field.
    Each message belongs to a specific chat session and maintains its content and timestamp.

    Attributes:
        session (ForeignKey): Reference to the ChatSession model
        role (CharField): Role of the message sender, either 'user' or 'agent'
        content (TextField): The text content of the message
        created_at (DateTimeField): Timestamp when the message was created

    Class Constants:
        USER (str): Constant representing user role
        AGENT (str): Constant representing agent role
        ROLE_CHOICES (list): Available role choices for the role field

    Relationships:
        - Belongs to one ChatSession (ForeignKey)
    """
    USER = "user"
    AGENT = "agent"
    ROLE_CHOICES = [
        (USER, "User"),
        (AGENT, "Agent"),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} @ {self.created_at}: {self.content[:30]}"
