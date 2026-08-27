# -*- coding: utf-8 -*-
"""Prepare a rolling calendar-day window of MCP market data for the public repo.

Copies MCP_MARKET_DATA_YYYYMMDD.json, referenced HIST/current CSVs, and
auxiliary sidecars (BOND_INFO, dividends, classification, …) from a source
snapshots directory (default Z:\\market_data\\snapshots) into
<repo>/market_data, preserving relative paths so MCP Python
(MRawMarketManager / MLiveMarketDataStore / MMarketDataJsonReader) still
resolves hist_file and sidecars against that folder.

Source MUST be the snapshots directory. Never walk the parent
Z:\\market_data tree (live / qh / extra dumps).

This script does not run git commit or git push. weekly_sync.ps1 owns git.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


DEFAULT_SOURCE = r"Z:\market_data\snapshots"
DEFAULT_DEST = r"D:\work\mcp\github\mcp_marketdata"
DEFAULT_DAYS = 90
JSON_NAME_RE = re.compile(r"^MCP_MARKET_DATA_(\d{8})\.json$", re.IGNORECASE)
# Published GitHub market_data root = contents of Z:\market_data\snapshots only.
PUBLISHED_DIR = "market_data"
LEGACY_PUBLISHED_DIR = "snapshots"
REPORTS_DIR = "reports"
PARENT_SOURCE_SIBLINGS = frozenset(
    {"live", "qh", "dumps", "dump", "extra", "hist", "current"}
)
FILE_REF_KEYS = (
    "hist_file",
    "current_file",
    "file",
    "file_path",
    "bond_info",
    "dividend_file",
    "dividends_file",
    "dividends",
    "corporate_actions",
    "corporate_actions_file",
    "classification_file",
    "instrument_classification",
)
HIST_REF_KEYS = ("hist_file",)
CURRENT_FILE_KEYS = ("current_file",)
# Do not delete hand-written dest files that are not copied from source.
DEST_KEEP_RELPATHS = frozenset({"README.md"})
DATE_HEADER_CANDIDATES = (
    "valuation_date",
    "asof_date",
    "ex_date",
    "exdate",
    "date",
    "Date",
    "DATE",
    "trade_date",
    "TradeDate",
    "TRADEDATE",
)
# Loader-needed sidecars that JSON often does not list (BatchManager / ch03).
WELL_KNOWN_EXACT = frozenset(
    {
        "BOND_INFO.csv",
        "BOND_INFO.json",
        "BOND_INFO_SPEC.csv",
        "dividends.csv",
        "corporate_actions.csv",
        "INSTRUMENT_CLASSIFICATION.csv",
        "INSTRUMENT_VOLATILITY.csv",
        "EQUITY_INFO.csv",
        "FUND_INFO.csv",
        "FUTURE_INFO.csv",
        "future_multipliers.csv",
        "instrument_fees.csv",
        "fund_fees.csv",
        "bond_tax_rates.csv",
        "CALLABLEBOND_IR_VOLS.csv",
        "IR_INDEX_FIXINGS_HIST.csv",
        "code_mapping.csv",
        "benchmark_mapping.csv",
        "BENCHMARK_EQUITY.json",
        "bond_future_deliverables.csv",
        "brinson_stock_holdings.csv",
        "brinson_sector_benchmark.csv",
        "funding_rates.csv",
    }
)
# Event / static tables: copy whole. Do not trim by maturity_date / ex_date.
REFERENCE_NO_TRIM = frozenset(
    {
        "BOND_INFO.CSV",
        "BOND_INFO.JSON",
        "BOND_INFO_SPEC.CSV",
        "DIVIDENDS.CSV",
        "CORPORATE_ACTIONS.CSV",
        "INSTRUMENT_CLASSIFICATION.CSV",
        "EQUITY_INFO.CSV",
        "FUND_INFO.CSV",
        "FUTURE_INFO.CSV",
        "FUTURE_MULTIPLIERS.CSV",
        "INSTRUMENT_FEES.CSV",
        "FUND_FEES.CSV",
        "BOND_TAX_RATES.CSV",
        "CALLABLEBOND_IR_VOLS.CSV",
        "CODE_MAPPING.CSV",
        "BENCHMARK_MAPPING.CSV",
        "BENCHMARK_EQUITY.JSON",
        "BOND_FUTURE_DELIVERABLES.CSV",
        "BRINSON_STOCK_HOLDINGS.CSV",
        "BRINSON_SECTOR_BENCHMARK.CSV",
        "FUNDING_RATES.CSV",
    }
)
# Dated aux that is not *_HIST* but should follow the 90-day window.
DATED_AUX_TRIM = frozenset({"INSTRUMENT_VOLATILITY.CSV"})
SKIP_SIDECAR_RE = re.compile(r"(\.bak|\(2\)|~\$)", re.I)
GITHUB_SOFT_LIMIT_BYTES = 90 * 1024 * 1024
GITHUB_HARD_LIMIT_BYTES = 100 * 1024 * 1024
# Publish cap: GitHub.com rejects blobs >= 100MB and this repo must not use LFS.
GITHUB_PUBLISH_CAP_BYTES = 99 * 1024 * 1024


def source_looks_like_parent_market_data(source: str) -> bool:
    """True if *source* is the parent tree (e.g. Z:\\market_data), not snapshots.

    The parent typically contains a snapshots/ child plus live/qh/extra dumps.
    Never walk that tree: published files come only from snapshots/.
    """
    try:
        names = os.listdir(source)
    except OSError:
        return False
    lower = {n.lower() for n in names}
    snap_child = os.path.join(source, "snapshots")
    has_snap_child = "snapshots" in lower and os.path.isdir(snap_child)
    if not has_snap_child:
        return False
    if lower.intersection(PARENT_SOURCE_SIBLINGS):
        return True
    return os.path.basename(os.path.normpath(source)).lower() == "market_data"


def reject_parent_source(source: str) -> Optional[str]:
    if source_looks_like_parent_market_data(source):
        return (
            "source must be the snapshots directory "
            f"(expected ...\\snapshots, got {source}). "
            "Do not pass the parent Z:\\market_data tree (live/qh/extra dumps)."
        )
    return None


def remove_legacy_snapshots_tree(dest: str, dry_run: bool) -> List[str]:
    """Drop leftover dest/snapshots so GitHub does not publish two data trees."""
    notes: List[str] = []
    legacy = os.path.join(dest, LEGACY_PUBLISHED_DIR)
    published = os.path.join(dest, PUBLISHED_DIR)
    if not os.path.isdir(legacy):
        return notes
    if os.path.normpath(os.path.abspath(legacy)) == os.path.normpath(os.path.abspath(published)):
        return notes
    notes.append(
        f"legacy dest/{LEGACY_PUBLISHED_DIR}/ present; "
        f"{'would remove' if dry_run else 'removing'} so only {PUBLISHED_DIR}/ is published"
    )
    if not dry_run:
        shutil.rmtree(legacy)
    return notes


def parse_yyyymmdd(text: str) -> Optional[date]:
    s = (text or "").strip()
    if len(s) != 8 or not s.isdigit():
        return None
    try:
        return date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
    except ValueError:
        return None


def date_cell_to_yyyymmdd(ds: str) -> str:
    """Match raw_market_data_loader._hist_vol_date_cell_to_yyyymmdd, plus year-last slash dates.

    Loader handles YYYYMMDD, YYYY-MM-DD, and YYYY/M/D. HIST CSVs on Z: actually use
    M/D/YYYY (e.g. 5/30/2024, 1/10/2025, 07/01/2026), which the loader function
    does not parse. Year-last slash forms are accepted so the 90-day trim works.
    Ambiguous a/b/YYYY (both a,b <= 12) is treated as M/D/YYYY, consistent with
    Excel-exported rows such as 5/30/2024.
    """
    s = (ds or "").strip()
    if not s:
        return ""
    if len(s) == 8 and s.isdigit():
        return s
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s[:4] + s[5:7] + s[8:10]
    if "/" in s:
        parts = [p.strip() for p in s.split("/")]
        if len(parts) == 3:
            try:
                a, b, c = int(parts[0]), int(parts[1]), int(parts[2])
            except ValueError:
                return ""
            if len(parts[0]) == 4:
                y, mo, d = a, b, c
            elif len(parts[2]) == 4:
                y = c
                if a > 12 and b <= 12:
                    mo, d = b, a
                else:
                    mo, d = a, b
            else:
                return ""
            if 1 <= mo <= 12 and 1 <= d <= 31 and 1900 <= y <= 2999:
                return f"{y:04d}{mo:02d}{d:02d}"
            return ""
    return ""


def window_bounds(as_of: date, days: int) -> Tuple[date, date]:
    if days < 1:
        raise ValueError("days must be >= 1")
    start = as_of - timedelta(days=days)
    return start, as_of


def json_filename_date(name: str) -> Optional[date]:
    m = JSON_NAME_RE.match(os.path.basename(name))
    if not m:
        return None
    return parse_yyyymmdd(m.group(1))


def list_source_json(source: str) -> List[str]:
    if not os.path.isdir(source):
        return []
    out = []
    for name in os.listdir(source):
        if json_filename_date(name):
            out.append(os.path.join(source, name))
    out.sort()
    return out


def looks_like_relpath(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return False
    low = v.lower()
    return low.endswith(".csv") or low.endswith(".json")


def is_file_ref_key(key: str) -> bool:
    k = str(key)
    if k in FILE_REF_KEYS:
        return True
    kl = k.lower()
    if kl.endswith("_file") or kl.endswith("_path"):
        return True
    if "dividend" in kl and "method" not in kl:
        return True
    return False


def walk_file_refs(obj: Any) -> Iterable[Tuple[str, str]]:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if is_file_ref_key(key) and isinstance(value, str) and looks_like_relpath(value):
                rel = value.strip().replace("\\", "/")
                if rel:
                    yield key, rel
            yield from walk_file_refs(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_file_refs(item)


def sidecar_skip(name: str) -> bool:
    return bool(SKIP_SIDECAR_RE.search(name or ""))


def is_well_known_sidecar_name(name: str) -> bool:
    if not name or sidecar_skip(name):
        return False
    if name in WELL_KNOWN_EXACT:
        return True
    upper = name.upper()
    if upper.startswith("BOND_INFO") and upper.endswith((".CSV", ".JSON")):
        return True
    if "DIVIDEND" in upper and upper.endswith(".CSV"):
        return True
    if upper.startswith("INSTRUMENT_CLASSIFICATION") and upper.endswith(".CSV"):
        return True
    if upper.startswith("FUND_HOLDINGS_BREAKDOWN_") and upper.endswith(".JSON"):
        return True
    return False


def list_well_known_sidecars(source: str) -> Tuple[Set[str], List[str]]:
    """Return (present relative names, WELL_KNOWN_EXACT names missing on source)."""
    present: Set[str] = set()
    if os.path.isdir(source):
        for name in os.listdir(source):
            if is_well_known_sidecar_name(name) and os.path.isfile(os.path.join(source, name)):
                present.add(name)
    missing = sorted(n for n in WELL_KNOWN_EXACT if n not in present)
    return present, missing


def should_trim_csv(rel: str, is_hist_ref: bool) -> bool:
    name = os.path.basename(rel)
    upper = name.upper()
    if is_hist_ref or "_HIST" in upper:
        return True
    if upper in DATED_AUX_TRIM:
        return True
    if upper.startswith("BOND_INFO"):
        return False
    if "DIVIDEND" in upper:
        return False
    if upper.startswith("INSTRUMENT_CLASSIFICATION"):
        return False
    if upper.startswith("FUND_HOLDINGS_BREAKDOWN_"):
        return False
    if upper in REFERENCE_NO_TRIM:
        return False
    return False


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def collect_refs_from_json_files(paths: Iterable[str]) -> Tuple[Set[str], Set[str], Dict[str, str]]:
    """Return (all_refs, hist_refs, hist_date_columns)."""
    all_refs: Set[str] = set()
    hist_refs: Set[str] = set()
    date_cols: Dict[str, str] = {}
    for path in paths:
        try:
            data = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"WARN cannot parse {path}: {exc}", file=sys.stderr)
            continue
        for key, rel in walk_file_refs(data):
            all_refs.add(rel)
            if key in HIST_REF_KEYS:
                hist_refs.add(rel)
        pidx = data.get("price_data_index") if isinstance(data, dict) else None
        if isinstance(pidx, dict):
            for entry in pidx.values():
                if not isinstance(entry, dict):
                    continue
                col = str(entry.get("date_column") or "").strip()
                hist = str(entry.get("hist_file") or "").strip().replace("\\", "/")
                if hist and col:
                    date_cols[hist] = col
    return all_refs, hist_refs, date_cols


def safe_relpath(rel: str) -> Optional[str]:
    """Reject absolute paths and parent-directory escapes."""
    if not rel or rel.startswith("/") or rel.startswith("\\"):
        return None
    if re.match(r"^[A-Za-z]:", rel):
        return None
    parts = [p for p in rel.replace("\\", "/").split("/") if p and p != "."]
    if any(p == ".." for p in parts):
        return None
    return "/".join(parts)


def detect_date_column(headers: List[str], preferred: Optional[str] = None) -> int:
    cleaned = [str(h).strip() for h in headers]
    if preferred:
        try:
            return cleaned.index(preferred)
        except ValueError:
            pass
    for name in DATE_HEADER_CANDIDATES:
        try:
            return cleaned.index(name)
        except ValueError:
            continue
    return -1


def dir_size_bytes(root: str) -> int:
    total = 0
    if not os.path.isdir(root):
        return 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            fp = os.path.join(dirpath, name)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def format_mb(n: int) -> str:
    return f"{n / (1024 * 1024):.2f} MB"


def files_identical(src: str, dest: str) -> bool:
    try:
        s = os.stat(src)
        d = os.stat(dest)
    except OSError:
        return False
    return s.st_size == d.st_size and int(s.st_mtime) == int(d.st_mtime)


def copy_file(src: str, dest: str) -> str:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def trim_or_copy_csv(
    src: str,
    dest: str,
    cutoff: date,
    date_column: Optional[str],
    trim: bool,
    dry_run: bool,
) -> Dict[str, Any]:
    """Copy a CSV; if trim, keep header + rows with parsed date >= cutoff."""
    stats: Dict[str, Any] = {
        "src": src,
        "dest": dest,
        "trim": trim,
        "rows_before": 0,
        "rows_after": 0,
        "rows_unparsed": 0,
        "bytes_dest": 0,
        "action": "copy",
        "date_column": date_column or "",
        "missing": False,
    }
    if not os.path.isfile(src):
        stats["missing"] = True
        stats["action"] = "missing"
        return stats

    if not trim:
        stats["action"] = "copy"
        if not dry_run:
            copy_file(src, dest)
            stats["bytes_dest"] = os.path.getsize(dest)
        else:
            stats["bytes_dest"] = os.path.getsize(src)
        return stats

    stats["action"] = "trim"
    tmp = dest + ".tmp"
    if not dry_run:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

    src_size = os.path.getsize(src)
    out_fh = None
    try:
        with open(src, "r", encoding="utf-8-sig", newline="") as inf:
            header_line = inf.readline()
            if not header_line:
                if not dry_run:
                    open(dest, "w", encoding="utf-8", newline="").close()
                return stats
            headers = next(csv.reader([header_line]))
            idx = detect_date_column(headers, date_column)
            stats["date_column"] = headers[idx] if idx >= 0 else ""
            if idx < 0:
                stats["action"] = "copy_no_date_column"
                if not dry_run:
                    copy_file(src, dest)
                    stats["bytes_dest"] = os.path.getsize(dest)
                else:
                    stats["bytes_dest"] = src_size
                return stats
            if not dry_run:
                out_fh = open(tmp, "w", encoding="utf-8", newline="")
                out_fh.write(header_line if header_line.endswith("\n") else header_line + "\n")
            for line in inf:
                stats["rows_before"] += 1
                row = line.rstrip("\r\n").split(",") if '"' not in line else next(csv.reader([line]), [])
                if idx >= len(row):
                    stats["rows_unparsed"] += 1
                    continue
                ymd = date_cell_to_yyyymmdd(row[idx])
                parsed = parse_yyyymmdd(ymd) if ymd else None
                if parsed is None:
                    stats["rows_unparsed"] += 1
                    continue
                if parsed < cutoff:
                    continue
                stats["rows_after"] += 1
                if out_fh is not None:
                    out_fh.write(line if line.endswith("\n") else line + "\n")
    finally:
        if out_fh is not None:
            out_fh.close()

    if not dry_run:
        os.replace(tmp, dest)
        stats["bytes_dest"] = os.path.getsize(dest)
        cap = cap_csv_to_github_limit(dest, date_column, GITHUB_PUBLISH_CAP_BYTES)
        if cap:
            stats["rows_after"] = cap["rows_after"]
            stats["bytes_dest"] = cap["bytes_dest"]
            stats["github_cap_from"] = cap["min_date"]
            stats["action"] = "trim+github_cap"
    elif stats["rows_before"] > 0:
        stats["bytes_dest"] = int(src_size * stats["rows_after"] / stats["rows_before"])
        if stats["bytes_dest"] >= GITHUB_HARD_LIMIT_BYTES:
            stats["bytes_dest"] = GITHUB_PUBLISH_CAP_BYTES
            stats["action"] = "trim+github_cap"
    else:
        stats["bytes_dest"] = 0
    return stats


def cap_csv_to_github_limit(path: str, date_column: Optional[str], max_bytes: int) -> Optional[Dict[str, Any]]:
    """If dest CSV is still over GitHub's blob limit, keep newest dates until it fits."""
    if not os.path.isfile(path):
        return None
    size = os.path.getsize(path)
    if size <= max_bytes:
        return None
    date_bytes: Dict[str, int] = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as inf:
        header_line = inf.readline()
        if not header_line:
            return None
        headers = next(csv.reader([header_line]))
        idx = detect_date_column(headers, date_column)
        if idx < 0:
            return None
        header_size = len(header_line.encode("utf-8"))
        for line in inf:
            row = line.rstrip("\r\n").split(",") if '"' not in line else next(csv.reader([line]), [])
            if idx >= len(row):
                continue
            ymd = date_cell_to_yyyymmdd(row[idx])
            if not ymd:
                continue
            date_bytes[ymd] = date_bytes.get(ymd, 0) + len(line.encode("utf-8"))
    kept: List[str] = []
    acc = header_size
    for ymd in sorted(date_bytes.keys(), reverse=True):
        nxt = acc + date_bytes[ymd]
        if kept and nxt > max_bytes:
            break
        if not kept and nxt > max_bytes:
            break
        acc = nxt
        kept.append(ymd)
    if not kept:
        return None
    min_keep = min(kept)
    min_date = parse_yyyymmdd(min_keep)
    if min_date is None:
        return None
    tmp = path + ".cap.tmp"
    rows_after = 0
    with open(path, "r", encoding="utf-8-sig", newline="") as inf, open(tmp, "w", encoding="utf-8", newline="") as outf:
        header_line = inf.readline()
        outf.write(header_line if header_line.endswith("\n") else header_line + "\n")
        headers = next(csv.reader([header_line]))
        idx = detect_date_column(headers, date_column)
        for line in inf:
            row = line.rstrip("\r\n").split(",") if '"' not in line else next(csv.reader([line]), [])
            if idx >= len(row):
                continue
            parsed = parse_yyyymmdd(date_cell_to_yyyymmdd(row[idx]))
            if parsed is None or parsed < min_date:
                continue
            outf.write(line if line.endswith("\n") else line + "\n")
            rows_after += 1
    os.replace(tmp, path)
    return {
        "min_date": min_date.isoformat(),
        "rows_after": rows_after,
        "bytes_dest": os.path.getsize(path),
    }


