"""
AI Service Facade for BuggyMan
"""
import os
import logging
from django.conf import settings
from .prompts import build_hint_prompt, build_feedback_prompt, build_explanation_prompt, build_personalized_feedback_prompt
from .providers import GeminiAIProvider, OpenAIAIProvider, MockAIProvider

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.mock_provider = MockAIProvider()

    def _get_provider(self):
        provider_name = getattr(settings, 'AI_PROVIDER', 'gemini').lower().strip()
        gemini_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
        openai_key = getattr(settings, 'OPENAI_API_KEY', '') or os.getenv('OPENAI_API_KEY', '')

        if provider_name == 'gemini' and gemini_key:
            return GeminiAIProvider(api_key=gemini_key)
        elif provider_name == 'openai' and openai_key:
            return OpenAIAIProvider(api_key=openai_key)
        elif gemini_key:
            return GeminiAIProvider(api_key=gemini_key)
        elif openai_key:
            return OpenAIAIProvider(api_key=openai_key)
        else:
            return self.mock_provider

    def generate_hint(self, context: dict) -> dict:
        prompt = build_hint_prompt(context)
        provider = self._get_provider()

        if isinstance(provider, MockAIProvider):
            return provider.generate_hint(context, prompt)

        try:
            return provider.generate_hint(context, prompt)
        except Exception as e:
            logger.warning(f"AI Provider '{provider.__class__.__name__}' failed: {e}. Falling back to MockAIProvider.")
            fallback_res = self.mock_provider.generate_hint(context, prompt)
            fallback_res['fallbackReason'] = str(e)
            return fallback_res

    def generate_feedback(self, context: dict) -> dict:
        prompt = build_feedback_prompt(context)
        provider = self._get_provider()

        if isinstance(provider, MockAIProvider):
            return provider.generate_feedback(context, prompt)

        try:
            return provider.generate_feedback(context, prompt)
        except Exception as e:
            logger.warning(f"AI Provider '{provider.__class__.__name__}' feedback failed: {e}. Falling back to MockAIProvider.")
            fallback_res = self.mock_provider.generate_feedback(context, prompt)
            fallback_res['fallbackReason'] = str(e)
            return fallback_res

    def generate_explanation(self, context: dict) -> dict:
        prompt = build_explanation_prompt(context)
        provider = self._get_provider()

        if isinstance(provider, MockAIProvider):
            return provider.generate_explanation(context, prompt)

        try:
            return provider.generate_explanation(context, prompt)
        except Exception as e:
            logger.warning(f"AI Provider '{provider.__class__.__name__}' explanation failed: {e}. Falling back to MockAIProvider.")
            fallback_res = self.mock_provider.generate_explanation(context, prompt)
            fallback_res['fallbackReason'] = str(e)
            return fallback_res

    def generate_personalized_feedback(self, context: dict) -> dict:
        prompt = build_personalized_feedback_prompt(context)
        provider = self._get_provider()

        if isinstance(provider, MockAIProvider):
            return provider.generate_personalized_feedback(context, prompt)

        try:
            return provider.generate_personalized_feedback(context, prompt)
        except Exception as e:
            logger.warning(f"AI Provider '{provider.__class__.__name__}' personalized feedback failed: {e}. Falling back to MockAIProvider.")
            fallback_res = self.mock_provider.generate_personalized_feedback(context, prompt)
            fallback_res['fallbackReason'] = str(e)
            return fallback_res

ai_service = AIService()
