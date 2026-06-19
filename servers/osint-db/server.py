# -*- coding: utf-8 -*-
"""osint-db — remote MCP server over the Israeli gov OSINT SQLite database.

Mirrors the local osint-db MCP: three read-only tools (list_tables,
describe_table, query_db) over osint.db (exemptions, knesset_bills,
knesset_votes, mavat_plans, legislation, mevaker_reports,
police_announcements, ...).

Env vars:
  OSINT_DB_PATH  path to the SQLite file (default ./osint.db)
  HOST           bind address (default 0.0.0.0)
  PORT           HTTP port (default 8765)

The DB is opened read-only (mode=ro). Auth is handled in front of the
server (nginx Bearer check or Tailscale) — see README.md.
"""

import json
import os
import re
import sqlite3
import time

from fastmcp import FastMCP

DB_PATH = os.environ.get("OSINT_DB_PATH", "./osint.db")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8765"))

# Hard caps
MAX_LIMIT = 500                 # max rows per query
MAX_OUTPUT_CHARS = 50_000       # max characters in tool output
PROGRESS_EVERY = 10_000         # sqlite VM instructions between progress callbacks
MAX_PROGRESS_CALLS = 100        # 100 * 10,000 = ~1,000,000 opcodes
QUERY_TIMEOUT_SEC = 10.0        # wall-clock timeout per query

mcp = FastMCP("osint-db")


class QueryAborted(Exception):
    pass


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _guarded_connect() -> sqlite3.Connection:
    """Read-only connection with an opcode + wall-clock guard."""
    conn = _connect()
    state = {"calls": 0, "deadline": time.monotonic() + QUERY_TIMEOUT_SEC}

    def _progress():
        state["calls"] += 1
        if state["calls"] > MAX_PROGRESS_CALLS:
            return 1  # abort: opcode budget (~1M VM steps) exhausted
        if time.monotonic() > state["deadline"]:
            return 1  # abort: timeout
        return 0

    conn.set_progress_handler(_progress, PROGRESS_EVERY)
    return conn


def _strip_leading_comments(sql: str) -> str:
    """Remove leading whitespace, -- line comments and /* */ block comments."""
    s = sql
    while True:
        s = s.lstrip()
        if s.startswith("--"):
            nl = s.find("\n")
            if nl == -1:
                return ""
            s = s[nl + 1:]
            continue
        if s.startswith("/*"):
            end = s.find("*/")
            if end == -1:
                return ""
            s = s[end + 2:]
            continue
        return s


def _truncate(text: str, note: str = "") -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    cut = text[:MAX_OUTPUT_CHARS]
    # cut on a line boundary so we never emit half a JSON object
    nl = cut.rfind("\n")
    if nl > 0:
        cut = cut[:nl]
    return cut + f"\n-- TRUNCATED: output exceeded {MAX_OUTPUT_CHARS} chars{note}. Narrow the query (fewer columns, smaller limit, WHERE clause)."


@mcp.tool
def list_tables() -> str:
    """List all tables in the OSINT database with their row counts.
    Returns one JSON object per line: {"table": ..., "rows": ...}."""
    conn = _guarded_connect()
    try:
        names = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        lines = []
        for name in names:
            try:
                (count,) = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()
            except sqlite3.OperationalError as e:
                count = f"error: {e}"
            lines.append(json.dumps({"table": name, "rows": count}, ensure_ascii=False))
        return _truncate("\n".join(lines)) if lines else "(no tables)"
    finally:
        conn.close()


@mcp.tool
def describe_table(name: str) -> str:
    """Describe a table's columns (PRAGMA table_info). `name` must be an
    existing table. Returns one JSON object per column:
    {"cid", "name", "type", "notnull", "default", "pk"}."""
    conn = _guarded_connect()
    try:
        # Validate against sqlite_master to prevent injection via PRAGMA arg.
        row = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type IN ('table','view') AND name = ?",
            (name,),
        ).fetchone()
        if row is None:
            return f"error: no such table: {name!r}. Use list_tables() to see available tables."
        real_name = row[0]
        cols = conn.execute(f'PRAGMA table_info("{real_name}")').fetchall()
        lines = [
            json.dumps(
                {
                    "cid": c["cid"],
                    "name": c["name"],
                    "type": c["type"],
                    "notnull": c["notnull"],
                    "default": c["dflt_value"],
                    "pk": c["pk"],
                },
                ensure_ascii=False,
            )
            for c in cols
        ]
        return _truncate("\n".join(lines)) if lines else "(no columns)"
    finally:
        conn.close()


@mcp.tool
def query_db(sql: str, limit: int = 100) -> str:
    """Run a read-only SELECT (or WITH ... SELECT) against the OSINT database.
    Anything other than SELECT/WITH is rejected. Returns one JSON object per
    row. `limit` caps the number of rows (hard max 500); output is truncated
    at 50,000 characters. Queries are killed after ~1M sqlite VM steps or 10s.
    """
    stripped = _strip_leading_comments(sql)
    if not re.match(r"(?is)^\s*(select|with)\b", stripped):
        return "error: only read-only SELECT / WITH queries are allowed."

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 100
    if limit < 1:
        limit = 1
    if limit > MAX_LIMIT:
        limit = MAX_LIMIT

    conn = _guarded_connect()
    try:
        cur = conn.execute(stripped)
        rows = cur.fetchmany(limit + 1)
        truncated_rows = len(rows) > limit
        rows = rows[:limit]
        if not rows:
            return "(no rows)"
        lines = [json.dumps(dict(r), ensure_ascii=False, default=str) for r in rows]
        out = "\n".join(lines)
        if truncated_rows:
            out += f"\n-- NOTE: more rows exist beyond limit={limit} (hard max {MAX_LIMIT})."
        return _truncate(out)
    except sqlite3.OperationalError as e:
        if "interrupted" in str(e).lower():
            return (
                "error: query aborted — exceeded ~1,000,000 sqlite VM steps "
                f"or {QUERY_TIMEOUT_SEC:.0f}s timeout. Add WHERE filters / indexes-friendly conditions."
            )
        return f"error: {e}"
    except sqlite3.Error as e:
        return f"error: {e}"
    finally:
        conn.close()


