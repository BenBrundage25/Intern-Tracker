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

- [ ] Docker Desktop:
- [ ] uv:
- [ ] Python:
- [ ] Node.js:
- [ ] Ollama:
- [ ] Local model pulled:
- [ ] GitHub repository:
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
