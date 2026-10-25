"""Renders final files from text. Only generated text on flat colour: no third-party media, so rights-safe."""
import subprocess, shutil, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
NAVY, TEAL, WHITE, MUTED = (11, 18, 38), (45, 212, 191), (245, 247, 252), (150, 163, 190)
FOOTER = "Independent creator test. Not an official IncuBrix account."

class RenderError(Exception):
    pass

def font(size, bold=True):
    return ImageFont.truetype(str(FONTS / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)

def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_block(im, text, box, size, color=WHITE, bold=True, align="left"):
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = box
    while size > 24:
        f = font(size, bold); lines = wrap(d, text, f, x1 - x0)
        lh = int(size * 1.28)
        if lh * len(lines) <= (y1 - y0): break
        size -= 4
    total = lh * len(lines); y = y0 + ((y1 - y0) - total) // 2
    for ln in lines:
        tw = d.textlength(ln, font=f)
        x = x0 if align == "left" else x0 + (x1 - x0 - tw) / 2
        d.text((x, y), ln, font=f, fill=color); y += lh

def frame(text, size, idx, total, kind):
    w, h = size
    im = Image.new("RGB", size, NAVY); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 14], fill=TEAL)
    m = 90
    if kind == "video":  # keep inside platform UI safe zone
        draw_block(im, text, (m, 330, w - m, 1450), 92)
        d.rectangle([m, 1540, m + int((w - 2 * m) * (idx + 1) / total), 1552], fill=TEAL)
        d.rectangle([m + int((w - 2 * m) * (idx + 1) / total), 1540, w - m, 1552], fill=(40, 52, 84))
        d.text((m, 1580), f"{idx + 1}/{total}", font=font(34, False), fill=MUTED)
        d.text((m, 1650), FOOTER, font=font(28, False), fill=MUTED)
    else:
        draw_block(im, text, (m, 200, w - m, h - 260), 74 if idx else 84)
        d.text((m, h - 150), FOOTER, font=font(26, False), fill=MUTED)
        d.text((w - m - 90, h - 150), f"{idx + 1}/{total}", font=font(30, False), fill=MUTED)
        d.rectangle([m, h - 190, m + int((w - 2 * m) * (idx + 1) / total), h - 182], fill=TEAL)
    return im

def beat_seconds(text):
    return round(min(5.0, max(2.6, 1.4 + 0.42 * len(text.split()))), 1)

def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def render_video(a, outdir, simulate_failure=False):
    if simulate_failure: raise RenderError("simulated render failure")
    if not shutil.which("ffmpeg"): raise RenderError("ffmpeg not found")
    outdir = Path(outdir); tmp = outdir / f".frames_{a['asset_id']}"; tmp.mkdir(parents=True, exist_ok=True)
    beats = a["beats"]; secs = [beat_seconds(b) for b in beats]; a["beat_seconds"] = secs
    lst = []
    for i, b in enumerate(beats):
        p = tmp / f"f{i:02}.png"; frame(b, (1080, 1920), i, len(beats), "video").save(p)
        lst.append(f"file '{p.name}'\nduration {secs[i]}")
    lst.append(f"file '{(tmp / f'f{len(beats)-1:02}.png').name}'")
    (tmp / "list.txt").write_text("\n".join(lst))
    mp4 = outdir / f"{a['asset_id']}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-r", "30", "-pix_fmt", "yuv420p",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-movflags", "+faststart", str(mp4)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RenderError(r.stderr[-300:])
    t = 0.0; srt = []
    for i, b in enumerate(beats):
        srt.append(f"{i+1}\n{srt_time(t)} --> {srt_time(t+secs[i])}\n{b}\n"); t += secs[i]
    (outdir / f"{a['asset_id']}.srt").write_text("\n".join(srt), encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
    return [mp4]

def render_carousel(a, outdir, simulate_failure=False):
    if simulate_failure: raise RenderError("simulated render failure")
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    s = a["slides"]; imgs = []
    for i, t in enumerate(s):
        im = frame(t, (1080, 1350), i, len(s), "slide"); p = outdir / f"{a['asset_id']}_slide{i+1:02}.png"; im.save(p); imgs.append(im)
    pdf = outdir / f"{a['asset_id']}.pdf"
    imgs[0].save(pdf, save_all=True, append_images=imgs[1:], resolution=100.0)
    return [pdf]

def render_graphic(a, outdir, simulate_failure=False):
    if simulate_failure: raise RenderError("simulated render failure")
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    text = "\n".join(a["slides"]) if a["slides"] else a["hook"]
    im = frame(" ".join(text.split("\n")), (1080, 1350), 0, 1, "slide"); p = outdir / f"{a['asset_id']}.png"; im.save(p)
    return [p]

def render_text(a, outdir, simulate_failure=False):
    if simulate_failure: raise RenderError("simulated render failure")
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    p = outdir / f"{a['asset_id']}.txt"; p.write_text(a["final_caption"], encoding="utf-8"); return [p]

RENDERERS = {"Short video": render_video, "Carousel": render_carousel, "Graphic": render_graphic, "Text post": render_text}

def render_asset(a, outdir, simulate_failure=False):
    return RENDERERS[a["format"]](a, outdir, simulate_failure)
