"""Shared fixtures for agentic-playwright-mcp tests."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = str(PROJECT_ROOT / "domains")


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@pytest.fixture
def domains_dir() -> str:
    """Return the path to the domains/ directory."""
    return DOMAINS_DIR


# ---------------------------------------------------------------------------
# Temporary YAML fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_yaml(tmp_path):
    """Factory: write a YAML dict to a temp file and return its path."""

    def _write(filename: str, data: dict) -> str:
        path = tmp_path / filename
        path.write_text(yaml.dump(data, allow_unicode=True), encoding="utf-8")
        return str(tmp_path)

    return _write


@pytest.fixture
def sample_domain_data():
    """A minimal domain config dict matching the DomainConfig schema."""
    return {
        "name": "test_site",
        "base_url": "https://example.com",
        "locators": {
            "submit_btn": {
                "css": ["#submit", "button[type='submit']"],
                "xpath": ["//button[@id='submit']"],
            },
            "search_input": {
                "css": ["#search", "input[name='q']"],
                "xpath": ["//input[@id='search']"],
            },
        },
    }


@pytest.fixture
def sample_yaml_dir(tmp_path, sample_domain_data):
    """Write a sample domain YAML to tmp_path and return the directory."""
    path = tmp_path / "test_site.yaml"
    path.write_text(
        yaml.dump(sample_domain_data, allow_unicode=True),
        encoding="utf-8",
    )
    return str(tmp_path)


# ---------------------------------------------------------------------------
# Playwright Page mock
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_page():
    """A MagicMock pretending to be a Playwright Page.

    Default behavior:
    - is_visible() returns True for '#default-selector'
    - click() / fill() / goto() succeed
    """
    page = MagicMock()
    page.url = "https://example.com"
    page.is_visible.return_value = True
    page.click.return_value = None
    page.fill.return_value = None
    page.screenshot.return_value = None

    # goto returns a mock response
    response = MagicMock()
    response.status = 200
    page.goto.return_value = response

    return page
