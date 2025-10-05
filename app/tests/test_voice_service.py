from unittest.mock import patch, Mock
from django.test import TestCase
from app.models.agent import Agent
from app.models.chatsession import ChatSession
from app.services.voice_service import VoiceService


class VoiceServiceTestCase(TestCase):
    """Test cases for VoiceService"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = Agent.objects.create(
            name="Voice Agent",
            prompt="You are a voice assistant."
        )
        self.session = ChatSession.objects.create(
            agent=self.agent
        )
        self.voice_service = VoiceService()

    @patch('app.services.voice_service.OpenAI')
    def test_speech_to_text_success(self, mock_openai_class):
        """Test successful speech to text conversion"""
        # Create mock audio file
        mock_audio_file = Mock()
        mock_audio_file.chunks.return_value = [b'audio data chunk 1', b'audio data chunk 2']

        # Mock OpenAI client
        mock_client = mock_openai_class.return_value
        mock_client.audio.transcriptions.create.return_value = "Transcribed text"
        self.voice_service.client = mock_client

        result = self.voice_service.speech_to_text(mock_audio_file)

        self.assertEqual(result, "Transcribed text")
        mock_client.audio.transcriptions.create.assert_called_once()

        # Verify the call arguments
        call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
        self.assertEqual(call_kwargs['model'], "whisper-1")
        self.assertEqual(call_kwargs['response_format'], "text")

    @patch('app.services.voice_service.OpenAI')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_speech_to_text_cleanup(self, mock_remove, mock_exists, mock_openai_class):
        """Test that temporary files are cleaned up"""
        mock_audio_file = Mock()
        mock_audio_file.chunks.return_value = [b'data']

        mock_exists.return_value = True

        # Mock OpenAI client
        mock_client = mock_openai_class.return_value
        mock_client.audio.transcriptions.create.return_value = "Text"
        self.voice_service.client = mock_client

        self.voice_service.speech_to_text(mock_audio_file)

        # Verify cleanup was called
        self.assertTrue(mock_remove.called)

    @patch('app.services.voice_service.OpenAI')
    @patch('os.path.exists')
    @patch('os.remove')
    def test_speech_to_text_cleanup_on_error(self, mock_remove, mock_exists, mock_openai_class):
        """Test that temporary files are cleaned up even on error"""
        mock_audio_file = Mock()
        mock_audio_file.chunks.return_value = [b'data']

        mock_exists.return_value = True

        # Mock OpenAI client to raise error
        mock_client = mock_openai_class.return_value
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")
        self.voice_service.client = mock_client

        with self.assertRaises(Exception):
            self.voice_service.speech_to_text(mock_audio_file)

        # Verify cleanup was still called
        self.assertTrue(mock_remove.called)

    @patch('app.services.voice_service.OpenAI')
    def test_speech_to_text_with_large_file(self, mock_openai_class):
        """Test speech to text with large audio file chunks"""
        # Create mock audio file with many chunks
        mock_audio_file = Mock()
        large_chunks = [b'chunk' * 1000 for _ in range(10)]
        mock_audio_file.chunks.return_value = large_chunks

        mock_client = mock_openai_class.return_value
        mock_client.audio.transcriptions.create.return_value = "Large file transcribed"
        self.voice_service.client = mock_client

        result = self.voice_service.speech_to_text(mock_audio_file)

        self.assertEqual(result, "Large file transcribed")

    @patch('app.services.voice_service.OpenAI')
    def test_text_to_speech_success(self, mock_openai_class):
        """Test successful text to speech conversion"""
        expected_audio = b'audio data bytes'

        # Mock OpenAI client
        mock_client = mock_openai_class.return_value
        mock_response = Mock()
        mock_response.content = expected_audio
        mock_client.audio.speech.create.return_value = mock_response
        self.voice_service.client = mock_client

        result = self.voice_service.text_to_speech("Hello world")

        self.assertEqual(result, expected_audio)
        mock_client.audio.speech.create.assert_called_once_with(
            model="tts-1",
            voice="alloy",
            input="Hello world",
            response_format="mp3"
        )

    @patch('app.services.voice_service.OpenAI')
    def test_text_to_speech_empty_string(self, mock_openai_class):
        """Test text to speech with empty string"""
        mock_client = mock_openai_class.return_value
        mock_response = Mock()
        mock_response.content = b''
        mock_client.audio.speech.create.return_value = mock_response
        self.voice_service.client = mock_client

        result = self.voice_service.text_to_speech("")

        self.assertEqual(result, b'')

    @patch('app.services.voice_service.OpenAI')
    def test_text_to_speech_long_text(self, mock_openai_class):
        """Test text to speech with long text input"""
        long_text = "This is a very long text. " * 100

        mock_client = mock_openai_class.return_value
        mock_response = Mock()
        mock_response.content = b'long audio'
        mock_client.audio.speech.create.return_value = mock_response
        self.voice_service.client = mock_client

        result = self.voice_service.text_to_speech(long_text)

        self.assertEqual(result, b'long audio')
        # Verify the full text was passed
        call_kwargs = mock_client.audio.speech.create.call_args[1]
        self.assertEqual(call_kwargs['input'], long_text)

    @patch('app.services.voice_service.OpenAI')
    def test_text_to_speech_special_characters(self, mock_openai_class):
        """Test text to speech with special characters"""
        special_text = "Hello! How are you? I'm fine. Cost: $100 (50% off)"

        mock_client = mock_openai_class.return_value
        mock_response = Mock()
        mock_response.content = b'special audio'
        mock_client.audio.speech.create.return_value = mock_response
        self.voice_service.client = mock_client

        result = self.voice_service.text_to_speech(special_text)

        self.assertEqual(result, b'special audio')

    @patch.object(VoiceService, 'text_to_speech')
    @patch.object(VoiceService, 'speech_to_text')
    @patch('app.services.voice_service.ChatService')
    def test_process_voice_message_full_pipeline(self, mock_chat_service_class, mock_stt, mock_tts):
        """Test complete voice message processing pipeline"""
        # Setup mocks
        mock_audio_file = Mock()
        mock_stt.return_value = "User's spoken text"

        mock_chat_instance = mock_chat_service_class.return_value
        mock_chat_instance.generate_response.return_value = "Agent's text response"

        mock_tts.return_value = b'agent audio response'

        # Override the chat service instance
        self.voice_service.chat_service = mock_chat_instance

        result = self.voice_service.process_voice_message(
            session_id=self.session.id,
            audio_file=mock_audio_file
        )

        # Verify pipeline steps
        mock_stt.assert_called_once_with(mock_audio_file)
        mock_chat_instance.generate_response.assert_called_once_with(
            session_id=self.session.id,
            user_message="User's spoken text"
        )
        mock_tts.assert_called_once_with("Agent's text response")

        self.assertEqual(result, b'agent audio response')

    @patch.object(VoiceService, 'speech_to_text')
    def test_process_voice_message_transcription_failure(self, mock_stt):
        """Test handling of transcription failure"""
        mock_audio_file = Mock()
        mock_stt.side_effect = Exception("Transcription failed")

        with self.assertRaises(Exception) as context:
            self.voice_service.process_voice_message(
                session_id=self.session.id,
                audio_file=mock_audio_file
            )

        self.assertIn("Transcription failed", str(context.exception))

    @patch.object(VoiceService, 'text_to_speech')
    @patch.object(VoiceService, 'speech_to_text')
    @patch('app.services.voice_service.ChatService')
    def test_process_voice_message_chat_failure(self, mock_chat_service_class, mock_stt, mock_tts):
        """Test handling of chat service failure"""
        mock_audio_file = Mock()
        mock_stt.return_value = "User text"

        mock_chat_instance = mock_chat_service_class.return_value
        mock_chat_instance.generate_response.side_effect = Exception("Chat failed")
        self.voice_service.chat_service = mock_chat_instance

        with self.assertRaises(Exception) as context:
            self.voice_service.process_voice_message(
                session_id=self.session.id,
                audio_file=mock_audio_file
            )

        self.assertIn("Chat failed", str(context.exception))
        mock_tts.assert_not_called()

    @patch.object(VoiceService, 'text_to_speech')
    @patch.object(VoiceService, 'speech_to_text')
    @patch('app.services.voice_service.ChatService')
    def test_process_voice_message_tts_failure(self, mock_chat_service_class, mock_stt, mock_tts):
        """Test handling of TTS failure"""
        mock_audio_file = Mock()
        mock_stt.return_value = "User text"

        mock_chat_instance = mock_chat_service_class.return_value
        mock_chat_instance.generate_response.return_value = "Agent response"
        self.voice_service.chat_service = mock_chat_instance

        mock_tts.side_effect = Exception("TTS failed")

        with self.assertRaises(Exception) as context:
            self.voice_service.process_voice_message(
                session_id=self.session.id,
                audio_file=mock_audio_file
            )

        self.assertIn("TTS failed", str(context.exception))
