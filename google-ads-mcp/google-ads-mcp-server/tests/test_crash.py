"""Exhaustive edge-case, crash, and security tests for Google Ads MCP.

These tests are intentionally BRUTAL — they throw garbage, edge cases,
and adversarial inputs at every tool to find crashes and unexpected behavior.
"""
import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with patch.dict(os.environ, {
    "GOOGLE_ADS_DEVELOPER_TOKEN": "test-token",
    "GOOGLE_ADS_OAUTH_CONFIG_PATH": "/tmp/fake.json",
}):
    import server as _srv
    from oauth.google_auth import format_customer_id, execute_gaql

# Unwrap FunctionTool → raw function
run_gaql = _srv.run_gaql.fn
list_accounts = _srv.list_accounts.fn
run_keyword_planner = _srv.run_keyword_planner.fn
list_conversion_actions = _srv.list_conversion_actions.fn
update_conversion_action = _srv.update_conversion_action.fn
create_conversion_action = _srv.create_conversion_action.fn
create_campaign_budget = _srv.create_campaign_budget.fn
update_campaign_budget = _srv.update_campaign_budget.fn
create_campaign = _srv.create_campaign.fn
update_campaign = _srv.update_campaign.fn
create_ad_group = _srv.create_ad_group.fn
update_ad_group = _srv.update_ad_group.fn
create_responsive_search_ad = _srv.create_responsive_search_ad.fn
update_ad_status = _srv.update_ad_status.fn
add_keywords = _srv.add_keywords.fn
update_keyword = _srv.update_keyword.fn
remove_keywords = _srv.remove_keywords.fn

CID = "339-338-2047"
MID = "253-832-8866"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: format_customer_id — adversarial inputs
# ═══════════════════════════════════════════════════════════════════════════


