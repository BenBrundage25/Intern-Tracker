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

## Development workflow

1. Create a focused branch from `main`.
2. Make one coherent change and add tests where behavior changes.
3. Open a pull request that explains the decision, validation, and tradeoffs.
4. Merge only after the checks pass.

The initial environment checklist and decisions log are in [DECISIONS.md](DECISIONS.md).
