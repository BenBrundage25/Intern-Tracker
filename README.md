# Internship Tracker

Internship Tracker ranks internship postings against a resume using hybrid search, structured skill extraction, and a fine-tuned reranker.

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

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL
integration enabled, and save `postings.csv` from the
[LinkedIn job postings dataset](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings)
under `data/raw/`. Then:

```bash
make setup   # installs uv, Node 22, Ollama + model, Python deps, .env; starts and migrates Postgres
make load    # prints row counts for each cleaning/dedup step
make check   # lint + tests
make help    # every command
```

`make setup` is safe to re-run. It skips anything already installed.

`etl/load.py` keeps internships and entry-level roles, plus a deterministic 5% sample of
other postings (`--background-rate`) to serve as negatives during evaluation. Re-running it
is safe: postings already in the database are skipped by `content_hash`.

## Development workflow

1. Create a focused branch from `main`.
2. Make one coherent change and add tests where behavior changes.
3. Open a pull request that explains the decision, validation, and tradeoffs.
4. Merge only after the checks pass.

The initial environment checklist and decisions log are in [DECISIONS.md](DECISIONS.md).
