#!/usr/bin/env node
// Drawing → 3D: starts on the user's own drawing, finds the 3D object inside it (circles, box, outlines traced over the
// drawing), takes over with marker and colour, wipes to the real render and turns it round.
//   node reveal.mjs <drawing.png|jpg> <model file> --out <dir> [options]
// Options:
//   --size 1080x1080   any frame size     --fps 60
//   --look marker|classic                 --pal whitePaper|redSheet|pencil|blueprint
//   --az 38 --el 24 --rot 0 --rotX 0 --fit 1.35 --aim x,y,z    camera and object, as in sketch-to-3d
//   --turn 0           camera turn during the draw-on, deg/s (default 0, so the traced lines stay on the drawing)
//   --no-colour  --no-circles  --drop a,b  --tone name=skip     as in sketch-to-3d
//   --intro 1          seconds on the drawing alone at the start
//   --underlay 0.35    how strong the drawing stays while the model's lines trace over it (0..1)
//   --match 1          size of the drawing against the model on screen (1 = same size)
//   --nudge x,y        move the drawing, as a share of the frame (e.g. 0.02,-0.01)
//   --spin 360         degrees the finished render turns at the end (0 = none)    --spin-time 3
//   --studio '#hex'    the render's background     --hold 0.8   seconds on the final render after the turn
//   --only stills      stills, compare sheet and report only (fast; use it to match the angle first)
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

// the sketch-to-3d skill this one builds on: its engine, bundler, three.js and browser
const HERE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const candidates = [process.env.SKETCH_TO_3D, path.join(HERE, '..', 'sketch-to-3d'), path.join(os.homedir(), '.claude/skills/sketch-to-3d')].filter(Boolean);
const BASE = candidates.find((d) => fs.existsSync(path.join(d, 'engine/stage.js')));
if (!BASE) {
  console.error('sketch-to-3d is not installed. Install it first (see this skill\'s README), or set SKETCH_TO_3D to its folder.\nLooked in:\n  ' + candidates.join('\n  '));
  process.exit(1);
}
if (!fs.existsSync(path.join(BASE, 'node_modules/three'))) {
  console.error(`sketch-to-3d is at ${BASE} but its packages are missing. Run: cd ${BASE} && pnpm install (or npm install)`);
  process.exit(1);
}
const {bundle} = await import(path.join(BASE, 'scripts/lib.mjs'));

const args = process.argv.slice(2);
const flag = (k) => args.includes(`--${k}`);
const opt = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i === -1 ? d : args[i + 1];
};
const VALUED = ['size', 'fps', 'look', 'pal', 'az', 'el', 'rot', 'rotX', 'fit', 'turn', 'aim', 'drop', 'tone', 'only', 'out', 'intro', 'underlay', 'match', 'nudge', 'spin', 'spin-time', 'studio', 'hold'];
const pos = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && VALUED.includes(args[i - 1].slice(2))));
const [drawing, model] = pos;
if (!drawing || !model) {
  console.error('usage: reveal.mjs <drawing image> <model file> --out <dir> [options]');
  process.exit(1);
}
for (const f of [drawing, model]) if (!fs.existsSync(f)) (console.error(`not found: ${f}`), process.exit(1));