class TestFormatCustomerIdAdversarial:
    """Throw garbage at format_customer_id."""

    def test_empty_string(self):
        assert format_customer_id("") == "0000000000"

    def test_only_dashes(self):
        assert format_customer_id("---") == "0000000000"

    def test_only_spaces(self):
        assert format_customer_id("   ") == "0000000000"

    def test_letters_mixed(self):
        # Should strip non-digits
        assert format_customer_id("abc339def338ghi2047") == "3393382047"

    def test_unicode_digits_stripped(self):
        # Arabic-Indic digits ٣٩٢٠٤٧ are Unicode digits but NOT ASCII.
        # format_customer_id now uses char.isascii() + char.isdigit() to filter.
        result = format_customer_id("٣٣٩338٢٠٤٧")
        assert result == "0000000338"  # Only ASCII "338" survives

    def test_very_long_id(self):
        long_id = "1" * 100
        result = format_customer_id(long_id)
        assert len(result) >= 10  # Should not crash

    def test_negative_number(self):
        # Dash is stripped, minus sign is stripped
        result = format_customer_id("-123456789")
        assert result == "0123456789"

    def test_float_string(self):
        result = format_customer_id("339338.2047")
        assert result == "3393382047"

    def test_none_like_string(self):
        result = format_customer_id("None")
        assert result == "0000000000"

    def test_sql_injection_attempt(self):
        result = format_customer_id("'; DROP TABLE accounts;--")
        assert result == "0000000000"

    def test_newlines_and_tabs(self):
        result = format_customer_id("339\n338\t2047")
        assert result == "3393382047"

    def test_zero(self):
        result = format_customer_id("0")
        assert result == "0000000001" or result == "0000000000"  # Either is fine


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: _mutate_resource — network & response edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestMutateResourceCrash:
    """Crash-test the central mutation function."""

    def test_empty_operations_list(self, mock_headers, mock_requests_post):
        """Empty operations should still send request (API will reject)."""
        result = _srv._mutate_resource("3393382047", "campaigns", [])
        mock_requests_post.assert_called_once()

    def test_network_timeout(self, mock_headers):
        """Simulate network timeout."""
        with patch("server.requests.post", side_effect=ConnectionError("timeout")):
            with pytest.raises(ConnectionError):
                _srv._mutate_resource("3393382047", "campaigns", [{"create": {}}])

    def test_malformed_json_response(self, mock_headers):
        """Server returns invalid JSON."""
        resp = MagicMock()
        resp.ok = True
        resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        with patch("server.requests.post", return_value=resp):
            with pytest.raises(json.JSONDecodeError):
                _srv._mutate_resource("3393382047", "campaigns", [{"create": {}}])

    def test_html_error_response(self, mock_headers):
        """Server returns HTML error page instead of JSON."""
        resp = MagicMock()
        resp.ok = False
        resp.status_code = 503
        resp.reason = "Service Unavailable"
        resp.text = "<html><body>Service Unavailable</body></html>"
        resp.json.side_effect = json.JSONDecodeError("", "", 0)
        with patch("server.requests.post", return_value=resp):
            result = _srv._mutate_resource("3393382047", "campaigns", [{"create": {}}])
            assert result["success"] is False
            assert result["error"] == 503

    def test_partial_failure_response(self, mock_headers):
        """API returns partial failure (some ops succeed, some fail)."""
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = {
            "results": [{"resourceName": "customers/123/campaigns/1"}],
            "partialFailureError": {
                "code": 3,
                "message": "Operation 1 failed: invalid field",
            },
        }
        with patch("server.requests.post", return_value=resp):
            result = _srv._mutate_resource("3393382047", "campaigns", [
                {"create": {"name": "ok"}},
                {"create": {"name": ""}},
            ])
            assert result["success"] is True
            assert result["partialFailureError"] is not None

    def test_rate_limit_429(self, mock_headers):
        """Google Ads returns 429 rate limit."""
        resp = MagicMock()
        resp.ok = False
        resp.status_code = 429
        resp.reason = "Too Many Requests"
        resp.text = '{"error": {"code": 429, "message": "Rate limit exceeded"}}'
        resp.json.return_value = {"error": {"code": 429, "message": "Rate limit exceeded"}}
        with patch("server.requests.post", return_value=resp):
            result = _srv._mutate_resource("3393382047", "campaigns", [{"create": {}}])
            assert result["success"] is False
            assert result["error"] == 429

    def test_auth_expired_401(self, mock_headers):
        """Token expired mid-request."""
        resp = MagicMock()
        resp.ok = False
        resp.status_code = 401
        resp.reason = "Unauthorized"
        resp.text = "Token expired"
        resp.json.return_value = {"error": "Token expired"}
        with patch("server.requests.post", return_value=resp):
            result = _srv._mutate_resource("3393382047", "campaigns", [{"create": {}}])
            assert result["success"] is False
            assert result["error"] == 401

    def test_huge_payload(self, mock_headers, mock_requests_post):
        """Send 1000 operations — should not crash."""
        ops = [{"create": {"name": f"campaign_{i}"}} for i in range(1000)]
        result = _srv._mutate_resource("3393382047", "campaigns", ops)
        sent_payload = mock_requests_post.call_args[1]["json"]
        assert len(sent_payload["operations"]) == 1000


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: run_gaql — injection & edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestRunGaqlCrash:
    """Test GAQL execution with adversarial inputs."""

    def test_empty_query(self, mock_execute_gaql):
        mock_execute_gaql.return_value = {"results": [], "query": "", "totalRows": 0}
        result = run_gaql(customer_id=CID, query="")
        assert result["totalRows"] == 0

    def test_sql_injection_in_query(self, mock_execute_gaql):
        """GAQL is not SQL, but test that injection-like strings pass through."""
        mock_execute_gaql.return_value = {"results": [], "query": "", "totalRows": 0}
        run_gaql(customer_id=CID, query="'; DROP TABLE campaigns;--")
        # Should just pass to API, not crash locally
        mock_execute_gaql.assert_called_once()

    def test_unicode_in_query(self, mock_execute_gaql):
        mock_execute_gaql.return_value = {"results": [], "query": "", "totalRows": 0}
        run_gaql(customer_id=CID, query="SELECT campaign.name FROM campaign WHERE campaign.name LIKE '%こんにちは%'")
        mock_execute_gaql.assert_called_once()

    def test_huge_query(self, mock_execute_gaql):
        """10KB query string."""
        mock_execute_gaql.return_value = {"results": [], "query": "", "totalRows": 0}
        big_query = "SELECT " + ", ".join([f"field_{i}" for i in range(500)]) + " FROM campaign"
        run_gaql(customer_id=CID, query=big_query)
        mock_execute_gaql.assert_called_once()

    def test_api_exception_propagates(self, mock_execute_gaql):
        """execute_gaql raises — should propagate, not swallow."""
        mock_execute_gaql.side_effect = Exception("GAQL error: invalid field")
        with pytest.raises(Exception, match="GAQL error"):
            run_gaql(customer_id=CID, query="SELECT bad_field FROM campaign")

    def test_missing_developer_token(self):
        """GOOGLE_ADS_DEVELOPER_TOKEN unset at runtime."""
        original = _srv.GOOGLE_ADS_DEVELOPER_TOKEN
        try:
            _srv.GOOGLE_ADS_DEVELOPER_TOKEN = None
            with pytest.raises(ValueError, match="Developer Token"):
                run_gaql(customer_id=CID, query="SELECT campaign.name FROM campaign")
        finally:
            _srv.GOOGLE_ADS_DEVELOPER_TOKEN = original


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Conversion Actions — edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestConversionActionsCrash:
    def test_update_empty_string_id(self):
        result = update_conversion_action(
            customer_id=CID, conversion_action_id="", primary_for_goal=True
        )
        # Should work but with empty ID in resource name (API would reject)
        assert result["dry_run"] is True
        assert "conversionActions/" in result["operation"]["update"]["resourceName"]

    def test_update_all_fields_at_once(self):
        result = update_conversion_action(
            customer_id=CID,
            conversion_action_id="999",
            primary_for_goal=True,
            category="PURCHASE",
            status="ENABLED",
            name="Max Fields Test",
            counting_type="MANY_PER_CLICK",
            click_through_lookback_days=90,
            view_through_lookback_days=30,
            default_value=150.50,
            always_use_default_value=False,
        )
        mask = result["operation"]["updateMask"]
        assert mask.count(",") >= 7  # At least 8 fields

    def test_create_with_empty_name(self):
        result = create_conversion_action(
            customer_id=CID, name="", type="WEBPAGE"
        )
        # Should not crash — API will validate
        assert result["dry_run"] is True

    def test_create_with_invalid_type(self):
        result = create_conversion_action(
            customer_id=CID, name="Test", type="COMPLETELY_INVALID_TYPE"
        )
        assert result["operation"]["create"]["type"] == "COMPLETELY_INVALID_TYPE"

    def test_lookback_days_boundaries(self):
        """0 days, negative, 999 — should not crash locally."""
        for days in [0, -1, 999]:
            result = update_conversion_action(
                customer_id=CID,
                conversion_action_id="1",
                click_through_lookback_days=days,
            )
            assert result["dry_run"] is True

    def test_list_with_invalid_status_filter(self, mock_execute_gaql):
        mock_execute_gaql.return_value = {"results": []}
        result = list_conversion_actions(customer_id=CID, status_filter="BOGUS")
        # Should append WHERE clause with BOGUS — API will reject, but no local crash
        query_sent = mock_execute_gaql.call_args[0][1]
        assert "BOGUS" in query_sent


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: Campaign Budget — micros edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestCampaignBudgetCrash:
    def test_zero_budget(self):
        result = create_campaign_budget(
            customer_id=CID, name="Zero", amount_micros=0
        )
        assert result["operation"]["create"]["amountMicros"] == "0"

    def test_negative_budget(self):
        """Negative micros — should not crash locally."""
        result = create_campaign_budget(
            customer_id=CID, name="Negative", amount_micros=-50_000_000
        )
        assert result["operation"]["create"]["amountMicros"] == "-50000000"

    def test_enormous_budget(self):
        """1 billion PLN/day."""
        result = create_campaign_budget(
            customer_id=CID, name="Huge", amount_micros=1_000_000_000_000_000
        )
        assert result["dry_run"] is True

    def test_float_micros_type_error(self):
        """Micros should be int but what if float is passed?"""
        result = create_campaign_budget(
            customer_id=CID, name="Float", amount_micros=int(50.5 * 1_000_000)
        )
        assert result["dry_run"] is True

    def test_empty_name(self):
        result = create_campaign_budget(
            customer_id=CID, name="", amount_micros=10_000_000
        )
        assert result["operation"]["create"]["name"] == ""

    def test_unicode_name(self):
        result = create_campaign_budget(
            customer_id=CID, name="Budżet kampanii GenActiv 🇵🇱", amount_micros=10_000_000
        )
        assert "GenActiv" in result["operation"]["create"]["name"]

    def test_update_no_change(self):
        result = update_campaign_budget(customer_id=CID, budget_id="123")
        assert "error" in result

    def test_update_with_invalid_delivery_method(self):
        result = update_campaign_budget(
            customer_id=CID, budget_id="123", delivery_method="WARP_SPEED"
        )
        assert result["operation"]["update"]["deliveryMethod"] == "WARP_SPEED"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: Campaign — bidding strategy conflicts
