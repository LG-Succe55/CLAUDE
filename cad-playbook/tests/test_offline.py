"""Offline tests: parsing, storage, search, export. No API key or network needed."""

from pathlib import Path

from playbook import sources
from playbook.models import Step, VideoExtraction, Workflow
from playbook.store import Playbook, export_markdown

SRT = """1
00:00:05,000 --> 00:00:09,000
Today we blend the hood into the fender with G2.

2
00:01:10,500 --> 00:01:14,000
Open Skin from the Surfaces palette, pick both curves.
"""


def canned() -> VideoExtraction:
    return VideoExtraction(
        summary="Building a G2 hood-to-fender blend in Alias.",
        workflows=[Workflow(
            title="G2 blend between hood and fender", software="Autodesk Alias",
            app_or_workbench="Surfaces palette", vehicle_areas=["hood", "fender"],
            level="intermediate", goal="Curvature-continuous blend surface.",
            start_s=5, end_s=300,
            steps=[
                Step(order=1, action="Create the blend surface", command="Skin",
                     menu_path="Surfaces > Skin", settings="", timestamp_s=70, why=""),
                Step(order=2, action="Match continuity to the hood", command="Align",
                     menu_path="Surface Edit > Align", settings="G2, explicit control on",
                     timestamp_s=150, why="Avoid a visible highlight break"),
            ],
            tips=["Check with zebra stripes"], pitfalls=["Too many spans"],
        )],
    )


def test_youtube_ids():
    assert sources.youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=3") == "dQw4w9WgXcQ"
    assert sources.youtube_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert sources.youtube_id("https://example.com/x") is None


def test_srt_and_text(tmp_path: Path):
    f = tmp_path / "hood.srt"
    f.write_text(SRT)
    src = sources.from_caption_file(f)
    assert [l.start for l in src.lines] == [5, 70]
    assert "[1:10] Open Skin" in src.transcript_text()
    t = tmp_path / "notes.txt"
    t.write_text("[0:05] intro\ncontinued\n[1:02:03] late")
    assert [l.start for l in sources.from_caption_file(t).lines] == [5, 5, 3723]


def test_store_search_export(tmp_path: Path):
    pb = Playbook(tmp_path / "p.db")
    src = sources.Source("abc123def45", "Hood blend", "https://www.youtube.com/watch?v=abc123def45",
                         [sources.Line(0, "x")])
    assert pb.save(src, canned()) == 1
    assert pb.save(src, canned()) == 1          # re-saving replaces, not duplicates
    assert len(pb.all_workflows()) == 1
    hits = pb.search("fender blending g2")
    assert hits and hits[0]["title"].startswith("G2 blend")
    assert pb.search("fender", "CATIA 3DEXPERIENCE") == []
    md = export_markdown(pb)
    assert "**Align**" in md and "watch?v=abc123def45&t=150s" in md


PAGE = """<html><head><title>Create Objects in Alias | Autodesk</title>
<script>var x = "ignore me";</script></head><body><nav>Products Menu</nav>
<h1>Create objects in Alias</h1>{player}
<p>In this tutorial you build primitives and revolve a profile curve.</p>
<ol><li>Open the Palette and choose Surfaces &gt; Primitives &gt; Sphere.</li>
<li>Draw a CV curve, then use Surfaces &gt; Revolve and set the sweep angle to 360.</li>
<li>Use Object Edit &gt; Rebuild to reduce spans before evaluating with zebra stripes.</li></ol>
<footer>Copyright</footer></body></html>"""


def test_web_page_written_steps(tmp_path: Path):
    f = tmp_path / "alias.html"
    f.write_text(PAGE.format(player=""))
    src = sources.from_web(str(f))
    text = src.transcript_text()
    assert src.title == "Create Objects in Alias | Autodesk"
    assert "Revolve" in text and "ignore me" not in text and "Products Menu" not in text


def test_web_page_caption_track(monkeypatch):
    html = PAGE.format(player='<track kind="captions" src="/media/alias-objects.vtt">')
    vtt = "WEBVTT\n\n00:00:12.000 --> 00:00:15.000\nChoose Revolve from the palette.\n"
    pages = {"https://www.autodesk.com/learn/t/create-objects": html,
             "https://www.autodesk.com/media/alias-objects.vtt": vtt}
    monkeypatch.setattr(sources, "_http_get", lambda u: pages[u])
    src = sources.from_web("https://www.autodesk.com/learn/t/create-objects")
    assert [(l.start, l.text) for l in src.lines] == [(12, "Choose Revolve from the palette.")]
    assert src.url.endswith("create-objects")


def test_web_page_embedded_youtube(tmp_path: Path, monkeypatch):
    f = tmp_path / "alias.html"
    f.write_text(PAGE.format(player='<iframe src="https://www.youtube.com/embed/abcDEF12345"></iframe>'))
    monkeypatch.setattr(sources, "from_youtube", lambda vid, langs=None: sources.Source(
        vid, "yt", f"https://www.youtube.com/watch?v={vid}", [sources.Line(3, "hi")]))
    src = sources.from_web(str(f))
    assert src.source_id == "abcDEF12345" and src.title.startswith("Create Objects")
