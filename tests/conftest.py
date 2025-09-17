import pytest
import httpx


@pytest.fixture
def query():
    return 'startsWith("B*27")'
