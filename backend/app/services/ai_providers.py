from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Protocol

from app.core.config import settings

try:
    from openai import AzureOpenAI, OpenAI
except Exception:  # pragma: no cover - optional import guard
    AzureOpenAI = None
    OpenAI = None

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional import guard
    genai = None


class ProviderUnavailable(RuntimeError):
    pass


PROVIDER_TIMEOUT_SECONDS = 20


class AnalysisProvider(Protocol):
    name: str

    def analyze(self, prompt: str) -> dict[str, Any]:
        ...


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if not cleaned:
        return {}

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return {}
    return {}


@dataclass
class RuleBasedAnalysisProvider:
    name: str = "rule-based"

    def analyze(self, prompt: str) -> dict[str, Any]:
        return {
            "summary": "Rule-based analysis produced by AVIP when no provider key is configured.",
            "steps": [],
            "recommendations": {},
            "risks": [],
            "mitigations": [],
            "kpi_mapping": [],
            "benchmark": {},
            "confidence": 55,
        }


@dataclass
class OpenAIAnalysisProvider:
    name: str = "openai"
    model: str = settings.openai_model

    def analyze(self, prompt: str) -> dict[str, Any]:
        if OpenAI is None or not settings.openai_api_key:
            raise ProviderUnavailable("OpenAI is not configured")

        client = OpenAI(api_key=settings.openai_api_key, timeout=PROVIDER_TIMEOUT_SECONDS, max_retries=1)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert intelligent automation presales analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=settings.analysis_temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        payload = _extract_json(content)
        payload["_provider"] = self.name
        payload["_model"] = self.model
        return payload


@dataclass
class AzureOpenAIAnalysisProvider:
    name: str = "azure-openai"
    model: str = settings.azure_openai_model

    def analyze(self, prompt: str) -> dict[str, Any]:
        if AzureOpenAI is None or not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
            raise ProviderUnavailable("Azure OpenAI is not configured")

        deployment = settings.azure_openai_deployment or self.model
        client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version=settings.azure_openai_api_version,
            timeout=PROVIDER_TIMEOUT_SECONDS,
            max_retries=1,
        )
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are an expert intelligent automation presales analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=settings.analysis_temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        payload = _extract_json(content)
        payload["_provider"] = self.name
        payload["_model"] = deployment
        return payload


@dataclass
class GeminiAnalysisProvider:
    name: str = "gemini"
    model: str = settings.gemini_model

    def analyze(self, prompt: str) -> dict[str, Any]:
        if genai is None or not settings.gemini_api_key:
            raise ProviderUnavailable("Gemini is not configured")

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": settings.analysis_temperature,
                "response_mime_type": "application/json",
            },
            request_options={"timeout": PROVIDER_TIMEOUT_SECONDS},
        )
        payload = _extract_json(getattr(response, "text", "") or "")
        payload["_provider"] = self.name
        payload["_model"] = self.model
        return payload


def build_provider() -> AnalysisProvider:
    selected = settings.analysis_provider.lower().strip()

    if selected == "openai":
        return OpenAIAnalysisProvider()
    if selected in {"azure", "azure-openai"}:
        return AzureOpenAIAnalysisProvider()
    if selected == "gemini":
        return GeminiAnalysisProvider()
    if selected in {"rule", "rules", "deterministic"}:
        return RuleBasedAnalysisProvider()

    if settings.openai_api_key:
        return OpenAIAnalysisProvider()
    if settings.azure_openai_api_key and settings.azure_openai_endpoint:
        return AzureOpenAIAnalysisProvider()
    if settings.gemini_api_key:
        return GeminiAnalysisProvider()

    return RuleBasedAnalysisProvider()
