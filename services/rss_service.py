"""Fetch and parse news headlines from an RSS feed."""

import logging
from typing import Any

import feedparser
import requests

logger = logging.getLogger(__name__)

DEFAULT_RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"
REQUEST_TIMEOUT = 15


class RSSServiceError(Exception):
    """Raised when RSS feed cannot be fetched or parsed."""


def fetch_headlines(feed_url: str = DEFAULT_RSS_URL, limit: int = 5) -> list[dict[str, Any]]:
    """
    Fetch the latest headlines from an RSS feed.

    Args:
        feed_url: URL of the RSS feed (defaults to BBC News).
        limit: Maximum number of headlines to return.

    Returns:
        A list of headline dicts with id, title, summary, and link.

    Raises:
        RSSServiceError: If the feed is unavailable or contains no entries.
    """
    try:
        response = requests.get(feed_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
    except requests.RequestException as exc:
        logger.exception("Failed to fetch RSS feed from %s", feed_url)
        raise RSSServiceError(f"Could not fetch RSS feed: {exc}") from exc
    except Exception as exc:
        logger.exception("Failed to parse RSS feed from %s", feed_url)
        raise RSSServiceError(f"Could not read RSS feed: {exc}") from exc

    if getattr(parsed, "bozo", False) and not parsed.entries:
        logger.warning("RSS feed parse warning: %s", getattr(parsed, "bozo_exception", "unknown"))

    if not parsed.entries:
        raise RSSServiceError("No headlines found in the RSS feed.")

    headlines: list[dict[str, Any]] = []
    for index, entry in enumerate(parsed.entries[:limit]):
        title = (entry.get("title") or "").strip()
        if not title:
            continue

        summary = (entry.get("summary") or entry.get("description") or "").strip()
        link = (entry.get("link") or "").strip()

        headlines.append(
            {
                "id": str(index),
                "title": title,
                "summary": _clean_summary(summary),
                "link": link,
            }
        )

    if not headlines:
        raise RSSServiceError("RSS feed entries did not contain usable headlines.")

    return headlines


def _clean_summary(raw_summary: str) -> str:
    """Remove simple HTML tags often present in RSS summaries."""
    if not raw_summary:
        return "No summary available for this headline."

    cleaned = raw_summary
    for tag in ("<p>", "</p>", "<br>", "<br/>", "<br />"):
        cleaned = cleaned.replace(tag, " ")

    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")

    return cleaned.strip() or "No summary available for this headline."
