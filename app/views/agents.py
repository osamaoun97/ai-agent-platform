from rest_framework import viewsets
from app.models.agent import Agent
from app.serializers.agent import AgentSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AgentViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing **Agents** in the system.

    Agents define the behavior of an AI assistant using a `prompt`.
    Each agent has:
    - `name`: Human-readable identifier
    - `prompt`: A system prompt that defines its behavior
    - `created_at`: Timestamp when the agent was created
    - `updated_at`: Timestamp when the agent was last modified
    """

    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    @swagger_auto_schema(
        operation_summary="List all agents",
        operation_description="Retrieve a list of all available agents with their details.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve an agent",
        operation_description="Fetch details of a single agent by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "id", openapi.IN_PATH, description="Agent ID", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new agent",
        operation_description="Create a new agent by providing a `name` and `prompt`.",
        request_body=AgentSerializer,
        responses={201: AgentSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update an agent",
        operation_description="Update an existing agent's details by its ID.",
        request_body=AgentSerializer,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update an agent",
        operation_description="Update one or more fields of an existing agent by its ID.",
        request_body=AgentSerializer,
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete an agent",
        operation_description="Delete an agent permanently by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "id", openapi.IN_PATH, description="Agent ID", type=openapi.TYPE_INTEGER
            )
        ],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
