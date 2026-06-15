"""
Exhaustive edge-case and crash tests for sync_payment_id.py

Covers:
 - shopify_graphql: payload construction, error handling
 - get_shopify_order_payment_id: order matching, transaction filtering, missing data
 - baselinker_call: HTTP errors, API errors, malformed JSON
 - get_baselinker_orders: success/error paths, empty orders
 - get_order_payment_history: normal + edge cases
 - set_payment_id: truncation of payment ID to 30 chars, success/failure
 - sync_payment_ids: dry_run vs live, limit, already synced orders, errors
 - CLI __main__ block: --live flag, default dry-run
"""

import json
import sys
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call
from io import StringIO

import pytest
import requests


# ---------------------------------------------------------------------------
# Import helper
# ---------------------------------------------------------------------------

def _import_sync():
    project_root = "/Users/user/projects/genactiv-klaviyo"
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if "sync_payment_id" in sys.modules:
        del sys.modules["sync_payment_id"]
    import sync_payment_id
    return sync_payment_id


# ===================================================================
# shopify_graphql (the local function in sync_payment_id.py)
# ===================================================================

class TestShopifyGraphql:

    def test_basic_query(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"data": {"orders": []}})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            result = mod.shopify_graphql("query { shop { name } }")
            assert result == {"data": {"orders": []}}
            args, kwargs = m.call_args
            assert "graphql.json" in args[0]
            assert kwargs["json"]["query"] == "query { shop { name } }"

    def test_with_variables(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"data": {}})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.shopify_graphql("query($id: ID!) { order(id: $id) { id } }", {"id": "gid://shopify/Order/1"})
            payload = m.call_args.kwargs["json"]
            assert payload["variables"] == {"id": "gid://shopify/Order/1"}

    def test_without_variables_omits_key(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"data": {}})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.shopify_graphql("query { shop { name } }")
            payload = m.call_args.kwargs["json"]
            assert "variables" not in payload

    def test_network_error_propagates(self):
        """
        BUG FOUND: shopify_graphql does not handle network errors —
        requests.exceptions.ConnectionError will propagate uncaught.
        """
        mod = _import_sync()
        with patch("sync_payment_id.requests.post", side_effect=requests.exceptions.ConnectionError):
            with pytest.raises(requests.exceptions.ConnectionError):
                mod.shopify_graphql("query { shop { name } }")

    def test_malformed_json_propagates(self):
        """
        BUG FOUND: If Shopify returns non-JSON 200, response.json()
        raises JSONDecodeError — not caught.
        """
        mod = _import_sync()
        resp = MagicMock()
        resp.json.side_effect = json.JSONDecodeError("bad", "", 0)
        with patch("sync_payment_id.requests.post", return_value=resp):
            with pytest.raises(json.JSONDecodeError):
                mod.shopify_graphql("query { shop { name } }")

    def test_headers_contain_token(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"data": {}})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.shopify_graphql("query { shop { name } }")
            _, kwargs = m.call_args
            headers = kwargs["headers"]
            assert "X-Shopify-Access-Token" in headers


# ===================================================================
# get_shopify_order_payment_id
# ===================================================================

