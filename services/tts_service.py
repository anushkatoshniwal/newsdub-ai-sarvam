"""Generate speech audio using the official Sarvam AI Text-to-Speech SDK."""

import base64
import logging
import os
import uuid
from pathlib import Path
from typing import Any

from sarvamai import SarvamAI
from sarvamai.core.api_error import ApiError

from services.translation_service import SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

AUDIO_DIR = Path(__file__).resolve().parent.parent / "generated_audio"
MAX_TTS_CHARACTERS = 2500  # bulbul:v3 REST limit per official docs


class TTSServiceError(Exception):
    """Raised when text-to-speech generation fails."""


def _get_client() -> SarvamAI:
    api_key = os.getenv("SARVAM_API_KEY")
    print("TTS Service API Key:", api_key)
    if not api_key:
        raise TTSServiceError("SARVAM_API_KEY is not set. Add it to your .env file.")
    return SarvamAI(api_subscription_key=api_key)


def _ensure_audio_dir() -> Path:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    return AUDIO_DIR


def generate_speech(text: str, target_language_code: str) -> dict[str, Any]:
    """
    Convert translated text to speech using client.text_to_speech.convert().

    Docs: https://docs.sarvam.ai/api-reference-docs/getting-started/models/bulbul.mdx
    Response format: https://docs.sarvam.ai/api-reference-docs/text-to-speech/convert
    """
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise TTSServiceError("Text for speech synthesis cannot be empty.")

    if target_language_code not in SUPPORTED_LANGUAGES:
        raise TTSServiceError(f"Unsupported target language: {target_language_code}")

    if len(cleaned_text) > MAX_TTS_CHARACTERS:
        cleaned_text = cleaned_text[:MAX_TTS_CHARACTERS]
        logger.warning("Text truncated to %s characters for TTS.", MAX_TTS_CHARACTERS)

    client = _get_client()

    try:
        response = client.text_to_speech.convert(
            text=cleaned_text,
            target_language_code=target_language_code,
            model="bulbul:v3",
        )
    except ApiError as exc:
        logger.exception("Sarvam TTS API error (status %s)", exc.status_code)
        raise TTSServiceError(_format_api_error(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected TTS error")
        raise TTSServiceError(f"Speech generation failed: {exc}") from exc

    audios = getattr(response, "audios", None) or []
    if not audios:
        raise TTSServiceError("TTS API returned no audio data.")

    try:
        combined_audio = "".join(audios)
        audio_bytes = base64.b64decode(combined_audio)
    except Exception as exc:
        raise TTSServiceError("Failed to decode audio from TTS response.") from exc

    filename = f"newsdub_{uuid.uuid4().hex[:12]}.wav"
    filepath = _ensure_audio_dir() / filename
    filepath.write_bytes(audio_bytes)

    return {
        "filename": filename,
        "filepath": str(filepath),
        "request_id": getattr(response, "request_id", None),
        "audio_url": f"/generated_audio/{filename}",
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
        return "Text is too long or the language is not supported for TTS."
    if body:
        return f"Sarvam TTS error ({status}): {body}"
    return f"Sarvam TTS error ({status})."
