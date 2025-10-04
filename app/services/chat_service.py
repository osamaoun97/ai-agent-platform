from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from app.models.chatsession import ChatSession
from app.models.message import Message
from config.config_manager import ConfigManager
from langchain_groq import ChatGroq

config = ConfigManager()
import os

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = config.get("OPENAI_API_KEY")

if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = config.get("GROQ_API_KEY")

class ChatService:
    def __init__(self):
        self.llm = ChatGroq(model="openai/gpt-oss-20b",temperature=0)
        # self.llm = ChatOpenAI(
        #     model="gpt-4",
        #     temperature=0.7,
        # )

    def get_session_context(self, session: ChatSession) -> List[Dict]:
        """
        Retrieve all messages from the session to build conversation context.
        """
        messages = session.messages.order_by('created_at').all()
        context = []

        for msg in messages:
            context.append({
                'role': msg.role,
                'content': msg.content
            })

        return context

    def build_langchain_messages(self, agent_prompt: str, context: List[Dict], user_message: str):
        """
        Build LangChain message format with system prompt, context, and new user message.
        """
        messages = [SystemMessage(content=agent_prompt)]

        # Add conversation history
        for msg in context:
            if msg['role'] == Message.USER:
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == Message.AGENT:
                messages.append(AIMessage(content=msg['content']))

        # Add new user message
        messages.append(HumanMessage(content=user_message))

        return messages

    def generate_response(self, session_id: int, user_message: str) -> str:
        """
        Generate agent response based on session context and user message.
        """
        # Get session and agent
        session = ChatSession.objects.select_related('agent').get(id=session_id)
        agent = session.agent

        # Get conversation context
        context = self.get_session_context(session)

        # Save user message
        Message.objects.create(
            session=session,
            role=Message.USER,
            content=user_message
        )

        # Build messages for LangChain
        messages = self.build_langchain_messages(
            agent_prompt=agent.prompt,
            context=context,
            user_message=user_message
        )

        # Generate response
        response = self.llm.invoke(messages)
        agent_response = response.content

        # Save agent response
        Message.objects.create(
            session=session,
            role=Message.AGENT,
            content=agent_response
        )

        return agent_response