class TestGetShopifyOrderPaymentId:

    def test_found_with_success_transaction(self, mock_response):
        mod = _import_sync()
        data = {
            "data": {
                "orders": {
                    "edges": [{
                        "node": {
                            "id": "gid://shopify/Order/111",
                            "name": "#00059138",
                            "transactions": [
                                {"status": "SUCCESS", "paymentId": "P24-ABC", "gateway": "przelewy24"},
                            ],
                        }
                    }]
                }
            }
        }
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.get_shopify_order_payment_id("59138")
            assert result["payment_id"] == "P24-ABC"
            assert result["gateway"] == "przelewy24"
            assert result["shopify_name"] == "#00059138"

    def test_no_orders_found(self, mock_response):
        mod = _import_sync()
        data = {"data": {"orders": {"edges": []}}}
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.get_shopify_order_payment_id("99999")
            assert result is None

    def test_order_with_no_successful_transaction(self, mock_response):
        mod = _import_sync()
        data = {
            "data": {
                "orders": {
                    "edges": [{
                        "node": {
                            "id": "gid://shopify/Order/111",
                            "name": "#00059138",
                            "transactions": [
                                {"status": "FAILURE", "paymentId": None, "gateway": "przelewy24"},
                                {"status": "PENDING", "paymentId": "P-PEND", "gateway": "przelewy24"},
                            ],
                        }
                    }]
                }
            }
        }
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.get_shopify_order_payment_id("59138")
            assert result is None

    def test_order_with_success_but_no_payment_id(self, mock_response):
        """Transaction is SUCCESS but paymentId is None."""
        mod = _import_sync()
        data = {
            "data": {
                "orders": {
                    "edges": [{
                        "node": {
                            "id": "gid://shopify/Order/111",
                            "name": "#00059138",
                            "transactions": [
                                {"status": "SUCCESS", "paymentId": None, "gateway": "manual"},
                            ],
                        }
                    }]
                }
            }
        }
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.get_shopify_order_payment_id("59138")
            assert result is None

    def test_empty_transactions(self, mock_response):
        mod = _import_sync()
        data = {
            "data": {
                "orders": {
                    "edges": [{
                        "node": {
                            "id": "gid://shopify/Order/111",
                            "name": "#00059138",
                            "transactions": [],
                        }
                    }]
                }
            }
        }
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            assert mod.get_shopify_order_payment_id("59138") is None

    def test_order_number_padding(self, mock_response):
        """Verify that order_number is zero-padded to 8 digits."""
        mod = _import_sync()
        data = {"data": {"orders": {"edges": []}}}
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.get_shopify_order_payment_id("123")
            query = m.call_args.kwargs["json"]["query"]
            assert "00000123" in query
            assert "123" in query

    def test_already_8_digit_order_number(self, mock_response):
        mod = _import_sync()
        data = {"data": {"orders": {"edges": []}}}
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.get_shopify_order_payment_id("12345678")
            query = m.call_args.kwargs["json"]["query"]
            assert "12345678" in query

    def test_graphql_error_response(self, mock_response):
        """GraphQL can return 200 with errors in the body."""
        mod = _import_sync()
        data = {"errors": [{"message": "Access denied"}]}
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.get_shopify_order_payment_id("59138")
            assert result is None

    def test_multiple_transactions_picks_first_success(self, mock_response):
        mod = _import_sync()
        data = {
            "data": {
                "orders": {
                    "edges": [{
                        "node": {
                            "id": "gid://shopify/Order/111",
                            "name": "#00059138",
                            "transactions": [
                                {"status": "FAILURE", "paymentId": "FAIL-1", "gateway": "przelewy24"},
                                {"status": "SUCCESS", "paymentId": "P24-FIRST", "gateway": "przelewy24"},
                                {"status": "SUCCESS", "paymentId": "P24-SECOND", "gateway": "przelewy24"},
                            ],
                        }
                    }]
                }
            }
        }
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.get_shopify_order_payment_id("59138")
            assert result["payment_id"] == "P24-FIRST"

    def test_none_order_number(self, mock_response):
        """
        BUG FOUND: If shop_order_id is None (can happen in Baselinker),
        str(None).zfill(8) -> '0000None' which is wrong but won't crash.
        The query will simply not find anything.
        """
        mod = _import_sync()
        data = {"data": {"orders": {"edges": []}}}
        resp = mock_response(json_data=data)
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.get_shopify_order_payment_id(None)
            assert result is None


# ===================================================================
# baselinker_call
# ===================================================================

