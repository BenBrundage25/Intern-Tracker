"""Load the Kaggle LinkedIn job postings CSV into Postgres.

Usage:
    uv run etl/load.py [--csv data/raw/postings.csv] [--background-rate 0.05]

Expects the schema to exist already (`uv run alembic -c backend/alembic.ini upgrade head`).
Safe to re-run: rows whose content_hash is already in the table are skipped.
"""

import argparse
import csv
import sys
from collections import Counter
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from itertools import batched
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from app.config import database_url
from app.db.models import Posting
from etl.clean import clean_text, content_hash
from etl.filters import in_background_sample, is_target_role

# Kaggle column -> our column. Only these are read; the rest of the CSV is ignored.
CSV_COLUMNS = {
    "job_id": "source_job_id",
    "title": "title",
    "company_name": "company",
    "location": "location",
    "description": "description",
    "formatted_experience_level": "experience_level",
    "listed_time": "posted_at",
    "job_posting_url": "url",
}


def parse_epoch_ms(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromtimestamp(float(value) / 1000, tz=UTC)
    except (ValueError, OverflowError, OSError):
        return None


def _blank_to_none(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def prepare_postings(
    rows: Iterable[dict[str, str]], background_rate: float, stats: Counter
) -> Iterator[dict]:
    """Clean, deduplicate, and filter raw CSV rows. Updates `stats` as it goes."""
    seen: set[str] = set()
    for row in rows:
        stats["rows_read"] += 1
        title = clean_text(row.get("title"))
        description = clean_text(row.get("description"))
        if not title or not description:
            stats["dropped_missing_text"] += 1
            continue

        company = _blank_to_none(clean_text(row.get("company_name")))
        digest = content_hash(title, company, description)
        if digest in seen:
            stats["dropped_duplicate"] += 1
            continue
        seen.add(digest)

        experience_level = _blank_to_none(row.get("formatted_experience_level"))
        if is_target_role(title, experience_level):
            stats["kept_target"] += 1
        elif in_background_sample(digest, background_rate):
            stats["kept_background"] += 1
        else:
            stats["dropped_not_target"] += 1
            continue

        yield {
            "source_job_id": _blank_to_none(row.get("job_id")),
            "title": title,
            "company": company,
            "location": _blank_to_none(row.get("location")),
            "description": description,
            "experience_level": experience_level,
            "posted_at": parse_epoch_ms(row.get("listed_time")),
            "url": _blank_to_none(row.get("job_posting_url")),
            "content_hash": digest,
        }


def read_csv(path: Path) -> Iterator[dict[str, str]]:
    csv.field_size_limit(sys.maxsize)  # some descriptions exceed the 128KB default
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = set(CSV_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"{path} is missing expected columns: {sorted(missing)}")
        yield from reader


def insert_postings(engine: Engine, postings: Iterable[dict], batch_size: int = 1000) -> int:
    inserted = 0
    with engine.begin() as conn:
        for batch in batched(postings, batch_size):
            stmt = (
                insert(Posting)
                .values(list(batch))
                .on_conflict_do_nothing(index_elements=["content_hash"])
                .returning(Posting.id)
            )
            inserted += len(conn.execute(stmt).all())
    return inserted


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=Path("data/raw/postings.csv"))
    parser.add_argument(
        "--background-rate",
        type=float,
        default=0.05,
        help="Share of non-internship postings to keep as hard negatives (default 0.05).",
    )
    args = parser.parse_args(argv)

    if not args.csv.exists():
        raise SystemExit(
            f"{args.csv} not found. Download the Kaggle LinkedIn job postings dataset "
            "and put postings.csv under data/raw/."
        )

    stats: Counter = Counter()
    engine = create_engine(database_url())
    postings = prepare_postings(read_csv(args.csv), args.background_rate, stats)
    inserted = insert_postings(engine, postings)
    kept = stats["kept_target"] + stats["kept_background"]
    stats["already_in_db"] = kept - inserted
    stats["inserted"] = inserted

    width = max(map(len, stats))
    for key in (
        "rows_read",
        "dropped_missing_text",
        "dropped_duplicate",
        "dropped_not_target",
        "kept_target",
        "kept_background",
        "already_in_db",
        "inserted",
    ):
        print(f"{key:<{width}}  {stats[key]:>8,}")


if __name__ == "__main__":
    main()
