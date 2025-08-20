from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain_community.llms import HuggingFacePipeline
from typing import Optional
import os

def get_llm(provider: str = "openai", model_name: str = "gpt-3.5-turbo", hf_embedding: bool = False):
    """
    Factory function to create LLM instances.

    Args:
        provider: str, "openai", "anthropic", "huggingface"
        model_name: str, model identifier
        hf_embedding: bool, True if using HuggingFace embeddings only

    Returns:
        LLM instance
    """

    provider = provider.lower()

    # ---------------- OpenAI ----------------
    if provider == "openai":
        from dotenv import load_dotenv
        import os

        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set!")
        return ChatOpenAI(model_name=model_name, temperature=0, openai_api_key=api_key)

    # ---------------- Anthropic ----------------
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set!")
        return ChatAnthropic(model=model_name, temperature=0, anthropic_api_key=api_key)

    # ---------------- HuggingFace ----------------
    elif provider == "huggingface":
        if hf_embedding:
            # For embedding-only usage, just return None
            # Embeddings are handled separately in vectorstore.py
            return None
        # Generative model
        return HuggingFacePipeline(model_name=model_name, task="text-generation")

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
