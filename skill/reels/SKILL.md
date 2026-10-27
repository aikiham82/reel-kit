---
name: reels
description: Make vertical social media reels (Instagram, TikTok, Shorts) from the user's own footage with the reel-kit project (Remotion + ffmpeg). Use when the user asks to make, edit, re-cut or render a reel or short promo video from their videos, for any topic (yoga, aikido, classes, events).
---

# Reels with reel-kit

You edit real footage on the user's computer. You need a tool that runs shell commands and reads files there (for example the Desktop Commander extension in Claude Desktop, or Claude Code). Without one, say so and point the user to `docs/guia-windows.md`. Do not try to do this with uploaded files in the chat sandbox.

## Setup

1. Find the `reel-kit` folder (ask the user once if you can't find it). Run every command from there.
2. First time: `npm install` and `pip install numpy`. Check that `ffmpeg -version` and `node -v` work.
3. Pick the style file in this skill's `styles/` folder that matches the topic (`yoga.md`, `aikido.md`). If none fits, start from `yoga.md` and agree the differences with the user. Ask the user for the facts the reel shows (name, dates, place, URL); never invent them.

## Workflow

1. **Look at the footage.** For each long video: `python tools/reel.py sheet <video> --every 10`. Read the sheet images in `out/sheets/` to find the good moments. Go finer (`--every 2`) on a promising part before choosing exact times.
2. **Choose clips.** Write `out/<name>-clips.tsv`, tab separated, one clip per line: `id<TAB>source path<TAB>start<TAB>end` (seconds or mm:ss). Follow the style file for clip length and what each clip must contain.
3. **Cut.** `python tools/reel.py cut out/<name>-clips.tsv`. Each clip becomes vertical 1080x1920 in `public/clips/`; landscape footage is cropped following the movement (`--frame center` for a fixed centre crop, `--frame keep` to scale without tracking). Add `--gpu` only if the PC has an NVIDIA card. The command prints one JSON line per clip with its exact length.
4. **Describe the reel.** Create `reels/<name>.json` (see the format below), pasting the clip lines from step 3.
5. **Render.** `python tools/reel.py render <name>` writes `out/<name>.mp4` with loudness normalized for social media.
6. **Check.** Pull 3-4 frames (`ffmpeg -i out/<name>.mp4 -vf "fps=1/4,scale=360:-2,tile=4x1" -frames:v 1 out/<name>-check.jpg`) and look at them before telling the user it is done. Tell the user the file path and the length.

Changes the user asks for afterwards ("remove the slow part", "no music"): edit the TSV or the JSON and run only the steps after it. Keep earlier versions by using a new name (`<name>-v2`) so the user can go back.

## reels/<name>.json

```json
{
  "clips": [{ "file": "clips/a1.mp4", "seconds": 6.5 }],
  "transition": "fade",
  "fadeSeconds": 0.5,
  "clipVolume": 0,
  "music": { "file": "music/calm.mp3", "volume": 0.5 },
  "accent": "#7FA88B",
  "intro": [{ "kicker": "Yoga · Murcia", "title": "Clase abierta", "sub": "Sábado 10:00" }],
  "outro": { "text": "Reserva tu plaza", "url": "example.com", "image": "poster.jpg", "seconds": 3.5 }
}
```

- Only `clips` is required. Paths are relative to `public/`; put music in `public/music/` and images in `public/`.
- `transition`: `"cut"` (hard cuts, default) or `"fade"`.
- `clipVolume`: 1 keeps the original sound, 0 mutes it. Music fades out on its own at the end.
- `intro`: text cards, 2.5 s each, shown over the first clips.
- `outro`: closing screen with text, URL and/or an image (poster, logo).
- Only use music the user provides or confirms they have the rights to.

## Rules

- Video work is heavy. Run one ffmpeg or render job at a time; the tools already run at low priority.
- Use `npm run studio` only if the user wants to preview and tweak by hand.
- To change the look itself (fonts, layout), edit `src/Reel.tsx`; Remotion's official skill (`npx skills add remotion-dev/skills`) helps there.
