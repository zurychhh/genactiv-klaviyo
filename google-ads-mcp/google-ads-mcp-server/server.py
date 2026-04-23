from fastmcp import FastMCP, Context
from typing import Any, Dict, List, Optional
import os
import logging
import requests

# Load environment variables FIRST
from dotenv import load_dotenv
load_dotenv()

# Import OAuth modules after environment is loaded
from oauth.google_auth import format_customer_id, get_headers_with_auto_token, execute_gaql

# Get environment variables
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('google_ads_server')

mcp = FastMCP("Google Ads Tools")

# Server startup
logger.info("Starting Google Ads MCP Server...")

def get_customer_name(customer_id: str) -> str:
    """Retrieve descriptive_name for the given customer ID."""
    try:
        query = "SELECT customer.descriptive_name FROM customer"
        result = execute_gaql(customer_id, query)
        rows = result.get('results', [])
        if not rows:
            return "Name not available (no results)"
        customer = rows[0].get('customer', {})
        return customer.get('descriptiveName', "Name not available (missing field)")
    except Exception:
        return "Name not available (error)"

def is_manager_account(customer_id: str) -> bool:
    """Check if a customer account is a manager (MCC)."""
    try:
        query = "SELECT customer.manager FROM customer"
        result = execute_gaql(customer_id, query)
        rows = result.get('results', [])
        if not rows:
            return False
        return bool(rows[0].get('customer', {}).get('manager', False))
    except Exception:
        return False

def get_sub_accounts(manager_id: str) -> List[Dict[str, Any]]:
    """List sub-accounts under a manager account."""
    try:
        query = (
            "SELECT customer_client.id, customer_client.descriptive_name, "
            "customer_client.level, customer_client.manager "
            "FROM customer_client WHERE customer_client.level > 0"
        )
        result = execute_gaql(manager_id, query)
        rows = result.get('results', [])
        subs = []
        for row in rows:
            client = row.get('customerClient', {}) or row.get('customer_client', {})
            cid = format_customer_id(str(client.get('id', '')))
            subs.append({
                'id': cid,
                'name': client.get('descriptiveName', f"Sub-account {cid}"),
                'access_type': 'managed',
                'is_manager': bool(client.get('manager', False)),
                'parent_id': manager_id,
                'level': int(client.get('level', 0))
            })
        return subs
    except Exception:
        return []

@mcp.tool
def run_gaql(
    customer_id: str,
    query: str,
    manager_id: str = "",
    ctx: Context = None
) -> Dict[str, Any]:
    """Execute GAQL using the non-streaming search endpoint for consistent JSON parsing."""
    if ctx:
        ctx.info(f"Executing GAQL query for customer {customer_id}...")
        ctx.info(f"Query: {query}")

    if not GOOGLE_ADS_DEVELOPER_TOKEN:
        raise ValueError("Google Ads Developer Token is not set in environment variables.")

    try:
        # This will automatically trigger OAuth flow if needed
        result = execute_gaql(customer_id, query, manager_id)
        if ctx:
            ctx.info(f"GAQL query successful. Found {result['totalRows']} rows.")
        return result
    except Exception as e:
        if ctx:
            ctx.error(f"GAQL query failed: {str(e)}")
        raise

@mcp.tool
def list_accounts(ctx: Context = None) -> Dict[str, Any]:
    """List all accessible accounts including nested sub-accounts."""
    if ctx:
        ctx.info("Checking credentials and preparing to list accounts...")

    if not GOOGLE_ADS_DEVELOPER_TOKEN:
        raise ValueError("Google Ads Developer Token is not set in environment variables.")

    try:
        # This will automatically trigger OAuth flow if needed
        headers = get_headers_with_auto_token()
        
        # Fetch top-level accessible customers
        url = "https://googleads.googleapis.com/v23/customers:listAccessibleCustomers"
        resp = requests.get(url, headers=headers)
        if not resp.ok:
            if ctx:
                ctx.error(f"Failed to list accessible accounts: {resp.status_code} {resp.reason}")
            raise Exception(
                f"Error listing accounts: {resp.status_code} {resp.reason} - {resp.text}"
            )
        data = resp.json()
        resource_names = data.get('resourceNames', [])
        if not resource_names:
            if ctx:
                ctx.info("No accessible Google Ads accounts found.")
            return {'accounts': [], 'message': 'No accessible accounts found.'}

        if ctx:
            ctx.info(f"Found {len(resource_names)} top-level accessible accounts. Fetching details...")

        accounts = []
        seen = set()
        for resource in resource_names:
            cid = resource.split('/')[-1]
            fid = format_customer_id(cid)
            name = get_customer_name(fid)
            manager = is_manager_account(fid)
            account = {
                'id': fid,
                'name': name,
                'access_type': 'direct',
                'is_manager': manager,
                'level': 0
            }
            accounts.append(account)
            seen.add(fid)
            # Include sub-accounts (and nested)
            if manager:
                subs = get_sub_accounts(fid)
                for sub in subs:
                    if sub['id'] not in seen:
                        accounts.append(sub)
                        seen.add(sub['id'])
                        # nested level
                        if sub['is_manager']:
                            nested = get_sub_accounts(sub['id'])
                            for n in nested:
                                if n['id'] not in seen:
                                    accounts.append(n)
                                    seen.add(n['id'])

        if ctx:
            ctx.info(f"Finished processing. Found a total of {len(accounts)} accounts.")

        return {
            'accounts': accounts,
            'total_accounts': len(accounts)
        }
    except Exception as e:
        if ctx:
            ctx.error(f"Error listing accounts: {str(e)}")
        raise

