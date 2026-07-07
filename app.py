"""NewsDub AI — Flask application entry point."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory

from services.rss_service import RSSServiceError, fetch_headlines
from services.translation_service import (
    TranslationServiceError,
    get_supported_languages,
    translate_text,
)
import services.translation_service as ts

print("=" * 60)
print("Translation service loaded from:")
print(ts.__file__)
print("=" * 60)
from services.tts_service import TTSServiceError, generate_speech

load_dotenv()
print(os.getenv("SARVAM_API_KEY"))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "generated_audio"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")


@app.route("/")
def index():
    """Render the main page."""
    return render_template(
        "index.html",
        languages=get_supported_languages(),
        rss_feed_url=os.getenv("RSS_FEED_URL", "http://feeds.bbci.co.uk/news/rss.xml"),
    )


@app.route("/api/headlines")
def api_headlines():
    """Return the latest news headlines as JSON."""
    feed_url = os.getenv("RSS_FEED_URL", "http://feeds.bbci.co.uk/news/rss.xml")
    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        limit = 5

    try:
        headlines = fetch_headlines(feed_url=feed_url, limit=limit)
        return jsonify({"success": True, "headlines": headlines})
    except RSSServiceError as exc:
        logger.warning("Headlines fetch failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 502


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """Translate headline and summary to the selected Indian language."""
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    summary = (payload.get("summary") or "").strip()
    target_language = (payload.get("target_language") or "").strip()

    if not title:
        return jsonify({"success": False, "error": "Headline title is required."}), 400
    if not target_language:
        return jsonify({"success": False, "error": "Target language is required."}), 400

    combined_text = f"{title}. {summary}" if summary else title

    try:
        result = translate_text(combined_text, target_language_code=target_language)
        return jsonify({"success": True, **result})
    except TranslationServiceError as exc:
        logger.warning("Translation failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 502


@app.route("/api/synthesize", methods=["POST"])
def api_synthesize():
    """Generate speech audio from translated text."""
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    target_language = (payload.get("target_language") or "").strip()

    if not text:
        return jsonify({"success": False, "error": "Translated text is required."}), 400
    if not target_language:
        return jsonify({"success": False, "error": "Target language is required."}), 400

    try:
        result = generate_speech(text, target_language_code=target_language)
        return jsonify({"success": True, **result})
    except TTSServiceError as exc:
        logger.warning("TTS failed: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 502


@app.route("/generated_audio/<path:filename>")
def serve_audio(filename: str):
    """Serve generated WAV files for playback and download."""
    return send_from_directory(AUDIO_DIR, filename, mimetype="audio/wav")


@app.route("/api/languages")
def api_languages():
    """Return supported Indian languages."""
    return jsonify({"success": True, "languages": get_supported_languages()})


if __name__ == "__main__":
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    debug = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes"}
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, host="0.0.0.0", port=port)
