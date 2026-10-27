"""Configuration loaded from environment variables."""

import os


class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://REMOVED_USERNAME:REMOVED_PASSWORD@localhost:5433/revipote",
    )


settings = Settings()
