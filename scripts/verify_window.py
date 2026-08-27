# -*- coding: utf-8 -*-
"""Assert dest published data stays inside the rolling window and file refs resolve."""

from __future__ import annotations

import argparse
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from prepare_sync import (
    CURRENT_FILE_KEYS,
    DEFAULT_DAYS,
    DEFAULT_DEST,
    DEFAULT_SOURCE,
    HIST_REF_KEYS,
    PUBLISHED_DIR,
    collect_refs_from_json_files,
    json_filename_date,
    list_well_known_sidecars,
    parse_as_of,
    reject_parent_source,
    safe_relpath,
    walk_file_refs,
    load_json,
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


def collect_refs_by_key(paths):
    """Return (all_refs, hist_refs, current_refs, other_refs)."""
    all_refs, hist_refs, _date_cols = collect_refs_from_json_files(paths)
    current_refs = set()
    other_refs = set()
    for path in paths:
        try:
            data = load_json(path)
        except (OSError, ValueError):
            continue
        for key, rel in walk_file_refs(data):
            if key in HIST_REF_KEYS:
                continue
            if key in CURRENT_FILE_KEYS:
                current_refs.add(rel)
            else:
                other_refs.add(rel)
    return all_refs, hist_refs, current_refs, other_refs


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify dest market-data window, hist refs, and auxiliary files."
    )
    parser.add_argument("--dest", default=DEFAULT_DEST)
    parser.add_argument("--source", default=DEFAULT_SOURCE)
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

    parent_err = reject_parent_source(args.source)
    if parent_err:
        print(f"ERROR {parent_err}", file=sys.stderr)
        return 2

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

    _all_refs, hist_refs, current_refs, other_refs = collect_refs_by_key(json_paths)

    for rel in sorted(hist_refs):
        safe = safe_relpath(rel)
        if not safe:
            errors.append(f"unsafe hist_file ref: {rel}")
            continue
        full = os.path.join(published, *safe.split("/"))
        if not os.path.isfile(full):
            errors.append(f"dangling hist_file: {safe}")

    for rel in sorted(other_refs):
        safe = safe_relpath(rel)
        if not safe:
            errors.append(f"unsafe aux ref: {rel}")
            continue
        full = os.path.join(published, *safe.split("/"))
        if not os.path.isfile(full):
            errors.append(f"dangling aux file: {safe}")

    for rel in sorted(current_refs - hist_refs - other_refs):
        safe = safe_relpath(rel)
        if not safe:
            continue
        full = os.path.join(published, *safe.split("/"))
        if not os.path.isfile(full):
            warnings.append(f"missing current_file (ok if loader falls back to hist_file): {safe}")

    sidecar_present, sidecar_missing_source = list_well_known_sidecars(args.source)
    if os.path.isdir(args.source):
        for rel in sorted(sidecar_present):
            safe = safe_relpath(rel)
            if not safe:
                continue
            full = os.path.join(published, *safe.split("/"))
            if not os.path.isfile(full):
                errors.append(f"missing auxiliary sidecar (present on source): {safe}")
        for name in sidecar_missing_source:
            warnings.append(f"well-known sidecar missing on source: {name}")
    else:
        warnings.append(f"source not available for sidecar check: {args.source}")

    print(f"window {start.isoformat()} .. {end.isoformat()}")
    print(f"json_files {len(json_paths)}")
    print(f"hist_refs {len(hist_refs)}")
    print(f"aux_refs {len(other_refs)}")
    print(f"source_sidecars {len(sidecar_present)}")
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
