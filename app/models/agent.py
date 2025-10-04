from django.db import models

class Agent(models.Model):
    """
    Represents an AI agent in the system.

    An Agent is a virtual assistant that can engage in conversations with users.
    Each agent has its own personality and behavior defined by its prompt.

    Attributes:
        name (str): The display name of the agent
        prompt (str): The system prompt that defines the agent's behavior and personality
        created_at (datetime): Timestamp when the agent was created
        updated_at (datetime): Timestamp when the agent was last modified
    """
    name = models.CharField(max_length=100)
    prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
