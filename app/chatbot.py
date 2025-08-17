"""
chatbot.py
- Conversational RAG chain with modern message history
- Retriever inject hota hai (already hybrid/ensemble)
- LLM can be injected for flexible provider (OpenAI, HF, Anthropic, etc.)
"""

from typing import Dict, Optional
from langchain.chains import ConversationalRetrievalChain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

def build_chatbot(retriever, llm=None, system_message: Optional[str] = None):
    """
    Conversational RAG with memory.
    - `llm` can be any LangChain-compatible LLM instance.
    - `system_message` optionally sets system prompt.
    """
    if llm is None:
        raise ValueError("LLM must be provided. Use get_llm() from llm_factory.py.")

    # Build RAG chain
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
