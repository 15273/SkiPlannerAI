"""Shared pytest fixtures for SkiPlannerAI API contract tests."""
import pytest
from starlette.testclient import TestClient

from skiplanner_api.main import app


@pytest.fixture(scope="session")
def client():
    """Session-scoped test client; lifespan runs once for the entire test session."""
    with TestClient(app) as c:
        yield c
