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
from html import unescape
from html.parser import HTMLParser
from urllib.parse import parse_qs, urljoin, urlparse


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
    pdf_b64: str = ""       # set for PDF manuals; locations are then page numbers

    @property
    def kind(self) -> str:
        return "document" if self.pdf_b64 else "video"

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


def parse_captions(raw: str, kind: str) -> list[Line]:
    """Parse caption text. `kind` is 'srt', 'vtt', or 'txt' ([mm:ss] prefixes optional)."""
    lines: list[Line] = []
    if kind in {"srt", "vtt"}:
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
    return lines


def from_caption_file(path: str | Path, title: str | None = None, url: str = "") -> Source:
    """Parse .srt, .vtt, or plain text (optionally with [mm:ss] prefixes)."""
    p = Path(path)
    raw = p.read_text(encoding="utf-8", errors="replace")
    lines = parse_captions(raw, p.suffix.lower().lstrip("."))
    if not lines:
        raise ValueError(f"No caption text found in {p}")
    return Source(p.stem, title or p.stem, url, lines)


MAX_PDF_BYTES = 30 * 1024 * 1024  # API request limit is 32 MB including base64 overhead


def from_pdf(path: str | Path, title: str | None = None, url: str = "") -> Source:
    """A PDF manual or course book. Claude reads the pages directly, figures included."""
    p = Path(path)
    data = p.read_bytes()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"{p} is not a PDF")
    b64 = base64.standard_b64encode(data).decode()
    if len(b64) > MAX_PDF_BYTES:
        raise ValueError(f"{p} is too large ({len(data) // 1_000_000} MB). Split it into "
                         "smaller PDFs (e.g. one per chapter) and add each one.")
    return Source(p.stem, title or p.stem, url, [], pdf_b64=b64)


# ---------------------------------------------------------------- web pages

_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _http_get(url: str) -> str:
    from urllib.request import Request, urlopen

    with urlopen(Request(url, headers=_BROWSER_HEADERS), timeout=30) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", errors="replace")


class _PageText(HTMLParser):
    """Visible text of a page, skipping scripts, styles, nav and footers."""
    SKIP = {"script", "style", "noscript", "nav", "footer", "header", "svg", "form"}

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.title = ""
        self._in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in {"p", "li", "h1", "h2", "h3", "h4", "br", "div", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.depth:
            self.depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self.depth and data.strip():
            self.parts.append(data.strip() + " ")

    def text(self) -> str:
        return re.sub(r"\n\s*\n+", "\n", "".join(self.parts)).strip()


def from_web(url_or_file: str, title: str | None = None, languages: list[str] | None = None) -> Source:
    """A tutorial web page (e.g. Autodesk Learn), by URL or as a saved .html file.

    Looks for, in order: an embedded YouTube video (uses its captions), a linked
    caption track (.vtt/.srt), and finally the page's written instructions.
    """
    is_file = Path(url_or_file).exists()
    html = Path(url_or_file).read_text(encoding="utf-8", errors="replace") if is_file else _http_get(url_or_file)
    page_url = "" if is_file else url_or_file
    parser = _PageText()
    parser.feed(html)
    page_title = title or unescape(parser.title).strip() or Path(url_or_file).stem

    m = re.search(r"(?:youtube(?:-nocookie)?\.com/embed/|youtu\.be/|youtube\.com/watch\?v=)([\w-]{11})", html)
    if m:
        try:
            src = from_youtube(m.group(1), languages)
            src.title = page_title
            return src
        except Exception:
            pass  # fall through to other sources

    if page_url:
        for cap in re.findall(r"""["'(]([^"'()\s]+\.(?:vtt|srt))(?:\?[^"'()\s]*)?["')]""", html):
            try:
                cap_url = urljoin(page_url, unescape(cap))
                lines = parse_captions(_http_get(cap_url), cap_url.rsplit(".", 1)[-1].split("?")[0])
                if lines:
                    return Source(_slug(page_url), page_title, page_url, lines)
            except Exception:
                continue

    text = parser.text()
    if len(text) < 200:
        raise ValueError(
            "Couldn't find captions or written steps on that page. Open the video, "
            "use its Transcript/CC option if it has one, save the text as a .txt or .vtt "
            "file, and add that file instead.")
    lines = [Line(0.0, row) for row in text.splitlines() if row.strip()]
    return Source(_slug(page_url or url_or_file), page_title, page_url, lines)


def _slug(s: str) -> str:
    return re.sub(r"[^\w-]+", "-", urlparse(s).path.strip("/") or Path(s).stem).strip("-")[-80:] or "page"


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
