"""
InsightAgent LLM Service
Unified client supporting Google Gemini REST API, OpenAI-compatible APIs, and Deterministic Fallback.
"""

import json
from typing import Any
import httpx
from backend.config import settings


class LLMService:
    """Manages LLM inference across Gemini, OpenAI, or local deterministic fallback."""

    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY
        self.model = settings.DEFAULT_MODEL

    def is_gemini_configured(self) -> bool:
        return bool(self.gemini_key and len(self.gemini_key.strip()) > 5)

    def is_openai_configured(self) -> bool:
        return bool(self.openai_key and len(self.openai_key.strip()) > 5)

    def get_active_provider(self) -> str:
        if self.is_gemini_configured():
            return "gemini"
        elif self.is_openai_configured():
            return "openai"
        return "deterministic"

    def generate(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> str:
        """Synchronous text generation with auto-routing."""
        provider = self.get_active_provider()

        if provider == "gemini":
            return self._call_gemini(prompt, system_prompt, temperature)
        elif provider == "openai":
            return self._call_openai(prompt, system_prompt, temperature)
        else:
            return ""

    def _call_gemini(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> str:
        """Invokes Google Gemini generateContent endpoint with automatic multi-model failover."""
        models_to_try = [self.model, "gemini-3-flash-preview", "gemini-flash-lite-latest"]
        # Remove duplicate models
        seen = set()
        models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

        payload: dict[str, Any] = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
            }
        }

        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }

        with httpx.Client(timeout=20.0) as client:
            last_err = None
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.gemini_key}"
                try:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "").strip()
                    else:
                        last_err = f"[{resp.status_code}] {resp.text[:150]}"
                except Exception as e:
                    last_err = str(e)
            
            print(f"[LLM Warning] Gemini call failed on all models: {last_err}. Falling back to deterministic engine.")
            return ""

    def _call_openai(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2) -> str:
        """Invokes OpenAI-compatible completion endpoint."""
        url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model if "gemini" not in self.model else "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[LLM Warning] OpenAI call failed: {e}. Falling back to deterministic engine.")
            return ""


llm_service = LLMService()
