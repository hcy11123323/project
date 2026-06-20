"""Tests for layer_3.config_updater — selector priority self-healing."""

from __future__ import annotations

import yaml
import pytest

from src.layer_3.config_updater import _is_xpath, update_selector_priority


# ---------------------------------------------------------------------------
# _is_xpath
# ---------------------------------------------------------------------------


class TestIsXpath:
    """Tests for the _is_xpath helper."""

    @pytest.mark.parametrize(
        "selector, expected",
        [
            ("//div[@id='x']", True),
            ("/html/body", True),
            ("  //div", True),  # leading whitespace
            ("#submit", False),
            ("button[type='submit']", False),
            (".btn-search", False),
            ("text=搜索", False),
            ("role=button", False),
        ],
    )
    def test_xpath_detection(self, selector, expected):
        assert _is_xpath(selector) == expected


# ---------------------------------------------------------------------------
# update_selector_priority
# ---------------------------------------------------------------------------


class TestUpdateSelectorPriority:
    """Tests for update_selector_priority()."""

    def test_promote_css_fallback(self, sample_yaml_dir):
        """Should move a CSS selector to index 0 when it's not already first."""
        result = update_selector_priority(
            domain_name="test_site",
            element_name="submit_btn",
            successful_selector="button[type='submit']",
            domains_dir=sample_yaml_dir,
        )
        assert result is True

        # Verify the file was rewritten
        with open(f"{sample_yaml_dir}/test_site.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        css_list = data["locators"]["submit_btn"]["css"]
        assert css_list[0] == "button[type='submit']"

    def test_promote_xpath_fallback(self, sample_yaml_dir):
        """Should move an XPath selector to index 0 of the xpath list."""
        result = update_selector_priority(
            domain_name="test_site",
            element_name="submit_btn",
            successful_selector="//button[@id='submit']",
            domains_dir=sample_yaml_dir,
        )
        assert result is True

        with open(f"{sample_yaml_dir}/test_site.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        xpath_list = data["locators"]["submit_btn"]["xpath"]
        assert xpath_list[0] == "//button[@id='submit']"

    def test_already_first(self, sample_yaml_dir):
        """Should return True without modifying file when selector is already first."""
        result = update_selector_priority(
            domain_name="test_site",
            element_name="submit_btn",
            successful_selector="#submit",  # already at index 0
            domains_dir=sample_yaml_dir,
        )
        assert result is True

    def test_selector_not_in_list(self, sample_yaml_dir):
        """Should return False when the selector doesn't exist in the list."""
        result = update_selector_priority(
            domain_name="test_site",
            element_name="submit_btn",
            successful_selector="#nonexistent",
            domains_dir=sample_yaml_dir,
        )
        assert result is False

    def test_missing_yaml_file(self, tmp_path):
        """Should return False when the YAML file doesn't exist."""
        result = update_selector_priority(
            domain_name="ghost",
            element_name="btn",
            successful_selector="#btn",
            domains_dir=str(tmp_path),
        )
        assert result is False

    def test_missing_element(self, sample_yaml_dir):
        """Should return False when the element name doesn't exist."""
        result = update_selector_priority(
            domain_name="test_site",
            element_name="nonexistent_element",
            successful_selector="#submit",
            domains_dir=sample_yaml_dir,
        )
        assert result is False
