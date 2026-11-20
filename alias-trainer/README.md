# Alias Trainer

A practice loop that teaches an AI agent in VS Code to build Class A vehicle surfaces in
Autodesk Alias, level by level, keeping what it learns in files.

**How it learns:** the model itself doesn't change. Each session it reads `memory/` and
`skills/`, practises a task from `curriculum/levels.yaml`, measures the result with Alias's
own evaluation tools, grades it (`python -m grader`), and writes down what worked. Proven
tool sequences become reusable skills. You sign off the tasks that need a pro's eye.

## Setup (Windows PC with Alias 2027.1 and VS Code)

1. Clone this repository and open the repo folder in VS Code.
2. Put the playbook you downloaded (`playbook.db`) in `cad-playbook/`, then:
   ```powershell
   cd cad-playbook; py -m pip install -r requirements.txt; cd ..
   py -m pip install pyyaml pytest
   ```
3. In Alias 2027.1, turn on the **Alias MCP server** (public beta) and connect it to your
   AI tool in VS Code, following Autodesk's MCP instructions. Check that the model can see its tools.
4. In Alias, create a project named `alias_trainer_sandbox` (File > Project > New Project).
   The agent works only there.
5. Put target scans or meshes in `alias-trainer/targets/` (see `curriculum/TARGETS.md`).

## Run it

Open a chat in agent mode with the workspace on `alias-trainer/`, choose your strongest
model, and say:

> Follow AGENTS.md. Start a training session.

- First session: it runs `tasks/00-discover.md` and fills in `memory/capabilities.md`.
  Review that before going further. It tells you what's actually automatable.
- Later sessions: it works through the curriculum. Check `memory/progress.md`; write
  `approved` after a line to pass a task marked for human review.
- To keep it going unattended, start new sessions on a schedule. Every session resumes
  from the memory files.

## Files

| Path | Purpose |
|---|---|
| `AGENTS.md` | The agent's operating instructions (also loaded via `CLAUDE.md`) |
| `curriculum/levels.yaml` | Levels 1–6 with pass thresholds — tighten them over time |
| `grader/` | `python -m grader runs/<id>` grades `metrics.json`; visual checklist for screenshots |
| `memory/` | Capabilities, progress, lessons, pitfalls — the agent's memory |
| `skills/` | Proven scripts and recipes |
| `runs/` | Per-attempt metrics, screenshots and notes (git-ignored) |

## Safety notes

The agent is told to stay inside the sandbox project and save every attempt as a new file.
Still: back up your Alias data before the first session, and keep tool-approval prompts on
in VS Code until you trust what it does.
