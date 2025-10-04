from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from app.models.agent import Agent

class AgentViewSetTests(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        self.agent = Agent.objects.create(
            name="Test Agent",
            prompt="This is a test prompt"
        )
        self.list_url = reverse('agent-list')
        self.detail_url = reverse('agent-detail', kwargs={'pk': self.agent.pk})

    def test_list_agents(self):
        """Test retrieving a list of agents"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_agent(self):
        """Test creating a new agent"""
        data = {
            'name': 'New Agent',
            'prompt': 'New prompt'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agent.objects.count(), 2)
        self.assertEqual(Agent.objects.get(name='New Agent').prompt, 'New prompt')

    def test_retrieve_agent(self):
        """Test retrieving a single agent"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Agent')

    def test_update_agent(self):
        """Test updating an agent"""
        data = {
            'name': 'Updated Agent',
            'prompt': 'Updated prompt'
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.name, 'Updated Agent')

    def test_partial_update_agent(self):
        """Test partially updating an agent"""
        data = {'name': 'Partially Updated Agent'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.name, 'Partially Updated Agent')

    def test_delete_agent(self):
        """Test deleting an agent"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Agent.objects.count(), 0)

    def test_create_agent_invalid_data(self):
        """Test creating an agent with invalid data"""
        data = {'name': ''}  # Missing required prompt field
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