const out = path.resolve(opt('out', 'drawing-to-3d-out'));
const [W, H] = opt('size', '1080x1080').split('x').map(Number);
const fps = Number(opt('fps', 60));
const num = (k, d) => (opt(k) === undefined ? d : Number(opt(k)));
const list = (k) => (opt(k) ? opt(k).split(',').map((s) => s.trim()) : undefined);
const engineOpts = {
  look: opt('look'), pal: opt('pal'), az: num('az'), el: num('el'), rot: num('rot'), rotX: num('rotX'), fit: num('fit'), turn: num('turn', 0),
  look3: opt('aim') ? opt('aim').split(',').map(Number) : undefined,
  colour: flag('no-colour') ? false : undefined, circles: flag('no-circles') ? false : undefined, drop: list('drop'),
  tone: list('tone') ? Object.fromEntries(list('tone').map((t) => t.split('='))) : undefined,
  alpha: true, hold: 0, stopAt: 'render',
};
for (const k of Object.keys(engineOpts)) if (engineOpts[k] === undefined) delete engineOpts[k];
const timing = {
  intro: num('intro', 1), underlay: num('underlay', 0.35), match: num('match', 1),
  nudge: opt('nudge') ? opt('nudge').split(',').map(Number) : [0, 0],
  spin: num('spin', 360), spinTime: num('spin-time', 3), hold: num('hold', 0.8), studio: opt('studio', '#efede8'),
};
const name = path.basename(model).replace(/\.[^.]+$/, '');
fs.mkdirSync(path.join(out, 'stills'), {recursive: true});

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'drawing3d-'));
const entry = path.join(tmp, 'entry.js');
fs.writeFileSync(
  entry,
  `import {createStage, loadModel, inspect} from ${JSON.stringify(path.join(BASE, 'engine/stage.js'))};
const cfg = window.__CFG;
const {W, H, tm} = cfg;
document.body.style.margin = '0';
const view = document.createElement('canvas');
view.width = W; view.height = H;
document.body.appendChild(view);
const cx = view.getContext('2d');
const gl = document.createElement('canvas');
let report;
const object = async (THREE, renderer) => {
  const o = await loadModel('/model/' + ${JSON.stringify(path.basename(model))}, renderer, '/decoders/');
  report = inspect(o, cfg.opts);
  return o;
};
const st = await createStage({canvas: gl, object, width: W, height: H, opts: cfg.opts});
const paper = st.ground;

// the drawing: paper turned clear, the marks kept in their own colour
const img = new Image();
img.src = '/drawing';
await img.decode();
const iw = img.naturalWidth, ih = img.naturalHeight;
const ink = document.createElement('canvas');
ink.width = iw; ink.height = ih;
const ix = ink.getContext('2d', {willReadFrequently: true});
ix.drawImage(img, 0, 0);
const id = ix.getImageData(0, 0, iw, ih);
const d = id.data;
const lum = new Float32Array(iw * ih);
for (let i = 0; i < lum.length; i++) lum[i] = (0.2126 * d[i * 4] + 0.7152 * d[i * 4 + 1] + 0.0722 * d[i * 4 + 2]) * (d[i * 4 + 3] / 255) + 255 * (1 - d[i * 4 + 3] / 255);
const sorted = Float32Array.from(lum).sort();
const P = (q) => sorted[Math.min(sorted.length - 1, Math.floor(q * sorted.length))];
const paperL = P(0.6), darkL = Math.min(P(0.005), paperL - 40);
// paper level from the bright majority of the page, ink level from the darkest marks
const cols = new Uint32Array(iw), rows = new Uint32Array(ih);
let marked = 0;
for (let y = 0; y < ih; y++)
  for (let x = 0; x < iw; x++) {
    const i = y * iw + x;
    let a = (paperL - 12 - lum[i]) / (paperL - 12 - darkL);
    a = Math.max(0, Math.min(1, a * 1.25));
    a = a < 0.1 ? 0 : a;
    d[i * 4 + 3] = Math.round(a * 255);
    if (a > 0.35) cols[x]++, rows[y]++, marked++;
  }
ix.putImageData(id, 0, 0);
// where the marks are, trimming stray specks at the edges
const span = (arr) => {
  const tot = arr.reduce((s, v) => s + v, 0), cut = tot * 0.003;
  let a = 0, b = arr.length - 1, s = 0;
  while (a < b && (s += arr[a]) < cut) a++;
  s = 0;
  while (b > a && (s += arr[b]) < cut) b--;
  return [a, b + 1];
};
const [dx0, dx1] = span(cols), [dy0, dy1] = span(rows);

// put the drawing where the model sits on screen
const B = st.bounds();
const bw = B.x1 - B.x0, bh = B.y1 - B.y0, dw = dx1 - dx0, dh = dy1 - dy0;
const s = Math.min(bw / dw, bh / dh) * tm.match;
const ox = (B.x0 + B.x1) / 2 - ((dx0 + dx1) / 2) * s + tm.nudge[0] * W;
const oy = (B.y0 + B.y1) / 2 - ((dy0 + dy1) / 2) * s + tm.nudge[1] * H;

// when the engine's stages finish (seconds of its own timeline)
const done = (k) => {
  for (let t = 0; t <= st.duration; t += 0.01) if (st.stagesAt(t)[k] >= 0.999) return t;
  return st.duration;
};
const T = {lines: done('lines'), ink: done('ink'), colour: cfg.opts.colour === false ? null : done('colour'), engine: st.duration};
const total = tm.intro + st.duration + (tm.spin ? tm.spinTime : 0) + tm.hold;
const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

// one picture: paper, the drawing underneath, the engine on top (its paper is clear), studio grey behind the render
const compose = (u, wipeX) => {
  cx.globalAlpha = 1;
  cx.globalCompositeOperation = 'source-over';
  cx.fillStyle = paper;
  cx.fillRect(0, 0, W, H);
  if (wipeX > 0) (cx.fillStyle = tm.studio), cx.fillRect(0, 0, wipeX, H);
  if (u > 0.001) {
    cx.globalAlpha = u;
    cx.globalCompositeOperation = 'multiply';
    cx.drawImage(ink, ox, oy, iw * s, ih * s);
    cx.globalAlpha = 1;
    cx.globalCompositeOperation = 'source-over';
  }
  cx.drawImage(gl, 0, 0);
};
const blank = () => {
  st.renderer.setClearColor(0x000000, 0);
  st.renderer.clear();
};
// video time → picture.
// The drawing stays full strength while the circles and box are found on it, sinks to the underlay level while the
// model's outlines trace over it, and is gone once the marker fill has covered it.
window.FRAME = (t) => {
  if (t < tm.intro) {
    blank();
    compose(1, 0);
  } else if (t < tm.intro + st.duration) {
    const te = t - tm.intro;
    st.frame(te);
    const sg = st.stagesAt(te);
    const u = (1 - (1 - tm.underlay) * sg.lines) * (1 - sg.ink);
    compose(u, Math.round(sg.wipe * W));
  } else {
    const ts = t - tm.intro - st.duration;
    st.frame(st.duration, {spin: tm.spin ? tm.spin * ease(ts / tm.spinTime) : 0});
    compose(0, W);
  }
  return view.toDataURL('image/png');
};
const at = (te) => window.FRAME(tm.intro + te);
window.STILLS = () => ({
  drawing: window.FRAME(0),
  found: at((T.lines + T.ink) / 2 - 0.5), // the model's lines over the drawing
  sketch: at(T.ink + 0.05),
  ...(T.colour ? {colour: at(T.colour + 0.05)} : {}),
  real: at(st.duration),
});
// for the compare sheet: the drawing alone, and the model's finished sketch alone, in the same frame
window.COMPARE = () => {
  blank();
  compose(1, 0);
  const a = view.toDataURL('image/png');
  st.frame(T.ink + 0.05);
  compose(0, 0);
  return [a, view.toDataURL('image/png')];
};
window.INFO = () => ({report, sketch: st.info, bounds: B, drawingBox: [dx0, dy0, dx1, dy1], image: [iw, ih], marked: marked / (iw * ih), place: {s, ox, oy}, T, total});
window.READY = true;
`,
);
const js = await bundle(entry);
const modelDir = path.dirname(path.resolve(model));
const decoders = path.join(BASE, 'node_modules/three/examples/jsm/libs');
const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  let file = null;
  if (u === '/' || u === '/index.html') return res.end('<!doctype html><html><body><script type="module" src="/app.js"></script></body></html>');
  if (u === '/app.js') return res.writeHead(200, {'content-type': 'text/javascript'}), res.end(js);
  if (u === '/drawing') file = path.resolve(drawing);
  if (u.startsWith('/model/')) file = path.join(modelDir, u.slice(7));
  if (u.startsWith('/decoders/')) file = path.join(decoders, u.slice(10));
  if (!file || !fs.existsSync(file)) return res.writeHead(404), res.end();
  const type = {'.js': 'text/javascript', '.wasm': 'application/wasm', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}[path.extname(file).toLowerCase()] ?? 'application/octet-stream';
  res.writeHead(200, {'content-type': type});
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/`;

const {chromium} = (await import(path.join(BASE, 'node_modules/playwright/index.mjs'))).default;
const launch = {args: [...(process.platform === 'darwin' ? ['--use-angle=metal'] : []), '--ignore-gpu-blocklist', '--enable-gpu-rasterization', '--enable-webgl']};
if (process.env.CHROMIUM_PATH) launch.executablePath = process.env.CHROMIUM_PATH;
const browser = await chromium.launch(launch);
const page = await browser.newPage({viewport: {width: W, height: H}, deviceScaleFactor: 1});
page.on('pageerror', (e) => console.error('[page error]', e.message));
await page.addInitScript((c) => (window.__CFG = c), {W, H, opts: engineOpts, tm: timing});
await page.goto(url);
await page.waitForFunction(() => window.READY, null, {timeout: 120000});
const info = await page.evaluate(() => window.INFO());
const png = (d) => Buffer.from(d.split(',')[1], 'base64');

const stills = await page.evaluate(() => window.STILLS());
for (const [k, v] of Object.entries(stills)) fs.writeFileSync(path.join(out, 'stills', `${k}.png`), png(v));
const [ca, cb] = await page.evaluate(() => window.COMPARE());
fs.writeFileSync(path.join(tmp, 'ca.png'), png(ca));
fs.writeFileSync(path.join(tmp, 'cb.png'), png(cb));
const run = (a) => new Promise((r) => spawn('ffmpeg', a, {stdio: 'inherit'}).on('close', r));
const ch = 540;
const cw = Math.round((ch * W) / H);
await run(['-v', 'error', '-y', '-i', path.join(tmp, 'ca.png'), '-i', path.join(tmp, 'cb.png'), '-filter_complex', `[0]scale=${cw}:${ch}[a];[1]scale=${cw}:${ch}[b];[a][b]hstack=2`, '-frames:v', '1', path.join(out, 'compare.png')]);

// checks
const checks = [];
const b = info.bounds;
const share = Math.max(b.core[2] - b.core[0], b.core[3] - b.core[1]) / Math.min(b.W, b.H);
checks.push({check: 'object fills the frame', pass: share >= 0.495, detail: `its longest side is ${Math.round(share * 100)}% of the frame's short side (needs 50% or more; closer with a lower --fit)`});
checks.push({check: 'object inside the frame', pass: b.x0 > -0.02 * b.W && b.x1 < 1.02 * b.W && b.y0 > -0.02 * b.H && b.y1 < 1.02 * b.H, detail: `box ${[b.x0, b.y0, b.x1, b.y1].map(Math.round).join(',')} in ${b.W}x${b.H}`});
checks.push({check: 'drawing found on the page', pass: info.marked > 0.002 && info.marked < 0.45, detail: `${(info.marked * 100).toFixed(1)}% of the image is marks (expected 0.2% to 45%; outside that, crop the photo or light it more evenly)`});
const [x0, y0, x1, y1] = info.drawingBox;
const ra = (x1 - x0) / (y1 - y0);
const rb = (b.x1 - b.x0) / (b.y1 - b.y0);
const off = Math.abs(Math.log(ra / rb));
checks.push({check: 'drawing and model have the same shape on screen', pass: off < 0.2, detail: `drawing ${ra.toFixed(2)} wide per 1 tall, model ${rb.toFixed(2)} (more than about 20% apart: change --az, --el or --rot until compare.png matches)`});

