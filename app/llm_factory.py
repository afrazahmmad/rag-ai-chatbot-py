from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain_community.llms import HuggingFacePipeline
from typing import Optional

def get_llm(provider: str = "openai", model_name: str = "gpt-3.5-turbo", hf_embedding=False):
    """
    Factory function to create LLM instances.

    Args:
        provider: str, "openai", "anthropic", "huggingface"
        model_name: str, model identifier
        hf_embedding: bool, True if model is an embedding model

    Returns:
        LLM instance
    """

    if provider.lower() == "openai":
        return ChatOpenAI(model_name=model_name, temperature=0)

    elif provider.lower() == "anthropic":
        return ChatAnthropic(model=model_name, temperature=0)

    elif provider.lower() == "huggingface":
        # HuggingFace embeddings or generative LLMs
        if hf_embedding:
            # Embedding model
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name=model_name)
        else:
            # Generative model
            return HuggingFacePipeline(model_name=model_name, task="text-generation")

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
