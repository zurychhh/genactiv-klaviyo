"""
Exhaustive edge-case and crash tests for shopify_graphql.py

Covers:
 - execute_query: payload, headers, HTTP errors, malformed JSON, timeouts
 - get_orders_with_transactions: query structure, variable passing
 - get_single_order_transactions: order_id formats, edge cases
 - get_installed_apps: normal flow
 - print_json: unicode, None, huge data
 - CLI __main__ block: all commands, missing args, unknown commands
"""

import json
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

import pytest
import requests


# ---------------------------------------------------------------------------
# Import helper
# ---------------------------------------------------------------------------

def _import_shopify_gql():
    project_root = "/Users/user/projects/genactiv-klaviyo"
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if "shopify_graphql" in sys.modules:
        del sys.modules["shopify_graphql"]
    import shopify_graphql
    return shopify_graphql


# ===================================================================
# execute_query
# ===================================================================

class TestExecuteQuery:

    def test_basic_query(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {"shop": {"name": "GenActiv"}}})
        with patch("shopify_graphql.requests.post", return_value=resp) as m:
            result = mod.execute_query("query { shop { name } }")
            assert result == {"data": {"shop": {"name": "GenActiv"}}}
            args, kwargs = m.call_args
            assert "graphql.json" in args[0]
            assert kwargs["json"]["query"] == "query { shop { name } }"
            assert kwargs["headers"]["X-Shopify-Access-Token"] is not None

    def test_with_variables(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {}})
        with patch("shopify_graphql.requests.post", return_value=resp) as m:
            mod.execute_query("query($id: ID!) { order(id: $id) { id } }", {"id": "gid://shopify/Order/1"})
            payload = m.call_args.kwargs["json"]
            assert payload["variables"]["id"] == "gid://shopify/Order/1"

    def test_without_variables_no_key(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {}})
        with patch("shopify_graphql.requests.post", return_value=resp) as m:
            mod.execute_query("query { shop { name } }")
            payload = m.call_args.kwargs["json"]
            assert "variables" not in payload

    def test_http_404_returns_none(self, mock_response, capsys):
        mod = _import_shopify_gql()
        resp = mock_response(json_data=None, status_code=404, text="Not Found")
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.execute_query("query { shop { name } }")
            assert result is None
            out = capsys.readouterr().out
            assert "404" in out

    def test_http_401_returns_none(self, mock_response, capsys):
        mod = _import_shopify_gql()
        resp = mock_response(json_data=None, status_code=401, text='{"errors":"Unauthorized"}')
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.execute_query("query { shop { name } }")
            assert result is None
            out = capsys.readouterr().out
            assert "401" in out

    def test_http_500_returns_none(self, mock_response, capsys):
        mod = _import_shopify_gql()
        resp = mock_response(json_data=None, status_code=500, text="Internal Server Error")
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.execute_query("query { shop { name } }")
            assert result is None

    def test_http_429_rate_limit(self, mock_response, capsys):
        mod = _import_shopify_gql()
        resp = mock_response(json_data=None, status_code=429, text="Throttled")
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.execute_query("query { shop { name } }")
            assert result is None
            out = capsys.readouterr().out
            assert "429" in out

    def test_timeout_propagates(self):
        mod = _import_shopify_gql()
        with patch("shopify_graphql.requests.post", side_effect=requests.exceptions.Timeout("timeout")):
            with pytest.raises(requests.exceptions.Timeout):
                mod.execute_query("query { shop { name } }")

    def test_connection_error_propagates(self):
        mod = _import_shopify_gql()
        with patch("shopify_graphql.requests.post", side_effect=requests.exceptions.ConnectionError):
            with pytest.raises(requests.exceptions.ConnectionError):
                mod.execute_query("query { shop { name } }")

    def test_malformed_json_response(self):
        """
        BUG FOUND: If Shopify returns 200 with non-JSON body,
        response.json() raises JSONDecodeError — not caught.
        """
        mod = _import_shopify_gql()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = json.JSONDecodeError("bad", "", 0)
        with patch("shopify_graphql.requests.post", return_value=resp):
            with pytest.raises(json.JSONDecodeError):
                mod.execute_query("query { shop { name } }")

    def test_empty_query_string(self, mock_response):
        """Empty query should still be sent — API will reject it."""
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"errors": [{"message": "Parse error"}]})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.execute_query("")
            assert "errors" in result

    def test_graphql_error_in_response(self, mock_response):
        """GraphQL errors (200 OK but with errors key)."""
        mod = _import_shopify_gql()
        resp = mock_response(json_data={
            "data": None,
            "errors": [{"message": "Field 'nonexistent' doesn't exist"}],
        })
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.execute_query("query { nonexistent }")
            assert result is not None
            assert "errors" in result

    def test_endpoint_url_construction(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {}})
        with patch("shopify_graphql.requests.post", return_value=resp) as m:
            mod.execute_query("query { shop { name } }")
            url = m.call_args[0][0]
            assert "myshopify.com/admin/api/" in url
            assert "/graphql.json" in url


