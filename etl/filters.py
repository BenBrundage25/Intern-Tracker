"""Decide which postings to keep: internships, entry-level roles, and a background sample."""

import re

TARGET_EXPERIENCE_LEVELS = frozenset({"internship", "entry level"})

_TARGET_TITLE = re.compile(
    r"\b(intern|interns|internship|co-?op|new\s+grad(uate)?|entry[\s-]level|junior|jr\.?"
    r"|apprentice(ship)?|trainee)\b",
    re.I,
)


def is_target_role(title: str | None, experience_level: str | None) -> bool:
    level = (experience_level or "").strip().casefold()
    if level in TARGET_EXPERIENCE_LEVELS:
        return True
    return bool(title and _TARGET_TITLE.search(title))


def in_background_sample(content_hash: str, rate: float) -> bool:
    """Deterministically keep roughly `rate` of non-target postings.

    The sample is derived from the content hash, not a random seed, so re-running the
    ETL keeps the same postings and the sample doesn't drift between loads.
    """
    if rate <= 0:
        return False
    if rate >= 1:
        return True
    return int(content_hash[:8], 16) / 0xFFFFFFFF < rate