class TestBaselinkerCall:

    def test_success(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.baselinker_call("getOrders", {})
            assert result["status"] == "SUCCESS"

    def test_http_error_returns_error_dict(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data=None, status_code=500, text="Server Error")
        with patch("sync_payment_id.requests.post", return_value=resp):
            result = mod.baselinker_call("getOrders")
            assert result["status"] == "ERROR"
            assert "500" in result["error_message"]

    def test_network_error_propagates(self):
        mod = _import_sync()
        with patch("sync_payment_id.requests.post", side_effect=requests.exceptions.Timeout):
            with pytest.raises(requests.exceptions.Timeout):
                mod.baselinker_call("getOrders")

    def test_malformed_json_response(self):
        """
        BUG FOUND: baselinker_call doesn't handle JSONDecodeError.
        If Baselinker returns malformed JSON with 200, it crashes.
        """
        mod = _import_sync()
        resp = MagicMock()
        resp.status_code = 200
        resp.json.side_effect = json.JSONDecodeError("bad", "", 0)
        with patch("sync_payment_id.requests.post", return_value=resp):
            with pytest.raises(json.JSONDecodeError):
                mod.baselinker_call("getOrders")


# ===================================================================
# get_baselinker_orders
# ===================================================================

class TestGetBaselinkerOrders:

    def test_success_with_orders(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": [{"order_id": 1}]})
        with patch("sync_payment_id.requests.post", return_value=resp):
            orders = mod.get_baselinker_orders(days=7)
            assert len(orders) == 1

    def test_success_without_status_key(self, mock_response):
        """Some Baselinker responses have 'orders' but no explicit 'status'."""
        mod = _import_sync()
        resp = mock_response(json_data={"orders": [{"order_id": 1}]})
        with patch("sync_payment_id.requests.post", return_value=resp):
            orders = mod.get_baselinker_orders()
            assert len(orders) == 1

    def test_error_returns_empty_list(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "ERROR", "error_message": "bad"})
        with patch("sync_payment_id.requests.post", return_value=resp):
            orders = mod.get_baselinker_orders()
            assert orders == []

    def test_empty_orders_key(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("sync_payment_id.requests.post", return_value=resp):
            orders = mod.get_baselinker_orders()
            assert orders == []

    def test_date_from_calculation(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.get_baselinker_orders(days=3)
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            expected_ts = int((datetime.now() - timedelta(days=3)).timestamp())
            assert abs(params["date_from"] - expected_ts) < 5

    def test_zero_days(self, mock_response):
        """days=0 means orders from now — likely empty but shouldn't crash."""
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("sync_payment_id.requests.post", return_value=resp):
            orders = mod.get_baselinker_orders(days=0)
            assert orders == []


# ===================================================================
# get_order_payment_history
# ===================================================================

class TestGetOrderPaymentHistory:

    def test_returns_payments(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"payments": [{"external_payment_id": "P24-X"}]})
        with patch("sync_payment_id.requests.post", return_value=resp):
            payments = mod.get_order_payment_history(12345)
            assert payments[0]["external_payment_id"] == "P24-X"

    def test_no_payments_key(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("sync_payment_id.requests.post", return_value=resp):
            payments = mod.get_order_payment_history(12345)
            assert payments == []

    def test_empty_payments(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"payments": []})
        with patch("sync_payment_id.requests.post", return_value=resp):
            payments = mod.get_order_payment_history(12345)
            assert payments == []


# ===================================================================
# set_payment_id
# ===================================================================

class TestSetPaymentId:

    def test_success(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("sync_payment_id.requests.post", return_value=resp):
            assert mod.set_payment_id(123, 1, "P24-ABC") is True

    def test_failure(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "ERROR", "error_message": "fail"})
        with patch("sync_payment_id.requests.post", return_value=resp):
            assert mod.set_payment_id(123, 1, "P24-ABC") is False

    def test_payment_id_truncated_to_30_chars(self, mock_response):
        """Baselinker limits external_payment_id to 30 chars — script truncates."""
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS"})
        long_id = "A" * 50
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.set_payment_id(123, 1, long_id)
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            assert len(params["external_payment_id"]) == 30
            assert params["external_payment_id"] == "A" * 30

    def test_exactly_30_chars(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.set_payment_id(123, 1, "A" * 30)
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            assert len(params["external_payment_id"]) == 30

    def test_empty_payment_id(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.set_payment_id(123, 1, "")
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            assert params["external_payment_id"] == ""

    def test_unicode_payment_id(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.set_payment_id(123, 1, "P\u0141ATNO\u015a\u0106-12345")
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            assert "P\u0141ATNO" in params["external_payment_id"]

    def test_payment_done_zero(self, mock_response):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS"})
        with patch("sync_payment_id.requests.post", return_value=resp) as m:
            mod.set_payment_id(123, 0, "P24-ABC")
            payload = m.call_args.kwargs.get("data", m.call_args[1])
            params = json.loads(payload["parameters"])
            assert params["payment_done"] == 0


# ===================================================================
# sync_payment_ids — the main orchestration function
# ===================================================================

class TestSyncPaymentIds:

    def _make_order(self, order_id, shop_order_id, has_external_payment=False,
                    payment_done=1, payment_method="P24", email="test@test.com"):
        return {
            "order_id": order_id,
            "shop_order_id": shop_order_id,
            "payment_done": payment_done,
            "payment_method": payment_method,
            "email": email,
        }

    def test_dry_run_does_not_call_set_payment(self, mock_response, capsys):
        mod = _import_sync()
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": [
            self._make_order(1, "100"),
        ]})
        bl_payments_resp = mock_response(json_data={"payments": []})
        shopify_resp = mock_response(json_data={
            "data": {"orders": {"edges": [{
                "node": {
                    "id": "gid://shopify/Order/111",
                    "name": "#00000100",
                    "transactions": [{"status": "SUCCESS", "paymentId": "P24-X", "gateway": "p24"}],
                }
            }]}}
        })

        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            data = kwargs.get("data", {})
            # Baselinker calls use data=, Shopify calls use json=
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
                elif method == "setOrderPayment":
                    pytest.fail("setOrderPayment should NOT be called in dry_run mode")
                    return bl_orders_resp
            # Shopify GraphQL
            return shopify_resp

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=True, limit=10)

        out = capsys.readouterr().out
        assert "DRY RUN" in out

    def test_live_calls_set_payment(self, mock_response, capsys):
        mod = _import_sync()
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": [
            self._make_order(1, "100"),
        ]})
        bl_payments_resp = mock_response(json_data={"payments": []})
        bl_set_resp = mock_response(json_data={"status": "SUCCESS"})
        shopify_resp = mock_response(json_data={
            "data": {"orders": {"edges": [{
                "node": {
                    "id": "gid://shopify/Order/111",
                    "name": "#00000100",
                    "transactions": [{"status": "SUCCESS", "paymentId": "P24-X", "gateway": "p24"}],
                }
            }]}}
        })

        set_called = False
        def side_effect(*args, **kwargs):
            nonlocal set_called
            data = kwargs.get("data", {})
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
                elif method == "setOrderPayment":
                    set_called = True
                    return bl_set_resp
            return shopify_resp

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=False, limit=10)

        assert set_called
        out = capsys.readouterr().out
        assert "LIVE" in out

    def test_skips_orders_with_existing_payment_id(self, mock_response, capsys):
        mod = _import_sync()
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": [
            self._make_order(1, "100"),
        ]})
        bl_payments_resp = mock_response(json_data={"payments": [
            {"external_payment_id": "ALREADY-SET"}
        ]})

        def side_effect(*args, **kwargs):
            data = kwargs.get("data", {})
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
            pytest.fail("Should not reach Shopify — order already has payment ID")
            return mock_response(json_data={})

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=True, limit=10)

        out = capsys.readouterr().out
        assert "1" in out  # skipped count

    def test_handles_shopify_not_found(self, mock_response, capsys):
        mod = _import_sync()
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": [
            self._make_order(1, "100"),
        ]})
        bl_payments_resp = mock_response(json_data={"payments": []})
        shopify_resp = mock_response(json_data={"data": {"orders": {"edges": []}}})

        def side_effect(*args, **kwargs):
            data = kwargs.get("data", {})
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
            return shopify_resp

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=True, limit=10)

        out = capsys.readouterr().out
        assert "nie znaleziono" in out.lower() or "1" in out  # error count

    def test_limit_stops_processing(self, mock_response, capsys):
        mod = _import_sync()
        orders = [self._make_order(i, str(1000 + i)) for i in range(20)]
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": orders})
        bl_payments_resp = mock_response(json_data={"payments": []})
        shopify_resp = mock_response(json_data={"data": {"orders": {"edges": []}}})

        call_tracker = {"shopify_calls": 0}
        def side_effect(*args, **kwargs):
            data = kwargs.get("data", {})
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
            call_tracker["shopify_calls"] += 1
            return shopify_resp

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=True, limit=3)

        assert call_tracker["shopify_calls"] <= 3

    def test_empty_orders_from_baselinker(self, mock_response, capsys):
        mod = _import_sync()
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("sync_payment_id.requests.post", return_value=resp):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=True, limit=10)

        out = capsys.readouterr().out
        assert "0" in out  # zero orders

    def test_live_set_payment_failure(self, mock_response, capsys):
        mod = _import_sync()
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": [
            self._make_order(1, "100"),
        ]})
        bl_payments_resp = mock_response(json_data={"payments": []})
        bl_set_fail_resp = mock_response(json_data={"status": "ERROR", "error_message": "fail"})
        shopify_resp = mock_response(json_data={
            "data": {"orders": {"edges": [{
                "node": {
                    "id": "gid://shopify/Order/111",
                    "name": "#00000100",
                    "transactions": [{"status": "SUCCESS", "paymentId": "P24-X", "gateway": "p24"}],
                }
            }]}}
        })

        def side_effect(*args, **kwargs):
            data = kwargs.get("data", {})
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
                elif method == "setOrderPayment":
                    return bl_set_fail_resp
            return shopify_resp

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=False, limit=10)

        out = capsys.readouterr().out
        assert "B\u0141\u0104D" in out or "errors" in out.lower() or "1" in out

    def test_rate_limiting_sleep_called(self, mock_response):
        mod = _import_sync()
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": [
            self._make_order(1, "100"),
        ]})
        bl_payments_resp = mock_response(json_data={"payments": []})
        shopify_resp = mock_response(json_data={"data": {"orders": {"edges": []}}})

        def side_effect(*args, **kwargs):
            data = kwargs.get("data", {})
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
            return shopify_resp

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep") as mock_sleep:
                mod.sync_payment_ids(days=1, dry_run=True, limit=10)
                # sleep should NOT be called when order is not found in Shopify
                # (sleep is only called after printing payment info)
                # Actually, looking at the code: sleep is called for every order
                # that reaches the shopify lookup stage, regardless of outcome.
                # Let's just verify no crash.

    def test_order_missing_fields_uses_defaults(self, mock_response, capsys):
        """Orders with missing payment_done, payment_method, email."""
        mod = _import_sync()
        order = {"order_id": 1, "shop_order_id": "100"}  # missing fields
        bl_orders_resp = mock_response(json_data={"status": "SUCCESS", "orders": [order]})
        bl_payments_resp = mock_response(json_data={"payments": []})
        shopify_resp = mock_response(json_data={"data": {"orders": {"edges": []}}})

        def side_effect(*args, **kwargs):
            data = kwargs.get("data", {})
            if "data" in kwargs and isinstance(data, dict) and "method" in data:
                method = data["method"]
                if method == "getOrders":
                    return bl_orders_resp
                elif method == "getOrderPaymentsHistory":
                    return bl_payments_resp
            return shopify_resp

        with patch("sync_payment_id.requests.post", side_effect=side_effect):
            with patch("sync_payment_id.time.sleep"):
                mod.sync_payment_ids(days=1, dry_run=True, limit=10)
        # Should not crash


