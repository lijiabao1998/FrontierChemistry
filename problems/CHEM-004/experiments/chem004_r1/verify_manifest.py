#!/usr/bin/env python3
"""Check a frozen manifest against working files or an exact Git commit.

Use --git-revision HEAD after committing to detect checkout-only EOL matches.
This verifies artifact identity, not a scientific conclusion or a new rerun.
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent


def verify(read_bytes):
    errors = []
    seen = set()
    try:
        lines = read_bytes("results/r1/hashes.txt").decode("utf-8").splitlines()
        for line in lines:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.split(maxsplit=1)
            if len(fields) != 2 or not re.fullmatch(r"[0-9a-f]{64}", fields[0]):
                errors.append("malformed manifest record")
                continue
            digest, name = fields
            name = name.removeprefix("*")
            if (name in seen or not name or "\\" in name or ":" in name
                    or name.startswith("/") or ".." in name.split("/")):
                errors.append(f"invalid or duplicate path: {name}")
                continue
            seen.add(name)
            try:
                actual = hashlib.sha256(read_bytes(name)).hexdigest()
                if actual != digest:
                    errors.append(f"MISMATCH {name}")
            except (OSError, subprocess.CalledProcessError) as exc:
                errors.append(f"MISSING {name}: {exc}")
        if not seen:
            errors.append("empty manifest")
    except (OSError, UnicodeError, subprocess.CalledProcessError) as exc:
        errors.append(f"unreadable manifest: {exc}")
    return len(seen), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--git-revision")
    args = parser.parse_args()
    try:
        if args.git_revision:
            repo = ROOT.parents[1]
            commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--verify",
                         "--end-of-options", args.git_revision + "^{commit}"], encoding="ascii").strip()
            def read_bytes(name):
                return subprocess.check_output(["git", "-C", str(repo), "show",
                                                f"{commit}:problems/CHEM-004/{name}"], stderr=subprocess.PIPE)
        else:
            def read_bytes(name):
                path = ROOT / name
                if not path.resolve().is_relative_to(ROOT.resolve()):
                    raise ValueError("path escapes problem root")
                return path.read_bytes()
        count, errors = verify(read_bytes)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        count, errors = 0, [str(exc)]
    for error in errors:
        print(error)
    print(f"{'FAIL' if errors else 'PASS'}: {count} manifest entries ({'commit bytes' if args.git_revision else 'working bytes'})")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