@mcp.tool
def run_keyword_planner(
    customer_id: str,
    keywords: List[str],
    manager_id: str = "",
    page_url: Optional[str] = None,
    start_year: Optional[int] = None,
    start_month: Optional[str] = None,
    end_year: Optional[int] = None,
    end_month: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Generate keyword ideas using Google Ads KeywordPlanIdeaService.

    This tool allows you to generate keyword ideas based on seed keywords or a page URL. 
    You can specify targeting parameters such as language, location, and network to refine your keyword suggestions.

    Args:
        customer_id: The Google Ads customer ID (10 digits, no dashes)
        keywords: A list of seed keywords to generate ideas from
        manager_id: Manager ID if access type is 'managed'
        page_url: Optional page URL related to your business to generate ideas from
        start_year: Optional start year for historical data (defaults to previous year)
        start_month: Optional start month for historical data (defaults to JANUARY)
        end_year: Optional end year for historical data (defaults to current year)
        end_month: Optional end month for historical data (defaults to current month)

    Returns:
        A list of keyword ideas with associated metrics

    Note:
        - At least one of 'keywords' or 'page_url' must be provided
        - Ensure that the 'customer_id' is formatted as a string, even if it appears numeric
        - Valid months: JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE, JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER
    """
    if ctx:
        ctx.info(f"Generating keyword ideas for customer {customer_id}...")
        if keywords:
            ctx.info(f"Seed keywords: {', '.join(keywords)}")
        if page_url:
            ctx.info(f"Page URL: {page_url}")

    if not GOOGLE_ADS_DEVELOPER_TOKEN:
        raise ValueError("Google Ads Developer Token is not set in environment variables.")
    
    # Validate that at least one of keywords or page_url is provided
    if (not keywords or len(keywords) == 0) and not page_url:
        raise ValueError("At least one of keywords or page URL is required, but neither was specified.")
    
    try:
        # This will automatically trigger OAuth flow if needed
        headers = get_headers_with_auto_token()
        
        formatted_customer_id = format_customer_id(customer_id)
        url = f"https://googleads.googleapis.com/v23/customers/{formatted_customer_id}:generateKeywordIdeas"
        
        if manager_id:
            headers['login-customer-id'] = format_customer_id(manager_id)
        
        # Set up dynamic date range with user-provided values or smart defaults
        from datetime import datetime
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.strftime('%B').upper()
        
        valid_months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
                        'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
        
        # Use provided dates or fall back to defaults
        start_year_final = start_year or (current_year - 1)
        start_month_final = start_month.upper() if start_month and start_month.upper() in valid_months else 'JANUARY'
        end_year_final = end_year or current_year
        end_month_final = end_month.upper() if end_month and end_month.upper() in valid_months else current_month
        
        # Build the request body according to Google Ads API specification
        request_body = {
            'language': 'languageConstants/1000',
            'geoTargetConstants': ['geoTargetConstants/2840'],
            'keywordPlanNetwork': 'GOOGLE_SEARCH_AND_PARTNERS',
            'includeAdultKeywords': False,
            'pageSize': 25,
            'historicalMetricsOptions': {
                'yearMonthRange': {
                    'start': {
                        'year': start_year_final,
                        'month': start_month_final
                    },
                    'end': {
                        'year': end_year_final,
                        'month': end_month_final
                    }
                }
            }
        }
        
        # Set the appropriate seed based on what's provided
        if (not keywords or len(keywords) == 0) and page_url:
            request_body['urlSeed'] = {'url': page_url}
        elif keywords and len(keywords) > 0 and not page_url:
            request_body['keywordSeed'] = {'keywords': keywords}
        elif keywords and len(keywords) > 0 and page_url:
            request_body['keywordAndUrlSeed'] = {
                'url': page_url,
                'keywords': keywords
            }
        
        response = requests.post(url, headers=headers, json=request_body)
        
        if not response.ok:
            error_text = response.text
            if ctx:
                ctx.error(f"Keyword planner request failed: {response.status_code} {response.reason}")
            raise Exception(f"Error executing request: {response.status_code} {response.reason} - {error_text}")
        
        results = response.json()
        
        if 'results' not in results or not results['results']:
            message = f"No keyword ideas found for the provided inputs.\n\nKeywords: {', '.join(keywords) if keywords else 'None'}\nPage URL: {page_url or 'None'}\nAccount: {formatted_customer_id}"
            if ctx:
                ctx.info(message)
            return {
                "message": message,
                "keywords": keywords or [],
                "page_url": page_url,
                "date_range": f"{start_month_final} {start_year_final} to {end_month_final} {end_year_final}"
            }
        
        # Format the results for better readability
        formatted_results = []
        for result in results['results']:
            keyword_idea = result.get('keywordIdeaMetrics', {})
            keyword_text = result.get('text', 'N/A')
            
            formatted_result = {
                'keyword': keyword_text,
                'avg_monthly_searches': keyword_idea.get('avgMonthlySearches', 'N/A'),
                'competition': keyword_idea.get('competition', 'N/A'),
                'competition_index': keyword_idea.get('competitionIndex', 'N/A'),
                'low_top_of_page_bid_micros': keyword_idea.get('lowTopOfPageBidMicros', 'N/A'),
                'high_top_of_page_bid_micros': keyword_idea.get('highTopOfPageBidMicros', 'N/A')
            }
            formatted_results.append(formatted_result)
        
        if ctx:
            ctx.info(f"Found {len(formatted_results)} keyword ideas.")
        
        return {
            "keyword_ideas": formatted_results,
            "total_ideas": len(formatted_results),
            "input_keywords": keywords or [],
            "input_page_url": page_url,
            "date_range": f"{start_month_final} {start_year_final} to {end_month_final} {end_year_final}"
        }
        
    except Exception as e:
        if ctx:
            ctx.error(f"An unexpected error occurred: {e}")
        raise

# ---------------------------------------------------------------------------
# Phase 3: Conversion Action Management (Write Tools)
# ---------------------------------------------------------------------------

def _mutate_resource(
    customer_id: str,
    resource_type: str,
    operations: list,
    manager_id: str = "",
) -> Dict[str, Any]:
    """Execute a mutate call on the Google Ads REST API.

    Args:
        customer_id: 10-digit customer ID
        resource_type: e.g. 'conversionActions', 'campaigns'
        operations: list of {create: ...}, {update: ..., updateMask: ...}, or {remove: ...}
        manager_id: optional MCC manager ID
    """
    headers = get_headers_with_auto_token()
    formatted_id = format_customer_id(customer_id)

    if manager_id:
        headers['login-customer-id'] = format_customer_id(manager_id)

    url = f"https://googleads.googleapis.com/v23/customers/{formatted_id}/{resource_type}:mutate"
    payload = {"operations": operations}

    resp = requests.post(url, headers=headers, json=payload)

    if not resp.ok:
        error_detail = resp.text
        try:
            error_detail = resp.json()
        except Exception:
            pass
        return {
            "success": False,
            "error": resp.status_code,
            "reason": resp.reason,
            "detail": error_detail,
        }

    data = resp.json()
    return {
        "success": True,
        "results": data.get("results", []),
        "partialFailureError": data.get("partialFailureError"),
    }


@mcp.tool
def list_conversion_actions(
    customer_id: str,
    manager_id: str = "",
    status_filter: str = "ALL",
    ctx: Context = None,
) -> Dict[str, Any]:
    """List all conversion actions with their settings (primary/secondary, category, status, type).

    This is a READ-ONLY tool — use it to discover conversion actions before updating them.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        manager_id: MCC manager ID if needed (e.g. '253-832-8866')
        status_filter: 'ALL', 'ENABLED', 'HIDDEN', or 'REMOVED' (default ALL)
    """
    if ctx:
        ctx.info(f"Listing conversion actions for customer {customer_id}...")

    query = (
        "SELECT "
        "conversion_action.id, "
        "conversion_action.name, "
        "conversion_action.resource_name, "
        "conversion_action.status, "
        "conversion_action.type, "
        "conversion_action.category, "
        "conversion_action.primary_for_goal, "
        "conversion_action.counting_type, "
        "conversion_action.attribution_model_settings.attribution_model, "
        "conversion_action.click_through_lookback_window_days, "
        "conversion_action.view_through_lookback_window_days, "
        "conversion_action.value_settings.default_value, "
        "conversion_action.value_settings.always_use_default_value "
        "FROM conversion_action"
    )

    if status_filter and status_filter.upper() != "ALL":
        query += f" WHERE conversion_action.status = '{status_filter.upper()}'"

    result = execute_gaql(customer_id, query, manager_id)
    rows = result.get("results", [])

    actions = []
    for row in rows:
        ca = row.get("conversionAction", {})
        actions.append({
            "id": ca.get("id"),
            "name": ca.get("name"),
            "resourceName": ca.get("resourceName"),
            "status": ca.get("status"),
            "type": ca.get("type"),
            "category": ca.get("category"),
            "primaryForGoal": ca.get("primaryForGoal"),
            "countingType": ca.get("countingType"),
            "attributionModel": ca.get("attributionModelSettings", {}).get("attributionModel"),
            "clickThroughLookbackDays": ca.get("clickThroughLookbackWindowDays"),
            "viewThroughLookbackDays": ca.get("viewThroughLookbackWindowDays"),
            "defaultValue": ca.get("valueSettings", {}).get("defaultValue"),
            "alwaysUseDefaultValue": ca.get("valueSettings", {}).get("alwaysUseDefaultValue"),
        })

    if ctx:
        primary = sum(1 for a in actions if a.get("primaryForGoal"))
        ctx.info(f"Found {len(actions)} conversion actions ({primary} primary).")

    return {
        "conversion_actions": actions,
        "total": len(actions),
        "customer_id": format_customer_id(customer_id),
    }


@mcp.tool
def update_conversion_action(
    customer_id: str,
    conversion_action_id: str,
    primary_for_goal: Optional[bool] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    name: Optional[str] = None,
    counting_type: Optional[str] = None,
    click_through_lookback_days: Optional[int] = None,
    view_through_lookback_days: Optional[int] = None,
    default_value: Optional[float] = None,
    always_use_default_value: Optional[bool] = None,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Update an existing Google Ads conversion action.

    ⚠️ WRITE OPERATION — changes your Google Ads account.
    Set dry_run=False to actually execute. Default is dry_run=True (preview only).

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        conversion_action_id: ID of conversion action to update (use list_conversion_actions to find it)
        primary_for_goal: True = Primary (used for bidding), False = Secondary (observe only)
        category: PURCHASE, LEAD, SIGNUP, ADD_TO_CART, BEGIN_CHECKOUT, PAGE_VIEW, DEFAULT, etc.
        status: ENABLED, HIDDEN, or REMOVED
        name: New display name
        counting_type: ONE_CONVERSION or MANY_PER_CLICK
        click_through_lookback_days: 1-90 days
        view_through_lookback_days: 1-30 days
        default_value: Default conversion value (float)
        always_use_default_value: True to ignore dynamic values
        manager_id: MCC manager ID if needed (e.g. '253-832-8866')
        dry_run: If True (default), only preview the change — nothing is sent to Google Ads
    """
    formatted_id = format_customer_id(customer_id)
    resource_name = f"customers/{formatted_id}/conversionActions/{conversion_action_id}"

    update_obj = {"resourceName": resource_name}
    mask_parts = []

    if primary_for_goal is not None:
        update_obj["primaryForGoal"] = primary_for_goal
        mask_parts.append("primaryForGoal")
    if category is not None:
        update_obj["category"] = category.upper()
        mask_parts.append("category")
    if status is not None:
        update_obj["status"] = status.upper()
        mask_parts.append("status")
    if name is not None:
        update_obj["name"] = name
        mask_parts.append("name")
    if counting_type is not None:
        update_obj["countingType"] = counting_type.upper()
        mask_parts.append("countingType")
    if click_through_lookback_days is not None:
        update_obj["clickThroughLookbackWindowDays"] = click_through_lookback_days
        mask_parts.append("clickThroughLookbackWindowDays")
    if view_through_lookback_days is not None:
        update_obj["viewThroughLookbackWindowDays"] = view_through_lookback_days
        mask_parts.append("viewThroughLookbackWindowDays")
    if default_value is not None or always_use_default_value is not None:
        value_settings = {}
        if default_value is not None:
            value_settings["defaultValue"] = default_value
            mask_parts.append("valueSettings.defaultValue")
        if always_use_default_value is not None:
            value_settings["alwaysUseDefaultValue"] = always_use_default_value
            mask_parts.append("valueSettings.alwaysUseDefaultValue")
        update_obj["valueSettings"] = value_settings

    if not mask_parts:
        return {"error": "No fields to update. Provide at least one field to change."}

    operation = {
        "update": update_obj,
        "updateMask": ",".join(mask_parts),
    }

    if ctx:
        ctx.info(f"WRITE: update_conversion_action {conversion_action_id} — fields: {mask_parts}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "conversion_action_id": conversion_action_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING mutate on conversionActions for customer {formatted_id}")

    return _mutate_resource(formatted_id, "conversionActions", [operation], manager_id)


@mcp.tool
def create_conversion_action(
    customer_id: str,
    name: str,
    type: str,
    category: str = "DEFAULT",
    primary_for_goal: bool = False,
    counting_type: str = "ONE_CONVERSION",
    click_through_lookback_days: int = 30,
    view_through_lookback_days: int = 1,
    default_value: float = 0,
    always_use_default_value: bool = False,
    attribution_model: str = "GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN",
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Create a new Google Ads conversion action.

    ⚠️ WRITE OPERATION — creates a new conversion action in your Google Ads account.
    Set dry_run=False to actually execute. Default is dry_run=True (preview only).

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        name: Display name for the conversion action
        type: WEBPAGE, CLICK_TO_CALL, APP_INSTALL, IMPORT, etc.
        category: PURCHASE, LEAD, SIGNUP, ADD_TO_CART, BEGIN_CHECKOUT, PAGE_VIEW, DEFAULT
        primary_for_goal: True = Primary (used for bidding), False = Secondary
        counting_type: ONE_CONVERSION (unique) or MANY_PER_CLICK (every)
        click_through_lookback_days: 1-90 days (default 30)
        view_through_lookback_days: 1-30 days (default 1)
        default_value: Default conversion value (default 0)
        always_use_default_value: True to always use default, False for dynamic values
        attribution_model: GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN, EXTERNAL, etc.
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview — nothing is sent to Google Ads
    """
    formatted_id = format_customer_id(customer_id)

    create_obj = {
        "name": name,
        "type": type.upper(),
        "category": category.upper(),
        "primaryForGoal": primary_for_goal,
        "countingType": counting_type.upper(),
        "clickThroughLookbackWindowDays": click_through_lookback_days,
        "viewThroughLookbackWindowDays": view_through_lookback_days,
        "valueSettings": {
            "defaultValue": default_value,
            "alwaysUseDefaultValue": always_use_default_value,
        },
        "attributionModelSettings": {
            "attributionModel": attribution_model.upper(),
        },
        "status": "ENABLED",
    }

    operation = {"create": create_obj}

    if ctx:
        ctx.info(f"WRITE: create_conversion_action '{name}' type={type} category={category}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING create conversionAction for customer {formatted_id}")

    return _mutate_resource(formatted_id, "conversionActions", [operation], manager_id)


# ---------------------------------------------------------------------------
# Campaign Budgets
# ---------------------------------------------------------------------------

@mcp.tool
def create_campaign_budget(
    customer_id: str,
    name: str,
    amount_micros: int,
    delivery_method: str = "STANDARD",
    explicitly_shared: bool = False,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Create a new campaign budget.

    ⚠️ WRITE OPERATION — creates a budget in your Google Ads account.
    Set dry_run=False to actually execute. Default is dry_run=True (preview only).

    Amounts are in micros: 1 PLN = 1,000,000 micros.
    Example: 50 PLN/day → amount_micros=50000000

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        name: Budget name (e.g. 'Brand Campaign Budget 50 PLN')
        amount_micros: Daily budget in micros (1 PLN = 1,000,000)
        delivery_method: STANDARD (spread evenly) or ACCELERATED (spend quickly)
        explicitly_shared: True if budget is shared across multiple campaigns
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview — nothing is sent to Google Ads
    """
    formatted_id = format_customer_id(customer_id)

    create_obj = {
        "name": name,
        "amountMicros": str(amount_micros),
        "deliveryMethod": delivery_method.upper(),
        "explicitlyShared": explicitly_shared,
    }

    operation = {"create": create_obj}

    if ctx:
        pln = amount_micros / 1_000_000
        ctx.info(f"WRITE: create_campaign_budget '{name}' — {pln:.2f} PLN/day")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING create campaignBudget for customer {formatted_id}")

    return _mutate_resource(formatted_id, "campaignBudgets", [operation], manager_id)


@mcp.tool
def update_campaign_budget(
    customer_id: str,
    budget_id: str,
    amount_micros: Optional[int] = None,
    name: Optional[str] = None,
    delivery_method: Optional[str] = None,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Update an existing campaign budget.

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.
    Amounts in micros: 1 PLN = 1,000,000 micros.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        budget_id: Budget ID to update (find via GAQL: SELECT campaign_budget.id FROM campaign_budget)
        amount_micros: New daily budget in micros
        name: New budget name
        delivery_method: STANDARD or ACCELERATED
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    formatted_id = format_customer_id(customer_id)
    resource_name = f"customers/{formatted_id}/campaignBudgets/{budget_id}"

    update_obj = {"resourceName": resource_name}
    mask_parts = []

    if amount_micros is not None:
        update_obj["amountMicros"] = str(amount_micros)
        mask_parts.append("amountMicros")
    if name is not None:
        update_obj["name"] = name
        mask_parts.append("name")
    if delivery_method is not None:
        update_obj["deliveryMethod"] = delivery_method.upper()
        mask_parts.append("deliveryMethod")

    if not mask_parts:
        return {"error": "No fields to update. Provide at least one field to change."}

    operation = {"update": update_obj, "updateMask": ",".join(mask_parts)}

    if ctx:
        ctx.info(f"WRITE: update_campaign_budget {budget_id} — fields: {mask_parts}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "budget_id": budget_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING update campaignBudget for customer {formatted_id}")

    return _mutate_resource(formatted_id, "campaignBudgets", [operation], manager_id)


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

@mcp.tool
def create_campaign(
    customer_id: str,
    name: str,
    budget_resource_name: str,
    advertising_channel_type: str = "SEARCH",
    bidding_strategy_type: Optional[str] = None,
    target_spend: bool = False,
    manual_cpc: bool = False,
    enhanced_cpc: bool = False,
    target_cpa_micros: Optional[int] = None,
    target_roas: Optional[float] = None,
    search_network: bool = True,
    content_network: bool = False,
    partner_search_network: bool = False,
    status: str = "PAUSED",
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Create a new Google Ads campaign.

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.
    New campaigns are PAUSED by default — enable manually after review.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        name: Campaign name
        budget_resource_name: Full resource name (e.g. 'customers/3393382047/campaignBudgets/123456')
        advertising_channel_type: SEARCH, DISPLAY, SHOPPING, PERFORMANCE_MAX, VIDEO
        bidding_strategy_type: Ignored if specific strategy flags are set below
        target_spend: True to use Maximize Clicks (target spend) bidding
        manual_cpc: True to use Manual CPC bidding
        enhanced_cpc: If manual_cpc=True, set True to enable Enhanced CPC
        target_cpa_micros: Target CPA in micros for Target CPA bidding (1 PLN = 1,000,000)
        target_roas: Target ROAS ratio for Target ROAS bidding (e.g. 4.0 = 400%)
        search_network: Show ads on Google Search (default True)
        content_network: Show ads on Display Network (default False)
        partner_search_network: Show on search partners (default False)
        status: PAUSED (default) or ENABLED
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    formatted_id = format_customer_id(customer_id)

    create_obj = {
        "name": name,
        "advertisingChannelType": advertising_channel_type.upper(),
        "status": status.upper(),
        "campaignBudget": budget_resource_name,
        "networkSettings": {
            "targetGoogleSearch": search_network,
            "targetContentNetwork": content_network,
            "targetPartnerSearchNetwork": partner_search_network,
        },
    }

    # Bidding strategy — mutually exclusive
    if target_cpa_micros is not None:
        create_obj["targetCpa"] = {"targetCpaMicros": str(target_cpa_micros)}
    elif target_roas is not None:
        create_obj["targetRoas"] = {"targetRoas": target_roas}
    elif manual_cpc:
        create_obj["manualCpc"] = {"enhancedCpcEnabled": enhanced_cpc}
    elif target_spend:
        create_obj["targetSpend"] = {}
    else:
        # Default: Maximize Clicks
        create_obj["targetSpend"] = {}

    operation = {"create": create_obj}

    if ctx:
        ctx.info(f"WRITE: create_campaign '{name}' channel={advertising_channel_type} status={status}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING create campaign for customer {formatted_id}")

    return _mutate_resource(formatted_id, "campaigns", [operation], manager_id)


@mcp.tool
def update_campaign(
    customer_id: str,
    campaign_id: str,
    status: Optional[str] = None,
    name: Optional[str] = None,
    campaign_budget: Optional[str] = None,
    target_cpa_micros: Optional[int] = None,
    target_roas: Optional[float] = None,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Update an existing Google Ads campaign.

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        campaign_id: Campaign ID to update
        status: ENABLED, PAUSED, or REMOVED
        name: New campaign name
        campaign_budget: New budget resource name (e.g. 'customers/3393382047/campaignBudgets/123456')
        target_cpa_micros: New target CPA in micros (only for Target CPA campaigns)
        target_roas: New target ROAS ratio (only for Target ROAS campaigns)
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    formatted_id = format_customer_id(customer_id)
    resource_name = f"customers/{formatted_id}/campaigns/{campaign_id}"

    update_obj = {"resourceName": resource_name}
    mask_parts = []

    if status is not None:
        update_obj["status"] = status.upper()
        mask_parts.append("status")
    if name is not None:
        update_obj["name"] = name
        mask_parts.append("name")
    if campaign_budget is not None:
        update_obj["campaignBudget"] = campaign_budget
        mask_parts.append("campaignBudget")
    if target_cpa_micros is not None:
        update_obj["targetCpa"] = {"targetCpaMicros": str(target_cpa_micros)}
        mask_parts.append("targetCpa.targetCpaMicros")
    if target_roas is not None:
        update_obj["targetRoas"] = {"targetRoas": target_roas}
        mask_parts.append("targetRoas.targetRoas")

    if not mask_parts:
        return {"error": "No fields to update. Provide at least one field to change."}

    operation = {"update": update_obj, "updateMask": ",".join(mask_parts)}

    if ctx:
        ctx.info(f"WRITE: update_campaign {campaign_id} — fields: {mask_parts}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "campaign_id": campaign_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING update campaign for customer {formatted_id}")

    return _mutate_resource(formatted_id, "campaigns", [operation], manager_id)


# ---------------------------------------------------------------------------
# Ad Groups
# ---------------------------------------------------------------------------

@mcp.tool
def create_ad_group(
    customer_id: str,
    campaign_id: str,
    name: str,
    ad_group_type: str = "SEARCH_STANDARD",
    cpc_bid_micros: Optional[int] = None,
    status: str = "PAUSED",
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Create a new ad group within a campaign.

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.
    New ad groups are PAUSED by default.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        campaign_id: Parent campaign ID
        name: Ad group name
        ad_group_type: SEARCH_STANDARD, DISPLAY_STANDARD, SHOPPING_PRODUCT_ADS, etc.
        cpc_bid_micros: Default max CPC bid in micros (e.g. 2000000 = 2 PLN)
        status: PAUSED (default) or ENABLED
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    formatted_id = format_customer_id(customer_id)
    campaign_rn = f"customers/{formatted_id}/campaigns/{campaign_id}"

    create_obj = {
        "name": name,
        "campaign": campaign_rn,
        "type": ad_group_type.upper(),
        "status": status.upper(),
    }

    if cpc_bid_micros is not None:
        create_obj["cpcBidMicros"] = str(cpc_bid_micros)

    operation = {"create": create_obj}

    if ctx:
        ctx.info(f"WRITE: create_ad_group '{name}' in campaign {campaign_id} type={ad_group_type}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "campaign_id": campaign_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING create adGroup for customer {formatted_id}")

    return _mutate_resource(formatted_id, "adGroups", [operation], manager_id)


@mcp.tool
def update_ad_group(
    customer_id: str,
    ad_group_id: str,
    status: Optional[str] = None,
    name: Optional[str] = None,
    cpc_bid_micros: Optional[int] = None,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Update an existing ad group.

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        ad_group_id: Ad group ID to update
        status: ENABLED, PAUSED, or REMOVED
        name: New ad group name
        cpc_bid_micros: New default max CPC bid in micros (1 PLN = 1,000,000)
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    formatted_id = format_customer_id(customer_id)
    resource_name = f"customers/{formatted_id}/adGroups/{ad_group_id}"

    update_obj = {"resourceName": resource_name}
    mask_parts = []

    if status is not None:
        update_obj["status"] = status.upper()
        mask_parts.append("status")
    if name is not None:
        update_obj["name"] = name
        mask_parts.append("name")
    if cpc_bid_micros is not None:
        update_obj["cpcBidMicros"] = str(cpc_bid_micros)
        mask_parts.append("cpcBidMicros")

    if not mask_parts:
        return {"error": "No fields to update. Provide at least one field to change."}

    operation = {"update": update_obj, "updateMask": ",".join(mask_parts)}

    if ctx:
        ctx.info(f"WRITE: update_ad_group {ad_group_id} — fields: {mask_parts}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "ad_group_id": ad_group_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING update adGroup for customer {formatted_id}")

    return _mutate_resource(formatted_id, "adGroups", [operation], manager_id)


# ---------------------------------------------------------------------------
# Responsive Search Ads
# ---------------------------------------------------------------------------

@mcp.tool
def create_responsive_search_ad(
    customer_id: str,
    ad_group_id: str,
    headlines: List[str],
    descriptions: List[str],
    final_urls: List[str],
    final_mobile_urls: Optional[List[str]] = None,
    path1: Optional[str] = None,
    path2: Optional[str] = None,
    status: str = "PAUSED",
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Create a Responsive Search Ad (RSA) in an ad group.

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.
    New ads are PAUSED by default.

    RSA requirements:
    - headlines: minimum 3, maximum 15 (each max 30 chars)
    - descriptions: minimum 2, maximum 4 (each max 90 chars)
    - final_urls: at least 1 landing page URL

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        ad_group_id: Parent ad group ID
        headlines: List of headline texts (min 3, max 15, each ≤30 chars)
        descriptions: List of description texts (min 2, max 4, each ≤90 chars)
        final_urls: List of landing page URLs
        final_mobile_urls: Optional mobile-specific landing page URLs
        path1: Display URL path part 1 (max 15 chars, e.g. 'colostrum')
        path2: Display URL path part 2 (max 15 chars, e.g. 'sklep')
        status: PAUSED (default) or ENABLED
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    if len(headlines) < 3:
        return {"error": "RSA requires at least 3 headlines."}
    if len(headlines) > 15:
        return {"error": "RSA allows a maximum of 15 headlines."}
    if len(descriptions) < 2:
        return {"error": "RSA requires at least 2 descriptions."}
    if len(descriptions) > 4:
        return {"error": "RSA allows a maximum of 4 descriptions."}
    if not final_urls:
        return {"error": "At least one final_url is required."}

    formatted_id = format_customer_id(customer_id)
    ad_group_rn = f"customers/{formatted_id}/adGroups/{ad_group_id}"

    headline_assets = [{"text": h} for h in headlines]
    description_assets = [{"text": d} for d in descriptions]

    ad_obj = {
        "responsiveSearchAd": {
            "headlines": headline_assets,
            "descriptions": description_assets,
        },
        "finalUrls": final_urls,
    }

    if final_mobile_urls:
        ad_obj["finalMobileUrls"] = final_mobile_urls
    if path1 is not None:
        ad_obj["responsiveSearchAd"]["path1"] = path1
    if path2 is not None:
        ad_obj["responsiveSearchAd"]["path2"] = path2

    create_obj = {
        "adGroup": ad_group_rn,
        "ad": ad_obj,
        "status": status.upper(),
    }

    operation = {"create": create_obj}

    if ctx:
        ctx.info(
            f"WRITE: create_responsive_search_ad in ad_group {ad_group_id} "
            f"— {len(headlines)} headlines, {len(descriptions)} descriptions"
        )

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "ad_group_id": ad_group_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING create adGroupAd for customer {formatted_id}")

    return _mutate_resource(formatted_id, "adGroupAds", [operation], manager_id)


@mcp.tool
def update_ad_status(
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    status: str,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Update the status of an ad (enable, pause, or remove).

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        ad_group_id: Ad group ID containing the ad
        ad_id: The ad ID to update
        status: ENABLED, PAUSED, or REMOVED
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    formatted_id = format_customer_id(customer_id)
    resource_name = f"customers/{formatted_id}/adGroupAds/{ad_group_id}~{ad_id}"

    update_obj = {
        "resourceName": resource_name,
        "status": status.upper(),
    }

    operation = {"update": update_obj, "updateMask": "status"}

    if ctx:
        ctx.info(f"WRITE: update_ad_status ad_group={ad_group_id} ad={ad_id} → {status.upper()}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "ad_group_id": ad_group_id,
            "ad_id": ad_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING update adGroupAd status for customer {formatted_id}")

    return _mutate_resource(formatted_id, "adGroupAds", [operation], manager_id)


# ---------------------------------------------------------------------------
# Keywords (Ad Group Criteria)
# ---------------------------------------------------------------------------

@mcp.tool
def add_keywords(
    customer_id: str,
    ad_group_id: str,
    keywords: List[Dict[str, str]],
    cpc_bid_micros: Optional[int] = None,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Add keywords to an ad group (batch, max 20 per call).

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        ad_group_id: Target ad group ID
        keywords: List of keyword objects, each with 'text' and 'match_type'.
                  match_type: EXACT, PHRASE, or BROAD.
                  Example: [{"text": "colostrum bovinum", "match_type": "PHRASE"},
                            {"text": "genactiv colostrum", "match_type": "EXACT"}]
        cpc_bid_micros: Optional CPC bid override in micros for all keywords (1 PLN = 1,000,000)
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    if not keywords:
        return {"error": "At least one keyword is required."}
    if len(keywords) > 20:
        return {"error": "Maximum 20 keywords per call to prevent accidents. Split into multiple calls."}

    formatted_id = format_customer_id(customer_id)
    ad_group_rn = f"customers/{formatted_id}/adGroups/{ad_group_id}"

    operations = []
    for kw in keywords:
        text = kw.get("text", "")
        match_type = kw.get("match_type", "BROAD").upper()
        if not text:
            continue

        create_obj = {
            "adGroup": ad_group_rn,
            "status": "ENABLED",
            "keyword": {
                "text": text,
                "matchType": match_type,
            },
        }

        if cpc_bid_micros is not None:
            create_obj["cpcBidMicros"] = str(cpc_bid_micros)

        operations.append({"create": create_obj})

    if not operations:
        return {"error": "No valid keywords found in the input."}

    if ctx:
        ctx.info(f"WRITE: add_keywords — {len(operations)} keywords to ad_group {ad_group_id}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "ad_group_id": ad_group_id,
            "keyword_count": len(operations),
            "operations": operations,
        }

    if ctx:
        ctx.info(f"EXECUTING add {len(operations)} keywords for customer {formatted_id}")

    return _mutate_resource(formatted_id, "adGroupCriteria", operations, manager_id)


@mcp.tool
def update_keyword(
    customer_id: str,
    ad_group_id: str,
    criterion_id: str,
    status: Optional[str] = None,
    cpc_bid_micros: Optional[int] = None,
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Update an existing keyword (status or bid).

    ⚠️ WRITE OPERATION. Set dry_run=False to execute.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        ad_group_id: Ad group containing the keyword
        criterion_id: Keyword criterion ID (find via GAQL on keyword_view)
        status: ENABLED, PAUSED, or REMOVED
        cpc_bid_micros: New CPC bid in micros (1 PLN = 1,000,000)
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    formatted_id = format_customer_id(customer_id)
    resource_name = f"customers/{formatted_id}/adGroupCriteria/{ad_group_id}~{criterion_id}"

    update_obj = {"resourceName": resource_name}
    mask_parts = []

    if status is not None:
        update_obj["status"] = status.upper()
        mask_parts.append("status")
    if cpc_bid_micros is not None:
        update_obj["cpcBidMicros"] = str(cpc_bid_micros)
        mask_parts.append("cpcBidMicros")

    if not mask_parts:
        return {"error": "No fields to update. Provide at least one of: status, cpc_bid_micros."}

    operation = {"update": update_obj, "updateMask": ",".join(mask_parts)}

    if ctx:
        ctx.info(f"WRITE: update_keyword criterion={criterion_id} — fields: {mask_parts}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to execute this change.",
            "customer_id": formatted_id,
            "ad_group_id": ad_group_id,
            "criterion_id": criterion_id,
            "operation": operation,
        }

    if ctx:
        ctx.info(f"EXECUTING update adGroupCriteria for customer {formatted_id}")

    return _mutate_resource(formatted_id, "adGroupCriteria", [operation], manager_id)


@mcp.tool
def remove_keywords(
    customer_id: str,
    ad_group_id: str,
    criterion_ids: List[str],
    manager_id: str = "",
    dry_run: bool = True,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Permanently remove keywords from an ad group.

    ⚠️ WRITE OPERATION — PERMANENT DELETE, cannot be undone.
    Set dry_run=False to execute. Max 20 per call.

    Args:
        customer_id: Google Ads account ID (e.g. '339-338-2047')
        ad_group_id: Ad group containing the keywords
        criterion_ids: List of keyword criterion IDs to remove
        manager_id: MCC manager ID if needed
        dry_run: If True (default), only preview
    """
    if not criterion_ids:
        return {"error": "At least one criterion_id is required."}
    if len(criterion_ids) > 20:
        return {"error": "Maximum 20 removals per call. Split into multiple calls."}

    formatted_id = format_customer_id(customer_id)

    operations = []
    for cid in criterion_ids:
        resource_name = f"customers/{formatted_id}/adGroupCriteria/{ad_group_id}~{cid}"
        operations.append({"remove": resource_name})

    if ctx:
        ctx.info(f"WRITE: remove_keywords — {len(operations)} keywords from ad_group {ad_group_id}")

    if dry_run:
        return {
            "dry_run": True,
            "message": "Preview only — set dry_run=False to PERMANENTLY DELETE these keywords.",
            "customer_id": formatted_id,
            "ad_group_id": ad_group_id,
            "criterion_ids": criterion_ids,
            "operations": operations,
        }

    if ctx:
        ctx.info(f"EXECUTING remove {len(operations)} keywords for customer {formatted_id}")

    return _mutate_resource(formatted_id, "adGroupCriteria", operations, manager_id)


@mcp.resource("gaql://reference")
def gaql_reference() -> str:
    """Google Ads Query Language (GAQL) reference documentation."""
    return """Schema Format:    
                ## Basic Query Structure
                '''
                SELECT field1, field2, ... 
                FROM resource_type
                WHERE condition
                ORDER BY field [ASC|DESC]
                LIMIT n
                '''

                ## Common Field Types

                ### Resource Fields
                - campaign.id, campaign.name, campaign.status
                - ad_group.id, ad_group.name, ad_group.status
                - ad_group_ad.ad.id, ad_group_ad.ad.final_urls
                - ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type (for keyword_view)

                ### Metric Fields
                - metrics.impressions
                - metrics.clicks
                - metrics.cost_micros
                - metrics.conversions
                - metrics.conversions_value (direct conversion revenue - primary revenue metric)
                - metrics.ctr
                - metrics.average_cpc

                ### Segment Fields
                - segments.date
                - segments.device
                - segments.day_of_week

                ## Common WHERE Clauses

                ### Date Ranges
                - WHERE segments.date DURING LAST_7_DAYS
                - WHERE segments.date DURING LAST_30_DAYS
                - WHERE segments.date BETWEEN '2023-01-01' AND '2023-01-31'

                ### Filtering
                - WHERE campaign.status = 'ENABLED'
                - WHERE metrics.clicks > 100
                - WHERE campaign.name LIKE '%Brand%'
                - Use LIKE '%keyword%' instead of CONTAINS 'keyword' (CONTAINS not supported)

                EXAMPLE QUERIES:

                1. Basic campaign metrics:
                SELECT 
                campaign.id,
                campaign.name, 
                metrics.clicks, 
                metrics.impressions,
                metrics.cost_micros
                FROM campaign 
                WHERE segments.date DURING LAST_7_DAYS

                2. Ad group performance:
                SELECT 
                campaign.id,
                ad_group.name, 
                metrics.conversions, 
                metrics.cost_micros,
                campaign.name
                FROM ad_group 
                WHERE metrics.clicks > 100

                3. Keyword analysis (CORRECT field names):
                SELECT 
                campaign.id,
                ad_group_criterion.keyword.text, 
                ad_group_criterion.keyword.match_type,
                metrics.average_position, 
                metrics.ctr
                FROM keyword_view 
                WHERE segments.date DURING LAST_30_DAYS
                ORDER BY metrics.impressions DESC

                4. Get conversion data with revenue:
                SELECT
                campaign.id,
                campaign.name,
                metrics.conversions,
                metrics.conversions_value,
                metrics.all_conversions_value,
                metrics.cost_micros
                FROM campaign
                WHERE segments.date DURING LAST_30_DAYS

                ## Campaign Budget Fields
                - campaign_budget.id, campaign_budget.name
                - campaign_budget.amount_micros (daily budget in micros, 1 PLN = 1,000,000)
                - campaign_budget.delivery_method (STANDARD, ACCELERATED)
                - campaign_budget.explicitly_shared
                - campaign_budget.status
                - campaign_budget.resource_name (needed for create_campaign budget_resource_name)

                Example — list budgets:
                SELECT campaign_budget.id, campaign_budget.name, campaign_budget.amount_micros,
                       campaign_budget.delivery_method, campaign_budget.status
                FROM campaign_budget

                ## Ad Group Fields
                - ad_group.id, ad_group.name, ad_group.status
                - ad_group.type (SEARCH_STANDARD, DISPLAY_STANDARD, etc.)
                - ad_group.cpc_bid_micros
                - ad_group.campaign (resource name)

                Example — list ad groups:
                SELECT campaign.id, ad_group.id, ad_group.name, ad_group.status,
                       ad_group.cpc_bid_micros, ad_group.type
                FROM ad_group
                WHERE campaign.id = 123456

                ## Ad Group Ad (RSA) Fields
                - ad_group_ad.ad.id, ad_group_ad.ad.type
                - ad_group_ad.ad.responsive_search_ad.headlines
                - ad_group_ad.ad.responsive_search_ad.descriptions
                - ad_group_ad.ad.final_urls
                - ad_group_ad.status (ENABLED, PAUSED, REMOVED)
                - ad_group_ad.ad.responsive_search_ad.path1, path2

                Example — list RSAs:
                SELECT campaign.id, ad_group.id, ad_group_ad.ad.id,
                       ad_group_ad.ad.responsive_search_ad.headlines,
                       ad_group_ad.ad.responsive_search_ad.descriptions,
                       ad_group_ad.ad.final_urls, ad_group_ad.status
                FROM ad_group_ad
                WHERE ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'

                ## Ad Group Criterion (Keyword) Fields
                - ad_group_criterion.criterion_id
                - ad_group_criterion.keyword.text
                - ad_group_criterion.keyword.match_type (EXACT, PHRASE, BROAD)
                - ad_group_criterion.status
                - ad_group_criterion.cpc_bid_micros
                - ad_group_criterion.quality_info.quality_score

                Example — list keywords with bids:
                SELECT campaign.id, ad_group.id, ad_group_criterion.criterion_id,
                       ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
                       ad_group_criterion.status, ad_group_criterion.cpc_bid_micros
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = 'KEYWORD'

                IMPORTANT NOTES & COMMON ERRORS TO AVOID:

                ### Field Errors to Avoid:
                WRONG: campaign.campaign_budget.amount_micros
                CORRECT: campaign_budget.amount_micros (query from campaign_budget resource)

                WRONG: keyword.text, keyword.match_type
                CORRECT: ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type

                ### Required Fields:
                - Always include campaign.id when querying ad_group, keyword_view, or other campaign-related resources
                - Some resources require specific reference fields in SELECT clause

                ### Revenue Metrics:
                - metrics.conversions_value = Direct conversion revenue (use for ROI calculations)
                - metrics.all_conversions_value = Total attributed revenue (includes view-through)

                ### String Matching:
                - Use LIKE '%keyword%' not CONTAINS 'keyword'
                - GAQL does not support CONTAINS operator

                ### Micros Convention:
                - All monetary values use micros (1 PLN = 1,000,000 micros)
                - campaign_budget.amount_micros, ad_group.cpc_bid_micros, metrics.cost_micros

                NOTE:
                - Date ranges must be finite: LAST_7_DAYS, LAST_30_DAYS, or BETWEEN dates
                - Cannot use open-ended ranges like >= '2023-01-31'
                - Always include campaign.id when error messages request it."""

if __name__ == "__main__":
    import sys
    
    # Check command line arguments for transport mode
    if "--http" in sys.argv:
        logger.info("Starting with HTTP transport on http://127.0.0.1:8000/mcp")
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
    else:
        # Default to STDIO for Claude Desktop compatibility
        logger.info("Starting with STDIO transport for Claude Desktop")
        mcp.run(transport="stdio")