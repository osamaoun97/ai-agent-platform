from unittest.mock import Mock, patch
from django.test import TestCase
from app.services.chat_service import ChatService
from app.models.chatsession import ChatSession
from app.models.message import Message
from app.models.agent import Agent


class ChatServiceTestCase(TestCase):
    """Test cases for ChatService"""

    def setUp(self):
        """Set up test fixtures"""
        # Create test agent
        self.agent = Agent.objects.create(
            name="Test Agent",
            prompt="You are a helpful assistant."
        )

        # Create test session
        self.session = ChatSession.objects.create(
            agent=self.agent
        )

        # Create some test messages
        Message.objects.create(
            session=self.session,
            role=Message.USER,
            content="Hello"
        )
        Message.objects.create(
            session=self.session,
            role=Message.AGENT,
            content="Hi! How can I help you?"
        )

        self.chat_service = ChatService()

    def test_get_session_context(self):
        """Test retrieving session context"""
        context = self.chat_service.get_session_context(self.session)

        self.assertEqual(len(context), 2)
        self.assertEqual(context[0]['role'], Message.USER)
        self.assertEqual(context[0]['content'], "Hello")
        self.assertEqual(context[1]['role'], Message.AGENT)
        self.assertEqual(context[1]['content'], "Hi! How can I help you?")

    def test_get_session_context_empty(self):
        """Test retrieving context from empty session"""
        empty_session = ChatSession.objects.create(
            agent=self.agent
        )

        context = self.chat_service.get_session_context(empty_session)
        self.assertEqual(len(context), 0)

    def test_get_session_context_order(self):
        """Test that messages are returned in correct chronological order"""
        # Create a new session with multiple messages
        session = ChatSession.objects.create(agent=self.agent)

        # Create messages with deliberate timing
        msg1 = Message.objects.create(
            session=session,
            role=Message.USER,
            content="First message"
        )
        msg2 = Message.objects.create(
            session=session,
            role=Message.AGENT,
            content="Second message"
        )
        msg3 = Message.objects.create(
            session=session,
            role=Message.USER,
            content="Third message"
        )

        context = self.chat_service.get_session_context(session)

        self.assertEqual(len(context), 3)
        self.assertEqual(context[0]['content'], "First message")
        self.assertEqual(context[1]['content'], "Second message")
        self.assertEqual(context[2]['content'], "Third message")

    def test_build_langchain_messages_with_context(self):
        """Test building LangChain messages with conversation history"""
        context = [
            {'role': Message.USER, 'content': 'Previous user message'},
            {'role': Message.AGENT, 'content': 'Previous agent response'}
        ]

        messages = self.chat_service.build_langchain_messages(
            agent_prompt="Test prompt",
            context=context,
            user_message="New message"
        )

        self.assertEqual(len(messages), 4)  # System + 2 context + 1 new
        self.assertEqual(messages[0].content, "Test prompt")
        self.assertEqual(messages[1].content, "Previous user message")
        self.assertEqual(messages[2].content, "Previous agent response")
        self.assertEqual(messages[3].content, "New message")

    def test_build_langchain_messages_no_context(self):
        """Test building LangChain messages without context"""
        messages = self.chat_service.build_langchain_messages(
            agent_prompt="Test prompt",
            context=[],
            user_message="Hello"
        )

        self.assertEqual(len(messages), 2)  # System + new message
        self.assertEqual(messages[0].content, "Test prompt")
        self.assertEqual(messages[1].content, "Hello")

    def test_build_langchain_messages_types(self):
        """Test that LangChain messages have correct types"""
        from langchain.schema import SystemMessage, HumanMessage, AIMessage

        context = [
            {'role': Message.USER, 'content': 'User message'},
            {'role': Message.AGENT, 'content': 'Agent message'}
        ]

        messages = self.chat_service.build_langchain_messages(
            agent_prompt="System prompt",
            context=context,
            user_message="New user message"
        )

        self.assertIsInstance(messages[0], SystemMessage)
        self.assertIsInstance(messages[1], HumanMessage)
        self.assertIsInstance(messages[2], AIMessage)
        self.assertIsInstance(messages[3], HumanMessage)

    @patch('app.services.chat_service.ChatOpenAI')
    def test_generate_response_success(self, mock_openai):
        """Test successful response generation"""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "This is the agent's response"
        mock_llm_instance = mock_openai.return_value
        mock_llm_instance.invoke.return_value = mock_response

        # Override the service's LLM with our mock
        self.chat_service.llm = mock_llm_instance

        response = self.chat_service.generate_response(
            session_id=self.session.id,
            user_message="What's the weather?"
        )

        # Verify response
        self.assertEqual(response, "This is the agent's response")

        # Verify messages were saved
        messages = Message.objects.filter(session=self.session).order_by('created_at')
        self.assertEqual(messages.count(), 4)  # 2 setup + 2 new
        self.assertEqual(messages[2].content, "What's the weather?")
        self.assertEqual(messages[2].role, Message.USER)
        self.assertEqual(messages[3].content, "This is the agent's response")
        self.assertEqual(messages[3].role, Message.AGENT)

        # Verify LLM was called
        mock_llm_instance.invoke.assert_called_once()

    @patch('app.services.chat_service.ChatOpenAI')
    def test_generate_response_preserves_context(self, mock_openai):
        """Test that conversation context is preserved"""
        mock_response = Mock()
        mock_response.content = "Response"
        mock_llm_instance = mock_openai.return_value
        mock_llm_instance.invoke.return_value = mock_response
        self.chat_service.llm = mock_llm_instance

        self.chat_service.generate_response(
            session_id=self.session.id,
            user_message="New question"
        )

        # Get the messages passed to invoke
        call_args = mock_llm_instance.invoke.call_args[0][0]

        # Should include system message + 2 context messages + new message
        self.assertEqual(len(call_args), 4)

    @patch('app.services.chat_service.ChatOpenAI')
    def test_generate_response_uses_agent_prompt(self, mock_openai):
        """Test that the agent's prompt is used as system message"""
        mock_response = Mock()
        mock_response.content = "Response"
        mock_llm_instance = mock_openai.return_value
        mock_llm_instance.invoke.return_value = mock_response
        self.chat_service.llm = mock_llm_instance

        # Create agent with specific prompt
        agent = Agent.objects.create(
            name="Specific Agent",
            prompt="You are a specialized assistant with specific instructions."
        )
        session = ChatSession.objects.create(agent=agent)

        self.chat_service.generate_response(
            session_id=session.id,
            user_message="Test"
        )

        # Get the messages passed to invoke
        call_args = mock_llm_instance.invoke.call_args[0][0]

        # First message should be the system message with agent prompt
        self.assertEqual(call_args[0].content, agent.prompt)

    def test_generate_response_invalid_session(self):
        """Test response generation with invalid session ID"""
        with self.assertRaises(ChatSession.DoesNotExist):
            self.chat_service.generate_response(
                session_id=99999,
                user_message="Test"
            )

    @patch('app.services.chat_service.ChatOpenAI')
    def test_generate_response_empty_message(self, mock_openai):
        """Test response generation with empty user message"""
        mock_response = Mock()
        mock_response.content = "I didn't receive a message"
        mock_llm_instance = mock_openai.return_value
        mock_llm_instance.invoke.return_value = mock_response
        self.chat_service.llm = mock_llm_instance

        response = self.chat_service.generate_response(
            session_id=self.session.id,
            user_message=""
        )

        # Should still process empty message
        self.assertEqual(response, "I didn't receive a message")

        # Verify empty message was saved
        user_messages = Message.objects.filter(
            session=self.session,
            role=Message.USER
        ).order_by('created_at')
        self.assertEqual(user_messages.last().content, "")

    @patch('app.services.chat_service.ChatOpenAI')
    def test_generate_response_select_related_optimization(self, mock_openai):
        """Test that select_related is used to optimize database queries"""
        mock_response = Mock()
        mock_response.content = "Response"
        mock_llm_instance = mock_openai.return_value
        mock_llm_instance.invoke.return_value = mock_response
        self.chat_service.llm = mock_llm_instance

        with self.assertNumQueries(4):  # Should use minimal queries with select_related
            # Expected queries:
            # 1. SELECT session with agent (select_related)
            # 2. SELECT messages for context
            # 3. INSERT user message
            # 4. INSERT agent message
            self.chat_service.generate_response(
                session_id=self.session.id,
                user_message="Test"
            )
