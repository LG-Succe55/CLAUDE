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
