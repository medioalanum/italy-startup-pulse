import os

import pytest


@pytest.fixture(scope="session")
def test_database_url() -> str:
    value = os.getenv("TEST_DATABASE_URL")
    if not value:
        pytest.skip("TEST_DATABASE_URL is not configured")
    if value == os.getenv("DATABASE_URL"):
        raise RuntimeError("TEST_DATABASE_URL must differ from DATABASE_URL")
    return value
