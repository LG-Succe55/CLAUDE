"""SQLite storage with full-text search over extracted workflows."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from .models import VideoExtraction, Workflow
from .sources import Source, fmt_time

SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    source_id TEXT PRIMARY KEY, title TEXT, url TEXT, summary TEXT, kind TEXT DEFAULT 'video',
    added_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY, source_id TEXT REFERENCES videos(source_id) ON DELETE CASCADE,
    title TEXT, software TEXT, app TEXT, level TEXT, data TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS wf_search USING fts5(
    title, software, app, areas, body, tokenize='porter unicode61'
);
"""


class Playbook:
    def __init__(self, path: str | Path = "playbook.db"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(SCHEMA)
        cols = [r[1] for r in self.db.execute("PRAGMA table_info(videos)")]
        if "kind" not in cols:  # databases made before PDF support
            self.db.execute("ALTER TABLE videos ADD COLUMN kind TEXT DEFAULT 'video'")

    def has(self, source_id: str) -> bool:
        return self.db.execute("SELECT 1 FROM videos WHERE source_id=?", (source_id,)).fetchone() is not None

    def save(self, src: Source, ex: VideoExtraction) -> int:
        with self.db:
            self.remove(src.source_id)
            self.db.execute(
                "INSERT INTO videos(source_id,title,url,summary,kind) VALUES(?,?,?,?,?)",
                (src.source_id, src.title, src.url, ex.summary, src.kind),
            )
            for wf in ex.workflows:
                cur = self.db.execute(
                    "INSERT INTO workflows(source_id,title,software,app,level,data) VALUES(?,?,?,?,?,?)",
                    (src.source_id, wf.title, wf.software, wf.app_or_workbench, wf.level, wf.model_dump_json()),
                )
                body = " ".join(
                    [wf.goal]
                    + [f"{s.action} {s.command} {s.menu_path} {s.settings} {s.why}" for s in wf.steps]
                    + wf.tips + wf.pitfalls
                )
                self.db.execute(
                    "INSERT INTO wf_search(rowid,title,software,app,areas,body) VALUES(?,?,?,?,?,?)",
                    (cur.lastrowid, wf.title, wf.software, wf.app_or_workbench, " ".join(wf.vehicle_areas), body),
                )
        return len(ex.workflows)

    def remove(self, source_id: str) -> None:
        ids = [r[0] for r in self.db.execute("SELECT id FROM workflows WHERE source_id=?", (source_id,))]
        for i in ids:
            self.db.execute("DELETE FROM wf_search WHERE rowid=?", (i,))
        self.db.execute("DELETE FROM workflows WHERE source_id=?", (source_id,))
        self.db.execute("DELETE FROM videos WHERE source_id=?", (source_id,))

    def search(self, query: str, software: str | None = None, limit: int = 6) -> list[sqlite3.Row]:
        words = re.findall(r"[\w-]+", query.lower())
        if not words:
            return []
        fts = " OR ".join(f'"{w}"' for w in words)
        sql = """SELECT w.*, v.url, v.title AS video_title, v.kind FROM wf_search s
                 JOIN workflows w ON w.id = s.rowid JOIN videos v ON v.source_id = w.source_id
                 WHERE wf_search MATCH ?"""
        args: list = [fts]
        if software:
            sql += " AND w.software LIKE ?"
            args.append(software)
        sql += " ORDER BY bm25(wf_search, 5.0, 1.0, 2.0, 3.0, 1.0) LIMIT ?"
        args.append(limit)
        return list(self.db.execute(sql, args))

    def videos(self) -> list[sqlite3.Row]:
        return list(self.db.execute(
            "SELECT v.*, COUNT(w.id) AS n FROM videos v LEFT JOIN workflows w USING(source_id) "
            "GROUP BY v.source_id ORDER BY v.added_at"))

    def all_workflows(self) -> list[sqlite3.Row]:
        return list(self.db.execute(
            "SELECT w.*, v.url, v.title AS video_title, v.kind FROM workflows w "
            "JOIN videos v USING(source_id) ORDER BY w.software, w.title"))


def link(url: str, video_title: str, seconds: float, kind: str = "video") -> str:
    if kind == "document":
        page = f"p. {int(seconds)}"
        return f"[{page}]({url}#page={int(seconds)})" if url else f"{video_title}, {page}"
    if not url:
        return f"{video_title} @ {fmt_time(seconds)}"
    return f"{url}&t={int(seconds)}s"


def render(row: sqlite3.Row, n: int | None = None) -> str:
    """Markdown for one workflow, with timestamped links."""
    wf = Workflow.model_validate_json(row["data"])
    kind = row["kind"] if "kind" in row.keys() else "video"

    def at(x: float) -> str:
        return link(row["url"], row["video_title"], x, kind)
    head = f"[{n}] " if n is not None else ""
    out = [f"### {head}{wf.title}",
           f"*{wf.software} · {wf.app_or_workbench or '-'} · {wf.level} · "
           f"{', '.join(wf.vehicle_areas) or '-'}*",
           f"Source: {at(wf.start_s)}", "",
           f"**Goal:** {wf.goal}", ""]
    for s in sorted(wf.steps, key=lambda s: s.order):
        bits = [f"{s.order}. {s.action}"]
        if s.command:
            bits.append(f"**{s.command}**")
        if s.menu_path:
            bits.append(f"({s.menu_path})")
        line = " ".join(bits)
        if s.settings:
            line += f" — settings: {s.settings}"
        if kind == "document":
            line += f" ({at(s.timestamp_s)})"
        else:
            line += f" [{fmt_time(s.timestamp_s)}]({at(s.timestamp_s)})"
        if s.why:
            line += f"\n   - Why: {s.why}"
        out.append(line)
    if wf.tips:
        out += ["", "**Tips**"] + [f"- {t}" for t in wf.tips]
    if wf.pitfalls:
        out += ["", "**Avoid**"] + [f"- {p}" for p in wf.pitfalls]
    return "\n".join(out)


def export_markdown(pb: Playbook) -> str:
    rows = pb.all_workflows()
    parts = ["# Vehicle Surfacing Playbook", "",
             f"{len(rows)} workflows from {len(pb.videos())} tutorials.", ""]
    current = None
    for r in rows:
        if r["software"] != current:
            current = r["software"]
            parts += [f"## {current}", ""]
        parts += [render(r), ""]
    return "\n".join(parts)

