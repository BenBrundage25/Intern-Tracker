import pytest

from etl.clean import content_hash
from etl.filters import in_background_sample, is_target_role


@pytest.mark.parametrize(
    "title",
    [
        "Software Engineering Intern",
        "Summer 2025 Internship - Data Science",
        "Co-op, Mechanical Engineering",
        "New Grad Software Engineer",
        "Entry-Level Analyst",
        "Junior Developer",
        "Jr. Data Analyst",
        "Apprentice Electrician",
    ],
)
def test_target_titles(title):
    assert is_target_role(title, None)


@pytest.mark.parametrize(
    "title",
    ["Senior Software Engineer", "International Sales Manager", "Internal Auditor", "Director"],
)
def test_non_target_titles(title):
    assert not is_target_role(title, "Mid-Senior level")


@pytest.mark.parametrize("level", ["Internship", "Entry level", " entry LEVEL "])
def test_target_experience_levels(level):
    assert is_target_role("Analyst", level)


def test_background_sample_is_deterministic():
    digest = content_hash("Senior Engineer", "Acme", "desc")
    assert in_background_sample(digest, 0.3) == in_background_sample(digest, 0.3)


def test_background_sample_edges():
    digest = content_hash("Senior Engineer", "Acme", "desc")
    assert not in_background_sample(digest, 0)
    assert in_background_sample(digest, 1)


def test_background_sample_rate_is_roughly_respected():
    hashes = [content_hash(f"Job {i}", "Acme", "desc") for i in range(5000)]
    kept = sum(in_background_sample(h, 0.1) for h in hashes)
    assert 400 < kept < 600
