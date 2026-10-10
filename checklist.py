#!/usr/bin/env python3
"""Print the pitfall catalog as a checklist, optionally filtered by domain.

    python checklist.py                       # everything
    python checklist.py --domain time-domain  # one domain
    python checklist.py --domains             # list domains
    python checklist.py --json                # machine-readable
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:  # keep the script dependency-free
    yaml = None

HERE = Path(__file__).resolve().parent


def load():
    text = (HERE / "pitfalls.yaml").read_text()
    if yaml is not None:
        return yaml.safe_load(text)["pitfalls"]
    # Minimal fallback parser for this file's flat "  - key: value" layout.
    items, cur = [], None
    for line in text.splitlines():
        if line.startswith("  - id:"):
            cur = {"id": line.split(":", 1)[1].strip()}
            items.append(cur)
        elif cur is not None and line.startswith("    ") and ":" in line:
            k, v = line.strip().split(":", 1)
            cur[k] = v.strip()
    return items


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--domain")
    p.add_argument("--domains", action="store_true", help="list the domains and exit")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    items = load()
    if a.domains:
        for d in sorted({i["domain"] for i in items}):
            print(d)
        return 0
    if a.domain:
        items = [i for i in items if i["domain"] == a.domain]
        if not items:
            print(f"no pitfalls in domain {a.domain!r}", file=sys.stderr)
            return 2
    if a.json:
        json.dump(items, sys.stdout, indent=1)
        print()
        return 0
    for i in items:
        print(f"[ ] {i['id']}  ({i['domain']})")
        print(f"    signature: {i['signature']}")
        print(f"    check:     {i['check']}")
        if i.get("implemented_in"):
            print(f"    code:      {i['implemented_in']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
