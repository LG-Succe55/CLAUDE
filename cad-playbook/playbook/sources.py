"""Getting tutorial text (and optionally frames) into the pipeline.

Supported sources:
  * A YouTube link: the published captions are fetched. The video itself is
    never downloaded (YouTube's terms forbid that).
  * A local caption file (.srt / .vtt / .txt), e.g. from a paid course you
    are licensed to use or from your own screen recordings.
  * Optionally a local video file you have the rights to, from which still
    frames are sampled so the model can see menus and dialogs.
"""

from __future__ import annotations

import base64
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qs, urlparse


@dataclass
class Line:
    start: float
    text: str


@dataclass
class Source:
    source_id: str          # YouTube id or file stem
    title: str
    url: str                # link used for citations ("" for local files)
    lines: list[Line]
    frames: list[tuple[float, str]] = field(default_factory=list)  # (seconds, base64 jpeg)

    def transcript_text(self) -> str:
        return "\n".join(f"[{fmt_time(l.start)}] {l.text}" for l in self.lines)


def fmt_time(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def youtube_id(url: str) -> str | None:
    u = urlparse(url.strip())
    host = (u.hostname or "").lower()
    if host.endswith("youtu.be"):
        return u.path.lstrip("/").split("/")[0] or None
    if "youtube.com" in host:
        if u.path == "/watch":
            return parse_qs(u.query).get("v", [None])[0]
        m = re.match(r"^/(shorts|embed|live)/([\w-]{11})", u.path)
        if m:
            return m.group(2)
    if re.fullmatch(r"[\w-]{11}", url.strip()):
        return url.strip()
    return None


def from_youtube(url: str, languages: list[str] | None = None) -> Source:
    from youtube_transcript_api import YouTubeTranscriptApi

    vid = youtube_id(url)
    if not vid:
        raise ValueError(f"Not a YouTube link: {url}")
    fetched = YouTubeTranscriptApi().fetch(vid, languages=languages or ["en"])
    lines = [Line(s.start, s.text.replace("\n", " ")) for s in fetched.snippets]
    return Source(vid, f"YouTube {vid}", f"https://www.youtube.com/watch?v={vid}", lines)


_TS = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})(?:[.,]\d+)?")


def _to_seconds(stamp: str) -> float:
    m = _TS.match(stamp.strip())
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(s)


def from_caption_file(path: str | Path, title: str | None = None, url: str = "") -> Source:
    """Parse .srt, .vtt, or plain text (optionally with [mm:ss] prefixes)."""
    p = Path(path)
    raw = p.read_text(encoding="utf-8", errors="replace")
    lines: list[Line] = []
    if p.suffix.lower() in {".srt", ".vtt"}:
        for block in re.split(r"\n\s*\n", raw.replace("\r", "")):
            rows = [r for r in block.split("\n") if r.strip()]
            stamp = next((r for r in rows if "-->" in r), None)
            if not stamp:
                continue
            text_rows = rows[rows.index(stamp) + 1:]
            text = re.sub(r"<[^>]+>", "", " ".join(text_rows)).strip()
            if text:
                lines.append(Line(_to_seconds(stamp.split("-->")[0]), text))
    else:
        for row in raw.splitlines():
            m = re.match(r"^\s*\[?((?:\d+:)?\d{1,2}:\d{2})\]?\s*(.*)$", row)
            if m:
                lines.append(Line(_to_seconds(m.group(1)), m.group(2)))
            elif row.strip():
                lines.append(Line(lines[-1].start if lines else 0.0, row.strip()))
    if not lines:
        raise ValueError(f"No caption text found in {p}")
    return Source(p.stem, title or p.stem, url, lines)


def add_frames(src: Source, video: str | Path, every_s: int = 30, max_frames: int = 40) -> None:
    """Sample still frames from a local video you have the rights to use."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is not installed; install it or leave out --video")
    duration = src.lines[-1].start if src.lines else 0
    step = max(every_s, int(duration / max_frames) + 1) if duration else every_s
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", str(video),
             "-vf", f"fps=1/{step},scale=1280:-2", "-q:v", "4",
             str(Path(tmp) / "f%04d.jpg")],
            check=True,
        )
        for i, f in enumerate(sorted(Path(tmp).glob("f*.jpg"))[:max_frames]):
            src.frames.append((i * step, base64.standard_b64encode(f.read_bytes()).decode()))
