# Task 00 — Discover what you can do in Alias

Do this once, before any curriculum task. Don't build real geometry yet.

1. List every tool the Alias MCP server exposes, with its parameters.
2. In a new file in the `alias_trainer_sandbox` project, try the smallest version of each
   ability below and record **yes / no / partly**, with the exact tool name you used:
   - create a curve by points or CVs; change its degree and spans
   - read a curve's or surface's CVs, degree and spans
   - move CVs
   - create a surface: Skin, Square, Rail, Freeform Blend, Surface Fillet
   - Align (Object Edit > Align) with continuity and Explicit Control options
   - project / intersect to make curves-on-surface; trim; trim convert
   - evaluation: Surface Continuity values, curvature comb, deviation to a mesh,
     Check Model, minimum radius
   - screenshots of a viewport with a diagnostic shader (zebra / iso-angle)
   - open / save files; layers; symmetry
   - run an Alias Python plugin or script
3. For every **no**, check whether the Alias Python API can do it instead; note how.
4. Write everything to `memory/capabilities.md` using the table already in that file.
5. Write a short summary in `memory/progress.md` and stop. The person will review it.
