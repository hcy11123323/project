"""
Example 01: Basic Browser Automation

Demonstrates:
- Launching a browser with BrowserManager
- Navigating to a URL
- Taking a screenshot
- Extracting page title and URL
- Closing the browser cleanly

Usage:
    python examples/01_basic_browser.py
"""

import sys
from pathlib import Path

# Add project root to path so we can import src
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.browser_manager import get_browser_manager, reset_browser_manager
from src.layer_1.actions import do_goto, do_screenshot


def main():
    # Reset any previous browser instance (clean start)
    reset_browser_manager()

    bm = get_browser_manager()

    print("=== Example 01: Basic Browser Automation ===\n")

    # 1. Launch browser (headed mode for visibility)
    print("[1] Launching browser...")
    page = bm.launch(headless=False, slow_mo=500)
    print(f"    Browser engine: {bm.engine}")
    print(f"    Initial URL: {page.url}\n")

    # 2. Navigate to a page
    print("[2] Navigating to example.com...")
    result = do_goto(page, "https://example.com")
    print(f"    {result}")
    print(f"    Page title: {page.title()}\n")

    # 3. Take a screenshot
    print("[3] Taking screenshot...")
    screenshot_path = do_screenshot(page, "examples/output/basic_screenshot.png")
    print(f"    Saved to: {screenshot_path}\n")

    # 4. Navigate to another page
    print("[4] Navigating to httpbin.org...")
    result = do_goto(page, "https://httpbin.org/html")
    print(f"    {result}")
    print(f"    Page title: {page.title()}\n")

    # 5. Extract page text
    print("[5] Extracting page text...")
    text = page.evaluate("document.body.innerText")
    preview = text[:200] + "..." if len(text) > 200 else text
    print(f"    Text preview: {preview}\n")

    # 6. Close browser
    print("[6] Closing browser...")
    bm.close()
    print("    Done!")

    print("\n=== Example complete ===")


if __name__ == "__main__":
    main()
