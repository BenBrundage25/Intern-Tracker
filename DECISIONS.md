# Decisions

This log records choices, evidence, and tradeoffs for the Job Matcher project.
It is intentionally part of the repository: explaining why a system was built
this way is as important as explaining what it does.

## How to use this file

For each meaningful decision, record:

- **Date**
- **Decision**
- **Context**
- **Alternatives considered**
- **Why we chose it**
- **How we will validate it**

## Week 0: environment

Complete this checklist locally and replace the placeholders with observed
versions. Do not record credentials, tokens, or other secrets.

Observed in WSL Ubuntu on 2026-11-12:

- [ ] Docker Desktop: not installed (enable WSL integration after installing)
- [x] uv: 0.12.21
- [x] Python: 3.12.3
- [ ] Node.js: 18.19.1 in WSL; needs 20+ before Week 7 frontend work
- [ ] Ollama: not installed
- [ ] Local model pulled:
- [x] GitHub repository: https://github.com/BenBrundage25/Intern-Tracker (public)
- [ ] Kaggle dataset download:

## Decision records

### D-001: Initial technology direction

- **Date:** 2026-11-12
- **Decision:** Use React + TypeScript, FastAPI, PostgreSQL + pgvector, Ollama
  for local LLM development, sentence-transformers for embeddings, and Docker
  Compose for local orchestration.
- **Context:** The project needs a low-cost local development path while
  retaining a credible production architecture.
- **Alternatives considered:** A hosted vector database, a hosted-only LLM
  workflow, and a single full-stack framework.
- **Why we chose it:** The selected tools are free or open source, expose the
  system's important engineering boundaries, and match the planned evaluation
  workflow.
- **How we will validate it:** Confirm that the Week 1 pipeline runs locally
  and that the Week 4 hybrid search can be measured end to end.

### D-002: Deduplicate on a normalized content hash

- **Date:** 2026-11-12
- **Decision:** `content_hash` is SHA-256 over cleaned title, company, and description,
  each lowercased with whitespace collapsed and joined by a separator character. It is a
  `UNIQUE` column, and inserts use `ON CONFLICT DO NOTHING`.
- **Context:** LinkedIn reposts the same job under new IDs, often with only formatting
  differences. Duplicates would inflate retrieval results and leak between eval splits.
- **Alternatives considered:** Dedup on source `job_id` (misses reposts); near-duplicate
  detection with MinHash or embeddings (catches more, but slower and needs tuning).
- **Why we chose it:** Exact hashing is cheap, deterministic, and makes the ETL idempotent.
  Company stays in the key so the same template posted by two employers is kept twice.
- **How we will validate it:** Record the duplicate count from the first full load. In
  Week 4, check for remaining near-duplicates by embedding similarity; add MinHash if
  there are many.

### D-003: Keep a deterministic background sample of non-internship postings

- **Date:** 2026-11-12
- **Decision:** Keep every posting whose experience level is Internship or Entry level, or
  whose title matches intern, co-op, new grad, junior, or similar. Keep about 5% of the
  rest, chosen by content hash rather than a random seed.
- **Context:** The product targets internships, but evaluation and reranker training need
  plausible negatives such as senior roles in the same field.
- **Alternatives considered:** Internships only (no hard negatives); a seeded random sample
  (shifts whenever row order or the filter changes).
- **Why we chose it:** Hash-based sampling gives the same postings on every run, so labels
  attached to postings stay valid across reloads.
- **How we will validate it:** Report the kept_target and kept_background counts after each
  load, and spot-check 50 target postings for false positives from the title regex.

### D-004: Schema additions beyond the original plan

- **Date:** 2026-11-12
- **Decision:** Add `source_job_id` and `experience_level` to `postings`. Make `source` part
  of the `labels` primary key. Add an index on `posting_skills.skill`.
- **Why:** `source_job_id` links each row back to Kaggle. `experience_level` feeds a
  frontend filter for free. Human and LLM labels on the same pair must coexist to compute
  Cohen's kappa in Week 5. The skill index supports skill-overlap scoring.

## Week 1 results

Fill in after the first full load (`uv run etl/load.py`):

- Rows read:
- Duplicates removed:
- Kept (target / background):
