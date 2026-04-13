"""Shared pytest fixtures for SkiPlannerAI API contract tests."""
import pytest
from httpx import ASGITransport, AsyncClient

from skiplanner_api.main import app


@pytest.fixture
def client():
    """Synchronous-style test client backed by ASGI transport (no real server)."""
    import httpx
    from starlette.testclient import TestClient

    with TestClient(app) as c:
        yield c
