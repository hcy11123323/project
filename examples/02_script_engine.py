"""
Example 02: Script Engine (Sandboxed Execution)

Demonstrates:
- Using the ScriptEngine to run AI-generated scripts safely
- Built-in functions available in the sandbox (goto, click, fill, screenshot)
- Capturing print output and errors
- The restricted namespace (no imports, no file system access)

Usage:
    python examples/02_script_engine.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.browser_manager import get_browser_manager, reset_browser_manager
from src.core.script_engine import get_script_engine, reset_script_engine
from src.layer_2.controls import get_controls_exports


def main():
    reset_browser_manager()
    reset_script_engine()

    bm = get_browser_manager()
    engine = get_script_engine()

    # Register Layer 2 controls into the script namespace
    engine.register_functions(get_controls_exports())

    print("=== Example 02: Script Engine ===\n")

    # Launch browser
    print("[0] Launching browser...")
    bm.launch(headless=False, slow_mo=300)

    # --- Script 1: Simple navigation and info extraction ---
    print("\n[1] Running script: navigate and extract info")
    script_1 = """
goto("https://example.com")
title = get_title()
url = get_url()
print(f"Page title: {title}")
print(f"Current URL: {url}")
screenshot("examples/output/script_example.png")
print("Screenshot saved!")
"""
    result = engine.execute(script_1)
    print(f"    Success: {result.success}")
    if result.output:
        print(f"    Output:\n    {result.output.strip()}")
    if result.error:
        print(f"    Error: {result.error}")
    if result.screenshots:
        print(f"    Screenshots: {result.screenshots}")

    # --- Script 2: Demonstrate error handling ---
    print("\n[2] Running script: error handling demo")
    script_2 = """
goto("https://httpbin.org/html")
print(f"Title: {get_title()}")

# This selector doesn't exist - will return failure dict
result = click("#nonexistent-button")
print(f"Click result: {result}")

# Show that the script continues after a failed click
print("Script continued after failed click!")
"""
    result = engine.execute(script_2)
    print(f"    Success: {result.success}")
    if result.output:
        print(f"    Output:\n    {result.output.strip()}")

    # --- Script 3: Show sandbox restrictions ---
    print("\n[3] Running script: sandbox restrictions")
    script_3 = """
# This will fail - imports are blocked in the sandbox
try:
    import os
    print("Import succeeded (unexpected!)")
except NameError as e:
    print(f"Import blocked as expected: {e}")

# This will fail - file operations are blocked
try:
    open("/tmp/test.txt", "w")
except NameError as e:
    print(f"File access blocked as expected: {e}")

# Safe builtins still work
numbers = [3, 1, 4, 1, 5, 9]
print(f"Sorted: {sorted(numbers)}")
print(f"Sum: {sum(numbers)}")
print(f"Length: {len(numbers)}")
"""
    result = engine.execute(script_3)
    print(f"    Success: {result.success}")
    if result.output:
        print(f"    Output:\n    {result.output.strip()}")

    # Cleanup
    print("\n[4] Closing browser...")
    bm.close()
    print("    Done!")

    print("\n=== Example complete ===")


if __name__ == "__main__":
    main()
