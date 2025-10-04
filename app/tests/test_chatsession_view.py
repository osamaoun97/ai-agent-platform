from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from app.models.chatsession import ChatSession
from app.models.message import Message
from app.models.agent import Agent  # Add this import
from unittest.mock import patch

class ChatSessionViewSetTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        # Create an agent first
        self.agent = Agent.objects.create(
            name="Test Agent",
        )
        self.chat_session = ChatSession.objects.create(agent=self.agent)
        self.message = Message.objects.create(
            session=self.chat_session,
            content="Hello",
            role=Message.USER
        )
        self.list_url = reverse('session-list')
        self.detail_url = reverse('session-detail', kwargs={'pk': self.chat_session.pk})

    def test_list_sessions(self):
        """Test retrieving list of chat sessions"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['agent'], self.agent.id)

    def test_list_sessions_filter_by_agent(self):
        """Test filtering chat sessions by agent"""
        response = self.client.get(f"{self.list_url}?agent={self.agent.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(f"{self.list_url}?agent=999")
        self.assertEqual(len(response.data), 0)

    def test_retrieve_session(self):
        """Test retrieving a single chat session"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.chat_session.id)
        self.assertEqual(response.data['agent'], self.agent.id)

    def test_create_session(self):
        """Test creating a new chat session"""
        data = {'agent': self.agent.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['agent'], self.agent.id)
        self.assertEqual(ChatSession.objects.count(), 2)

    def test_delete_session(self):
        """Test deleting a chat session"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ChatSession.objects.count(), 0)

    def test_get_session_messages(self):
        """Test retrieving messages for a chat session"""
        url = reverse('session-messages', kwargs={'pk': self.chat_session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "Hello")
        self.assertEqual(response.data[0]['role'], Message.USER)

    @patch('app.services.chat_service.ChatService.generate_response')
    def test_send_message(self, mock_generate_response):
        """Test sending a text message"""
        mock_generate_response.return_value = "Hello, how can I help?"
        url = reverse('session-send-message')
        data = {
            'session_id': self.chat_session.id,
            'content': 'Hi there'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['user_message'], 'Hi there')
        self.assertEqual(response.data['agent_response'], 'Hello, how can I help?')

        # Verify only the initial message exists (from setUp)
        messages = Message.objects.filter(session=self.chat_session).order_by('created_at')
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages.first().role, Message.USER)

    @patch('app.services.voice_service.VoiceService.process_voice_message')
    def test_send_voice_message(self, mock_process_voice):
        """Test sending a voice message"""
        mock_process_voice.return_value = b'fake_audio_data'
        url = reverse('session-send-voice-message')
        audio_file = open('test.mp3', 'wb')
        audio_file.write(b'fake_audio_data')
        audio_file.close()

        with open('test.mp3', 'rb') as audio_file:
            data = {
                'session_id': self.chat_session.id,
                'audio_file': audio_file
            }
            response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get('Content-Type'), 'audio/mpeg')
        self.assertEqual(response.get('Content-Disposition'), 'attachment; filename="agent_response.mp3"')

    def test_send_message_invalid_session(self):
        """Test sending message to invalid session"""
        url = reverse('session-send-message')
        data = {
            'session_id': 999,
            'content': 'Hi there'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_voice_message_invalid_session(self):
        """Test sending voice message to invalid session"""
        url = reverse('session-send-voice-message')
        audio_file = open('test.mp3', 'wb')
        audio_file.write(b'fake_audio_data')
        audio_file.close()

        with open('test.mp3', 'rb') as audio_file:
            data = {
                'session_id': 999,
                'audio_file': audio_file
            }
            response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        """Clean up any files created during testing"""
        import os
        if os.path.exists('test.mp3'):
            os.remove('test.mp3')
