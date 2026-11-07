"""Configuration loaded from environment variables."""

import os


class Settings:
    def __init__(self) -> None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL doit être définie dans l'environnement."
            )

        jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret_key:
            raise RuntimeError(
                "JWT_SECRET_KEY doit être définie dans l'environnement."
            )

        self.database_url = database_url
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes = int(
            os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )


settings = Settings()