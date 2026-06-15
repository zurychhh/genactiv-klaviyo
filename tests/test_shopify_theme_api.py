"""
Exhaustive edge-case and crash tests for shopify_theme_api.py

Covers:
 - api_get / api_put / api_delete: HTTP errors, empty bodies, JSON parsing
 - list_themes: 200, 403, 500, empty, None
 - get_main_theme: finding main, no main, empty list
 - list_assets: normal, errors, empty
 - get_asset: normal, 403, 404, encoded keys
 - update_asset: success, 403, other errors
 - delete_asset: success, 403, other errors
 - backup_asset: file write, asset without value, missing directory
 - find_consent_files: keyword matching, empty assets, edge cases
 - search_in_assets: text search, binary files skipped, unicode
 - print_json: edge cases
 - CLI __main__ block: all commands, missing args, unknown commands
"""

import json
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

import pytest
import requests


# ---------------------------------------------------------------------------
# Import helper
# ---------------------------------------------------------------------------

def _import_theme_api():
    project_root = "/Users/user/projects/genactiv-klaviyo"
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if "shopify_theme_api" in sys.modules:
        del sys.modules["shopify_theme_api"]
    import shopify_theme_api
    return shopify_theme_api


# ===================================================================
# api_get
# ===================================================================

class TestApiGet:

    def test_success(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"themes": []})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            status, data = mod.api_get("/themes.json")
            assert status == 200
            assert data == {"themes": []}

    def test_empty_body(self):
        """
        BUG FOUND: api_get does `response.json() if response.text else None`.
        If text is empty string (falsy), it returns None — good.
        But if text is whitespace-only, json() may fail.
        """
        mod = _import_theme_api()
        resp = MagicMock()
        resp.status_code = 200
        resp.text = ""
        with patch("shopify_theme_api.requests.get", return_value=resp):
            status, data = mod.api_get("/themes.json")
            assert status == 200
            assert data is None

    def test_whitespace_body(self):
        """
        BUG FOUND: If response.text is ' ' (whitespace), it's truthy,
        so response.json() will be called and will raise JSONDecodeError.
        """
        mod = _import_theme_api()
        resp = MagicMock()
        resp.status_code = 200
        resp.text = "  "
        resp.json.side_effect = json.JSONDecodeError("bad", "", 0)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            with pytest.raises(json.JSONDecodeError):
                mod.api_get("/themes.json")

    def test_network_error(self):
        mod = _import_theme_api()
        with patch("shopify_theme_api.requests.get", side_effect=requests.exceptions.ConnectionError):
            with pytest.raises(requests.exceptions.ConnectionError):
                mod.api_get("/themes.json")

    def test_timeout(self):
        mod = _import_theme_api()
        with patch("shopify_theme_api.requests.get", side_effect=requests.exceptions.Timeout):
            with pytest.raises(requests.exceptions.Timeout):
                mod.api_get("/themes.json")


# ===================================================================
# api_put
# ===================================================================

class TestApiPut:

    def test_success(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "test.liquid"}})
        with patch("shopify_theme_api.requests.put", return_value=resp):
            status, data = mod.api_put("/themes/1/assets.json", {"asset": {"key": "test.liquid", "value": "hi"}})
            assert status == 200
            assert data["asset"]["key"] == "test.liquid"

    def test_empty_response(self):
        mod = _import_theme_api()
        resp = MagicMock()
        resp.status_code = 200
        resp.text = ""
        with patch("shopify_theme_api.requests.put", return_value=resp):
            status, data = mod.api_put("/themes/1/assets.json", {})
            assert data is None


# ===================================================================
# api_delete
# ===================================================================

class TestApiDelete:

    def test_success(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={})
        with patch("shopify_theme_api.requests.delete", return_value=resp):
            status, data = mod.api_delete("/themes/1/assets.json?asset[key]=test.liquid")
            assert status == 200

    def test_empty_response(self):
        mod = _import_theme_api()
        resp = MagicMock()
        resp.status_code = 200
        resp.text = ""
        with patch("shopify_theme_api.requests.delete", return_value=resp):
            status, data = mod.api_delete("/themes/1/assets.json")
            assert data is None


# ===================================================================
# list_themes
# ===================================================================

