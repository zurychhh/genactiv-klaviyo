"""Tests for helper functions: format_customer_id, _mutate_resource."""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add parent dir to path so we can import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock OAuth imports before importing server
with patch.dict(os.environ, {
    "GOOGLE_ADS_DEVELOPER_TOKEN": "test-token",
    "GOOGLE_ADS_OAUTH_CONFIG_PATH": "/tmp/fake.json",
}):
    from oauth.google_auth import format_customer_id


class TestFormatCustomerId:
    def test_strips_dashes(self):
        assert format_customer_id("339-338-2047") == "3393382047"

    def test_strips_quotes(self):
        assert format_customer_id('"339-338-2047"') == "3393382047"

    def test_pads_short_id(self):
        assert format_customer_id("123") == "0000000123"

    def test_already_formatted(self):
        assert format_customer_id("3393382047") == "3393382047"

    def test_integer_input(self):
        assert format_customer_id(3393382047) == "3393382047"


class TestMutateResource:
    def test_success(self, mock_headers, mock_requests_post):
        from server import _mutate_resource

        result = _mutate_resource(
            "3393382047", "campaigns", [{"create": {"name": "Test"}}]
        )
        assert result["success"] is True
        assert len(result["results"]) == 1
        mock_requests_post.assert_called_once()
        call_url = mock_requests_post.call_args[0][0]
        assert "campaigns:mutate" in call_url
        assert "3393382047" in call_url

    def test_with_manager_id(self, mock_headers, mock_requests_post):
        from server import _mutate_resource

        _mutate_resource(
            "3393382047", "campaigns", [{"create": {}}], manager_id="2538328866"
        )
        call_headers = mock_requests_post.call_args[1].get("headers") or mock_headers.return_value
        # Manager ID should be set on headers before the call
        mock_headers.assert_called_once()

    def test_api_error(self, mock_headers, mock_requests_post):
        from server import _mutate_resource

        resp = MagicMock()
        resp.ok = False
        resp.status_code = 400
        resp.reason = "Bad Request"
        resp.text = '{"error": "invalid"}'
        resp.json.return_value = {"error": "invalid"}
        mock_requests_post.return_value = resp

        result = _mutate_resource("3393382047", "campaigns", [{"create": {}}])
        assert result["success"] is False
        assert result["error"] == 400
