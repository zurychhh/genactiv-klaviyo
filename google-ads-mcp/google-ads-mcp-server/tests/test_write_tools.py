"""Tests for all Google Ads MCP write tools.

Each write tool is tested for:
1. dry_run=True (default) returns preview without calling API
2. dry_run=False delegates to _mutate_resource
3. Parameter validation / edge cases
"""
import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with patch.dict(os.environ, {
    "GOOGLE_ADS_DEVELOPER_TOKEN": "test-token",
    "GOOGLE_ADS_OAUTH_CONFIG_PATH": "/tmp/fake.json",
}):
    import server as _srv

# FastMCP @mcp.tool wraps functions in FunctionTool objects.
# Access the raw function via .fn attribute.
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
list_conversion_actions = _srv.list_conversion_actions.fn

CUSTOMER_ID = "339-338-2047"
MANAGER_ID = "253-832-8866"


# ── Conversion Actions ──────────────────────────────────────────────────


class TestUpdateConversionAction:
    def test_dry_run_default(self):
        result = update_conversion_action(
            customer_id=CUSTOMER_ID,
            conversion_action_id="123",
            primary_for_goal=False,
        )
        assert result["dry_run"] is True
        assert "operation" in result
        assert result["conversion_action_id"] == "123"
        op = result["operation"]
        assert op["update"]["primaryForGoal"] is False
        assert "primaryForGoal" in op["updateMask"]

    def test_execute(self, mock_mutate_success):
        result = update_conversion_action(
            customer_id=CUSTOMER_ID,
            conversion_action_id="123",
            primary_for_goal=True,
            dry_run=False,
        )
        assert result["success"] is True
        mock_mutate_success.assert_called_once()
        args = mock_mutate_success.call_args
        assert args[0][0] == "3393382047"
        assert args[0][1] == "conversionActions"

    def test_no_fields_error(self):
        result = update_conversion_action(
            customer_id=CUSTOMER_ID,
            conversion_action_id="123",
        )
        assert "error" in result

    def test_multiple_fields(self):
        result = update_conversion_action(
            customer_id=CUSTOMER_ID,
            conversion_action_id="456",
            primary_for_goal=True,
            category="PURCHASE",
            status="ENABLED",
        )
        assert result["dry_run"] is True
        mask = result["operation"]["updateMask"]
        assert "primaryForGoal" in mask
        assert "category" in mask
        assert "status" in mask

    def test_value_settings(self):
        result = update_conversion_action(
            customer_id=CUSTOMER_ID,
            conversion_action_id="789",
            default_value=99.0,
            always_use_default_value=True,
        )
        update = result["operation"]["update"]
        assert update["valueSettings"]["defaultValue"] == 99.0
        assert update["valueSettings"]["alwaysUseDefaultValue"] is True


class TestCreateConversionAction:
    def test_dry_run_default(self):
        result = create_conversion_action(
            customer_id=CUSTOMER_ID,
            name="Test Purchase",
            type="WEBPAGE",
            category="PURCHASE",
        )
        assert result["dry_run"] is True
        create_obj = result["operation"]["create"]
        assert create_obj["name"] == "Test Purchase"
        assert create_obj["type"] == "WEBPAGE"
        assert create_obj["category"] == "PURCHASE"
        assert create_obj["primaryForGoal"] is False  # default

    def test_execute(self, mock_mutate_success):
        result = create_conversion_action(
            customer_id=CUSTOMER_ID,
            name="Test",
            type="WEBPAGE",
            dry_run=False,
        )
        assert result["success"] is True


class TestListConversionActions:
    def test_returns_actions(self, mock_execute_gaql):
        mock_execute_gaql.return_value = {
            "results": [
                {
                    "conversionAction": {
                        "id": "123",
                        "name": "Purchase",
                        "status": "ENABLED",
                        "primaryForGoal": True,
                        "type": "WEBPAGE",
                        "category": "PURCHASE",
                    }
                }
            ]
        }
        result = list_conversion_actions(customer_id=CUSTOMER_ID)
        assert result["total"] == 1
        assert result["conversion_actions"][0]["name"] == "Purchase"
        assert result["conversion_actions"][0]["primaryForGoal"] is True


