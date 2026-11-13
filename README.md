# Job Matcher

Job Matcher ranks internship postings against a resume using hybrid search, structured skill extraction, and a fine-tuned reranker.

## Project goals

- Build a working end-to-end application in small, reviewable pull requests.
- Measure retrieval quality on a held-out, human-labeled dataset.
- Keep the system inexpensive enough to run locally and deploy with free tiers.
- Make technical decisions and tradeoffs explicit in [DECISIONS.md](DECISIONS.md).

## Repository layout

```text
backend/   FastAPI service, database models, and API tests
etl/       Posting ingestion, cleaning, deduplication, and embedding jobs
ml/        Extraction, evaluation, and reranker experiments
frontend/  React + TypeScript application
infra/     Monitoring configuration
```

## Running locally

Requires Docker, [uv](https://docs.astral.sh/uv/), and the
[LinkedIn job postings dataset](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings)
with `postings.csv` saved under `data/raw/`.

```bash
cp .env.example .env
docker compose up -d postgres
uv sync
uv run alembic -c backend/alembic.ini upgrade head
uv run etl/load.py            # prints row counts for each cleaning/dedup step
uv run pytest
```

`etl/load.py` keeps internships and entry-level roles, plus a deterministic 5% sample of
other postings (`--background-rate`) to serve as negatives during evaluation. Re-running it
is safe: postings already in the database are skipped by `content_hash`.

## Development workflow

1. Create a focused branch from `main`.
2. Make one coherent change and add tests where behavior changes.
3. Open a pull request that explains the decision, validation, and tradeoffs.
4. Merge only after the checks pass.

The initial environment checklist and decisions log are in [DECISIONS.md](DECISIONS.md).
