import pytest
import website


@pytest.fixture
def client():
    """A test client for the app."""
    with website.app.test_client() as client:
        yield client