# Tables/columns searched by search_entity (name/company across the DB).
# Each entry: table -> (search_columns, return_columns)
_ENTITY_SEARCH = {
    "exemptions": (
        ["supplier_names", "contact_name", "publisher", "title"],
        ["id", "title", "publisher", "supplier_names", "amount_ils", "pub_date", "detail_url"],
    ),
    "knesset_mk_individuals": (
        ["mk_individual_name", "mk_individual_name_eng"],
        ["mk_individual_id", "mk_individual_name", "mk_individual_name_eng"],
    ),
    "legislation": (["title", "ministry"], ["id", "title", "ministry", "pub_date", "url"]),
    "mevaker_reports": (["title", "ministry"], ["id", "title", "ministry", "type", "pub_date", "url"]),
    "mavat_plans": (["pl_name", "ja_concat"], ["pl_number", "pl_name", "district_name", "depositing_date", "pl_url"]),
    "yosh_plans": (["pl_name", "ja_concat"], ["pl_number", "pl_name", "district_name", "depositing_date", "pl_url"]),
    "decisions": (["title", "summary"], ["id", "title", "decision_date", "url"]),
}


@mcp.tool
def search_entity(name: str, per_table_limit: int = 20) -> str:
    """Fuzzy-search a person or company name across the OSINT database in one
    call — exemptions (suppliers/contacts), Knesset MKs, legislation, comptroller
    reports, planning (Mavat + Yosh), and government decisions. Use this to build
    an entity dossier instead of writing a LIKE query per table. Returns JSON
    lines, each tagged with its source table. `name` is matched case-insensitively
    as a substring. Verify every hit against its source URL before publishing —
    a name match is a lead, not a fact."""
    term = (name or "").strip()
    if len(term) < 2:
        return "error: provide a name of at least 2 characters."
    try:
        per_table_limit = max(1, min(int(per_table_limit), 100))
    except (TypeError, ValueError):
        per_table_limit = 20

    like = f"%{term}%"
    # Discover which tables exist (one quick guarded connection).
    disc = _guarded_connect()
    try:
        existing = {r[0] for r in disc.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        disc.close()

    out_lines = []
    # Fresh guarded connection per table, so a heavy table (e.g. exemptions,
    # 137K rows) can't exhaust the opcode/time budget of the rest.
    for table, (search_cols, ret_cols) in _ENTITY_SEARCH.items():
        if table not in existing:
            continue
        where = " OR ".join(f'"{c}" LIKE ?' for c in search_cols)
        sel = ", ".join(f'"{c}"' for c in ret_cols)
        sql = f'SELECT {sel} FROM "{table}" WHERE {where} LIMIT {per_table_limit}'
        conn = _guarded_connect()
        try:
            rows = conn.execute(sql, tuple([like] * len(search_cols))).fetchall()
            for r in rows:
                rec = {"table": table}
                rec.update(dict(r))
                out_lines.append(json.dumps(rec, ensure_ascii=False, default=str))
        except sqlite3.OperationalError as e:
            msg = "scan too broad (aborted)" if "interrupted" in str(e).lower() else str(e)
            out_lines.append(json.dumps({"table": table, "note": msg}, ensure_ascii=False))
        except sqlite3.Error as e:
            out_lines.append(json.dumps({"table": table, "error": str(e)}, ensure_ascii=False))
        finally:
            conn.close()
    if not out_lines:
        return f"(no matches for {term!r})"
    return _truncate("\n".join(out_lines))


@mcp.tool
def new_since(table: str, since: str, limit: int = 100) -> str:
    """Return rows of `table` first seen on/after `since` (an ISO date/time string,
    e.g. '2026-06-10'), ordered newest-first by first_seen_at. Use this for daily
    lead generation — what entered the database since the last scan. The table must
    have a first_seen_at column. Returns one JSON object per row (hard max 500 rows,
    50,000 chars)."""
    conn = _guarded_connect()
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            (table,),
        ).fetchone()
        if row is None:
            return f"error: no such table: {table!r}. Use list_tables() first."
        real = row[0]
        cols = {c["name"] for c in conn.execute(f'PRAGMA table_info("{real}")').fetchall()}
        if "first_seen_at" not in cols:
            return f"error: table {real!r} has no first_seen_at column."
        try:
            lim = max(1, min(int(limit), MAX_LIMIT))
        except (TypeError, ValueError):
            lim = 100
        sql = (
            f'SELECT * FROM "{real}" WHERE first_seen_at >= ? '
            f'ORDER BY first_seen_at DESC LIMIT {lim}'
        )
        rows = conn.execute(sql, (since,)).fetchall()
        if not rows:
            return f"(no rows in {real} first seen on/after {since})"
        lines = [json.dumps(dict(r), ensure_ascii=False, default=str) for r in rows]
        return _truncate("\n".join(lines))
    except sqlite3.OperationalError as e:
        if "interrupted" in str(e).lower():
            return "error: query aborted — narrow the window or table."
        return f"error: {e}"
    except sqlite3.Error as e:
        return f"error: {e}"
    finally:
        conn.close()


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"osint-db: database file not found at OSINT_DB_PATH={DB_PATH}")
    mcp.run(transport="http", host=HOST, port=PORT)