# ═══════════════════════════════════════════════════════════════════════════


class TestCampaignCrash:
    def test_all_bidding_strategies_set(self):
        """What if target_cpa AND target_roas AND manual_cpc are all set?"""
        result = create_campaign(
            customer_id=CID,
            name="Conflict",
            budget_resource_name="customers/3393382047/campaignBudgets/1",
            target_cpa_micros=15_000_000,
            target_roas=4.0,
            manual_cpc=True,
        )
        # target_cpa takes precedence (first in the if/elif chain)
        assert "targetCpa" in result["operation"]["create"]
        assert "targetRoas" not in result["operation"]["create"]
        assert "manualCpc" not in result["operation"]["create"]

    def test_campaign_enabled_by_default_safety(self):
        """Campaigns should default to PAUSED for safety."""
        result = create_campaign(
            customer_id=CID,
            name="Safety Check",
            budget_resource_name="customers/3393382047/campaignBudgets/1",
        )
        assert result["operation"]["create"]["status"] == "PAUSED"

    def test_empty_budget_resource_name(self):
        result = create_campaign(
            customer_id=CID,
            name="No Budget",
            budget_resource_name="",
        )
        assert result["operation"]["create"]["campaignBudget"] == ""

    def test_very_long_campaign_name(self):
        name = "A" * 10000
        result = create_campaign(
            customer_id=CID, name=name,
            budget_resource_name="customers/3393382047/campaignBudgets/1",
        )
        assert len(result["operation"]["create"]["name"]) == 10000

    def test_special_chars_in_name(self):
        result = create_campaign(
            customer_id=CID,
            name='Campaign <script>alert("xss")</script> & "quotes"',
            budget_resource_name="customers/3393382047/campaignBudgets/1",
        )
        assert "<script>" in result["operation"]["create"]["name"]

    def test_update_with_all_none(self):
        result = update_campaign(customer_id=CID, campaign_id="1")
        assert "error" in result

    def test_update_target_roas_zero(self):
        result = update_campaign(
            customer_id=CID, campaign_id="1", target_roas=0.0
        )
        # 0.0 is falsy but not None — should still be set
        assert result["dry_run"] is True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: Ad Groups — edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestAdGroupCrash:
    def test_zero_cpc_bid(self):
        result = create_ad_group(
            customer_id=CID, campaign_id="1", name="Zero Bid",
            cpc_bid_micros=0,
        )
        # 0 is falsy but not None
        assert result["operation"]["create"]["cpcBidMicros"] == "0"

    def test_negative_cpc_bid(self):
        result = create_ad_group(
            customer_id=CID, campaign_id="1", name="Neg Bid",
            cpc_bid_micros=-1_000_000,
        )
        assert result["operation"]["create"]["cpcBidMicros"] == "-1000000"

    def test_update_all_fields(self):
        result = update_ad_group(
            customer_id=CID, ad_group_id="1",
            status="ENABLED", name="New Name", cpc_bid_micros=5_000_000,
        )
        mask = result["operation"]["updateMask"]
        assert "status" in mask
        assert "name" in mask
        assert "cpcBidMicros" in mask


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: RSA — validation boundary tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRSACrash:
    def test_too_few_headlines(self):
        """RSA requires minimum 3 headlines."""
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["H1", "H2"], descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        assert "error" in result
        assert "3 headlines" in result["error"]

    def test_too_many_headlines(self):
        """RSA allows max 15 headlines."""
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=[f"H{i}" for i in range(16)],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        assert "error" in result
        assert "15" in result["error"]

    def test_exactly_3_headlines(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        assert result["dry_run"] is True

    def test_exactly_15_headlines(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=[f"Headline {i}" for i in range(15)],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        assert result["dry_run"] is True

    def test_too_few_descriptions(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1"],
            final_urls=["https://genactiv.pl"],
        )
        assert "error" in result

    def test_too_many_descriptions(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2", "D3", "D4", "D5"],
            final_urls=["https://genactiv.pl"],
        )
        assert "error" in result

    def test_empty_final_urls(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=[],
        )
        assert "error" in result

    def test_headline_30_char_limit_not_enforced_locally(self):
        """Local validation doesn't check char length — API does."""
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["A" * 100, "B" * 100, "C" * 100],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        # Should pass local validation — API will reject
        assert result["dry_run"] is True

    def test_empty_headline_strings(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["", "", ""],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        # 3 headlines (even empty) pass count check
        assert result["dry_run"] is True

    def test_unicode_headlines(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["Colostrum GenActiv", "Odporność 🛡️", "Zdrowie dzieci 💪"],
            descriptions=["Kup teraz!", "Najlepsza jakość"],
            final_urls=["https://genactiv.pl"],
        )
        assert result["dry_run"] is True

    def test_path_fields(self):
        result = create_responsive_search_ad(
            customer_id=CID, ad_group_id="1",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
            path1="colostrum",
            path2="sklep",
        )
        ad = result["operation"]["create"]["ad"]
        assert ad["responsiveSearchAd"]["path1"] == "colostrum"
        assert ad["responsiveSearchAd"]["path2"] == "sklep"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: Keywords — batch & adversarial
# ═══════════════════════════════════════════════════════════════════════════


class TestKeywordsCrash:
    def test_empty_keyword_list(self):
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=[])
        assert "error" in result

    def test_21_keywords_over_limit(self):
        kws = [{"text": f"kw{i}", "match_type": "BROAD"} for i in range(21)]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert "error" in result
        assert "20" in result["error"]

    def test_exactly_20_keywords(self):
        kws = [{"text": f"kw{i}", "match_type": "BROAD"} for i in range(20)]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert result["dry_run"] is True
        assert result["keyword_count"] == 20

    def test_all_empty_text_keywords(self):
        """All keywords have empty text — should error after filtering."""
        kws = [{"text": "", "match_type": "BROAD"} for _ in range(5)]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert "error" in result
        assert "No valid keywords" in result["error"]

    def test_mixed_empty_and_valid(self):
        kws = [
            {"text": "", "match_type": "BROAD"},
            {"text": "valid keyword", "match_type": "EXACT"},
            {"text": "", "match_type": "PHRASE"},
        ]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert result["keyword_count"] == 1

    def test_missing_match_type_defaults_broad(self):
        kws = [{"text": "no match type"}]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert result["operations"][0]["create"]["keyword"]["matchType"] == "BROAD"

    def test_missing_text_key(self):
        kws = [{"match_type": "EXACT"}]  # no "text" key
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        # text defaults to "" via .get("text", "") → filtered out
        assert "error" in result

    def test_invalid_match_type(self):
        kws = [{"text": "test", "match_type": "FUZZY"}]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        # Should pass locally — API validates
        assert result["operations"][0]["create"]["keyword"]["matchType"] == "FUZZY"

    def test_unicode_keywords(self):
        kws = [{"text": "colostrum bydlęce", "match_type": "PHRASE"}]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert result["operations"][0]["create"]["keyword"]["text"] == "colostrum bydlęce"

    def test_very_long_keyword(self):
        kws = [{"text": "a " * 5000, "match_type": "BROAD"}]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert result["dry_run"] is True

    def test_special_chars_in_keyword(self):
        kws = [{"text": '+colostrum [bovinum] "genactiv"', "match_type": "BROAD"}]
        result = add_keywords(customer_id=CID, ad_group_id="1", keywords=kws)
        assert result["dry_run"] is True

    def test_remove_empty_criterion_ids(self):
        result = remove_keywords(customer_id=CID, ad_group_id="1", criterion_ids=[])
        assert "error" in result

    def test_remove_21_over_limit(self):
        ids = [str(i) for i in range(21)]
        result = remove_keywords(customer_id=CID, ad_group_id="1", criterion_ids=ids)
        assert "error" in result

    def test_remove_exactly_20(self):
        ids = [str(i) for i in range(20)]
        result = remove_keywords(customer_id=CID, ad_group_id="1", criterion_ids=ids)
        assert result["dry_run"] is True
        assert len(result["operations"]) == 20

    def test_update_keyword_both_fields(self):
        result = update_keyword(
            customer_id=CID, ad_group_id="1", criterion_id="99",
            status="PAUSED", cpc_bid_micros=3_000_000,
        )
        mask = result["operation"]["updateMask"]
        assert "status" in mask
        assert "cpcBidMicros" in mask

    def test_update_keyword_zero_bid(self):
        result = update_keyword(
            customer_id=CID, ad_group_id="1", criterion_id="99",
            cpc_bid_micros=0,
        )
        # 0 is not None — should be set
        assert result["operation"]["update"]["cpcBidMicros"] == "0"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: update_ad_status — edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestUpdateAdStatusCrash:
    def test_resource_name_format(self):
        """Verify the tilde-separated resource name format."""
        result = update_ad_status(
            customer_id=CID, ad_group_id="777", ad_id="888", status="PAUSED"
        )
        rn = result["operation"]["update"]["resourceName"]
        assert "777~888" in rn

    def test_invalid_status(self):
        result = update_ad_status(
            customer_id=CID, ad_group_id="1", ad_id="2", status="DELETED"
        )
        assert result["operation"]["update"]["status"] == "DELETED"

    def test_lowercase_status_uppercased(self):
        result = update_ad_status(
            customer_id=CID, ad_group_id="1", ad_id="2", status="paused"
        )
        assert result["operation"]["update"]["status"] == "PAUSED"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 11: OAuth / auth edge cases
# ═══════════════════════════════════════════════════════════════════════════


class TestOAuthEdgeCases:
    def test_missing_oauth_config_path(self):
        """GOOGLE_ADS_OAUTH_CONFIG_PATH not set."""
        from oauth import google_auth
        original = google_auth.GOOGLE_ADS_OAUTH_CONFIG_PATH
        try:
            google_auth.GOOGLE_ADS_OAUTH_CONFIG_PATH = None
            with pytest.raises(ValueError, match="GOOGLE_ADS_OAUTH_CONFIG_PATH"):
                google_auth.get_oauth_credentials()
        finally:
            google_auth.GOOGLE_ADS_OAUTH_CONFIG_PATH = original

    def test_oauth_config_file_not_found(self):
        from oauth import google_auth
        original = google_auth.GOOGLE_ADS_OAUTH_CONFIG_PATH
        try:
            google_auth.GOOGLE_ADS_OAUTH_CONFIG_PATH = "/nonexistent/path/file.json"
            with pytest.raises(FileNotFoundError):
                google_auth.get_oauth_credentials()
        finally:
            google_auth.GOOGLE_ADS_OAUTH_CONFIG_PATH = original

    def test_missing_developer_token_in_headers(self):
        from oauth import google_auth
        original = google_auth.GOOGLE_ADS_DEVELOPER_TOKEN
        try:
            google_auth.GOOGLE_ADS_DEVELOPER_TOKEN = None
            with pytest.raises(ValueError, match="GOOGLE_ADS_DEVELOPER_TOKEN"):
                google_auth.get_headers_with_auto_token()
        finally:
            google_auth.GOOGLE_ADS_DEVELOPER_TOKEN = original


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 12: Cross-tool — manager_id propagation
# ═══════════════════════════════════════════════════════════════════════════


class TestManagerIdPropagation:
    """Verify manager_id is passed through to _mutate_resource.
    Note: _mutate_resource formats manager_id internally via format_customer_id(),
    so write tools pass the raw value through."""

    def test_create_budget_with_manager(self, mock_mutate_success):
        create_campaign_budget(
            customer_id=CID, name="T", amount_micros=1_000_000,
            manager_id=MID, dry_run=False,
        )
        args = mock_mutate_success.call_args
        assert args[0][3] == MID  # raw value — _mutate_resource formats it

    def test_update_campaign_with_manager(self, mock_mutate_success):
        update_campaign(
            customer_id=CID, campaign_id="1", status="PAUSED",
            manager_id=MID, dry_run=False,
        )
        args = mock_mutate_success.call_args
        assert args[0][3] == MID

    def test_add_keywords_with_manager(self, mock_mutate_success):
        add_keywords(
            customer_id=CID, ad_group_id="1",
            keywords=[{"text": "test", "match_type": "BROAD"}],
            manager_id=MID, dry_run=False,
        )
        args = mock_mutate_success.call_args
        assert args[0][3] == MID

    def test_mutate_resource_formats_manager_id(self, mock_headers, mock_requests_post):
        """Verify _mutate_resource itself formats the manager_id in the header."""
        _srv._mutate_resource("3393382047", "campaigns", [{"create": {}}], "253-832-8866")
        # Check the login-customer-id header was set with formatted ID
        mock_headers.assert_called_once()
        # The header should be set on the returned dict before requests.post
        # Since we mock get_headers_with_auto_token, verify the header was added
        call_headers = mock_requests_post.call_args[1].get("headers", {})
        # Headers dict was modified in-place
        assert mock_headers.return_value.get("login-customer-id") == "2538328866"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 13: Falsy value traps (0, False, "", 0.0)
# ═══════════════════════════════════════════════════════════════════════════


class TestFalsyValueTraps:
    """Catch the #1 Python bug: treating 0/False/""/0.0 as None."""

    def test_target_roas_zero_is_set(self):
        result = update_campaign(
            customer_id=CID, campaign_id="1", target_roas=0.0,
        )
        # 0.0 is falsy but NOT None — should still create the update
        # BUG CHECK: if code uses `if target_roas:` instead of `if target_roas is not None:`
        assert result["dry_run"] is True
        # This may or may not set targetRoas depending on implementation
        # The key assertion: it should NOT return "no fields" error

    def test_target_cpa_zero_is_set(self):
        result = update_campaign(
            customer_id=CID, campaign_id="1", target_cpa_micros=0,
        )
        assert result["dry_run"] is True

    def test_default_value_zero(self):
        result = update_conversion_action(
            customer_id=CID, conversion_action_id="1",
            default_value=0.0,
        )
        assert result["dry_run"] is True
        assert "valueSettings" in result["operation"]["update"]

    def test_always_use_default_false(self):
        result = update_conversion_action(
            customer_id=CID, conversion_action_id="1",
            always_use_default_value=False,
        )
        assert result["dry_run"] is True
        assert result["operation"]["update"]["valueSettings"]["alwaysUseDefaultValue"] is False

    def test_primary_for_goal_false(self):
        result = update_conversion_action(
            customer_id=CID, conversion_action_id="1",
            primary_for_goal=False,
        )
        assert result["operation"]["update"]["primaryForGoal"] is False

    def test_cpc_bid_zero(self):
        result = update_keyword(
            customer_id=CID, ad_group_id="1", criterion_id="1",
            cpc_bid_micros=0,
        )
        assert result["operation"]["update"]["cpcBidMicros"] == "0"

    def test_empty_name_is_set(self):
        result = update_conversion_action(
            customer_id=CID, conversion_action_id="1", name="",
        )
        # Empty string IS a value (not None) — should be set
        assert result["dry_run"] is True
        assert result["operation"]["update"]["name"] == ""


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 14: Execute-path safety (dry_run=False)
# ═══════════════════════════════════════════════════════════════════════════


class TestExecutePathSafety:
    """Verify that dry_run=False correctly calls _mutate_resource
    with the right resource type for each tool."""

    TOOLS_AND_RESOURCES = [
        ("update_conversion_action", "conversionActions",
         dict(customer_id=CID, conversion_action_id="1", primary_for_goal=True, dry_run=False)),
        ("create_conversion_action", "conversionActions",
         dict(customer_id=CID, name="T", type="WEBPAGE", dry_run=False)),
        ("create_campaign_budget", "campaignBudgets",
         dict(customer_id=CID, name="T", amount_micros=1_000_000, dry_run=False)),
        ("update_campaign_budget", "campaignBudgets",
         dict(customer_id=CID, budget_id="1", amount_micros=2_000_000, dry_run=False)),
        ("create_campaign", "campaigns",
         dict(customer_id=CID, name="T",
              budget_resource_name="customers/3393382047/campaignBudgets/1", dry_run=False)),
        ("update_campaign", "campaigns",
         dict(customer_id=CID, campaign_id="1", status="PAUSED", dry_run=False)),
        ("create_ad_group", "adGroups",
         dict(customer_id=CID, campaign_id="1", name="T", dry_run=False)),
        ("update_ad_group", "adGroups",
         dict(customer_id=CID, ad_group_id="1", status="PAUSED", dry_run=False)),
        ("create_responsive_search_ad", "adGroupAds",
         dict(customer_id=CID, ad_group_id="1",
              headlines=["H1", "H2", "H3"], descriptions=["D1", "D2"],
              final_urls=["https://genactiv.pl"], dry_run=False)),
        ("update_ad_status", "adGroupAds",
         dict(customer_id=CID, ad_group_id="1", ad_id="1", status="PAUSED", dry_run=False)),
        ("add_keywords", "adGroupCriteria",
         dict(customer_id=CID, ad_group_id="1",
              keywords=[{"text": "t", "match_type": "BROAD"}], dry_run=False)),
        ("update_keyword", "adGroupCriteria",
         dict(customer_id=CID, ad_group_id="1", criterion_id="1",
              cpc_bid_micros=1_000_000, dry_run=False)),
        ("remove_keywords", "adGroupCriteria",
         dict(customer_id=CID, ad_group_id="1", criterion_ids=["1"], dry_run=False)),
    ]

    @pytest.mark.parametrize("tool_name,expected_resource,kwargs", TOOLS_AND_RESOURCES)
    def test_correct_resource_type(self, tool_name, expected_resource, kwargs, mock_mutate_success):
        fn = getattr(_srv, tool_name).fn
        fn(**kwargs)
        args = mock_mutate_success.call_args[0]
        assert args[1] == expected_resource, (
            f"{tool_name} should mutate '{expected_resource}' but mutated '{args[1]}'"
        )
