"""Grade one practice run against the curriculum thresholds.

A run folder holds metrics.json written by the agent from Alias's own evaluation tools.
Usage: python -m grader runs/<run-id>
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "curriculum" / "levels.yaml"
PROGRESS = ROOT / "memory" / "progress.md"

# check name -> (metrics key, comparison). "max" = metric must be <= limit, "min" = >=.
CHECKS = {
    "max_gap_mm": ("max_gap_mm", "max"),
    "max_angle_deg": ("max_angle_deg", "max"),
    "max_curv_dev": ("max_curv_dev", "max"),
    "max_deviation_mm": ("max_deviation_mm", "max"),
    "max_spans": ("max_spans", "max"),
    "max_degree": ("max_degree", "max"),
    "min_degree": ("min_degree", "min"),
    "inflections": ("inflections", "max"),
    "check_model_errors": ("check_model_errors", "max"),
    "three_sided_patches": ("three_sided_patches", "max"),
    "min_radius_mm": ("min_radius_mm", "min"),
}
# Defaults only apply to runs that produced surfaces (curves have no continuity joins).
SURFACE_ONLY = {"max_gap_mm", "max_angle_deg", "max_curv_dev", "check_model_errors"}


@dataclass
class Result:
    check: str
    limit: float
    value: float | None
    passed: bool

    def line(self) -> str:
        shown = "missing" if self.value is None else f"{self.value:g}"
        op = "<=" if CHECKS[self.check][1] == "max" else ">="
        return f"{'PASS' if self.passed else 'FAIL'}  {self.check}: {shown} (needs {op} {self.limit:g})"


def load_curriculum(path: Path = CURRICULUM) -> tuple[dict, dict[str, dict]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    tasks = {t["id"]: {**t, "level": lvl["level"]} for lvl in data["levels"] for t in lvl["tasks"]}
    return data.get("defaults", {}), tasks


def grade(metrics: dict, task: dict, defaults: dict) -> list[Result]:
    has_surfaces = bool(metrics.get("surface_count", 0))
    limits = {k: v for k, v in defaults.items() if has_surfaces or k not in SURFACE_ONLY}
    limits.update(task.get("checks") or {})
    results = []
    for name, limit in limits.items():
        if name not in CHECKS:
            raise ValueError(f"Unknown check '{name}' in task {task['id']}")
        key, kind = CHECKS[name]
        value = metrics.get(key)
        ok = value is not None and (value <= limit if kind == "max" else value >= limit)
        results.append(Result(name, limit, value, ok))
    return results


def record(run_id: str, task: dict, passed: bool, path: Path = PROGRESS) -> str:
    if task.get("review") == "human" and passed:
        status = "awaiting human review"
    else:
        status = "passed" if passed else "failed"
    line = f"- {date.today().isoformat()} {task['id']} run {run_id}: {status}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
    return status


def main(argv: list[str] | None = None) -> int:
    import sys

    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: python -m grader runs/<run-id>")
        return 2
    run = Path(args[0])
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    defaults, tasks = load_curriculum()
    task = tasks.get(metrics.get("task_id", ""))
    if task is None:
        print(f"Unknown task_id {metrics.get('task_id')!r}. Known: {', '.join(tasks)}")
        return 2
    results = grade(metrics, task, defaults)
    for r in results:
        print(r.line())
    passed = all(r.passed for r in results)
    status = record(run.name, task, passed)
    print(f"\n{task['id']}: {status.upper()}")
    if not (run / "screenshots").is_dir():
        print("Note: no screenshots/ folder; do the visual checklist before calling this done.")
    return 0 if passed else 1