if (opt('only') !== 'stills') {
  const n = Math.round(info.total * fps);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-movflags', '+faststart', path.join(out, `${name}-drawing-to-3d.mp4`)], {stdio: ['pipe', 'inherit', 'inherit']});
  const momentsDir = path.join(tmp, 'moments');
  fs.mkdirSync(momentsDir);
  const momentAt = [...Array(10).keys()].map((k) => Math.round(((k + 0.5) / 10) * (n - 1)));
  for (let i = 0; i < n; i++) {
    const buf = png(await page.evaluate((t) => window.FRAME(t), i / fps));
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
    const k = momentAt.indexOf(i);
    if (k !== -1) fs.writeFileSync(path.join(momentsDir, `m_${String(k).padStart(2, '0')}.png`), buf);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await run(['-v', 'error', '-y', '-framerate', '1', '-i', path.join(momentsDir, 'm_%02d.png'), '-vf', `scale=${Math.round((360 * W) / H)}:360,tile=5x2`, '-frames:v', '1', path.join(out, 'moments.png')]);
  console.log(`video → ${path.join(out, `${name}-drawing-to-3d.mp4`)} (${n} frames, ${info.total.toFixed(1)} s)`);
}

const {cal, ...sketchInfo} = info.sketch ?? {};
const report = {drawing: path.basename(drawing), object: path.basename(model), size: `${W}x${H}`, settings: {...engineOpts, ...timing}, timeline: {...info.T, intro: timing.intro, total: info.total}, model: info.report, sketch: sketchInfo, checks};
fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
await browser.close();
server.close();
fs.rmSync(tmp, {recursive: true, force: true});
console.log(opt('only') === 'stills' ? `stills, compare sheet and report → ${out}` : `stills, compare sheet, moments and report → ${out}`);
for (const w of info.report?.warn ?? []) console.log(`warning: ${w}`);
for (const c of checks) console.log(`${c.pass ? 'ok  ' : 'FAIL'} ${c.check}: ${c.detail}`);
