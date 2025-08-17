"""
chatbot.py
- Conversational RAG chain with modern message history
- Retriever inject hota hai (already hybrid/ensemble)
"""

from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from .config import CHAT_MODEL

def build_chatbot(retriever, system_message: str | None = None):
    """
    Conversational RAG with memory.
    NOTE: system_message agar chaho to add kar sakte ho advanced config me.
    """
    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",  # simple & reliable
    )

    # Session-wise memory store (in-memory)
    session_store: Dict[str, ChatMessageHistory] = {}

    def get_session_history(session_id: str) -> ChatMessageHistory:
        if session_id not in session_store:
            session_store[session_id] = ChatMessageHistory()
        return session_store[session_id]

    conversational = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )
    return conversational
