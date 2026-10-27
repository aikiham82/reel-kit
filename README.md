# reel-kit

Vertical reels (1080x1920) from your own footage, made by Claude: it looks through the videos, picks and cuts the clips, and renders the reel with Remotion.

- `tools/reel.py`: `sheet` (contact sheets to browse footage), `cut` (vertical clips, crop follows the movement), `render` (reel + loudness normalization), `skill-zip` (skill for claude.ai).
- `src/Reel.tsx`: one Remotion template driven by `reels/<name>.json` (clips, fade or cut, music, intro cards, outro).
- `skill/reels`: the Claude skill with the workflow and one style per topic (`styles/yoga.md`, `styles/aikido.md`).

Setup on Windows with Claude Desktop: [docs/guia-windows.md](docs/guia-windows.md) (Spanish).

## Manual use

```sh
npm install
pip install numpy
python tools/reel.py sheet path/to/video.mp4 --every 10
python tools/reel.py cut out/my-reel-clips.tsv
python tools/reel.py render my-reel
```

`reels/example.json` expects `public/clips/demo-1.mp4`, `public/clips/demo-2.mp4` and `public/music/demo.mp3`; replace them with your own.

Tests: `python tools/test_reel.py`.