class TestListThemes:

    def test_success(self, mock_response, themes_list_response):
        mod = _import_theme_api()
        resp = mock_response(json_data=themes_list_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            themes = mod.list_themes()
            assert len(themes) == 2
            assert themes[0]["role"] == "main"

    def test_403_forbidden(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.list_themes()
            assert result is None
            out = capsys.readouterr().out
            assert "403" in out

    def test_500_error(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Server Error"}, status_code=500)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.list_themes()
            assert result is None

    def test_empty_themes_list(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"themes": []})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            themes = mod.list_themes()
            assert themes == []

    def test_missing_themes_key(self, mock_response):
        """Response is 200 but doesn't have 'themes' key."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"something_else": []})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            themes = mod.list_themes()
            assert themes == []

    def test_200_but_none_data(self):
        """
        BUG-ADJACENT: If response.text is empty but status is 200,
        api_get returns (200, None). list_themes checks `if status == 200 and data:`
        which evaluates to False for None — falls through to else, prints error.
        """
        mod = _import_theme_api()
        resp = MagicMock()
        resp.status_code = 200
        resp.text = ""
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.list_themes()
            # data is None, so `if status == 200 and data:` is False
            # Falls to else branch, which prints error with status=200
            assert result is None


# ===================================================================
# get_main_theme
# ===================================================================

class TestGetMainTheme:

    def test_finds_main(self, mock_response, themes_list_response):
        mod = _import_theme_api()
        resp = mock_response(json_data=themes_list_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            theme = mod.get_main_theme()
            assert theme["role"] == "main"
            assert theme["id"] == 100

    def test_no_main_theme(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"themes": [
            {"id": 200, "name": "Draft", "role": "unpublished"},
        ]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            theme = mod.get_main_theme()
            assert theme is None

    def test_empty_themes(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"themes": []})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            assert mod.get_main_theme() is None

    def test_themes_api_error(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            assert mod.get_main_theme() is None

    def test_multiple_main_themes_returns_first(self, mock_response):
        """Edge case: two themes with role=main (shouldn't happen but let's test)."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"themes": [
            {"id": 100, "name": "Main 1", "role": "main"},
            {"id": 101, "name": "Main 2", "role": "main"},
        ]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            theme = mod.get_main_theme()
            assert theme["id"] == 100  # returns first match


# ===================================================================
# list_assets
# ===================================================================

class TestListAssets:

    def test_success(self, mock_response, assets_list_response):
        mod = _import_theme_api()
        resp = mock_response(json_data=assets_list_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            assets = mod.list_assets(100)
            assert len(assets) == 7

    def test_403(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.list_assets(100)
            assert result is None
            assert "403" in capsys.readouterr().out

    def test_500(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Error"}, status_code=500)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.list_assets(100)
            assert result is None

    def test_empty_assets(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": []})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            assets = mod.list_assets(100)
            assert assets == []


# ===================================================================
# get_asset
# ===================================================================

class TestGetAsset:

    def test_success(self, mock_response, asset_response):
        mod = _import_theme_api()
        resp = mock_response(json_data=asset_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            asset = mod.get_asset(100, "layout/theme.liquid")
            assert asset["key"] == "layout/theme.liquid"
            assert "content_for_header" in asset["value"]

    def test_404(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Not found"}, status_code=404)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.get_asset(100, "nonexistent.liquid")
            assert result is None
            assert "nie znaleziony" in capsys.readouterr().out.lower() or "404" in capsys.readouterr().out

    def test_403(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.get_asset(100, "layout/theme.liquid")
            assert result is None

    def test_url_encoding_of_asset_key(self, mock_response, asset_response):
        """Keys with special chars should be URL-encoded."""
        mod = _import_theme_api()
        resp = mock_response(json_data=asset_response)
        with patch("shopify_theme_api.requests.get", return_value=resp) as m:
            mod.get_asset(100, "assets/file name.js")
            url = m.call_args[0][0]
            assert "file%20name.js" in url

    def test_key_with_unicode(self, mock_response, asset_response):
        mod = _import_theme_api()
        resp = mock_response(json_data=asset_response)
        with patch("shopify_theme_api.requests.get", return_value=resp) as m:
            mod.get_asset(100, "assets/pl\u00f3d\u017a.liquid")
            url = m.call_args[0][0]
            # Should be encoded
            assert "pl" in url

    def test_empty_asset_value(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "empty.liquid", "value": ""}})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            asset = mod.get_asset(100, "empty.liquid")
            assert asset["value"] == ""

    def test_binary_asset_no_value(self, mock_response):
        """Binary assets (images) have no 'value' key, only 'public_url'."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "assets/logo.png", "public_url": "https://cdn.shopify.com/..."}})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            asset = mod.get_asset(100, "assets/logo.png")
            assert "value" not in asset
            assert asset["public_url"].startswith("https://")


# ===================================================================
# update_asset
# ===================================================================

class TestUpdateAsset:

    def test_success(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "layout/theme.liquid"}})
        with patch("shopify_theme_api.requests.put", return_value=resp):
            result = mod.update_asset(100, "layout/theme.liquid", "<html>new</html>")
            assert result["key"] == "layout/theme.liquid"
            assert "Zaktualizowano" in capsys.readouterr().out

    def test_403(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.put", return_value=resp):
            result = mod.update_asset(100, "layout/theme.liquid", "content")
            assert result is None
            assert "403" in capsys.readouterr().out

    def test_422_validation_error(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": {"asset": ["is invalid"]}}, status_code=422)
        with patch("shopify_theme_api.requests.put", return_value=resp):
            result = mod.update_asset(100, "layout/theme.liquid", "{{{{ invalid")
            assert result is None

    def test_empty_content(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "test.liquid"}})
        with patch("shopify_theme_api.requests.put", return_value=resp) as m:
            mod.update_asset(100, "test.liquid", "")
            payload = m.call_args.kwargs["json"]
            assert payload["asset"]["value"] == ""

    def test_huge_content(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "test.liquid"}})
        with patch("shopify_theme_api.requests.put", return_value=resp):
            big_content = "x" * 1_000_000
            result = mod.update_asset(100, "test.liquid", big_content)
            assert result is not None

    def test_unicode_content(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "test.liquid"}})
        with patch("shopify_theme_api.requests.put", return_value=resp) as m:
            mod.update_asset(100, "test.liquid", "Zdrowie i \u0142\u00f3d\u017a")
            payload = m.call_args.kwargs["json"]
            assert "\u0142\u00f3d\u017a" in payload["asset"]["value"]


# ===================================================================
# delete_asset
# ===================================================================

class TestDeleteAsset:

    def test_success(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={})
        with patch("shopify_theme_api.requests.delete", return_value=resp):
            result = mod.delete_asset(100, "snippets/old.liquid")
            assert result is True
            assert "Usuni\u0119to" in capsys.readouterr().out

    def test_403(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.delete", return_value=resp):
            result = mod.delete_asset(100, "snippets/old.liquid")
            assert result is False

    def test_404(self, mock_response, capsys):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Not found"}, status_code=404)
        with patch("shopify_theme_api.requests.delete", return_value=resp):
            result = mod.delete_asset(100, "nonexistent.liquid")
            assert result is False


# ===================================================================
# backup_asset
# ===================================================================

class TestBackupAsset:

    def test_successful_backup(self, mock_response, asset_response, tmp_path):
        mod = _import_theme_api()
        resp = mock_response(json_data=asset_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            with patch("shopify_theme_api.os.makedirs") as mock_makedirs:
                with patch("builtins.open", mock_open()) as mf:
                    result = mod.backup_asset(100, "layout/theme.liquid")
                    assert result is not None
                    assert "theme_backups" in result
                    assert "layout_theme.liquid" in result
                    mock_makedirs.assert_called_once_with("theme_backups", exist_ok=True)
                    mf.assert_called_once()

    def test_asset_without_value(self, mock_response):
        """Binary asset or asset where get_asset returns no 'value'."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "assets/logo.png"}})  # no 'value'
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.backup_asset(100, "assets/logo.png")
            assert result is None

    def test_asset_with_empty_value(self, mock_response):
        """Asset value is empty string (falsy) — backup should NOT be created."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"asset": {"key": "empty.liquid", "value": ""}})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.backup_asset(100, "empty.liquid")
            # asset.get("value") is "" which is falsy, so backup_asset returns None
            assert result is None

    def test_get_asset_returns_none(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Not found"}, status_code=404)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            result = mod.backup_asset(100, "nonexistent.liquid")
            assert result is None

    def test_slash_replacement_in_filename(self, mock_response, asset_response):
        mod = _import_theme_api()
        resp = mock_response(json_data=asset_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            with patch("shopify_theme_api.os.makedirs"):
                with patch("builtins.open", mock_open()) as mf:
                    result = mod.backup_asset(100, "layout/theme.liquid")
                    assert "/" not in result.split("theme_backups/")[1].split("_2")[0] or \
                           "layout_theme.liquid" in result

    def test_io_error_on_write(self, mock_response, asset_response):
        """
        BUG FOUND: If open() fails (disk full, permissions), backup_asset
        will raise an unhandled IOError/OSError.
        """
        mod = _import_theme_api()
        resp = mock_response(json_data=asset_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            with patch("shopify_theme_api.os.makedirs"):
                with patch("builtins.open", side_effect=IOError("Disk full")):
                    with pytest.raises(IOError):
                        mod.backup_asset(100, "layout/theme.liquid")


# ===================================================================
# find_consent_files
# ===================================================================

class TestFindConsentFiles:

    def test_finds_matching_files(self, mock_response, assets_list_response):
        mod = _import_theme_api()
        resp = mock_response(json_data=assets_list_response)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            # "pandectes" matches "assets/pandectes-settings.json"
            assert "assets/pandectes-settings.json" in found

    def test_no_matching_files(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": [
            {"key": "layout/theme.liquid"},
            {"key": "sections/header.liquid"},
        ]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert found == []

    def test_empty_assets(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": []})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert found == []

    def test_assets_api_error(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert found == []

    def test_case_insensitive_match(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": [
            {"key": "assets/COOKIE_settings.json"},
            {"key": "snippets/GDPR_banner.liquid"},
        ]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert len(found) == 2

    def test_multiple_keyword_matches(self, mock_response):
        """A file matching multiple keywords should appear only once."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": [
            {"key": "snippets/consent-cookie-gdpr.liquid"},
        ]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert len(found) == 1

    def test_google_keyword_matches(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": [
            {"key": "snippets/google-tag-manager.liquid"},
        ]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert len(found) == 1

    def test_gtm_and_gtag_keywords(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": [
            {"key": "snippets/gtm-head.liquid"},
            {"key": "snippets/gtag-config.liquid"},
        ]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert len(found) == 2

    def test_asset_with_empty_key(self, mock_response):
        """Edge case: asset dict with empty 'key'."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": [{"key": ""}, {"key": "snippets/consent.liquid"}]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert len(found) == 1  # only "consent" matches

    def test_asset_without_key(self, mock_response):
        """Edge case: asset dict missing 'key' entirely."""
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": [{}]})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.find_consent_files(100)
            assert found == []


# ===================================================================
# search_in_assets
# ===================================================================

class TestSearchInAssets:

    def _setup_search(self, mod, mock_response, assets, asset_contents):
        """
        Setup mocks: list_assets returns `assets`, and get_asset returns
        `asset_contents[key]` for each key.
        """
        list_resp = mock_response(json_data={"assets": assets})

        def get_side_effect(*args, **kwargs):
            url = args[0]
            # list_assets call
            if "assets.json" in url and "asset%5Bkey%5D" not in url and "asset[key]" not in url:
                return list_resp
            # get_asset call — extract key from URL
            for key, content in asset_contents.items():
                encoded = requests.utils.quote(key, safe='')
                if encoded in url:
                    return mock_response(json_data={"asset": {"key": key, "value": content}})
            return mock_response(json_data={"asset": {"key": "unknown", "value": ""}})

        return get_side_effect

    def test_finds_term_in_liquid_file(self, mock_response):
        mod = _import_theme_api()
        assets = [{"key": "layout/theme.liquid"}, {"key": "assets/style.css"}]
        contents = {
            "layout/theme.liquid": "<html>Pandectes consent banner</html>",
            "assets/style.css": "body { color: red; }",
        }
        side_effect = self._setup_search(mod, mock_response, assets, contents)
        with patch("shopify_theme_api.requests.get", side_effect=side_effect):
            found = mod.search_in_assets(100, "Pandectes")
            assert "layout/theme.liquid" in found
            assert "assets/style.css" not in found

    def test_case_insensitive_search(self, mock_response):
        mod = _import_theme_api()
        assets = [{"key": "layout/theme.liquid"}]
        contents = {"layout/theme.liquid": "PANDECTES is active"}
        side_effect = self._setup_search(mod, mock_response, assets, contents)
        with patch("shopify_theme_api.requests.get", side_effect=side_effect):
            found = mod.search_in_assets(100, "pandectes")
            assert len(found) == 1

    def test_skips_binary_files(self, mock_response):
        """Non-text extensions should be skipped entirely."""
        mod = _import_theme_api()
        assets = [{"key": "assets/logo.png"}, {"key": "layout/theme.liquid"}]
        contents = {"layout/theme.liquid": "findme"}
        side_effect = self._setup_search(mod, mock_response, assets, contents)
        with patch("shopify_theme_api.requests.get", side_effect=side_effect):
            found = mod.search_in_assets(100, "findme")
            assert "assets/logo.png" not in found

    def test_empty_search_term(self, mock_response):
        """Empty string matches everything."""
        mod = _import_theme_api()
        assets = [{"key": "layout/theme.liquid"}]
        contents = {"layout/theme.liquid": "some content"}
        side_effect = self._setup_search(mod, mock_response, assets, contents)
        with patch("shopify_theme_api.requests.get", side_effect=side_effect):
            found = mod.search_in_assets(100, "")
            assert len(found) == 1

    def test_no_assets(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"assets": []})
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.search_in_assets(100, "anything")
            assert found == []

    def test_assets_api_error(self, mock_response):
        mod = _import_theme_api()
        resp = mock_response(json_data={"errors": "Forbidden"}, status_code=403)
        with patch("shopify_theme_api.requests.get", return_value=resp):
            found = mod.search_in_assets(100, "anything")
            assert found == []

    def test_asset_with_no_value_key(self, mock_response):
        """get_asset might return asset without 'value' for binary files."""
        mod = _import_theme_api()
        assets = [{"key": "assets/app.js"}]

        def side_effect(*args, **kwargs):
            url = args[0]
            if "asset%5Bkey%5D" not in url and "asset[key]" not in url:
                return mock_response(json_data={"assets": assets})
            return mock_response(json_data={"asset": {"key": "assets/app.js"}})  # no 'value'

        with patch("shopify_theme_api.requests.get", side_effect=side_effect):
            found = mod.search_in_assets(100, "anything")
            assert found == []

    def test_unicode_search_term(self, mock_response):
        mod = _import_theme_api()
        assets = [{"key": "snippets/footer.liquid"}]
        contents = {"snippets/footer.liquid": "Polityka plik\u00f3w Cookkies"}
        side_effect = self._setup_search(mod, mock_response, assets, contents)
        with patch("shopify_theme_api.requests.get", side_effect=side_effect):
            found = mod.search_in_assets(100, "Cookkies")
            assert len(found) == 1

    def test_text_extensions_coverage(self, mock_response):
        """Verify all supported text extensions are checked."""
        mod = _import_theme_api()
        assets = [
            {"key": "layout/theme.liquid"},
            {"key": "config/settings_schema.json"},
            {"key": "assets/app.js"},
            {"key": "assets/style.css"},
            {"key": "templates/index.html"},
        ]
        contents = {
            "layout/theme.liquid": "TARGET",
            "config/settings_schema.json": "TARGET",
            "assets/app.js": "TARGET",
            "assets/style.css": "TARGET",
            "templates/index.html": "TARGET",
        }
        side_effect = self._setup_search(mod, mock_response, assets, contents)
        with patch("shopify_theme_api.requests.get", side_effect=side_effect):
            found = mod.search_in_assets(100, "TARGET")
            assert len(found) == 5


# ===================================================================
# print_json
# ===================================================================

class TestPrintJson:

    def test_dict(self, capsys):
        mod = _import_theme_api()
        mod.print_json({"key": "val"})
        assert '"key"' in capsys.readouterr().out

    def test_none(self, capsys):
        mod = _import_theme_api()
        mod.print_json(None)
        assert "null" in capsys.readouterr().out

    def test_list(self, capsys):
        mod = _import_theme_api()
        mod.print_json([1, 2, 3])
        out = capsys.readouterr().out
        assert "1" in out and "3" in out

    def test_unicode(self, capsys):
        mod = _import_theme_api()
        mod.print_json({"city": "\u0141\u00f3d\u017a"})
        assert "\u0141\u00f3d\u017a" in capsys.readouterr().out


# ===================================================================
# CLI __main__ block
# ===================================================================

class TestCLI:

    def _run_main(self, argv_args, mock_get_response=None, mock_put_response=None):
        mod = _import_theme_api()
        full_argv = ["shopify_theme_api.py"] + argv_args
        source_path = mod.__file__
        with open(source_path) as f:
            source = f.read()
        code = compile(source, source_path, "exec")
        ns = {"__name__": "__main__", "__file__": source_path}

        mock_get = MagicMock(return_value=mock_get_response) if mock_get_response else MagicMock()
        mock_put = MagicMock(return_value=mock_put_response) if mock_put_response else MagicMock()

        with patch.object(sys, "argv", full_argv):
            with patch("requests.get", mock_get):
                with patch("requests.put", mock_put):
                    try:
                        exec(code, ns)
                    except SystemExit:
                        pass  # some commands call sys.exit

    def test_no_args_shows_help(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main([], resp)
        out = capsys.readouterr().out
        assert "SHOPIFY THEME API" in out

    def test_themes_command(self, mock_response, capsys, themes_list_response):
        resp = mock_response(json_data=themes_list_response)
        self._run_main(["themes"], resp)
        out = capsys.readouterr().out
        assert "GEN-6" in out or "100" in out

    def test_assets_command(self, mock_response, capsys, themes_list_response, assets_list_response):
        """assets without theme_id should use main theme."""
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_response(json_data=themes_list_response)
            return mock_response(json_data=assets_list_response)

        mock_get = MagicMock(side_effect=side_effect)
        mod = _import_theme_api()
        source_path = mod.__file__
        with open(source_path) as f:
            source = f.read()
        code = compile(source, source_path, "exec")
        ns = {"__name__": "__main__", "__file__": source_path}
        with patch.object(sys, "argv", ["shopify_theme_api.py", "assets"]):
            with patch("requests.get", mock_get):
                exec(code, ns)
        out = capsys.readouterr().out
        assert "layout" in out.lower() or "pliki" in out.lower()

    def test_get_command_without_key(self, mock_response, capsys):
        """get without asset_key should show usage and exit."""
        resp = mock_response(json_data={})
        self._run_main(["get"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "get" in out.lower()

    def test_backup_command_without_key(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["backup"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "backup" in out.lower()

    def test_search_command_without_term(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["search"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "search" in out.lower()

    def test_update_command_without_args(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["update"], resp)
        out = capsys.readouterr().out
        assert "ycie" in out or "update" in out.lower()

    def test_help_command(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["help"], resp)
        out = capsys.readouterr().out
        assert "KOMENDY" in out or "themes" in out.lower()

    def test_dash_h_flag(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["-h"], resp)
        out = capsys.readouterr().out
        assert "KOMENDY" in out or "themes" in out.lower()

    def test_unknown_command(self, mock_response, capsys):
        resp = mock_response(json_data={})
        self._run_main(["blargh"], resp)
        out = capsys.readouterr().out
        assert "Nieznana" in out or "blargh" in out

    def test_find_consent_command(self, mock_response, capsys, themes_list_response, assets_list_response):
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_response(json_data=themes_list_response)
            return mock_response(json_data=assets_list_response)

        mock_get = MagicMock(side_effect=side_effect)
        mod = _import_theme_api()
        source_path = mod.__file__
        with open(source_path) as f:
            source = f.read()
        code = compile(source, source_path, "exec")
        ns = {"__name__": "__main__", "__file__": source_path}
        with patch.object(sys, "argv", ["shopify_theme_api.py", "find-consent"]):
            with patch("requests.get", mock_get):
                exec(code, ns)
        out = capsys.readouterr().out
        assert "consent" in out.lower() or "pandectes" in out.lower() or "Szukam" in out

    def test_update_nonexistent_local_file(self, mock_response, capsys, themes_list_response):
        """update with a local file that doesn't exist."""
        resp = mock_response(json_data=themes_list_response)
        self._run_main(["update", "layout/theme.liquid", "/tmp/nonexistent_file_xyz.liquid"], resp)
        out = capsys.readouterr().out
        assert "nie istnieje" in out.lower() or "nonexistent" in out.lower()


# ===================================================================
# Edge cases: module-level globals
# ===================================================================

class TestModuleGlobals:

    def test_base_url_construction(self):
        mod = _import_theme_api()
        assert "myshopify.com" in mod.BASE_URL
        assert "/admin/api/" in mod.BASE_URL

    def test_headers_have_required_keys(self):
        mod = _import_theme_api()
        assert "Content-Type" in mod.HEADERS
        assert "X-Shopify-Access-Token" in mod.HEADERS
        assert mod.HEADERS["Content-Type"] == "application/json"

    def test_default_env_values(self, monkeypatch):
        """If env vars are missing, defaults should be used.
        We must also patch load_dotenv to prevent .env from repopulating them."""
        monkeypatch.delenv("SHOPIFY_DOMAIN", raising=False)
        monkeypatch.delenv("SHOPIFY_ACCESS_TOKEN", raising=False)
        monkeypatch.delenv("SHOPIFY_API_VERSION", raising=False)
        with patch("dotenv.load_dotenv", return_value=None):
            mod = _import_theme_api()
        # Defaults defined in the script
        assert "genactiv.myshopify.com" in mod.BASE_URL
        assert mod.ACCESS_TOKEN == ""
