"""Command line: python -m playbook <command> ...

  add <link-or-file> [...]     Extract workflows from YouTube links, tutorial web pages
                               (e.g. Autodesk Learn), PDF manuals, caption files, or saved
                               .html pages
  add --list links.txt         ...or from a text file with one link/path per line
  list                         Show the tutorials in the playbook
  search "g2 blend fender"     Find matching workflows (no AI call, free)
  ask ["question"]             Ask the coach; no question starts a chat
  export playbook.md           Write the whole playbook as a Markdown file
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import llm, sources
from .store import Playbook, export_markdown, render

SOFTWARE = {"catia": "CATIA%", "alias": "Autodesk Alias"}


def _load(item: str, args) -> sources.Source:
    path = Path(item)
    if path.exists() and path.suffix.lower() == ".pdf":
        src = sources.from_pdf(item, title=args.title, url=args.url or "")
        if args.video:
            raise ValueError("--video can't be used with a PDF")
        return src
    if path.exists() and path.suffix.lower() in {".html", ".htm"}:
        src = sources.from_web(item, title=args.title, languages=args.lang)
    elif path.exists():
        src = sources.from_caption_file(item, title=args.title, url=args.url or "")
    elif sources.youtube_id(item):
        src = sources.from_youtube(item, languages=args.lang)
        if args.title:
            src.title = args.title
    elif item.startswith(("http://", "https://")):
        src = sources.from_web(item, title=args.title, languages=args.lang)
    else:
        raise ValueError("not a file, YouTube link, or web page")
    if args.video:
        sources.add_frames(src, args.video, every_s=args.frame_every)
    return src


def cmd_add(args, pb: Playbook) -> int:
    items = list(args.items)
    if args.list:
        items += [l.strip() for l in Path(args.list).read_text().splitlines()
                  if l.strip() and not l.lstrip().startswith("#")]
    if not items:
        print("Nothing to add. Give a YouTube link, a caption file, or --list links.txt")
        return 1
    failed = 0
    for item in items:
        try:
            src = _load(item, args)
            if pb.has(src.source_id) and not args.redo:
                print(f"skip  {item} (already in playbook; use --redo to re-extract)")
                continue
            if src.kind == "document":
                print(f"read  {src.title}: PDF, {len(src.pdf_b64) * 3 // 4 // 1000} KB")
            else:
                print(f"read  {src.title}: {len(src.lines)} caption lines, {len(src.frames)} frames")
            n = pb.save(src, llm.extract(src))
            print(f"saved {n} workflows")
        except Exception as e:  # keep going through the list
            failed += 1
            print(f"FAIL  {item}: {e}", file=sys.stderr)
    return 1 if failed else 0


def cmd_list(args, pb: Playbook) -> int:
    for v in pb.videos():
        print(f"{v['n']:3d} workflows  {v['title']}  {v['url']}")
        print(f"     {v['summary']}")
    return 0


def cmd_search(args, pb: Playbook) -> int:
    rows = pb.search(" ".join(args.query), SOFTWARE.get(args.software or ""), limit=args.limit)
    if not rows:
        print("No matches.")
    for i, r in enumerate(rows, 1):
        print(render(r, i), end="\n\n")
    return 0


def cmd_ask(args, pb: Playbook) -> int:
    history: list[dict] = []
    software = SOFTWARE.get(args.software or "")

    def one(q: str) -> None:
        rows = pb.search(q, software)
        excerpts = "\n\n".join(render(r, i) for i, r in enumerate(rows, 1))
        for chunk in llm.answer(q, excerpts, history):
            print(chunk, end="", flush=True)
        print("\n")

    if args.question:
        one(" ".join(args.question))
        return 0
    print("Ask about CATIA 3DEXPERIENCE / Alias surfacing. Empty line to quit.")
    while (q := input("> ").strip()):
        one(q)
    return 0


def cmd_export(args, pb: Playbook) -> int:
    Path(args.out).write_text(export_markdown(pb), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="playbook", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--db", default="playbook.db", help="playbook database file")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="extract workflows from tutorials")
    a.add_argument("items", nargs="*")
    a.add_argument("--list", help="text file with one link or caption path per line")
    a.add_argument("--video", help="local video you have rights to; frames are sampled for the model")
    a.add_argument("--frame-every", type=int, default=30, help="seconds between frames (default 30)")
    a.add_argument("--title", help="title to show for this tutorial")
    a.add_argument("--url", help="link to cite for a local caption file")
    a.add_argument("--lang", nargs="+", default=["en"], help="caption languages to try, in order")
    a.add_argument("--redo", action="store_true", help="re-extract tutorials already in the playbook")

    sub.add_parser("list", help="list tutorials")

    s = sub.add_parser("search", help="search workflows (no AI call)")
    s.add_argument("query", nargs="+")
    s.add_argument("--software", choices=SOFTWARE)
    s.add_argument("--limit", type=int, default=5)

    q = sub.add_parser("ask", help="ask the surfacing coach")
    q.add_argument("question", nargs="*")
    q.add_argument("--software", choices=SOFTWARE)

    e = sub.add_parser("export", help="write the playbook to Markdown")
    e.add_argument("out", nargs="?", default="playbook.md")

    args = p.parse_args(argv)
    pb = Playbook(args.db)
    return {"add": cmd_add, "list": cmd_list, "search": cmd_search,
            "ask": cmd_ask, "export": cmd_export}[args.cmd](args, pb)


if __name__ == "__main__":
    sys.exit(main())
