
"""Configuration loaded from environment variables."""

import os


class Settings:
    def __init__(self) -> None:
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError(
                "DATABASE_URL doit être définie dans l'environnement."
            )

        self.database_url = database_url


settings = Settings()
