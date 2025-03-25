import os
import openai
import anthropic
from dataclasses import dataclass
from typing import Dict, List, Optional
import google.generativeai as genai


@dataclass
class ModelConfig:
    display_name: str
    max_tokens: int = 500
    temperature: float = 0.7

class LLMService:
    def __init__(self):
        # Initialize API clients
        self.openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Define available models and their configurations
        self.MODELS = {
            "OpenAI": {
                "gpt-4o": ModelConfig("GPT-4o"),
                "gpt-4o-mini": ModelConfig("GPT-4o mini")
            },
            "Anthropic": {
                "claude-3-7-sonnet-latest": ModelConfig("Claude 3.7 Sonnet"),
                "claude-3-haiku-20240307": ModelConfig("Claude 3 Opus"),
                "claude-3-5-haiku-latest": ModelConfig("Claude 3 Haiku")
            },
            "Google": {
                "gemini-1.5-pro": ModelConfig("Gemini 1.5 Pro"),
                "gemini-1.5-flash": ModelConfig("Gemini 1.5 Flash")
            }
        }

    def get_providers(self) -> List[str]:
        """Returns list of available providers."""
        return list(self.MODELS.keys())

    def get_models(self, provider: str) -> Dict[str, str]:
        """Returns available models for a given provider."""
        return {
            model_id: config.display_name 
            for model_id, config in self.MODELS[provider].items()
        }

    def check_api_keys(self) -> Dict[str, bool]:
        """Checks the status of API keys."""
        return {
            "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
            "Anthropic": bool(os.getenv("ANTHROPIC_API_KEY"))
        }

    def generate_content(
        self,
        provider: str,
        model: str,
        system_prompt: str,
        user_prompt: str
    ) -> Optional[str]:
        """
        Generates content using the selected provider and model.
        Returns the generated text or None if an error occurs.
        """
        try:
            if provider == "OpenAI":
                return self._generate_openai(model, system_prompt, user_prompt)
            elif provider == "Anthropic":
                return self._generate_anthropic(model, system_prompt, user_prompt)
        except Exception as e:
            raise Exception(f"Error generating content with {provider} {model}: {e}")

    def _generate_openai(self, model: str, system_prompt: str, user_prompt: str) -> str:
        """Generates content using OpenAI's API."""
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.MODELS["OpenAI"][model].temperature,
            max_tokens=self.MODELS["OpenAI"][model].max_tokens
        )
        return response.choices[0].message.content.strip()

    def _generate_anthropic(self, model: str, system_prompt: str, user_prompt: str) -> str:
        """Generates content using Anthropic's API."""
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=self.MODELS["Anthropic"][model].max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text.strip()
    
    def _generate_gemini(self, model: str, system_prompt: str, user_prompt: str) -> str:
        """Generates content using Google's Gemini API."""
        # Get the Gemini model
        gemini_model = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": self.MODELS["Google"][model].temperature,
                "max_output_tokens": self.MODELS["Google"][model].max_tokens,
            }
        )
        
        # Gemini handles system prompts differently than OpenAI and Anthropic
        # We'll prepend it to the user prompt for consistency
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Generate the response
        response = gemini_model.generate_content(combined_prompt)
        
        return response.text.strip()