def managed_dest_paths(published: str) -> Tuple[Set[str], Set[str]]:
    """Return (json_basenames, other_relpaths) already in dest published dir."""
    json_names: Set[str] = set()
    others: Set[str] = set()
    if not os.path.isdir(published):
        return json_names, others
    for dirpath, _dirnames, filenames in os.walk(published):
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, published).replace("\\", "/")
            if json_filename_date(name) and os.path.dirname(rel) in ("", "."):
                json_names.add(name)
            else:
                others.add(rel)
    return json_names, others


def write_report(path: str, body: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)


def build_report(
    as_of: date,
    start: date,
    days: int,
    source: str,
    dest: str,
    dry_run: bool,
    json_added: List[str],
    json_updated: List[str],
    json_unchanged: List[str],
    json_deleted: List[str],
    source_outside: int,
    hist_stats: List[Dict[str, Any]],
    dangling: List[str],
    dest_size: int,
    warnings: List[str],
    sidecar_missing: Optional[List[str]] = None,
) -> str:
    lines = [
        f"# SYNC_REPORT_{as_of.strftime('%Y%m%d')}",
        "",
        f"- as_of: {as_of.isoformat()}",
        f"- window: {start.isoformat()} .. {as_of.isoformat()} ({days} calendar days)",
        f"- source: `{source}`",
        f"- dest: `{dest}`",
        f"- published_dir: `{PUBLISHED_DIR}` (GitHub market_data root; source is snapshots only)",
        f"- dry_run: {str(dry_run).lower()}",
        f"- dest_published_size: {format_mb(dest_size)}",
        "",
        "## JSON",
        "",
        f"- source_outside_window: {source_outside}",
        f"- added ({len(json_added)}):",
    ]
    lines.extend(f"  - {n}" for n in json_added) if json_added else lines.append("  - (none)")
    lines.append(f"- updated ({len(json_updated)}):")
    lines.extend(f"  - {n}" for n in json_updated) if json_updated else lines.append("  - (none)")
    lines.append(f"- unchanged ({len(json_unchanged)}):")
    lines.extend(f"  - {n}" for n in json_unchanged) if json_unchanged else lines.append("  - (none)")
    lines.append(f"- deleted ({len(json_deleted)}):")
    lines.extend(f"  - {n}" for n in json_deleted) if json_deleted else lines.append("  - (none)")
    lines.extend(["", "## HIST / referenced / auxiliary files", ""])
    lines.append("| file | action | rows_before | rows_after | unparsed | dest_size |")
    lines.append("|---|---|---:|---:|---:|---|")
    for st in hist_stats:
        rel = os.path.basename(st.get("dest") or st.get("src") or "")
        if st.get("src"):
            rel = os.path.relpath(st["dest"], os.path.join(dest, PUBLISHED_DIR)).replace("\\", "/") if st.get("dest") else rel
        lines.append(
            f"| {rel} | {st.get('action')} | {st.get('rows_before', 0)} | "
            f"{st.get('rows_after', 0)} | {st.get('rows_unparsed', 0)} | "
            f"{format_mb(int(st.get('bytes_dest') or 0))} |"
        )
    if not hist_stats:
        lines.append("| (none) | | | | | |")
    lines.extend(["", "## Dangling refs", ""])
    if dangling:
        lines.extend(f"- `{p}`" for p in dangling)
    else:
        lines.append("- (none)")
    lines.extend(["", "## Well-known sidecars missing on source", ""])
    if sidecar_missing:
        lines.extend(f"- `{p}`" for p in sidecar_missing)
    else:
        lines.append("- (none)")
    lines.extend(["", "## Warnings", ""])
    if warnings:
        lines.extend(f"- {w}" for w in warnings)
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def prepare(
    source: str,
    dest: str,
    days: int,
    as_of: date,
    dry_run: bool,
) -> int:
    if not os.path.isdir(source):
        print(f"ERROR source missing: {source}", file=sys.stderr)
        return 2
    parent_err = reject_parent_source(source)
    if parent_err:
        print(f"ERROR {parent_err}", file=sys.stderr)
        return 2

    start, end = window_bounds(as_of, days)
    cutoff_ymd = start.strftime("%Y%m%d")
    published = os.path.join(dest, PUBLISHED_DIR)
    reports = os.path.join(dest, REPORTS_DIR)
    print(f"window {start.isoformat()} .. {end.isoformat()} ({days} calendar days)")
    print(f"source {source}")
    print(f"dest   {dest}")
    print(f"published {published}")
    print(f"dry_run {dry_run}")

    all_json = list_source_json(source)
    keep_json = []
    outside = 0
    for path in all_json:
        d = json_filename_date(path)
        assert d is not None
        if d >= start:
            keep_json.append(path)
        else:
            outside += 1
    keep_names = {os.path.basename(p) for p in keep_json}
    print(f"JSON keep {len(keep_json)} / source {len(all_json)} (outside {outside})")

    refs, hist_refs, date_cols = collect_refs_from_json_files(keep_json)
    sidecar_present, sidecar_missing = list_well_known_sidecars(source)
    refs.update(sidecar_present)
    safe_refs: Set[str] = set()
    dangling: List[str] = []
    for rel in sorted(refs):
        safe = safe_relpath(rel)
        if not safe:
            dangling.append(f"{rel} (unsafe path)")
            continue
        src_path = os.path.join(source, *safe.split("/"))
        if not os.path.isfile(src_path):
            dangling.append(safe)
        safe_refs.add(safe)
    hist_safe = {r for r in (safe_relpath(x) or "" for x in hist_refs) if r}

    existing_json, existing_others = managed_dest_paths(published)
    json_added: List[str] = []
    json_updated: List[str] = []
    json_unchanged: List[str] = []
    json_deleted: List[str] = []

    if not dry_run:
        os.makedirs(published, exist_ok=True)
        os.makedirs(reports, exist_ok=True)

    for src in keep_json:
        name = os.path.basename(src)
        dest_json = os.path.join(published, name)
        existed = name in existing_json
        if existed and files_identical(src, dest_json):
            json_unchanged.append(name)
            continue
        if dry_run:
            (json_updated if existed else json_added).append(name)
            continue
        copy_file(src, dest_json)
        (json_updated if existed else json_added).append(name)

    for name in sorted(existing_json - keep_names):
        dest_json = os.path.join(published, name)
        json_deleted.append(name)
        if not dry_run and os.path.isfile(dest_json):
            os.remove(dest_json)

    hist_stats: List[Dict[str, Any]] = []
    warnings: List[str] = []
    warnings.extend(remove_legacy_snapshots_tree(dest, dry_run))
    for rel in sorted(safe_refs):
        src_path = os.path.join(source, *rel.split("/"))
        dest_path = os.path.join(published, *rel.split("/"))
        is_hist = rel in hist_safe
        do_trim = should_trim_csv(rel, is_hist)
        st = trim_or_copy_csv(
            src_path,
            dest_path,
            start,
            date_cols.get(rel),
            trim=do_trim,
            dry_run=dry_run,
        )
        st["dest"] = dest_path
        hist_stats.append(st)
        print(
            f"  {rel}: {st['action']} before={st['rows_before']} after={st['rows_after']} "
            f"unparsed={st['rows_unparsed']} size={format_mb(int(st.get('bytes_dest') or 0))}"
        )
        if st.get("missing") and rel in hist_safe:
            warnings.append(f"missing hist_file: {rel}")
        elif st.get("missing") and rel in sidecar_present:
            warnings.append(f"missing auxiliary file: {rel}")
        if int(st.get("rows_unparsed") or 0) > 0 and do_trim:
            warnings.append(f"{rel}: {st['rows_unparsed']} rows dropped (unparsed date)")
        if st.get("github_cap_from"):
            warnings.append(
                f"{rel}: GitHub 99MB cap applied; HIST rows kept from {st['github_cap_from']} "
                f"(90-day window still used for JSON)"
            )
        if int(st.get("bytes_dest") or 0) >= GITHUB_HARD_LIMIT_BYTES:
            warnings.append(
                f"{rel}: dest size {format_mb(int(st['bytes_dest']))} exceeds GitHub 100MB "
                f"file limit (no LFS). Push may fail."
            )
        elif int(st.get("bytes_dest") or 0) >= GITHUB_SOFT_LIMIT_BYTES:
            warnings.append(
                f"{rel}: dest size {format_mb(int(st['bytes_dest']))} is near GitHub 100MB limit."
            )

    if sidecar_missing:
        warnings.append(
            "well-known sidecars missing on source (not published): "
            + ", ".join(sidecar_missing)
        )

    stale_others = existing_others - safe_refs - DEST_KEEP_RELPATHS
    for rel in sorted(stale_others):
        dest_path = os.path.join(published, *rel.split("/"))
        if not dry_run and os.path.isfile(dest_path):
            os.remove(dest_path)
            parent = os.path.dirname(dest_path)
            if parent.startswith(published) and parent != published:
                try:
                    os.rmdir(parent)
                except OSError:
                    pass
        warnings.append(f"deleted dest file outside published set: {rel}")

    dest_size = dir_size_bytes(published) if (not dry_run and os.path.isdir(published)) else 0
    if dry_run:
        dest_size = sum(int(st.get("bytes_dest") or 0) for st in hist_stats)
        for src in keep_json:
            try:
                dest_size += os.path.getsize(src)
            except OSError:
                pass

    body = build_report(
        as_of,
        start,
        days,
        source,
        dest,
        dry_run,
        json_added,
        json_updated,
        json_unchanged,
        json_deleted,
        outside,
        hist_stats,
        dangling,
        dest_size,
        warnings,
        sidecar_missing,
    )
    report_name = f"SYNC_REPORT_{as_of.strftime('%Y%m%d')}.md"
    report_path = os.path.join(reports, report_name)
    if dry_run:
        print(body)
        print(f"(dry-run) report not written: {report_path}")
    else:
        write_report(report_path, body)
        print(f"wrote {report_path}")

    print(f"WINDOW={start.isoformat()}..{end.isoformat()}")
    print(f"JSON added={len(json_added)} updated={len(json_updated)} "
          f"unchanged={len(json_unchanged)} deleted={len(json_deleted)}")
    print(f"dangling={len(dangling)} dest_size={format_mb(dest_size)}")
    return 0


def parse_as_of(text: Optional[str]) -> date:
    if not text:
        return date.today()
    t = text.strip()
    if len(t) == 8 and t.isdigit():
        d = parse_yyyymmdd(t)
        if d:
            return d
    return datetime.strptime(t, "%Y-%m-%d").date()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare 90-day MCP market-data window for GitHub.")
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help="Source snapshots directory only (never parent Z:\\market_data)",
    )
    parser.add_argument(
        "--dest",
        default=DEFAULT_DEST,
        help="Destination repo root; published data goes to <dest>/market_data",
    )
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Rolling calendar-day window")
    parser.add_argument("--as-of", dest="as_of", default=None, help="Anchor date YYYY-MM-DD or YYYYMMDD")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing dest data")
    args = parser.parse_args(argv)
    try:
        as_of = parse_as_of(args.as_of)
    except ValueError:
        print(f"ERROR invalid --as-of: {args.as_of}", file=sys.stderr)
        return 2
    return prepare(args.source, args.dest, args.days, as_of, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
