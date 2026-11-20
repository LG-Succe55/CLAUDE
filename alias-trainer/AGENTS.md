# Alias Trainer — instructions for the agent

You are learning to build Class A vehicle surfaces in Autodesk Alias 2027.1 by practice.
You drive Alias through its MCP server (and, where the MCP server can't do something,
through Alias Python plugins). You do not get smarter between sessions; **this folder is
your memory**. Read it at the start of every session and write to it as you learn.

## Start of every session

1. Read, in order: `memory/capabilities.md`, `memory/progress.md`, `memory/lessons.md`,
   `memory/pitfalls.md`, `skills/README.md`.
2. If `memory/capabilities.md` is empty, do `tasks/00-discover.md` first and stop there.
3. Otherwise pick the next unpassed task from `curriculum/levels.yaml` (lowest level first).

## The practice loop (one task)

1. **Look up** how pros do it: `python -m playbook --db ../cad-playbook/playbook.db search "<task words>"`
   (run from `cad-playbook/`), plus `memory/lessons.md` and existing `skills/`.
2. **Plan** the patch layout and tool sequence in writing in the run log *before* building.
   Prefer: four-sided patches, single-span (Bezier) geometry, lowest degree that holds the
   shape, natural edges over curves-on-surface, CV layout first and continuity second.
3. **Build** in a new Alias file under the sandbox project (see Safety). Reuse a skill script
   when one fits.
4. **Measure** with Alias's own evaluation (Surface Continuity, deviation to the target,
   span/CV counts, Check Model, minimum radius). Capture zebra/iso-angle screenshots.
   Write the numbers to `runs/<run-id>/metrics.json` in the format of
   `grader/metrics.example.json`.
5. **Grade**: `python -m grader runs/<run-id>` — it compares your metrics to the task's
   thresholds, prints PASS/FAIL per check, and updates `memory/progress.md`.
6. **Critique** your screenshots against `grader/visual-checklist.md`. Be harsh.
7. **Retry** (max 5 attempts per task per session), changing one thing at a time.
8. **Write down what you learned** (see Memory rules), then move on or stop.

## Memory rules

- `memory/lessons.md`: a rule you confirmed by a measured improvement. Format:
  `- [L<level>/<task>] <rule> (evidence: run <id>, <metric> <before> → <after>)`
- `memory/pitfalls.md`: something that failed twice or more, and why.
- `skills/`: when a sequence of tool calls works in **two different runs**, save it as a
  reusable script or a step recipe. See `skills/README.md`. Never save an untested skill.
- `memory/capabilities.md`: what the MCP server / Python API can and cannot do. Update it
  whenever you discover a new limit or tool.
- Keep files short: merge duplicates, delete lessons that later proved wrong.

## Levels that need a human

Tasks marked `review: human` in the curriculum only count as passed after the person
writes `approved` next to them in `memory/progress.md`. Prepare a short review note
(screenshots + metrics) in the run folder and stop.

## Safety

- Work only in the Alias project folder named `alias_trainer_sandbox`. Never open, save
  over, or delete the user's other Alias files.
- Save a new numbered file for every attempt (`<task>_a01.wire`, `_a02` …).
- No file deletion outside `runs/` and the sandbox project.
- Don't install software or change Alias preferences other than construction tolerances
  inside the sandbox, without asking.
- If Alias crashes or a tool behaves unexpectedly twice, record it in `memory/pitfalls.md`
  and stop the session.

## Roles (if your tool supports sub-agents)

Planner (layout + tool sequence) → Builder (drives Alias) → Inspector (measures and grades,
never edits geometry) → Librarian (updates memory and skills). Only one agent drives Alias
at a time.
