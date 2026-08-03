#!/usr/bin/env python3
"""Easy, interactive runner for the LYR Explorer knowledge export.

    python explorer/run.py

Downloads the demo source if needed, asks for your Anthropic API key (hidden
input, optionally saved for next time), asks how many chapters, then runs the
real LLM extraction over Pride and Prejudice and writes the knowledge.json the
explorer renders. No flags to remember.
"""
from __future__ import annotations

import getpass
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DATA = HERE / "data"
ENV = HERE / ".env"
SRC = DATA / "pride-and-prejudice.raw.txt"
EXPORT = HERE / "pipeline" / "export_knowledge.py"
GUTENBERG = "https://www.gutenberg.org/files/1342/1342-0.txt"
MODEL = "claude-haiku-4-5"  # cheap + fast; change to claude-opus-4-8 for max quality


def say(m: str = "") -> None:
    print(m)


def ensure_source() -> None:
    if SRC.exists():
        return
    say("↓  Downloading Pride and Prejudice (public domain)…")
    DATA.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(GUTENBERG, SRC)
    say(f"   saved → explorer/data/{SRC.name}")


def check_anthropic() -> None:
    try:
        import anthropic  # noqa: F401
    except ImportError:
        say("✗  The 'anthropic' package isn't installed. Install it with:")
        say("       pip install anthropic")
        sys.exit(1)


def env_file_key() -> str | None:
    if not ENV.exists():
        return None
    for line in ENV.read_text().splitlines():
        if line.strip().startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def get_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY") or env_file_key()
    if key:
        say("✓  Using the Anthropic API key already configured.")
        return key
    say("This run calls the Anthropic API, so it needs your key.")
    say("Get one at https://console.anthropic.com/  (it starts with 'sk-ant-').")
    key = getpass.getpass("   Paste your Anthropic API key (hidden): ").strip()
    if not key:
        say("No key entered — aborting.")
        sys.exit(1)
    if input("   Save it to explorer/.env for next time? [y/N]: ").strip().lower() == "y":
        ENV.write_text(f"ANTHROPIC_API_KEY={key}\n")
        try:
            os.chmod(ENV, 0o600)
        except OSError:
            pass
        say("   saved (gitignored) → explorer/.env")
    return key


def ask_chapters() -> int:
    raw = input("How many chapters to process? [10]  (61 = whole book): ").strip()
    if not raw:
        return 10
    try:
        return max(1, int(raw))
    except ValueError:
        say("   (not a number — using 10)")
        return 10


def main() -> None:
    say("── LYR Explorer — build a living knowledge space ─────────────")
    say("Demo source: Pride and Prejudice.  Model: Claude Haiku (low cost).")
    say("")
    ensure_source()
    check_anthropic()
    key = get_key()
    n = ask_chapters()
    out = DATA / ("knowledge.full.json" if n >= 61 else f"knowledge.ch{n:02d}.json")

    say(f"\n▶  Extracting knowledge from {n} chapter(s) — about {n}+ API calls. One moment…\n")
    env = {**os.environ, "ANTHROPIC_API_KEY": key}  # passed via env, never on the command line
    cmd = [
        sys.executable, str(EXPORT),
        "--extractor", "llm", "--provider", "anthropic", "--consolidator", "llm",
        "--model", MODEL, "--limit", str(n), "--out", str(out),
    ]
    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        say(f"\n✓  Done. Knowledge written to explorer/data/{out.name}")
        say("   That file is what the explorer renders. Re-run any time to redo or extend it.")
    else:
        say("\n✗  The run failed above. Most common causes:")
        say("   • the API key is wrong or has no billing/credit")
        say("   • no network access")
        say("   Fix and run  python explorer/run.py  again.")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
