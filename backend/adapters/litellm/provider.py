"""litellm adapter — ModelProviderPort implementation (FR-11)."""
import litellm

from ports.model_provider import ModelProviderPort


class LiteLLMProvider(ModelProviderPort):
    """Provider-agnostic LLM invocation via litellm."""

    async def invoke(self, model: str, messages: list[dict], **kwargs) -> str:
        """Call LLM via litellm.acompletion and return content string."""
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            **kwargs,
        )
        return response.choices[0].message.content
