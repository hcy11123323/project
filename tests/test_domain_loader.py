"""Tests for layer_3.domain_loader — YAML parsing and selector extraction."""

from __future__ import annotations

import pytest

from src.layer_3.domain_loader import (
    DomainConfig,
    LocatorItem,
    get_element_selectors,
    load_domain,
)


# ---------------------------------------------------------------------------
# load_domain
# ---------------------------------------------------------------------------


class TestLoadDomain:
    """Tests for load_domain()."""

    def test_load_valid_yaml(self, sample_yaml_dir):
        """Should parse a valid YAML into DomainConfig."""
        cfg = load_domain("test_site", domains_dir=sample_yaml_dir)
        assert isinstance(cfg, DomainConfig)
        assert cfg.name == "test_site"
        assert cfg.base_url == "https://example.com"
        assert "submit_btn" in cfg.locators
        assert "search_input" in cfg.locators

    def test_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing YAML."""
        with pytest.raises(FileNotFoundError, match="不存在"):
            load_domain("nonexistent", domains_dir=str(tmp_path))

    def test_invalid_yaml_structure(self, tmp_path):
        """Should raise ValidationError when YAML lacks required fields."""
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("name: bad\n", encoding="utf-8")  # missing locators
        with pytest.raises(Exception):  # pydantic.ValidationError
            load_domain("bad", domains_dir=str(tmp_path))

    def test_empty_locators(self, tmp_path):
        """Should accept an empty locators dict."""
        data = {"name": "empty", "locators": {}}
        import yaml

        f = tmp_path / "empty.yaml"
        f.write_text(yaml.dump(data), encoding="utf-8")
        cfg = load_domain("empty", domains_dir=str(tmp_path))
        assert cfg.locators == {}


# ---------------------------------------------------------------------------
# get_element_selectors
# ---------------------------------------------------------------------------


class TestGetElementSelectors:
    """Tests for get_element_selectors()."""

    def test_css_then_xpath(self, sample_yaml_dir):
        """Should return CSS selectors first, then XPath."""
        cfg = load_domain("test_site", domains_dir=sample_yaml_dir)
        sels = get_element_selectors(cfg, "submit_btn")
        assert sels == ["#submit", "button[type='submit']", "//button[@id='submit']"]

    def test_element_not_found(self, sample_yaml_dir):
        """Should raise ValueError for unknown element name."""
        cfg = load_domain("test_site", domains_dir=sample_yaml_dir)
        with pytest.raises(ValueError, match="不存在"):
            get_element_selectors(cfg, "nonexistent_button")

    def test_css_only(self):
        """Should work when only CSS selectors are defined."""
        cfg = DomainConfig(
            name="css_only",
            locators={
                "btn": LocatorItem(css=[".btn"]),
            },
        )
        sels = get_element_selectors(cfg, "btn")
        assert sels == [".btn"]

    def test_xpath_only(self):
        """Should work when only XPath selectors are defined."""
        cfg = DomainConfig(
            name="xpath_only",
            locators={
                "btn": LocatorItem(xpath=["//button"]),
            },
        )
        sels = get_element_selectors(cfg, "btn")
        assert sels == ["//button"]


# ---------------------------------------------------------------------------
# Pydantic model edge cases
# ---------------------------------------------------------------------------


class TestLocatorItem:
    """Tests for LocatorItem model."""

    def test_both_none(self):
        """Should allow both css and xpath to be None."""
        item = LocatorItem()
        assert item.css is None
        assert item.xpath is None

    def test_both_set(self):
        """Should allow both css and xpath to be set."""
        item = LocatorItem(css=[".a"], xpath=["//a"])
        assert item.css == [".a"]
        assert item.xpath == ["//a"]
