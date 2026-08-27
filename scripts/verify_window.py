# -*- coding: utf-8 -*-
"""Assert dest published data stays inside the rolling window and hist refs resolve."""

from __future__ import annotations

import argparse
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from prepare_sync import (
    DEFAULT_DAYS,
    DEFAULT_DEST,
    PUBLISHED_DIR,
    collect_refs_from_json_files,
    json_filename_date,
    parse_as_of,
    safe_relpath,
    window_bounds,
)


def list_dest_json(published: str):
    if not os.path.isdir(published):
        return []
    out = []
    for name in os.listdir(published):
        if json_filename_date(name):
            out.append(os.path.join(published, name))
    return sorted(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Verify dest market-data window and hist refs.")
    parser.add_argument("--dest", default=DEFAULT_DEST)
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--as-of", dest="as_of", default=None)
    args = parser.parse_args(argv)

    try:
        as_of = parse_as_of(args.as_of)
    except ValueError:
        print(f"ERROR invalid --as-of: {args.as_of}", file=sys.stderr)
        return 2

    start, end = window_bounds(as_of, args.days)
    published = os.path.join(args.dest, PUBLISHED_DIR)
    errors = []
    warnings = []

    if not os.path.isdir(published):
        errors.append(f"published dir missing: {published}")
        print("\n".join(errors))
        return 1

    json_paths = list_dest_json(published)
    if not json_paths:
        errors.append(f"no MCP_MARKET_DATA_*.json under {published}")

    for path in json_paths:
        d = json_filename_date(path)
        name = os.path.basename(path)
        if d is None or d < start:
            errors.append(f"JSON outside window: {name} (window {start.isoformat()} .. {end.isoformat()})")

    refs, hist_refs, _date_cols = collect_refs_from_json_files(json_paths)
    for rel in sorted(hist_refs):
        safe = safe_relpath(rel)
        if not safe:
            errors.append(f"unsafe hist_file ref: {rel}")
            continue
        full = os.path.join(published, *safe.split("/"))
        if not os.path.isfile(full):
            errors.append(f"dangling hist_file: {safe}")

    for rel in sorted(refs - hist_refs):
        safe = safe_relpath(rel)
        if not safe:
            continue
        full = os.path.join(published, *safe.split("/"))
        if not os.path.isfile(full):
            warnings.append(f"missing non-hist ref (ok if only current_file): {safe}")

    print(f"window {start.isoformat()} .. {end.isoformat()}")
    print(f"json_files {len(json_paths)}")
    print(f"hist_refs {len(hist_refs)}")
    for w in warnings:
        print(f"WARN {w}")
    if errors:
        for e in errors:
            print(f"ERROR {e}")
        return 1
    print("verify_window: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
