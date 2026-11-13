from collections import Counter
from datetime import UTC, datetime

from etl.load import parse_epoch_ms, prepare_postings


def row(**overrides) -> dict[str, str]:
    base = {
        "job_id": "1",
        "title": "Software Engineering Intern",
        "company_name": "Acme",
        "location": "Austin, TX",
        "description": "<p>Write Python.</p>",
        "formatted_experience_level": "Internship",
        "listed_time": "1713397508000.0",
        "job_posting_url": "https://example.com/1",
    }
    return base | overrides


def run(rows, rate=0.0):
    stats: Counter = Counter()
    return list(prepare_postings(rows, rate, stats)), stats


def test_cleans_and_maps_fields():
    [posting], _ = run([row()])
    assert posting["title"] == "Software Engineering Intern"
    assert posting["description"] == "Write Python."
    assert posting["source_job_id"] == "1"
    assert posting["posted_at"] == datetime(2024, 4, 17, 23, 45, 8, tzinfo=UTC)
    assert len(posting["content_hash"]) == 64


def test_drops_duplicates_that_differ_only_in_formatting():
    rows = [
        row(job_id="1"),
        row(job_id="2", description="<div>Write   Python.</div>"),
        row(job_id="3", title="SOFTWARE ENGINEERING INTERN"),
    ]
    postings, stats = run(rows)
    assert [p["source_job_id"] for p in postings] == ["1"]
    assert stats["dropped_duplicate"] == 2


def test_keeps_reposts_at_different_companies():
    postings, _ = run([row(job_id="1"), row(job_id="2", company_name="Globex")])
    assert len(postings) == 2


def test_drops_rows_without_text():
    postings, stats = run([row(description=""), row(title="<br>")])
    assert postings == []
    assert stats["dropped_missing_text"] == 2


def test_filters_non_target_roles():
    senior = row(title="Senior Engineer", formatted_experience_level="Mid-Senior level")
    postings, stats = run([senior], rate=0.0)
    assert postings == []
    assert stats["dropped_not_target"] == 1

    postings, stats = run([senior], rate=1.0)
    assert len(postings) == 1
    assert stats["kept_background"] == 1


def test_blank_optional_fields_become_none():
    [posting], _ = run([row(company_name="", location=" ", listed_time="", job_posting_url="")])
    assert posting["company"] is None
    assert posting["location"] is None
    assert posting["posted_at"] is None
    assert posting["url"] is None


def test_parse_epoch_ms_bad_values():
    assert parse_epoch_ms("not a number") is None
    assert parse_epoch_ms(None) is None
