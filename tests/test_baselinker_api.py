"""
Exhaustive edge-case and crash tests for baselinker_api.py

Covers:
 - call_api: HTTP errors, API errors, malformed JSON, timeouts, network failures
 - get_orders: default date_from, custom date_from, empty results
 - get_order_payments_history: valid/invalid order IDs
 - get_order_sources: normal + error paths
 - print_json: unicode, None, nested data
 - CLI main block: all argv branches, missing arguments, invalid types
"""

import json
import sys
import os
import importlib
import types
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
from io import StringIO

import pytest
import requests


# ---------------------------------------------------------------------------
# Helpers to import the module fresh (it runs load_dotenv at import time)
# ---------------------------------------------------------------------------

def _import_baselinker():
    """Import baselinker_api from project root, reloading each time."""
    project_root = "/Users/user/projects/genactiv-klaviyo"
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # Force reimport so env var patches in conftest take effect
    if "baselinker_api" in sys.modules:
        del sys.modules["baselinker_api"]
    import baselinker_api
    return baselinker_api


# ===================================================================
# call_api
# ===================================================================

class TestCallApi:

    def test_successful_call(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("baselinker_api.requests.post", return_value=resp) as m:
            result = mod.call_api("getOrders", {"date_from": 0})
            assert result == {"status": "SUCCESS", "orders": []}
            m.assert_called_once()

    def test_http_error_returns_none(self, mock_response, capsys):
        mod = _import_baselinker()
        resp = mock_response(json_data=None, status_code=500, text="Internal Server Error")
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.call_api("getOrders")
            assert result is None
            out = capsys.readouterr().out
            assert "HTTP Error: 500" in out

    def test_api_error_returns_none(self, mock_response, capsys):
        mod = _import_baselinker()
        error_data = {
            "status": "ERROR",
            "error_code": "ERROR_INVALID_TOKEN",
            "error_message": "Invalid token",
        }
        resp = mock_response(json_data=error_data)
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.call_api("getOrders")
            assert result is None
            out = capsys.readouterr().out
            assert "ERROR_INVALID_TOKEN" in out

    def test_api_error_with_missing_error_fields(self, mock_response, capsys):
        """API returns ERROR status but no error_code or error_message."""
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "ERROR"})
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.call_api("getOrders")
            assert result is None
            out = capsys.readouterr().out
            assert "None" in out  # error_code and error_message are None

    def test_network_timeout(self):
        mod = _import_baselinker()
        with patch("baselinker_api.requests.post", side_effect=requests.exceptions.Timeout("timed out")):
            with pytest.raises(requests.exceptions.Timeout):
                mod.call_api("getOrders")

    def test_connection_error(self):
        mod = _import_baselinker()
        with patch("baselinker_api.requests.post", side_effect=requests.exceptions.ConnectionError("DNS fail")):
            with pytest.raises(requests.exceptions.ConnectionError):
                mod.call_api("getOrders")

    def test_malformed_json_response(self):
        """
        BUG FOUND: If the API returns 200 but non-JSON body, response.json()
        will raise json.JSONDecodeError, which is not caught by call_api.
        The function will crash instead of returning None.
        """
        mod = _import_baselinker()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        with patch("baselinker_api.requests.post", return_value=resp):
            with pytest.raises(json.JSONDecodeError):
                mod.call_api("getOrders")

    def test_parameters_none_defaults_to_empty_dict(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("baselinker_api.requests.post", return_value=resp) as m:
            mod.call_api("someMethod")
            posted_data = m.call_args[1].get("data") or m.call_args[0][1] if len(m.call_args[0]) > 1 else m.call_args[1].get("data")
            # Verify parameters key is "{}"
            actual_call = m.call_args
            assert json.loads(actual_call.kwargs.get("data", actual_call[1])["parameters"]) == {}

    def test_payload_contains_token_and_method(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("baselinker_api.requests.post", return_value=resp) as m:
            mod.call_api("getOrders", {"date_from": 123})
            args, kwargs = m.call_args
            payload = kwargs.get("data") or args[1]
            assert payload["method"] == "getOrders"
            assert json.loads(payload["parameters"]) == {"date_from": 123}

    def test_http_429_rate_limit(self, mock_response, capsys):
        """Rate-limited response should return None."""
        mod = _import_baselinker()
        resp = mock_response(json_data=None, status_code=429, text="Too Many Requests")
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.call_api("getOrders")
            assert result is None
            assert "429" in capsys.readouterr().out

    def test_http_403_forbidden(self, mock_response, capsys):
        mod = _import_baselinker()
        resp = mock_response(json_data=None, status_code=403, text="Forbidden")
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.call_api("getOrders")
            assert result is None

    def test_empty_200_response_crashes(self):
        """
        BUG FOUND: If the server returns 200 with an empty body,
        response.json() will raise, and there's no try/except.
        """
        mod = _import_baselinker()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        with patch("baselinker_api.requests.post", return_value=resp):
            with pytest.raises(json.JSONDecodeError):
                mod.call_api("getOrders")

    def test_unicode_in_parameters(self, mock_response):
        """Ensure Polish/unicode characters in params are handled."""
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("baselinker_api.requests.post", return_value=resp) as m:
            mod.call_api("someMethod", {"name": "Zdrowie i lek\u00f3w"})
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            assert params["name"] == "Zdrowie i lek\u00f3w"


# ===================================================================
# get_orders
# ===================================================================

class TestGetOrders:

    def test_default_date_from(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": [{"id": 1}]})
        with patch("baselinker_api.requests.post", return_value=resp) as m:
            result = mod.get_orders()
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            # date_from should be roughly 7 days ago
            now_ts = int(datetime.now().timestamp())
            seven_days_ago = now_ts - 7 * 86400
            assert abs(params["date_from"] - seven_days_ago) < 10
            assert params["get_unconfirmed_orders"] is True

    def test_custom_date_from(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("baselinker_api.requests.post", return_value=resp) as m:
            mod.get_orders(date_from=1000000)
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            assert params["date_from"] == 1000000

    def test_returns_none_on_error(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "ERROR", "error_code": "X", "error_message": "Y"})
        with patch("baselinker_api.requests.post", return_value=resp):
            assert mod.get_orders() is None

    def test_empty_orders_list(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.get_orders()
            assert result["orders"] == []

    def test_limit_param_not_used(self, mock_response):
        """get_orders accepts limit param but doesn't pass it to API — ensure no crash."""
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.get_orders(limit=100)
            assert result is not None


# ===================================================================
# get_order_payments_history
# ===================================================================

class TestGetOrderPaymentsHistory:

    def test_valid_order(self, mock_response):
        mod = _import_baselinker()
        payments_data = {
            "status": "SUCCESS",
            "payments": [
                {"payment_id": 1, "external_payment_id": "P24-X"}
            ],
        }
        resp = mock_response(json_data=payments_data)
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.get_order_payments_history(12345)
            assert result["payments"][0]["external_payment_id"] == "P24-X"

    def test_nonexistent_order(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "ERROR", "error_code": "ERROR_ORDER_NOT_FOUND", "error_message": "Not found"})
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.get_order_payments_history(99999999)
            assert result is None

    def test_zero_order_id(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS", "payments": []})
        with patch("baselinker_api.requests.post", return_value=resp) as m:
            mod.get_order_payments_history(0)
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            assert json.loads(payload["parameters"])["order_id"] == 0

    def test_negative_order_id(self, mock_response):
        """Negative IDs shouldn't crash — API will reject them."""
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "SUCCESS", "payments": []})
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.get_order_payments_history(-1)
            assert result is not None


# ===================================================================
# get_order_sources
# ===================================================================

class TestGetOrderSources:

    def test_success(self, mock_response):
        mod = _import_baselinker()
        sources_data = {"status": "SUCCESS", "sources": [{"source_id": 1, "name": "Shopify"}]}
        resp = mock_response(json_data=sources_data)
        with patch("baselinker_api.requests.post", return_value=resp):
            result = mod.get_order_sources()
            assert result["sources"][0]["name"] == "Shopify"

    def test_error(self, mock_response):
        mod = _import_baselinker()
        resp = mock_response(json_data={"status": "ERROR", "error_code": "X", "error_message": "Y"})
        with patch("baselinker_api.requests.post", return_value=resp):
            assert mod.get_order_sources() is None


# ===================================================================
# print_json
# ===================================================================

class TestPrintJson:

    def test_normal_dict(self, capsys):
        mod = _import_baselinker()
        mod.print_json({"key": "value"})
        out = capsys.readouterr().out
        assert '"key": "value"' in out

    def test_polish_unicode(self, capsys):
        mod = _import_baselinker()
        mod.print_json({"name": "\u0141\u00f3d\u017a"})
        out = capsys.readouterr().out
        assert "\u0141\u00f3d\u017a" in out  # ensure_ascii=False

    def test_none_value(self, capsys):
        mod = _import_baselinker()
        mod.print_json(None)
        out = capsys.readouterr().out
        assert "null" in out

    def test_empty_list(self, capsys):
        mod = _import_baselinker()
        mod.print_json([])
        out = capsys.readouterr().out
        assert "[]" in out

    def test_nested_deep(self, capsys):
        mod = _import_baselinker()
        data = {"a": {"b": {"c": {"d": [1, 2, 3]}}}}
        mod.print_json(data)
        out = capsys.readouterr().out
        assert '"d"' in out

    def test_huge_payload(self, capsys):
        """Ensure large data doesn't crash."""
        mod = _import_baselinker()
        data = {"items": [{"id": i, "name": f"item_{i}" * 100} for i in range(1000)]}
        mod.print_json(data)
        out = capsys.readouterr().out
        assert "item_999" in out


# ===================================================================
# CLI __main__ block
# ===================================================================

class TestCLI:

    def _run_main(self, argv_args, mock_post_response):
        """Helper: run the __main__ block of baselinker_api with given sys.argv."""
        mod = _import_baselinker()
        full_argv = ["baselinker_api.py"] + argv_args
        with patch("baselinker_api.requests.post", return_value=mock_post_response):
            with patch.object(sys, "argv", full_argv):
                # Re-execute __main__ block
                # We read the source and exec the __main__ guard
                import baselinker_api as bl
                source_path = bl.__file__
                with open(source_path) as f:
                    source = f.read()
                # Execute only the __main__ block
                code = compile(source, source_path, "exec")
                ns = {
                    "__name__": "__main__",
                    "__file__": source_path,
                }
                # Patch requests inside the new namespace
                with patch("requests.post", return_value=mock_post_response):
                    exec(code, ns)

    def test_orders_command(self, mock_response, capsys):
        resp = mock_response(json_data={
            "status": "SUCCESS",
            "orders": [
                {"order_id": 1, "shop_order_id": "100", "payment_method": "P24",
                 "payment_done": 1, "order_page": ""},
            ],
        })
        self._run_main(["orders"], resp)
        out = capsys.readouterr().out
        assert "1" in out

    def test_sources_command(self, mock_response, capsys):
        resp = mock_response(json_data={"status": "SUCCESS", "sources": [{"id": 1}]})
        self._run_main(["sources"], resp)
        out = capsys.readouterr().out
        assert "sources" in out.lower() or "1" in out

    def test_payments_command(self, mock_response, capsys):
        resp = mock_response(json_data={"status": "SUCCESS", "payments": [{"id": 1}]})
        self._run_main(["payments", "12345"], resp)
        out = capsys.readouterr().out
        assert "12345" in out or "payments" in out.lower()

    def test_payments_without_id_shows_help(self, mock_response, capsys):
        """'payments' without an order ID should show usage help, not crash."""
        resp = mock_response(json_data={"status": "SUCCESS"})
        self._run_main(["payments"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "payments" in out.lower()  # "Użycie:" contains "ycie"

    def test_full_command(self, mock_response, capsys):
        resp = mock_response(json_data={
            "status": "SUCCESS",
            "orders": [
                {"order_id": 1, "shop_order_id": "100", "payment_method": "P24"},
            ],
            "payments": [],
        })
        self._run_main(["full"], resp)
        out = capsys.readouterr().out
        assert "100" in out or "Zamówienie" in out

    def test_unknown_command_shows_usage(self, mock_response, capsys):
        resp = mock_response(json_data={"status": "SUCCESS"})
        self._run_main(["nonexistent"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "orders" in out.lower()

    def test_no_args_default_behavior(self, mock_response, capsys):
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        self._run_main([], resp)
        out = capsys.readouterr().out
        assert "Pobieranie" in out or "SUCCESS" in out

    def test_payments_non_numeric_id(self, mock_response):
        """
        BUG FOUND: 'payments abc' will crash with ValueError because
        int(sys.argv[2]) is called without try/except.
        """
        resp = mock_response(json_data={"status": "SUCCESS"})
        with pytest.raises(ValueError):
            self._run_main(["payments", "abc"], resp)

    def test_orders_with_empty_result(self, mock_response, capsys):
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        self._run_main(["orders"], resp)
        out = capsys.readouterr().out
        assert "0" in out  # "Znaleziono 0 zamówień"

    def test_orders_api_returns_none(self, mock_response, capsys):
        """When API returns error, get_orders returns None — CLI should handle it."""
        resp = mock_response(json_data={"status": "ERROR", "error_code": "X", "error_message": "Y"})
        self._run_main(["orders"], resp)
        out = capsys.readouterr().out
        # Should not crash — result is None, so the if result: block is skipped
        assert "X" in out or "API Error" in out