# ── Campaign Budgets ─────────────────────────────────────────────────────


class TestCreateCampaignBudget:
    def test_dry_run_default(self):
        result = create_campaign_budget(
            customer_id=CUSTOMER_ID,
            name="Test Budget 50 PLN",
            amount_micros=50_000_000,
        )
        assert result["dry_run"] is True
        create_obj = result["operation"]["create"]
        assert create_obj["name"] == "Test Budget 50 PLN"
        assert create_obj["amountMicros"] == "50000000"
        assert create_obj["deliveryMethod"] == "STANDARD"

    def test_execute(self, mock_mutate_success):
        result = create_campaign_budget(
            customer_id=CUSTOMER_ID,
            name="Budget",
            amount_micros=10_000_000,
            dry_run=False,
        )
        assert result["success"] is True


class TestUpdateCampaignBudget:
    def test_dry_run_amount_change(self):
        result = update_campaign_budget(
            customer_id=CUSTOMER_ID,
            budget_id="999",
            amount_micros=100_000_000,
        )
        assert result["dry_run"] is True
        assert result["budget_id"] == "999"
        assert "amountMicros" in result["operation"]["updateMask"]

    def test_no_fields_error(self):
        result = update_campaign_budget(
            customer_id=CUSTOMER_ID,
            budget_id="999",
        )
        assert "error" in result


# ── Campaigns ────────────────────────────────────────────────────────────


class TestCreateCampaign:
    def test_dry_run_default(self):
        result = create_campaign(
            customer_id=CUSTOMER_ID,
            name="Brand Campaign",
            budget_resource_name="customers/3393382047/campaignBudgets/123",
        )
        assert result["dry_run"] is True
        create_obj = result["operation"]["create"]
        assert create_obj["name"] == "Brand Campaign"
        assert create_obj["status"] == "PAUSED"  # safe default
        assert create_obj["advertisingChannelType"] == "SEARCH"

    def test_target_cpa_bidding(self):
        result = create_campaign(
            customer_id=CUSTOMER_ID,
            name="CPA Campaign",
            budget_resource_name="customers/3393382047/campaignBudgets/123",
            target_cpa_micros=15_000_000,
        )
        create_obj = result["operation"]["create"]
        assert "targetCpa" in create_obj
        assert create_obj["targetCpa"]["targetCpaMicros"] == "15000000"

    def test_target_roas_bidding(self):
        result = create_campaign(
            customer_id=CUSTOMER_ID,
            name="ROAS Campaign",
            budget_resource_name="customers/3393382047/campaignBudgets/123",
            target_roas=4.0,
        )
        create_obj = result["operation"]["create"]
        assert create_obj["targetRoas"]["targetRoas"] == 4.0

    def test_manual_cpc_bidding(self):
        result = create_campaign(
            customer_id=CUSTOMER_ID,
            name="Manual CPC",
            budget_resource_name="customers/3393382047/campaignBudgets/123",
            manual_cpc=True,
            enhanced_cpc=True,
        )
        create_obj = result["operation"]["create"]
        assert create_obj["manualCpc"]["enhancedCpcEnabled"] is True

    def test_execute(self, mock_mutate_success):
        result = create_campaign(
            customer_id=CUSTOMER_ID,
            name="Test",
            budget_resource_name="customers/3393382047/campaignBudgets/123",
            dry_run=False,
        )
        assert result["success"] is True


class TestUpdateCampaign:
    def test_dry_run_pause(self):
        result = update_campaign(
            customer_id=CUSTOMER_ID,
            campaign_id="555",
            status="PAUSED",
        )
        assert result["dry_run"] is True
        assert result["campaign_id"] == "555"
        assert result["operation"]["update"]["status"] == "PAUSED"

    def test_no_fields_error(self):
        result = update_campaign(
            customer_id=CUSTOMER_ID,
            campaign_id="555",
        )
        assert "error" in result

    def test_budget_change(self):
        result = update_campaign(
            customer_id=CUSTOMER_ID,
            campaign_id="555",
            campaign_budget="customers/3393382047/campaignBudgets/999",
        )
        assert "campaignBudget" in result["operation"]["updateMask"]


