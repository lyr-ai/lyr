#!/usr/bin/env python3
"""Easy, interactive runner for the LYR Explorer knowledge export.

    python explorer/run.py

Pick a provider (OpenAI/ChatGPT or Anthropic/Claude), paste your API key (hidden,
optionally saved), choose how many chapters — then it runs the real LLM
extraction over Pride and Prejudice and writes the knowledge.json the explorer
renders. No flags to remember.
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

PROVIDERS = {
    "openai": {
        "label": "OpenAI (ChatGPT)",
        "env": "OPENAI_API_KEY",
        "model": "gpt-4o-mini",           # cheap + fast; use gpt-4o for max quality
        "import": "openai",
        "keys_url": "https://platform.openai.com/api-keys",
        "billing_url": "https://platform.openai.com/settings/organization/billing",
        "note": "The API needs its own credit — a ChatGPT Plus/Pro subscription does NOT include it.",
    },
    "anthropic": {
        "label": "Anthropic (Claude)",
        "env": "ANTHROPIC_API_KEY",
        "model": "claude-haiku-4-5",
        "import": "anthropic",
        "keys_url": "https://console.anthropic.com/settings/keys",
        "billing_url": "https://console.anthropic.com/settings/billing",
        "note": "Needs API credit under Plans & Billing.",
    },
}


def say(m: str = "") -> None:
    print(m)


def ensure_source() -> None:
    if SRC.exists():
        return
    say("↓  Downloading Pride and Prejudice (public domain)…")
    DATA.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(GUTENBERG, SRC)
    say(f"   saved → explorer/data/{SRC.name}")


def ask_provider() -> str:
    say("Which API do you want to use?")
    say("  [1] OpenAI (ChatGPT)")
    say("  [2] Anthropic (Claude)")
    choice = input("Choose [1]: ").strip() or "1"
    return "anthropic" if choice == "2" else "openai"


def check_pkg(cfg: dict) -> None:
    try:
        __import__(cfg["import"])
    except ImportError:
        say(f"✗  The '{cfg['import']}' package isn't installed. Install it with:")
        say(f"       pip install {cfg['import']}")
        sys.exit(1)


def _env_file_pairs() -> dict[str, str]:
    pairs: dict[str, str] = {}
    if ENV.exists():
        for line in ENV.read_text().splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                pairs[k.strip()] = v.strip().strip('"').strip("'")
    return pairs


def get_key(cfg: dict) -> str:
    var = cfg["env"]
    key = os.environ.get(var) or _env_file_pairs().get(var)
    if key:
        say(f"✓  Using the {cfg['label']} key already configured.")
        return key
    say(f"\nThis run calls the {cfg['label']} API, so it needs your key.")
    say(f"   Get one at {cfg['keys_url']}")
    say(f"   Note: {cfg['note']}")
    key = getpass.getpass("   Paste your API key (hidden): ").strip()
    if not key:
        say("No key entered — aborting.")
        sys.exit(1)
    if input("   Save it to explorer/.env for next time? [y/N]: ").strip().lower() == "y":
        pairs = _env_file_pairs()
        pairs[var] = key
        ENV.write_text("".join(f"{k}={v}\n" for k, v in pairs.items()))
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
    say("Demo source: Pride and Prejudice.")
    say("")
    ensure_source()
    provider = ask_provider()
    cfg = PROVIDERS[provider]
    say(f"→  {cfg['label']}, model {cfg['model']} (edit PROVIDERS in run.py to change).")
    check_pkg(cfg)
    key = get_key(cfg)
    n = ask_chapters()
    out = DATA / ("knowledge.full.json" if n >= 61 else f"knowledge.ch{n:02d}.json")

    say(f"\n▶  Extracting knowledge from {n} chapter(s) — about {n}+ API calls. One moment…\n")
    env = {**os.environ, cfg["env"]: key}  # key passed via env, never on the command line
    cmd = [
        sys.executable, str(EXPORT),
        "--extractor", "llm", "--provider", provider, "--consolidator", "llm",
        "--model", cfg["model"], "--limit", str(n), "--out", str(out),
    ]
    result = subprocess.run(cmd, env=env)

    if result.returncode == 0:
        say(f"\n✓  Extracted → explorer/data/{out.name}")
        # Canonicalization Layer — Explorer-side presentation; LYR core untouched.
        adapter = HERE / "adapters" / "pride-and-prejudice.aliases.json"
        canon = DATA / "knowledge.canonical.json"
        say("\n▶  Canonicalizing aliases (Explorer presentation layer)…\n")
        subprocess.run([
            sys.executable, str(HERE / "pipeline" / "canonicalize.py"),
            "--in", str(out), "--adapter", str(adapter), "--out", str(canon),
        ])
        say(f"\n✓  Done. The explorer reads explorer/data/{canon.name}")
        say("   Re-run any time to redo or extend it.")
    else:
        say("\n✗  The run failed above. Most common causes:")
        say("   • the API key is wrong, or the account has no credit/billing set up")
        say(f"     → add credit at {cfg['billing_url']}")
        say(f"     ({cfg['note']})")
        say("   • no network access")
        say("   Fix and run  python explorer/run.py  again.")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
