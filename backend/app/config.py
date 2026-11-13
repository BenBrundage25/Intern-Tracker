import os

DEFAULT_DATABASE_URL = "postgresql+psycopg://jobmatcher:jobmatcher@localhost:5432/jobmatcher"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
