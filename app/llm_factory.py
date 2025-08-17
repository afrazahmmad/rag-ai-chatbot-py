# llm_factory.py
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.llms import HuggingFacePipeline
from transformers import pipeline

# Default models for convenience
DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-2",
    "huggingface": "tiiuae/falcon-7b-instruct"
}

def get_llm(provider: str, model: str | None = None, temperature: float = 0, max_tokens: int = 512):
    """
    Returns a LangChain-compatible LLM instance.
    provider: "openai", "anthropic", or "huggingface"
    model: Optional model name; uses default if None
    temperature: Sampling temperature
    max_tokens: Max tokens for output (HF only)
    """
    provider = provider.lower()
    model = model or DEFAULT_MODELS.get(provider)

    if provider == "openai":
        return ChatOpenAI(model_name=model, temperature=temperature)

    elif provider == "anthropic":
        return ChatAnthropic(model=model, temperature=temperature)

    elif provider == "huggingface":
        # Hugging Face text-generation pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            max_length=max_tokens,
            temperature=temperature
        )
        return HuggingFacePipeline(pipeline=pipe)

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
