# Vehicle Surfacing Playbook

Turns CATIA 3DEXPERIENCE and Autodesk Alias tutorials into a searchable library of
step-by-step workflows, plus a chat "coach" that answers from that library and links
back to the exact moment in each video.

## What it does

1. **Reads a tutorial.** For a web page such as Autodesk Learn, it uses the embedded
   video's captions if it can find them, otherwise the page's written steps. For a YouTube link it fetches the published captions (it never
   downloads the video). For a course or your own recording, give it the caption file
   (`.srt`, `.vtt`, or `.txt`). If you have the rights to a video file, `--video` also
   samples still frames so Claude can see menus and dialogs.
2. **Extracts workflows.** Claude pulls out every task shown: exact command names, where
   to find them, settings, why, tips, pitfalls, and a timestamp for each step.
3. **Stores them** in a local `playbook.db` file with full-text search.
4. **Answers questions** using the most relevant workflows, citing them as `[1]`, `[2]`.

## Setup (Windows)

```powershell
cd cad-playbook
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # from console.anthropic.com
```

## Use

```powershell
# Add tutorials: one at a time, or a list file (one link/path per line, # for comments)
python -m playbook add https://www.youtube.com/watch?v=VIDEO_ID
python -m playbook add --list links.txt

# Tutorial web pages, e.g. Autodesk Learn. If the site blocks the request,
# save the page from your browser (Ctrl+S) and add the .html file instead.
python -m playbook add https://www.autodesk.com/learn/ondemand/tutorial/create-objects-in-alias
python -m playbook add "Create Objects in Alias.html"

# A course or screen recording you're licensed to use: captions + frames
python -m playbook add lesson3.srt --video lesson3.mp4 --title "Alias: A-pillar blend"

python -m playbook list
python -m playbook search "G2 blend fender" --software alias     # free, no AI call
python -m playbook ask "How do I get a G2 transition between hood and fender in Alias?"
python -m playbook ask --software catia                           # chat mode
python -m playbook export playbook.md                             # whole playbook as a document
```

## Costs and notes

- Uses Claude Opus 5.5. Rough estimate: 10–50 cents to extract an hour-long tutorial,
  more with `--video` frames. `search` is free; each `ask` is a few cents.
- Auto-generated captions mishear CAD terms. The prompt corrects obvious ones, but check
  important settings against the video (every step links to its timestamp).
- Videos without captions can't be read from a link. Use a caption file instead.
- YouTube may block caption requests from cloud servers, so run this on your own PC.

## Tests

```powershell
pip install pytest
python -m pytest tests
```
