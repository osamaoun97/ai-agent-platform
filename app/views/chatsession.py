from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.models.chatsession import ChatSession
from app.serializers.chatsession import ChatSessionSerializer
from app.serializers.send_message import SendMessageSerializer, VoiceMessageSerializer
from app.serializers.message import MessageSerializer
from app.services.chat_service import ChatService
from app.services.voice_service import VoiceService
import io


class ChatSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    A viewset for managing **Chat Sessions** between users and agents.

    A `ChatSession` represents an interaction between a user and an agent.
    Each session stores multiple `Message` objects that track user messages and agent responses.
    """

    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        """
        Optionally filter chat sessions by `agent` query parameter.
        Example: `/api/sessions/?agent=1`
        """
        queryset = ChatSession.objects.all()
        agent_id = self.request.query_params.get("agent", None)

        if agent_id is not None:
            queryset = queryset.filter(agent_id=agent_id)

        return queryset

    # ------------------------
    # CRUD METHODS
    # ------------------------

    @swagger_auto_schema(
        operation_summary="List all chat sessions",
        operation_description="Retrieve a list of all chat sessions. Can be filtered by agent ID using the `agent` query parameter.",
        manual_parameters=[
            openapi.Parameter(
                "agent",
                openapi.IN_QUERY,
                description="Filter sessions by agent ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            )
        ],
        responses={200: ChatSessionSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a chat session",
        operation_description="Get details of a specific chat session by ID.",
        responses={200: ChatSessionSerializer},
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="Chat session ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new chat session",
        operation_description="Create a new chat session by providing an `agent` ID.",
        request_body=ChatSessionSerializer,
        responses={201: ChatSessionSerializer},
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a chat session",
        operation_description="Delete an existing chat session by ID.",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="Chat session ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ],
        responses={204: "Session deleted successfully", 404: "Not found"},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # ------------------------
    # CUSTOM ACTIONS
    # ------------------------

    @swagger_auto_schema(
        operation_summary="Get all messages in a chat session",
        operation_description="Retrieve the full conversation (all messages) for a given session ID.",
        responses={200: MessageSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="Chat session ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific session."""
        session = self.get_object()
        messages = session.messages.order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Send a text message",
        operation_description="Send a text message to the agent and receive a response.",
        request_body=SendMessageSerializer,
        responses={
            200: openapi.Response(
                description="Agent response",
                examples={
                    "application/json": {
                        "status": "success",
                        "user_message": "Hello!",
                        "agent_response": "Hi there, how can I help you today?"
                    }
                },
            ),
            400: "Validation error",
            404: "Chat session not found",
            500: "Internal server error",
        }
    )
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send a text message to the agent and get a response."""
        serializer = SendMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        session_id = serializer.validated_data['session_id']
        user_message = serializer.validated_data['content']

        try:
            chat_service = ChatService()
            agent_response = chat_service.generate_response(session_id, user_message)

            return Response(
                {
                    'status': 'success',
                    'user_message': user_message,
                    'agent_response': agent_response,
                },
                status=status.HTTP_200_OK
            )

        except ChatSession.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Send a voice message",
        operation_description="Send an audio file (voice message) to the agent and receive an audio response (MP3).",
        request_body=VoiceMessageSerializer,
        responses={
            200: "Returns an MP3 audio file",
            400: "Validation error",
            404: "Chat session not found",
            500: "Internal server error",
        }
    )
    @action(detail=False, methods=['post'])
    def send_voice_message(self, request):
        """Send a voice message to the agent and get an audio response."""
        serializer = VoiceMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        session_id = serializer.validated_data['session_id']
        audio_file = serializer.validated_data['audio_file']

        try:
            # Verify session exists
            ChatSession.objects.get(id=session_id)

            # Process voice message
            voice_service = VoiceService()
            agent_audio = voice_service.process_voice_message(session_id, audio_file)

            # Return audio file as response
            audio_io = io.BytesIO(agent_audio)
            return FileResponse(
                audio_io,
                content_type='audio/mpeg',
                as_attachment=True,
                filename='agent_response.mp3'
            )

        except ChatSession.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
