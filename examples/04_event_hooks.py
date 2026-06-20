"""
Example 04: Event Hooks for Observability

Demonstrates:
- Registering hooks on the EventBus for lifecycle events
- Using @bus.on() decorator for before/after hooks
- One-shot hooks with bus.once()
- Modifying event data in before hooks (e.g., rewrite selectors)
- Cancelling actions from before hooks
- Using the lifecycle context manager
- Unregistering hooks

Usage:
    python examples/04_event_hooks.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.browser_manager import get_browser_manager, reset_browser_manager
from src.core.event_bus import (
    EVENT_BROWSER_LAUNCH,
    EVENT_BROWSER_CLOSE,
    EVENT_CLICK,
    EVENT_FILL,
    EVENT_GOTO,
    EVENT_SCREENSHOT,
    Event,
    Phase,
    get_event_bus,
    reset_event_bus,
)
from src.layer_1.actions import do_goto, do_click, do_fill, do_screenshot


def main():
    reset_browser_manager()
    reset_event_bus()

    bus = get_event_bus()

    print("=== Example 04: Event Hooks ===\n")

    # --- Hook 1: Log all navigations ---
    @bus.on(EVENT_GOTO, phase="after")
    def log_navigation(event: Event):
        url = event.data.get("url", "unknown")
        result = event.result or ""
        print(f"  [HOOK] Navigated to: {url}")
        print(f"  [HOOK] Result: {result[:80]}")

    # --- Hook 2: Timing for browser launch ---
    @bus.on(EVENT_BROWSER_LAUNCH, phase="before")
    def record_launch_start(event: Event):
        event.metadata["start_time"] = time.monotonic()
        print(f"  [HOOK] Browser launching (engine={event.data.get('engine')})...")

    @bus.on(EVENT_BROWSER_LAUNCH, phase="after")
    def record_launch_end(event: Event):
        start = event.metadata.get("start_time", time.monotonic())
        elapsed = (time.monotonic() - start) * 1000
        print(f"  [HOOK] Browser launched in {elapsed:.0f}ms")

    # --- Hook 3: Count clicks ---
    click_count = 0

    @bus.on(EVENT_CLICK, phase="after")
    def count_clicks(event: Event):
        nonlocal click_count
        click_count += 1
        success = event.result.get("success", False) if isinstance(event.result, dict) else False
        selector = event.result.get("used_selector", "?") if isinstance(event.result, dict) else "?"
        print(f"  [HOOK] Click #{click_count}: selector={selector}, success={success}")

    # --- Hook 4: One-shot hook (fires once then auto-removes) ---
    def on_first_screenshot(event: Event):
        print(f"  [HOOK] First screenshot captured! Path: {event.data.get('path')}")

    bus.once(EVENT_SCREENSHOT, on_first_screenshot, phase="after")

    # --- Hook 5: Modify fill value (before hook) ---
    @bus.on(EVENT_FILL, phase="before")
    def uppercase_fill_value(event: Event):
        original = event.data.get("value", "")
        # Demonstrate modifying event data before the action executes
        event.data["value"] = original.upper()
        print(f"  [HOOK] Modified fill value: '{original}' -> '{original.upper()}'")

    # --- Demonstrate hooks in action ---
    bm = get_browser_manager()

    print("[1] Launching browser (hooks will fire)...")
    page = bm.launch(headless=False, slow_mo=300)

    print("\n[2] Navigating (navigation hook will fire)...")
    do_goto(page, "https://example.com")

    print("\n[3] Filling text (fill hook will modify value)...")
    do_fill(page, ["#nonexistent"], "hello world")

    print("\n[4] Clicking (click counter hook)...")
    do_click(page, ["h1"])  # Click the heading

    print("\n[5] Taking screenshot (one-shot hook fires once)...")
    do_screenshot(page, "examples/output/hook_screenshot_1.png")

    print("\n[6] Taking another screenshot (one-shot hook already fired)...")
    do_screenshot(page, "examples/output/hook_screenshot_2.png")

    # --- Unregister a hook ---
    print("\n[7] Unregistering navigation hook...")
    removed = bus.unregister(EVENT_GOTO, log_navigation)
    print(f"    Removed: {removed}")

    print("\n[8] Navigating again (no navigation hook)...")
    do_goto(page, "https://httpbin.org/html")

    # --- Show hook counts ---
    print(f"\n[9] Hook summary:")
    print(f"    Total clicks recorded: {click_count}")
    print(f"    Registered events: {bus.list_events()}")
    print(f"    Total hooks: {bus.hook_count()}")

    # --- Lifecycle context manager ---
    print("\n[10] Using lifecycle context manager...")
    with bus.lifecycle("custom_operation", {"detail": "demo"}) as event:
        print(f"    Before phase data: {event.data}")
        event.result = "custom operation completed"
    print(f"    After phase result: {event.result}")

    # Cleanup
    print("\n[11] Closing browser...")
    bm.close()
    print("    Done!")

    print("\n=== Example complete ===")


if __name__ == "__main__":
    main()
