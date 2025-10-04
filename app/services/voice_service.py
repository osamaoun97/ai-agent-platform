from openai import OpenAI
from app.services.chat_service import ChatService
import os
import tempfile
from config.config_manager import ConfigManager

config = ConfigManager()

class VoiceService:
    def __init__(self):
        self.client = OpenAI(api_key=config.get("OPENAI_API_KEY"))
        self.chat_service = ChatService()

    def speech_to_text(self, audio_file) -> str:
        """
        Convert audio file to text using OpenAI Whisper API.
        """
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            for chunk in audio_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            # Open and transcribe
            with open(tmp_file_path, 'rb') as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
            return transcript
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech using OpenAI TTS API.
        Returns audio bytes.
        """
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            response_format="mp3"
        )

        return response.content

    def process_voice_message(self, session_id: int, audio_file) -> bytes:
        """
        Complete voice interaction pipeline:
        1. Convert speech to text
        2. Generate chat response
        3. Convert response to speech
        Returns audio bytes of the agent's response.
        """
        # Step 1: Speech to Text
        user_text = self.speech_to_text(audio_file)

        # Step 2: Generate chat response
        agent_text_response = self.chat_service.generate_response(
            session_id=session_id,
            user_message=user_text
        )

        # Step 3: Text to Speech
        agent_audio_response = self.text_to_speech(agent_text_response)

        return agent_audio_response