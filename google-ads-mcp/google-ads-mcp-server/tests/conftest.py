"""Shared fixtures for Google Ads MCP tests."""
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_headers():
    """Mock get_headers_with_auto_token to skip real OAuth."""
    with patch("server.get_headers_with_auto_token") as m:
        m.return_value = {
            "Authorization": "Bearer fake-token",
            "Developer-Token": "fake-dev-token",
            "Content-Type": "application/json",
        }
        yield m


@pytest.fixture
def mock_execute_gaql():
    """Mock execute_gaql for read tools."""
    with patch("server.execute_gaql") as m:
        yield m


@pytest.fixture
def mock_mutate_success():
    """Mock _mutate_resource returning success."""
    with patch("server._mutate_resource") as m:
        m.return_value = {
            "success": True,
            "results": [{"resourceName": "customers/3393382047/campaigns/123"}],
            "partialFailureError": None,
        }
        yield m


@pytest.fixture
def mock_mutate_error():
    """Mock _mutate_resource returning API error."""
    with patch("server._mutate_resource") as m:
        m.return_value = {
            "success": False,
            "error": 400,
            "reason": "Bad Request",
            "detail": {"error": {"message": "Invalid field"}},
        }
        yield m


@pytest.fixture
def mock_requests_post():
    """Mock requests.post for _mutate_resource integration tests."""
    with patch("server.requests.post") as m:
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = {
            "results": [{"resourceName": "customers/3393382047/campaigns/123"}]
        }
        m.return_value = resp
        yield m
