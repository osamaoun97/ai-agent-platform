from rest_framework import serializers


class SendMessageSerializer(serializers.Serializer):
    """
    Serializer for handling text message requests.

    This serializer validates incoming message data without being tied to a model.
    Used for processing new message submissions in the chat system.

    Fields:
        session_id (IntegerField): ID of the chat session where message will be sent
        content (CharField): Text content of the message to be sent

    Usage:
        Used in API endpoints to validate incoming message data before processing
        and creating actual Message instances.
    """
    session_id = serializers.IntegerField()
    content = serializers.CharField()


class VoiceMessageSerializer(serializers.Serializer):
    """
    Serializer for handling voice message uploads.

    Validates incoming voice message data including the audio file.
    Used for processing voice message submissions in the chat system.

    Fields:
        session_id (IntegerField): ID of the chat session where message will be sent
        audio_file (FileField): The uploaded audio file containing the voice message

    Usage:
        Used in API endpoints to validate incoming voice message data before
        processing and converting to text.
    """
    session_id = serializers.IntegerField()
    audio_file = serializers.FileField()