# ===================================================================
# get_orders_with_transactions
# ===================================================================

class TestGetOrdersWithTransactions:

    def test_default_limit(self, mock_response, shopify_orders_graphql_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data=shopify_orders_graphql_response)
        with patch("shopify_graphql.requests.post", return_value=resp) as m:
            result = mod.get_orders_with_transactions()
            # Default limit = 5
            payload = m.call_args.kwargs["json"]
            assert payload["variables"]["first"] == 5

    def test_custom_limit(self, mock_response, shopify_orders_graphql_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data=shopify_orders_graphql_response)
        with patch("shopify_graphql.requests.post", return_value=resp) as m:
            mod.get_orders_with_transactions(limit=20)
            payload = m.call_args.kwargs["json"]
            assert payload["variables"]["first"] == 20

    def test_zero_limit(self, mock_response):
        """Shopify API may reject 0 — but the script shouldn't crash."""
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {"orders": {"edges": []}}})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_orders_with_transactions(limit=0)
            assert result is not None

    def test_negative_limit(self, mock_response):
        """Negative limit — API will reject, but script should pass it through."""
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"errors": [{"message": "Value is invalid"}]})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_orders_with_transactions(limit=-1)
            assert result is not None  # returns error response, not None

    def test_returns_transaction_data(self, mock_response, shopify_orders_graphql_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data=shopify_orders_graphql_response)
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_orders_with_transactions(5)
            edges = result["data"]["orders"]["edges"]
            assert len(edges) == 1
            txns = edges[0]["node"]["transactions"]
            assert txns[0]["paymentId"] == "P24-ABC-123"

    def test_empty_orders(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {"orders": {"edges": []}}})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_orders_with_transactions()
            assert result["data"]["orders"]["edges"] == []


# ===================================================================
# get_single_order_transactions
# ===================================================================

class TestGetSingleOrderTransactions:

    def test_valid_gid(self, mock_response):
        mod = _import_shopify_gql()
        order_data = {
            "data": {
                "order": {
                    "id": "gid://shopify/Order/111",
                    "name": "#00059138",
                    "transactions": [
                        {"id": "gid://shopify/OrderTransaction/999", "status": "SUCCESS",
                         "paymentId": "P24-X", "kind": "SALE"},
                    ],
                }
            }
        }
        resp = mock_response(json_data=order_data)
        with patch("shopify_graphql.requests.post", return_value=resp) as m:
            result = mod.get_single_order_transactions("gid://shopify/Order/111")
            payload = m.call_args.kwargs["json"]
            assert payload["variables"]["id"] == "gid://shopify/Order/111"
            assert result["data"]["order"]["name"] == "#00059138"

    def test_nonexistent_order(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {"order": None}})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_single_order_transactions("gid://shopify/Order/99999999")
            assert result["data"]["order"] is None

    def test_invalid_gid_format(self, mock_response):
        """Non-GID string — API will reject, but script should not crash."""
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"errors": [{"message": "invalid id"}]})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_single_order_transactions("not-a-gid")
            assert "errors" in result

    def test_empty_string_gid(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"errors": [{"message": "invalid id"}]})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_single_order_transactions("")
            assert result is not None

    def test_unicode_in_gid(self, mock_response):
        """Unlikely but shouldn't crash."""
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"errors": [{"message": "invalid"}]})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_single_order_transactions("gid://shopify/Order/\u0141\u00f3d\u017a")
            assert result is not None


# ===================================================================
# get_installed_apps
# ===================================================================

