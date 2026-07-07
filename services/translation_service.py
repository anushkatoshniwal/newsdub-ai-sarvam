"""Translate news text using the official Sarvam AI SDK."""

import logging
import os
from typing import Any

from sarvamai import SarvamAI
from sarvamai.core.api_error import ApiError

logger = logging.getLogger(__name__)

# Languages supported by both mayura:v1 translation and bulbul:v3 TTS.
# Source: https://docs.sarvam.ai/api-reference-docs/getting-started/models/bulbul.mdx
SUPPORTED_LANGUAGES: dict[str, str] = {
    "hi-IN": "Hindi",
    "bn-IN": "Bengali",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "gu-IN": "Gujarati",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "mr-IN": "Marathi",
    "pa-IN": "Punjabi",
    "od-IN": "Odia",
}


class TranslationServiceError(Exception):
    """Raised when translation fails."""


def get_supported_languages() -> list[dict[str, str]]:
    """Return language options for the UI dropdown."""
    return [{"code": code, "name": name} for code, name in SUPPORTED_LANGUAGES.items()]


def _get_client() -> SarvamAI:
    api_key = os.getenv("SARVAM_API_KEY")
    print("=" * 40)
    print("API KEY FOUND:", api_key)
    print("=" * 40)


    if not api_key:
        raise TranslationServiceError(
            "SARVAM_API_KEY is not set. Add it to your .env file."
        )
    return SarvamAI(api_subscription_key=api_key)


def translate_text(
    text: str,
    target_language_code: str,
    source_language_code: str = "en-IN",
) -> dict[str, Any]:
    """
    Translate text using client.text.translate() from the Sarvam SDK.

    Docs: https://docs.sarvam.ai/api-reference-docs/api-guides-tutorials/text-processing/translation.mdx
    """
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise TranslationServiceError("Text to translate cannot be empty.")

    if target_language_code not in SUPPORTED_LANGUAGES:
        raise TranslationServiceError(f"Unsupported target language: {target_language_code}")

    client = _get_client()

    try:
        response = client.text.translate(
            input=cleaned_text,
            source_language_code=source_language_code,
            target_language_code=target_language_code,
            model="mayura:v1",
            output_script="fully-native",
        )
    except ApiError as exc:
        logger.exception("Sarvam translation API error (status %s)", exc.status_code)
        raise TranslationServiceError(_format_api_error(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected translation error")
        raise TranslationServiceError(f"Translation failed: {exc}") from exc

    translated_text = getattr(response, "translated_text", None) or ""
    if not translated_text:
        raise TranslationServiceError("Translation API returned an empty result.")

    return {
        "translated_text": translated_text,
        "source_language_code": getattr(response, "source_language_code", source_language_code),
        "request_id": getattr(response, "request_id", None),
    }


def _format_api_error(error: ApiError) -> str:
    """Turn SDK ApiError into a user-friendly message."""
    status = getattr(error, "status_code", None)
    body = getattr(error, "body", None)

    if status == 403:
        return "Invalid Sarvam API key. Check SARVAM_API_KEY in your .env file."
    if status == 429:
        return "Sarvam API rate limit exceeded. Please wait and try again."
    if status == 422:
        return "Text is too long or the language pair is not supported."
    if body:
        return f"Sarvam translation error ({status}): {body}"
    return f"Sarvam translation error ({status})."
