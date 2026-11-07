
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def db_session():
    """Provide an isolated PostgreSQL transaction for each test."""
    database_url = os.environ.get("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("TEST_DATABASE_URL n'est pas définie")

    if not database_url.startswith("postgresql"):
        pytest.fail("TEST_DATABASE_URL doit pointer vers PostgreSQL")

    engine = create_engine(database_url)

    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            session = Session(
                bind=connection,
                join_transaction_mode="create_savepoint",
            )

            try:
                yield session
            finally:
                session.close()
                if transaction.is_active:
                    transaction.rollback()
    finally:
        engine.dispose()
