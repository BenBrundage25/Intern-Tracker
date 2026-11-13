"""Text cleaning and deduplication helpers for job postings."""

import hashlib
import html
import re

_COMMENTS = re.compile(r"<!--.*?-->", re.S)
_SCRIPT_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.S | re.I)
# Tags that imply a line break in rendered text.
_BLOCK_TAGS = re.compile(
    r"</?\s*(br|p|div|li|ul|ol|h[1-6]|tr|table|section|article|header|footer)\b[^>]*>", re.I
)
# Require a letter after `<` so plain-text comparisons like "x < 5 > y" survive.
_ANY_TAG = re.compile(r"</?[a-zA-Z][^>]*>")

_INVISIBLE = str.maketrans({"​": "", "‌": "", "‍": "", "﻿": ""})
_SPACE_RUN = re.compile(r"[^\S\n]+")  # whitespace other than newlines
_BLANK_LINES = re.compile(r"\n{3,}")
_ALL_WS = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Remove HTML markup, turning block-level tags into newlines and decoding entities."""
    text = _COMMENTS.sub("", text)
    text = _SCRIPT_STYLE.sub("", text)
    text = _BLOCK_TAGS.sub("\n", text)
    text = _ANY_TAG.sub(" ", text)
    return html.unescape(text)


def normalize_whitespace(text: str) -> str:
    """Collapse runs of spaces, trim each line, and allow at most one blank line in a row."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").translate(_INVISIBLE)
    lines = (_SPACE_RUN.sub(" ", line).strip() for line in text.split("\n"))
    return _BLANK_LINES.sub("\n\n", "\n".join(lines)).strip()


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    return normalize_whitespace(strip_html(text))


def _dedupe_key_part(value: str | None) -> str:
    return _ALL_WS.sub(" ", value or "").strip().casefold()


def content_hash(title: str | None, company: str | None, description: str | None) -> str:
    """Stable SHA-256 over title, company, and description.

    Case and whitespace are ignored so reposts that differ only in formatting collapse
    to the same hash. Inputs should already be cleaned with `clean_text`.
    """
    key = "\x1f".join(_dedupe_key_part(v) for v in (title, company, description))
    return hashlib.sha256(key.encode("utf-8")).hexdigest()
