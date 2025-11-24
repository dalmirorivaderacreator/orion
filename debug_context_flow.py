import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

# Local imports
# pylint: disable=wrong-import-position
import database
from registry import build_system_prompt
from context import ContextManager


def debug_flow():
    print("=== DEBUGGING CONTEXT FLOW ===")

    # 1. Init DB
    database.init_db()

    # 2. Init ContextManager
    cm = ContextManager()
    print(f"Initial Context: {cm.context}")

    # 3. Simulate Update
    print("\nUpdating context with last_folder='debug_folder'...")
    cm.update("last_folder", "debug_folder")

    # 4. Check Context String
    ctx_str = cm.get_context_string()
    print(f"\nContext String from Manager:\n---\n{ctx_str}\n---")

    if "debug_folder" not in ctx_str:
        print("FAIL: 'debug_folder' not found in context string!")
    else:
        print("PASS: Context string contains updated value.")

    # 5. Check System Prompt
    sys_prompt = build_system_prompt(ctx_str)
    print(f"\nSystem Prompt (Snippet):\n---\n{sys_prompt[:500]}...\n---")

    if "**CONTEXTO ACTUAL (VARIABLES):**" in sys_prompt and "debug_folder" in sys_prompt:
        print("PASS: System prompt contains context section and value.")
    else:
        print("FAIL: System prompt missing context or value!")


if __name__ == "__main__":
    debug_flow()
