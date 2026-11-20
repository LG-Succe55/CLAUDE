"""Claude calls: extracting workflows and answering questions."""

from __future__ import annotations

from typing import Iterator

import anthropic

from .models import VideoExtraction
from .sources import Source, fmt_time

MODEL = "claude-opus-5-5"
FALLBACK_BETA = "server-side-fallback-2026-07-01"

EXTRACT_SYSTEM = """You turn CAD tutorial videos into precise, reusable workflows for \
automotive designers who use CATIA 3DEXPERIENCE and Autodesk Alias.

From the transcript (and frames, if provided) pull out every distinct task the \
presenter demonstrates. For each one, record the exact command names as they appear \
in the software, where to find them, the settings and values used, and the \
timestamp where each step happens. Keep the presenter's reasons, tips and warnings.

Only record what the video actually shows or says. If a command name or setting is \
unclear, leave the field empty rather than guessing. Captions are often \
auto-generated, so fix obvious mis-hearings of CAD terms (for example "G two" -> G2, \
"skin" vs "skim") only when the context makes the intended term clear."""

ANSWER_SYSTEM = """You are a surfacing coach for CATIA 3DEXPERIENCE and Autodesk Alias, \
answering from a playbook of workflows extracted from tutorial videos.

Answer with numbered, concrete steps (command names, where to find them, settings). \
Cite the playbook entries you used as [n], matching the numbers in the excerpts. \
If the playbook doesn't cover something, say so plainly and then give your best \
general guidance, clearly labelled as not from the playbook."""


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def extract(src: Source) -> VideoExtraction:
    content: list[dict] = []
    for seconds, b64 in src.frames:
        content.append({"type": "text", "text": f"Frame at {fmt_time(seconds)}:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}})
    content.append({
        "type": "text",
        "text": f"Video: {src.title}\n\nTranscript:\n{src.transcript_text()}",
    })

    resp = _client().beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=EXTRACT_SYSTEM,
        output_config={"effort": "high"},
        betas=[FALLBACK_BETA],
        fallbacks="default",
        messages=[{"role": "user", "content": content}],
        output_format=VideoExtraction,
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined to process {src.title}")
    if resp.stop_reason == "max_tokens":
        raise RuntimeError(f"Extraction for {src.title} was cut off; try a shorter video")
    if resp.parsed_output is None:
        raise RuntimeError(f"No structured output for {src.title}")
    return resp.parsed_output


def answer(question: str, excerpts: str, history: list[dict]) -> Iterator[str]:
    """Stream an answer. `history` is updated in place for follow-up questions."""
    history.append({
        "role": "user",
        "content": f"Playbook excerpts:\n{excerpts or '(no matching entries)'}\n\nQuestion: {question}",
    })
    with _client().beta.messages.stream(
        model=MODEL,
        max_tokens=16000,
        system=ANSWER_SYSTEM,
        output_config={"effort": "medium"},
        betas=[FALLBACK_BETA],
        fallbacks="default",
        messages=history,
    ) as stream:
        for text in stream.text_stream:
            yield text
        final = stream.get_final_message()
    if final.stop_reason == "refusal":
        yield "\n(Claude declined to answer this one.)"
    history.append({"role": "assistant", "content": final.content})