class TestGetInstalledApps:

    def test_returns_apps(self, mock_response):
        mod = _import_shopify_gql()
        apps_data = {
            "data": {
                "currentAppInstallation": {
                    "id": "gid://shopify/AppInstallation/1",
                    "app": {"title": "Test App", "handle": "test", "apiKey": "abc"},
                },
                "appInstallations": {"edges": []},
            }
        }
        resp = mock_response(json_data=apps_data)
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_installed_apps()
            assert result["data"]["currentAppInstallation"]["app"]["title"] == "Test App"

    def test_no_apps(self, mock_response):
        mod = _import_shopify_gql()
        resp = mock_response(json_data={"data": {"currentAppInstallation": None, "appInstallations": {"edges": []}}})
        with patch("shopify_graphql.requests.post", return_value=resp):
            result = mod.get_installed_apps()
            assert result["data"]["appInstallations"]["edges"] == []


# ===================================================================
# print_json
# ===================================================================

class TestPrintJson:

    def test_normal(self, capsys):
        mod = _import_shopify_gql()
        mod.print_json({"key": "val"})
        assert '"key"' in capsys.readouterr().out

    def test_none(self, capsys):
        mod = _import_shopify_gql()
        mod.print_json(None)
        assert "null" in capsys.readouterr().out

    def test_polish_chars(self, capsys):
        mod = _import_shopify_gql()
        mod.print_json({"name": "\u0141\u00f3d\u017a"})
        out = capsys.readouterr().out
        assert "\u0141\u00f3d\u017a" in out  # ensure_ascii=False

    def test_empty_dict(self, capsys):
        mod = _import_shopify_gql()
        mod.print_json({})
        assert "{}" in capsys.readouterr().out

    def test_deeply_nested(self, capsys):
        mod = _import_shopify_gql()
        data = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        mod.print_json(data)
        assert "deep" in capsys.readouterr().out


# ===================================================================
# CLI __main__ block
# ===================================================================

class TestCLI:

    def _run_main(self, argv_args, mock_post_response):
        mod = _import_shopify_gql()
        full_argv = ["shopify_graphql.py"] + argv_args
        source_path = mod.__file__
        with open(source_path) as f:
            source = f.read()
        code = compile(source, source_path, "exec")
        ns = {"__name__": "__main__", "__file__": source_path}
        with patch.object(sys, "argv", full_argv):
            with patch("requests.post", return_value=mock_post_response):
                exec(code, ns)

    def test_orders_command(self, mock_response, capsys, shopify_orders_graphql_response):
        resp = mock_response(json_data=shopify_orders_graphql_response)
        self._run_main(["orders"], resp)
        out = capsys.readouterr().out
        assert "P24-ABC-123" in out or "59138" in out

    def test_order_command(self, mock_response, capsys):
        resp = mock_response(json_data={
            "data": {"order": {"id": "gid://shopify/Order/111", "name": "#00059138", "transactions": []}}
        })
        self._run_main(["order", "gid://shopify/Order/111"], resp)
        out = capsys.readouterr().out
        assert "59138" in out

    def test_order_without_id_shows_help(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["order"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "order" in out.lower()

    def test_apps_command(self, mock_response, capsys):
        resp = mock_response(json_data={
            "data": {
                "currentAppInstallation": None,
                "appInstallations": {"edges": []},
            }
        })
        self._run_main(["apps"], resp)
        out = capsys.readouterr().out
        assert "appInstallations" in out or "aplikacj" in out.lower()

    def test_unknown_command_shows_help(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["unknown"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "orders" in out.lower()

    def test_no_args_default(self, mock_response, capsys, shopify_orders_graphql_response):
        resp = mock_response(json_data=shopify_orders_graphql_response)
        self._run_main([], resp)
        out = capsys.readouterr().out
        assert "Pobieranie" in out or "P24-ABC-123" in out

    def test_orders_with_none_result(self, mock_response, capsys):
        """
        BUG FOUND: If execute_query returns None (HTTP error), print_json(None)
        will print 'null' — not a crash, but potentially confusing.
        """
        resp = mock_response(json_data=None, status_code=500, text="Error")
        self._run_main(["orders"], resp)
        out = capsys.readouterr().out
        assert "null" in out or "500" in out