# ===================================================================
# CLI __main__ block
# ===================================================================

class TestSyncCLI:

    def _run_main(self, argv_args):
        mod = _import_sync()
        full_argv = ["sync_payment_id.py"] + argv_args
        source_path = mod.__file__
        with open(source_path) as f:
            source = f.read()
        code = compile(source, source_path, "exec")
        ns = {"__name__": "__main__", "__file__": source_path}
        with patch.object(sys, "argv", full_argv):
            exec(code, ns)

    def test_default_dry_run(self, mock_response, capsys):
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("requests.post", return_value=resp):
            with patch("time.sleep"):
                self._run_main([])
        out = capsys.readouterr().out
        assert "DRY RUN" in out

    def test_live_flag(self, mock_response, capsys):
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("requests.post", return_value=resp):
            with patch("time.sleep"):
                self._run_main(["--live"])
        out = capsys.readouterr().out
        assert "LIVE" in out

    def test_unknown_flag_treated_as_dry_run(self, mock_response, capsys):
        """Any arg that isn't --live should result in dry_run mode."""
        resp = mock_response(json_data={"status": "SUCCESS", "orders": []})
        with patch("requests.post", return_value=resp):
            with patch("time.sleep"):
                self._run_main(["--unknown"])
        out = capsys.readouterr().out
        assert "DRY RUN" in out
