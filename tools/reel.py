import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
OUT_W, OUT_H, OUT_FPS = 1080, 1920, 30
TRACK_W, TRACK_FPS = 240, 6


def lower_priority():
    if os.name == "posix":
        os.nice(19)


def run(cmd, **kwargs):
    flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
    return subprocess.run(cmd, check=True, creationflags=flags, **kwargs)


def parse_time(value):
    seconds = 0.0
    for part in value.split(":"):
        seconds = seconds * 60 + float(part)
    return seconds


def probe_size(path):
    info = json.loads(run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
         "-of", "json", str(path)], capture_output=True).stdout)["streams"][0]
    rotated = abs(int(next((d.get("rotation", 0) for d in info.get("side_data_list", [])), 0))) == 90
    return (info["height"], info["width"]) if rotated else (info["width"], info["height"])


def decode_args(gpu):
    return ["-hwaccel", "cuda"] if gpu else []


def encode_args(gpu):
    video = ["-c:v", "h264_nvenc", "-cq", "19", "-b:v", "0", "-preset", "p5"] if gpu else ["-c:v", "libx264", "-crf", "18", "-preset", "medium"]
    return [*video, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k"]


def track_centers(path, start, dur, width, height, gpu):
    import numpy as np

    track_h = round(TRACK_W * height / width / 2) * 2
    raw = run(["ffmpeg", "-v", "error", *decode_args(gpu), "-ss", str(start), "-t", str(dur), "-i", str(path),
               "-vf", f"scale={TRACK_W}:{track_h},fps={TRACK_FPS},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, track_h, TRACK_W).astype(np.int16)
    xs = np.arange(TRACK_W)
    centers = []
    for a, b in zip(frames[:-1], frames[1:]):
        motion = (np.abs(b - a)[track_h // 4:] > 18).sum(axis=0).astype(float)
        centers.append(np.nan if motion.sum() < 40 else xs[np.searchsorted(np.cumsum(motion) / motion.sum(), 0.5)] / TRACK_W)
    return smooth(np.array(centers))


def smooth(c):
    import numpy as np

    idx = np.arange(len(c))
    ok = ~np.isnan(c)
    if not ok.any():
        return np.full(max(len(c), 1), 0.5)
    c = np.interp(idx, idx[ok], c[ok])
    k = TRACK_FPS * 2 + 1
    padded = np.pad(c, k // 2, mode="edge")
    med = np.array([np.median(padded[i:i + k]) for i in range(len(c))])
    kernel = np.ones(TRACK_FPS) / TRACK_FPS
    return np.convolve(np.pad(med, TRACK_FPS // 2, mode="edge"), kernel, mode="valid")[:len(c)]


def x_expr(keys, src_w, crop_w):
    px = [(t, min(max(c * src_w - crop_w / 2, 0), src_w - crop_w)) for t, c in keys]
    expr = f"{px[-1][1]:.0f}"
    for (t0, x0), (t1, x1) in reversed(list(zip(px, px[1:]))):
        expr = f"if(lt(t,{t1:.2f}),{x0:.0f}+({x1 - x0:.0f})*(t-{t0:.2f})/{t1 - t0:.2f},{expr})"
    return expr


def vertical_filter(path, start, dur, frame, gpu):
    width, height = probe_size(path)
    fill = f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase:flags=lanczos,crop={OUT_W}:{OUT_H}"
    crop_w = round(height * OUT_W / OUT_H / 2) * 2
    if frame == "keep" or crop_w >= width:
        return f"{fill},fps={OUT_FPS}"
    if frame == "center":
        x = f"{(width - crop_w) / 2:.0f}"
    else:
        centers = track_centers(path, start, dur, width, height, gpu)
        step = TRACK_FPS // 2
        x = x_expr([(i / TRACK_FPS, centers[i]) for i in range(0, len(centers), step)], width, crop_w)
    return f"crop={crop_w}:{height}:'{x}':0,{fill},fps={OUT_FPS}"


def cmd_cut(args):
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for line in Path(args.list).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        clip_id, source, start, end = line.split("\t")
        start_s, end_s = parse_time(start), parse_time(end)
        dur = end_s - start_s
        vf = vertical_filter(source, start_s, dur, args.frame, args.gpu)
        run(["ffmpeg", "-v", "error", "-y", *decode_args(args.gpu), "-ss", str(start_s), "-t", f"{dur:.3f}", "-i", source,
             "-vf", vf, *encode_args(args.gpu), str(out_dir / f"{clip_id}.mp4")])
        print(json.dumps({"file": f"{out_dir.name}/{clip_id}.mp4", "seconds": round(dur, 2)}), flush=True)


def cmd_sheet(args):
    sheets = OUT / "sheets"
    sheets.mkdir(parents=True, exist_ok=True)
    stem = Path(args.video).stem
    run(["ffmpeg", "-v", "error", "-y", "-i", args.video, "-vf", f"fps=1/{args.every},scale=384:-2,tile=5x4",
         "-q:v", "4", str(sheets / f"{stem}-%03d.jpg")])
    print(f"{sheets}/{stem}-NNN.jpg: 20 frames per sheet, left to right, one every {args.every}s; sheet N, cell K = {args.every} * (20*(N-1) + K-1) seconds")


def cmd_render(args):
    OUT.mkdir(exist_ok=True)
    raw = OUT / f"{args.name}-raw.mp4"
    final = OUT / f"{args.name}.mp4"
    npx = shutil.which("npx") or "npx"
    run([npx, "remotion", "render", "Reel", str(raw), f"--props=reels/{args.name}.json", "--codec", "h264", "--crf", "18"], cwd=ROOT)
    run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-c:a", "aac", "-b:a", "192k", str(final)])
    raw.unlink()
    print(final)


def cmd_skill_zip(args):
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    print(shutil.make_archive(str(dist / "reels-skill"), "zip", ROOT / "skill", "reels"))


def main(argv=None):
    parser = argparse.ArgumentParser(prog="reel")
    sub = parser.add_subparsers(required=True)

    sheet = sub.add_parser("sheet", help="contact sheets to look through a long video")
    sheet.add_argument("video")
    sheet.add_argument("--every", type=float, default=10)
    sheet.set_defaults(func=cmd_sheet)

    cut = sub.add_parser("cut", help="cut clips listed in a TSV (id, source, start, end) to vertical 1080x1920")
    cut.add_argument("list")
    cut.add_argument("--out", default=str(ROOT / "public" / "clips"))
    cut.add_argument("--frame", choices=["track", "center", "keep"], default="track")
    cut.add_argument("--gpu", action="store_true", help="NVIDIA decode and encode")
    cut.set_defaults(func=cmd_cut)

    render = sub.add_parser("render", help="render reels/<name>.json to out/<name>.mp4 with normalized audio")
    render.add_argument("name")
    render.set_defaults(func=cmd_render)

    sub.add_parser("skill-zip", help="zip the skill for claude.ai").set_defaults(func=cmd_skill_zip)

    args = parser.parse_args(argv)
    lower_priority()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
