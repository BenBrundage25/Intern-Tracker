import os

DEFAULT_DATABASE_URL = "postgresql+psycopg://interntracker:interntracker@localhost:5432/interntracker"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
