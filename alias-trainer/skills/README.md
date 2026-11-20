# Skills library

A skill is a sequence that worked in two different runs. Save each as either:

- `skills/<name>.py` — an Alias Python plugin/script, or
- `skills/<name>.md` — a step recipe of MCP tool calls with parameters.

Every skill starts with this header:

```
name: g2-transition-square
does: Square between two primaries and two blend curves, G2 on primary edges, single span
inputs: two primary surfaces, two boundary blend curves
proven in runs: 2026-12-03-a, 2026-12-04-b
limits: fails when edges are trimmed; use trim convert first
```

Index (keep updated):

| Skill | Does | Proven in |
|---|---|---|
