"""
Gemini AI client for repository analysis.

Uses google-generativeai SDK to interact with Gemini Pro.
All prompts are centralised here for easy tuning.
"""

from __future__ import annotations

from typing import Optional

import google.generativeai as genai
import structlog

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError

logger = structlog.get_logger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not configured — AI features disabled")
            self._enabled = False
            return
        genai.configure(api_key=settings.gemini_api_key)
        model_name = settings.gemini_model or 'gemini-1.5-flash'
        self._model = genai.GenerativeModel(model_name)
        self._enabled = True
        logger.info("Gemini client initialized", model=model_name)

    # ── Public API ───────────────────────────────────────────────────────

    async def analyze_repository(
        self,
        repo_name: str,
        description: str | None,
        languages: dict[str, float],
        file_paths: list[str],
        readme: str | None,
    ) -> dict:
        """
        Single consolidated API call that returns all AI insights at once.
        This uses 1 API call instead of 4, critical for staying within free-tier quota.
        """
        file_tree_sample = "\n".join(file_paths[:150])
        readme_excerpt = (readme or "N/A")[:3000]

        prompt = (
            "You are an expert software engineer analyzing a GitHub repository.\n"
            "Provide a comprehensive analysis and return ONLY a valid JSON object "
            "with exactly these keys (no markdown fences, no extra text):\n\n"
            '{\n'
            '  "summary": "<concise project summary, max 300 words: purpose, features, tech stack, target audience>",\n'
            '  "architecture_analysis": "<architecture analysis, max 500 words: folder structure, patterns, separation of concerns, quality>",\n'
            '  "readme_score": <float 0-10>,\n'
            '  "readme_feedback": "<brief README quality feedback on completeness, clarity, setup instructions>",\n'
            '  "tech_stack": ["<framework1>", "<library1>", "<tool1>", ...]\n'
            '}\n\n'
            f"Repository: {repo_name}\n"
            f"Description: {description or 'N/A'}\n"
            f"Languages: {languages}\n\n"
            f"File tree (sample):\n{file_tree_sample}\n\n"
            f"README:\n{readme_excerpt}"
        )
        raw = await self._generate(prompt)
        return self._parse_combined_result(raw)

    # ── Private helpers ──────────────────────────────────────────────────

    async def _generate(self, prompt: str) -> str:
        if not self._enabled:
            return "AI analysis unavailable — Gemini API key not configured."
        try:
            response = await self._model.generate_content_async(prompt)
            return response.text or ""
        except Exception as exc:
            logger.error("Gemini API error", error=str(exc))
            raise ExternalServiceError("Gemini", str(exc)) from exc

    @staticmethod
    def _strip_fences(raw: str) -> str:
        """Remove markdown code fences from LLM output."""
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        return cleaned.strip()

    @classmethod
    def _parse_combined_result(cls, raw: str) -> dict:
        """Parse the single combined JSON response into all AI insight fields."""
        import json
        defaults = {
            "ai_summary": None,
            "readme_quality_score": None,
            "readme_quality_feedback": None,
            "detected_tech_stack": [],
            "architecture_analysis": None,
        }
        try:
            cleaned = cls._strip_fences(raw)
            data = json.loads(cleaned)
            return {
                "ai_summary": data.get("summary") or None,
                "readme_quality_score": float(data["readme_score"]) if data.get("readme_score") is not None else None,
                "readme_quality_feedback": data.get("readme_feedback") or None,
                "detected_tech_stack": data.get("tech_stack", []) if isinstance(data.get("tech_stack"), list) else [],
                "architecture_analysis": data.get("architecture_analysis") or None,
            }
        except (json.JSONDecodeError, ValueError, KeyError) as exc:
            logger.warning("Failed to parse combined Gemini response", error=str(exc), raw=raw[:500])
            # Fallback: use the raw text as summary
            return {**defaults, "ai_summary": raw[:2000] if raw else None}
