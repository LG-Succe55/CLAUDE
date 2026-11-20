import json
from pathlib import Path

import grader

TASK = {"id": "T1", "level": 2, "checks": {"max_spans": 1, "max_deviation_mm": 1.0}}
DEFAULTS = {"max_gap_mm": 0.01, "max_angle_deg": 0.1}


def test_curriculum_loads_and_uses_known_checks():
    defaults, tasks = grader.load_curriculum()
    assert "L1.1-bezier-curve" in tasks and "L6.1-half-body" in tasks
    for t in tasks.values():
        for check in (t.get("checks") or {}):
            assert check in grader.CHECKS, (t["id"], check)
    assert all(k in grader.CHECKS for k in defaults)


def test_pass_and_fail():
    good = {"surface_count": 1, "max_spans": 1, "max_deviation_mm": 0.8, "max_gap_mm": 0.004, "max_angle_deg": 0.05}
    assert all(r.passed for r in grader.grade(good, TASK, DEFAULTS))
    bad = {**good, "max_deviation_mm": 1.4}
    failed = [r.check for r in grader.grade(bad, TASK, DEFAULTS) if not r.passed]
    assert failed == ["max_deviation_mm"]


def test_missing_metric_fails_and_curve_runs_skip_surface_defaults():
    curve_only = {"max_spans": 1, "max_deviation_mm": 0.2}
    results = grader.grade(curve_only, TASK, DEFAULTS)
    assert {r.check for r in results} == {"max_spans", "max_deviation_mm"}
    missing = grader.grade({"surface_count": 1, "max_spans": 1}, TASK, DEFAULTS)
    assert not all(r.passed for r in missing)


def test_human_review_and_progress_log(tmp_path: Path):
    log = tmp_path / "progress.md"
    assert grader.record("r1", {**TASK, "review": "human"}, True, log) == "awaiting human review"
    assert grader.record("r2", TASK, False, log) == "failed"
    assert "T1 run r2: failed" in log.read_text()


def test_cli(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr(grader, "PROGRESS", tmp_path / "progress.md")
    monkeypatch.setattr(grader.record, "__defaults__", (tmp_path / "progress.md",))
    run = tmp_path / "run1"
    run.mkdir()
    example = json.loads((grader.ROOT / "grader" / "metrics.example.json").read_text())
    (run / "metrics.json").write_text(json.dumps(example))
    assert grader.main([str(run)]) == 0
    assert "L2.1-roof-from-mesh: PASSED" in capsys.readouterr().out
