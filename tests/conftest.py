"""
Shared fixtures for GenActiv Python script tests.
All external API calls are mocked — no real HTTP requests are made.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Environment isolation: make sure tests never use real tokens
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Ensure sensitive env vars are blank during every test."""
    monkeypatch.setenv("BASELINKER_TOKEN", "test-bl-token")
    monkeypatch.setenv("SHOPIFY_ACCESS_TOKEN", "test-shopify-token")
    monkeypatch.setenv("SHOPIFY_DOMAIN", "test-store.myshopify.com")
    monkeypatch.setenv("SHOPIFY_API_VERSION", "2024-01")


# ---------------------------------------------------------------------------
# Reusable mock response factory
# ---------------------------------------------------------------------------

class MockResponse:
    """Lightweight stand-in for requests.Response."""

    def __init__(self, json_data=None, status_code=200, text=None,
                 raise_for_json=False, raise_on_read=False):
        self._json_data = json_data
        self.status_code = status_code
        self.text = text if text is not None else (
            json.dumps(json_data) if json_data is not None else ""
        )
        self._raise_for_json = raise_for_json
        self._raise_on_read = raise_on_read

    def json(self):
        if self._raise_for_json:
            raise json.JSONDecodeError("Expecting value", "", 0)
        if self._json_data is not None:
            return self._json_data
        return json.loads(self.text)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


@pytest.fixture
def mock_response():
    """Factory fixture — call with kwargs to build a MockResponse."""
    return lambda **kw: MockResponse(**kw)


# ---------------------------------------------------------------------------
# Baselinker helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def bl_success_orders():
    """Sample successful Baselinker getOrders response."""
    return {
        "status": "SUCCESS",
        "orders": [
            {
                "order_id": 12345,
                "shop_order_id": "59138",
                "payment_method": "Przelewy24",
                "payment_done": 1,
                "email": "jan@example.com",
                "order_page": "",
            },
            {
                "order_id": 12346,
                "shop_order_id": "59139",
                "payment_method": "PayPo",
                "payment_done": 0,
                "email": "anna@example.com",
                "order_page": "",
            },
        ],
    }


@pytest.fixture
def bl_error_response():
    return {
        "status": "ERROR",
        "error_code": "ERROR_INVALID_TOKEN",
        "error_message": "Invalid API token",
    }


# ---------------------------------------------------------------------------
# Shopify GraphQL helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def shopify_orders_graphql_response():
    return {
        "data": {
            "orders": {
                "edges": [
                    {
                        "node": {
                            "id": "gid://shopify/Order/111",
                            "name": "#00059138",
                            "createdAt": "2026-04-20T10:00:00Z",
                            "totalPriceSet": {
                                "shopMoney": {"amount": "129.00", "currencyCode": "PLN"}
                            },
                            "displayFinancialStatus": "PAID",
                            "paymentGatewayNames": ["Przelewy24"],
                            "transactions": [
                                {
                                    "id": "gid://shopify/OrderTransaction/999",
                                    "kind": "SALE",
                                    "status": "SUCCESS",
                                    "gateway": "przelewy24",
                                    "formattedGateway": "Przelewy24",
                                    "createdAt": "2026-04-20T10:01:00Z",
                                    "amountSet": {
                                        "shopMoney": {"amount": "129.00", "currencyCode": "PLN"}
                                    },
                                    "paymentId": "P24-ABC-123",
                                    "receiptJson": "{}",
                                    "paymentDetails": None,
                                }
                            ],
                            "customer": {
                                "email": "jan@example.com",
                                "firstName": "Jan",
                                "lastName": "Kowalski",
                            },
                        }
                    }
                ]
            }
        }
    }


# ---------------------------------------------------------------------------
# Shopify Theme API helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def themes_list_response():
    return {
        "themes": [
            {"id": 100, "name": "GEN-6 global - slideshow", "role": "main"},
            {"id": 200, "name": "Draft theme", "role": "unpublished"},
        ]
    }


@pytest.fixture
def asset_response():
    return {
        "asset": {
            "key": "layout/theme.liquid",
            "value": "<html>{{ content_for_header }}</html>",
            "content_type": "text/html",
            "size": 42,
            "updated_at": "2026-04-20T10:00:00Z",
        }
    }


@pytest.fixture
def assets_list_response():
    return {
        "assets": [
            {"key": "layout/theme.liquid"},
            {"key": "snippets/breadcrumbs.liquid"},
            {"key": "assets/pandectes-settings.json"},
            {"key": "sections/header.liquid"},
            {"key": "templates/index.json"},
            {"key": "assets/style.css"},
            {"key": "assets/app.js"},
        ]
    }