# ── Ad Groups ────────────────────────────────────────────────────────────


class TestCreateAdGroup:
    def test_dry_run_default(self):
        result = create_ad_group(
            customer_id=CUSTOMER_ID,
            campaign_id="555",
            name="Test Ad Group",
        )
        assert result["dry_run"] is True
        create_obj = result["operation"]["create"]
        assert create_obj["name"] == "Test Ad Group"
        assert create_obj["status"] == "PAUSED"
        assert create_obj["type"] == "SEARCH_STANDARD"
        assert "customers/3393382047/campaigns/555" in create_obj["campaign"]

    def test_with_cpc_bid(self):
        result = create_ad_group(
            customer_id=CUSTOMER_ID,
            campaign_id="555",
            name="Bid Group",
            cpc_bid_micros=2_000_000,
        )
        assert result["operation"]["create"]["cpcBidMicros"] == "2000000"

    def test_execute(self, mock_mutate_success):
        result = create_ad_group(
            customer_id=CUSTOMER_ID,
            campaign_id="555",
            name="Test",
            dry_run=False,
        )
        assert result["success"] is True


class TestUpdateAdGroup:
    def test_dry_run_status(self):
        result = update_ad_group(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            status="ENABLED",
        )
        assert result["dry_run"] is True
        assert result["operation"]["update"]["status"] == "ENABLED"

    def test_no_fields_error(self):
        result = update_ad_group(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
        )
        assert "error" in result


# ── Ads ──────────────────────────────────────────────────────────────────


