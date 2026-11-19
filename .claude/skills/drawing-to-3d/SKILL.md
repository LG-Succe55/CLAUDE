---
name: drawing-to-3d
description: Turns a hand drawing into a 3D object and a video that runs sketch-to-3d the other way round. It starts on the person's own drawing, finds the object in it (circle and box guides, then the 3D model's outlines traced over the drawing), takes over with marker and colour, wipes to the real 3D render and turns it all the way round. Makes the 3D model from the drawing with an image-to-3D tool (Higgsfield's generate_3d when connected), or uses a model the person already has. Use it whenever someone wants a sketch, doodle, napkin drawing or concept drawing turned into 3D, a "sketch becomes real" or drawing-to-render reveal, or asks for sketch-to-3d in reverse, even if they don't name this skill.
---

# drawing-to-3d

The reverse of [sketch-to-3d](https://github.com/dannystuart/sketch-to-3d). That skill starts from a 3D model and draws it. This one starts from a drawing and ends on the 3D model, using the same engine so the look matches.

The video (about 11.7 s with the defaults):

| Time (s) | What happens |
|---|---|
| 0–1 | The person's drawing alone, its paper cleaned to the sketch paper |
| 1–3.3 | Circle guides and the construction box are found on top of the drawing |
| 3–4.3 | The model's outlines trace over the drawing. The drawing sinks back to a faint underlay |
| 4.2–5.2 | Marker fill and hatched shadow cover the drawing, which is gone after this |
| 5.2–6.3 | Colour stage |
| 6.6–7.9 | Wipe to the real 3D render |
| 7.9–11.7 | The render turns 360°, then holds |

## Before you start

This skill runs on sketch-to-3d's engine. Check that it's installed:

```bash
ls ~/.claude/skills/sketch-to-3d/engine/stage.js ~/.claude/skills/sketch-to-3d/node_modules/three
```

If either is missing, install it (see `README.md`). The scripts also look in a `sketch-to-3d` folder beside this one, or in `$SKETCH_TO_3D`. It needs Node 18+ and ffmpeg.

## Steps

1. **Get the drawing.** A photo or scan of one object, about square on, on plain paper. Crop away the desk and other drawings. Read it yourself: say what object you see and roughly what angle it's drawn from.

2. **Get the 3D model.** Two ways:
   - **The person has one** (GLB, GLTF, OBJ, FBX, STL, PLY, USDZ, 3MF or DAE): use it.
   - **Make it with Higgsfield** (when its tools are connected). This costs credits, so:
     1. `models_explore` with `type: '3d'`. Use `image_to_3d` with texturing on.
     2. Preflight with `get_cost: true`. Tell the person the cost and wait for a yes.
     3. Upload the drawing: `media_upload`, `curl -X PUT` the file to `upload_url`, then `media_confirm`.
     4. `generate_3d`, then `jobs_wait`. Download the GLB into the work folder.

     **Line drawings often make thin, flat or lumpy models.** For a better model, offer this first: turn the drawing into a clean product image with `generate_image`. Ask for the same object, same angle, plain light background, no text, and use the drawing as the reference. Then convert that image. It's one more paid step, so ask first.
   - **No Higgsfield:** the person can use any image-to-3D tool (Meshy, Tripo, Rodin and others) and give you the GLB.

3. **Match the angle (seconds).**
   `node scripts/reveal.mjs <drawing> <model> --out <dir> --only stills --size <final size>`
   - Open `compare.png`: the drawing on the left, the model's sketch on the right, in the same frame.
   - Change `--az` (turn around), `--el` (look down) and `--rot` / `--rotX` (turn the model itself) until they match. Re-run each time: it takes seconds.
   - The `same shape on screen` check catches big mismatches. Small ones are fine: the drawing fades as the model's lines come in.
   - If the drawing sits too big, too small or off-centre against the model, use `--match` and `--nudge`.
4. **Show the person `compare.png` and the stills** (`drawing`, `found`, `sketch`, `colour`, `real`) before making the video.
5. **Video:** `node scripts/reveal.mjs <drawing> <model> --out <dir> --size <same size> [same angle options]`
6. **Check before handing over.**
   - Every check in `report.json` passes.
   - Look at `moments.png`.
   - Say what each file is for.

## Options

| Option | Use |
|---|---|
| `--size WxH` | Frame. Default `1080x1080`. `1080x1920` vertical, `1920x1080` wide |
| `--az 38 --el 24` | Camera angle in degrees (around, and up). Match the drawing's angle |
| `--rot`, `--rotX` | Turn the model itself. Generated models often face the wrong way or lie on their side |
| `--fit 1.35` | Framing. Smaller is closer |
| `--aim x,y,z` | Move the aim point, as a share of the object's size |
| `--match 1` | Size of the drawing against the model on screen |
| `--nudge x,y` | Move the drawing, as a share of the frame, e.g. `0.02,-0.01` |
| `--underlay 0.35` | How strongly the drawing shows while the model's lines trace over it. `0` hides it as the lines come in, `0.6` keeps it strong |
| `--intro 1` | Seconds on the drawing alone at the start |
| `--spin 360 --spin-time 3` | How far and how long the finished render turns. `--spin 0` for none |
| `--hold 0.8` | Seconds on the render at the very end |
| `--turn 0` | Camera turn during the draw-on, in degrees per second. Default 0, so the traced lines stay on the drawing |
| `--pal`, `--look`, `--no-colour`, `--no-circles`, `--drop`, `--tone`, `--studio` | As in sketch-to-3d |

## Outputs

| File | What it is |
|---|---|
| `<model>-drawing-to-3d.mp4` | The video |
| `compare.png` | The drawing and the model's sketch side by side, for matching the angle |
| `stills/drawing.png` | The cleaned drawing, as the video opens |
| `stills/found.png` | The model's lines traced over the drawing |
| `stills/sketch.png` | Finished marker sketch |
| `stills/colour.png` | Colour stage (unless `--no-colour`) |
| `stills/real.png` | The 3D render |
| `moments.png` | Ten frames on one sheet, for review |
| `report.json` | Model report, timings, warnings and checks |

Also hand over the GLB itself: it's the 3D model of their drawing.

## Problems

- **Scribbly lines:** sketch-to-3d warns "Very dense". Generated models are one dense piece, so only sharp folds get lines. Try `--no-circles` if circles land on odd parts. Generating from a clean product image (step 2) helps most.
- **Model doesn't look like the drawing:** that's the image-to-3D step, not this script. Make the clean product image first, or give the 3D tool more views of the object (`multi_image_to_3d` takes 2–4).
- **Drawing not found, or the whole page shows as marks:** crop tighter, or photograph it in even light without shadows.
- **The model faces away or lies down:** `--rot 180`, or `--rotX 90` / `--rotX -90`.

Don't edit sketch-to-3d's `engine/`. Its look rules (lines only build, every stage drawn on, one hatch direction) still hold. This skill only adds the drawing underneath and the turn at the end.
