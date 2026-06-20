"""
Example 03: Domain-Driven Automation with Self-Healing Selectors

Demonstrates:
- Loading domain configurations from YAML files
- Using smart_click and smart_fill with domain selectors
- Self-healing mechanism: when primary selectors fail, fallbacks are tried
- Automatic priority promotion when a backup selector succeeds
- Composite operations: smart_search, smart_login, smart_fill_form

Prerequisites:
    - domains/example_baidu.yaml must exist (ships with the project)

Usage:
    python examples/03_domain_automation.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.browser_manager import get_browser_manager, reset_browser_manager
from src.layer_2.controls import (
    goto,
    smart_click,
    smart_fill,
    smart_search,
    smart_fill_form,
    wait_for_navigation,
    get_page_title,
    screenshot,
)
from src.layer_3.domain_loader import load_domain, get_element_selectors


def demo_domain_loading():
    """Show how domain YAML configs are loaded and validated."""
    print("--- Domain Loading ---")

    project_root = Path(__file__).resolve().parent.parent
    domains_dir = str(project_root / "domains")

    # Load the Baidu domain config
    config = load_domain("baidu", domains_dir=domains_dir)
    print(f"  Domain name: {config.name}")
    print(f"  Base URL: {config.base_url}")
    print(f"  Registered elements: {list(config.locators.keys())}")

    # Show selectors for search_input
    selectors = get_element_selectors(config, "search_input")
    print(f"  search_input selectors ({len(selectors)}):")
    for i, sel in enumerate(selectors):
        print(f"    [{i}] {sel}")

    print()


def demo_smart_operations():
    """Demonstrate domain-driven smart operations."""
    print("--- Smart Operations ---")

    # Navigate to Baidu
    print("\n[1] Navigating to Baidu...")
    result = goto("https://www.baidu.com")
    print(f"    {result}")

    # Smart fill: uses domain config for selector resolution
    print("\n[2] Filling search box via domain config...")
    result = smart_fill("search_input", "Playwright 自动化", domain="baidu")
    print(f"    Success: {result.get('success')}")
    print(f"    Used selector: {result.get('used_selector')}")
    print(f"    Selector index: {result.get('index')}")
    print(f"    Self-healed: {result.get('healed')}")

    # Smart click: uses domain config for selector resolution
    print("\n[3] Clicking search button via domain config...")
    result = smart_click("search_button", domain="baidu")
    print(f"    Success: {result.get('success')}")
    print(f"    Used selector: {result.get('used_selector')}")

    # Wait for results
    print("\n[4] Waiting for search results...")
    wait_for_navigation(timeout=10)
    print(f"    Page title: {get_page_title()}")

    # Screenshot the results
    print("\n[5] Taking screenshot of results...")
    path = screenshot("examples/output/baidu_search_results.png")
    print(f"    Saved to: {path}")


def demo_composite_operations():
    """Demonstrate composite smart operations."""
    print("\n--- Composite Operations ---")

    # smart_search combines navigate + fill + click + wait
    print("\n[1] Using smart_search (all-in-one)...")
    result = smart_search(
        domain="baidu",
        keyword="MCP Model Context Protocol",
        input_field="search_input",
        submit_field="search_button",
    )
    print(f"    Success: {result.get('success')}")
    print(f"    Steps completed: {len(result.get('steps', []))}")
    for step in result.get("steps", []):
        print(f"      - {step['step']}: {step['result'][:60]}...")

    # smart_fill_form for batch form filling
    print("\n[2] Using smart_fill_form (batch fill)...")
    # This demonstrates the API; Baidu only has one field so we show the pattern
    result = smart_fill_form(
        domain="baidu",
        field_values={"search_input": "批量填写测试"},
    )
    print(f"    Success: {result.get('success')}")
    for field_name, field_result in result.get("results", {}).items():
        print(f"      - {field_name}: selector={field_result.get('used_selector')}")


def main():
    reset_browser_manager()

    print("=== Example 03: Domain-Driven Automation ===\n")

    # Part 1: Show domain loading (no browser needed)
    demo_domain_loading()

    # Part 2 & 3: Browser operations
    bm = get_browser_manager()
    print("Launching browser...")
    bm.launch(headless=False, slow_mo=300)

    try:
        demo_smart_operations()
        demo_composite_operations()
    finally:
        print("\nClosing browser...")
        bm.close()

    print("\n=== Example complete ===")


if __name__ == "__main__":
    main()