class TestCreateResponsiveSearchAd:
    def test_dry_run_default(self):
        result = create_responsive_search_ad(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        assert result["dry_run"] is True
        create_obj = result["operation"]["create"]
        ad = create_obj["ad"]
        assert len(ad["responsiveSearchAd"]["headlines"]) == 3
        assert len(ad["responsiveSearchAd"]["descriptions"]) == 2
        assert ad["finalUrls"] == ["https://genactiv.pl"]

    def test_execute(self, mock_mutate_success):
        result = create_responsive_search_ad(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            headlines=["H1", "H2", "H3"],
            descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
            dry_run=False,
        )
        assert result["success"] is True
        args = mock_mutate_success.call_args
        assert args[0][1] == "adGroupAds"


class TestUpdateAdStatus:
    def test_dry_run_pause(self):
        result = update_ad_status(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            ad_id="888",
            status="PAUSED",
        )
        assert result["dry_run"] is True
        assert result["operation"]["update"]["status"] == "PAUSED"

    def test_execute(self, mock_mutate_success):
        result = update_ad_status(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            ad_id="888",
            status="ENABLED",
            dry_run=False,
        )
        assert result["success"] is True


# ── Keywords ─────────────────────────────────────────────────────────────


class TestAddKeywords:
    def test_dry_run_default(self):
        result = add_keywords(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            keywords=[
                {"text": "colostrum", "match_type": "BROAD"},
                {"text": "genactiv", "match_type": "EXACT"},
            ],
        )
        assert result["dry_run"] is True
        assert len(result["operations"]) == 2

    def test_with_global_bid(self):
        """cpc_bid_micros is a top-level param applied to all keywords, not per-keyword."""
        result = add_keywords(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            keywords=[
                {"text": "colostrum", "match_type": "EXACT"}
            ],
            cpc_bid_micros=3_000_000,
        )
        create_obj = result["operations"][0]["create"]
        assert create_obj["cpcBidMicros"] == "3000000"

    def test_execute(self, mock_mutate_success):
        result = add_keywords(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            keywords=[{"text": "test", "match_type": "BROAD"}],
            dry_run=False,
        )
        assert result["success"] is True
        args = mock_mutate_success.call_args
        assert args[0][1] == "adGroupCriteria"


class TestUpdateKeyword:
    def test_dry_run_bid_change(self):
        result = update_keyword(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            criterion_id="999",
            cpc_bid_micros=5_000_000,
        )
        assert result["dry_run"] is True
        assert "cpcBidMicros" in result["operation"]["updateMask"]

    def test_status_change(self):
        result = update_keyword(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            criterion_id="999",
            status="PAUSED",
        )
        assert result["operation"]["update"]["status"] == "PAUSED"

    def test_no_fields_error(self):
        result = update_keyword(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            criterion_id="999",
        )
        assert "error" in result


class TestRemoveKeywords:
    def test_dry_run_default(self):
        result = remove_keywords(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            criterion_ids=["111", "222"],
        )
        assert result["dry_run"] is True
        assert len(result["operations"]) == 2
        # Should be remove operations
        for op in result["operations"]:
            assert "remove" in op

    def test_execute(self, mock_mutate_success):
        result = remove_keywords(
            customer_id=CUSTOMER_ID,
            ad_group_id="777",
            criterion_ids=["111"],
            dry_run=False,
        )
        assert result["success"] is True


# ── Cross-cutting: customer_id formatting ────────────────────────────────


class TestCustomerIdFormatting:
    """Verify all write tools correctly format customer IDs with dashes."""

    def test_create_budget_formats_id(self):
        result = create_campaign_budget(
            customer_id="339-338-2047",
            name="Test",
            amount_micros=10_000_000,
        )
        assert result["customer_id"] == "3393382047"

    def test_update_campaign_formats_id(self):
        result = update_campaign(
            customer_id="339-338-2047",
            campaign_id="123",
            status="PAUSED",
        )
        assert result["customer_id"] == "3393382047"

    def test_add_keywords_formats_id(self):
        result = add_keywords(
            customer_id="339-338-2047",
            ad_group_id="777",
            keywords=[{"text": "test", "match_type": "BROAD"}],
        )
        assert result["customer_id"] == "3393382047"


# ── Dry run prevents API calls ──────────────────────────────────────────


class TestDryRunSafety:
    """Verify dry_run=True NEVER calls _mutate_resource."""

    def test_all_tools_dry_run_safe(self, mock_mutate_success):
        """Call every write tool with dry_run=True, assert _mutate_resource is never called."""
        create_campaign_budget(
            customer_id=CUSTOMER_ID, name="T", amount_micros=1_000_000
        )
        update_campaign_budget(
            customer_id=CUSTOMER_ID, budget_id="1", amount_micros=2_000_000
        )
        create_campaign(
            customer_id=CUSTOMER_ID, name="T",
            budget_resource_name="customers/3393382047/campaignBudgets/1",
        )
        update_campaign(
            customer_id=CUSTOMER_ID, campaign_id="1", status="PAUSED"
        )
        create_ad_group(
            customer_id=CUSTOMER_ID, campaign_id="1", name="T"
        )
        update_ad_group(
            customer_id=CUSTOMER_ID, ad_group_id="1", status="PAUSED"
        )
        create_responsive_search_ad(
            customer_id=CUSTOMER_ID, ad_group_id="1",
            headlines=["H1", "H2", "H3"], descriptions=["D1", "D2"],
            final_urls=["https://genactiv.pl"],
        )
        update_ad_status(
            customer_id=CUSTOMER_ID, ad_group_id="1", ad_id="1", status="PAUSED"
        )
        add_keywords(
            customer_id=CUSTOMER_ID, ad_group_id="1",
            keywords=[{"text": "t", "match_type": "BROAD"}],
        )
        update_keyword(
            customer_id=CUSTOMER_ID, ad_group_id="1", criterion_id="1",
            cpc_bid_micros=1_000_000,
        )
        remove_keywords(
            customer_id=CUSTOMER_ID, ad_group_id="1", criterion_ids=["1"],
        )
        update_conversion_action(
            customer_id=CUSTOMER_ID, conversion_action_id="1",
            primary_for_goal=False,
        )
        create_conversion_action(
            customer_id=CUSTOMER_ID, name="T", type="WEBPAGE",
        )

        # _mutate_resource should NEVER have been called
        mock_mutate_success.assert_not_called()
