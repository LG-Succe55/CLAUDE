# drawing-to-3d

[sketch-to-3d](https://github.com/dannystuart/sketch-to-3d) the other way round: start with your own drawing, end on a turning 3D model.

Ask Claude in plain words: "Turn this drawing into 3D and make a square video for Instagram."

1. Claude turns your drawing into a 3D model with an image-to-3D tool (Higgsfield, when connected), or uses one you already have.
2. It lines the model up with your drawing and shows you a side-by-side check.
3. It makes the video: circle and box guides and the model's outlines trace over your drawing, then marker fill and colour cover it, then it wipes to the real render and turns all the way round.

## Install

You need Claude Code, Node 18 or newer, git and ffmpeg. This skill runs on sketch-to-3d's engine, so install that first:

```bash
git clone https://github.com/dannystuart/sketch-to-3d.git ~/.claude/skills/sketch-to-3d
cd ~/.claude/skills/sketch-to-3d
pnpm install        # or: npm install
npx playwright install chromium
```

Then copy this folder to `~/.claude/skills/drawing-to-3d`. If you work inside this repository, Claude Code picks it up from `.claude/skills/` anyway.

If sketch-to-3d lives somewhere else, set `SKETCH_TO_3D` to its folder.

## Run it yourself

```bash
node scripts/reveal.mjs drawing.jpg model.glb --out out --only stills   # quick check: open out/compare.png
node scripts/reveal.mjs drawing.jpg model.glb --out out --az 30 --el 20 # the video
```

Every option is listed in `SKILL.md`.

## Credit

The drawing engine is sketch-to-3d by Danny Stuart, under the MIT licence. This skill doesn't copy it. It loads the engine from your installed copy.
