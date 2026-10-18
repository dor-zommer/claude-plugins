# -*- coding: utf-8 -*-
"""שקף וידאו לקרוסלה: חלון מקליפ -> MP4 בגודל שאר השקפים, עם לוגו וקרדיט.

  python3 make_video_slide.py IN.mp4 OUT.mp4 --start 12.5 --dur 20 \
      --credit "תיעוד: בצלם" [--mode fill|fit] [--bg ink|ivory] [--mute] \
      [--logo bottom|top|none] [--strip]

- fill: ממלא את הפריים וחותך עודפים (ברירת מחדל). fit: כל הפריים נראה, והשאר רקע
  דיו או שנהב (לצילומי מסך מוקלטים, מסמכים, וידאו אנכי צר).
- הלוגו הריבועי נרסטר מה-SVG של ה-DS (אלפא נשמר, צובעים רק RGB), לבן על fill/דיו,
  דיו על שנהב. הקרדיט ב-Graphik HLAR עם libraqm (עברית מימין לשמאל).
- פלט: OUT.mp4 (H.264 yuv420p, 30fps, faststart) + OUT.poster.jpg לשקף הממלא את
  מקומו ב-Figma.
דורש: ffmpeg, PIL עם raqm, cairosvg, numpy.
"""
import argparse, os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, features

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.normpath(f"{HERE}/../../../design-system")
LOGO_SVG = f"{DS}/assets/logo/logo-square-black.svg"
F_REG = f"{DS}/assets/fonts/graphikhlar-regular.otf"
INK, IVORY = (20, 20, 19), (250, 249, 245)
STRIP = [(217, 119, 87), (120, 140, 93), (142, 111, 168)]  # טרקוטה · מרווה · אברש (מימין לשמאל)


def logo(width, rgb, tmp):
    import cairosvg, numpy as np
    raw = f"{tmp}/logo.png"
    cairosvg.svg2png(url=LOGO_SVG, write_to=raw, output_width=width * 4)
    a = np.array(Image.open(raw).convert("RGBA"))
    a[..., 0], a[..., 1], a[..., 2] = rgb
    im = Image.fromarray(a)
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def overlay(a, W, H, tmp):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dark = a.mode == "fill" or a.bg == "ink"
    fg = (255, 255, 255) if dark else INK
    if a.mode == "fill":  # גרדיאנט דיו בתחתית - רק שקיפות דיו, לקריאות הקרדיט והלוגו
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        px = g.load()
        y0 = int(H * 0.80)
        for y in range(y0, H):
            al = int(200 * ((y - y0) / (H - y0)) ** 1.3)
            for x in range(W):
                px[x, y] = (*INK, al)
        img = Image.alpha_composite(img, g)
    d = ImageDraw.Draw(img)
    if a.logo != "none":
        lg = logo(48, fg, tmp)
        y = 48 if a.logo == "top" else H - 106
        img.alpha_composite(lg, ((W - lg.width) // 2, y))
    if a.credit:
        f = ImageFont.truetype(F_REG, 20, layout_engine=ImageFont.Layout.RAQM)
        col = (*fg, 150)
        d.text((24, H - 37), a.credit, font=f, fill=col, anchor="ls", direction="rtl")
    if a.strip:
        w3 = W // 3
        for i, c in enumerate(STRIP):  # טרקוטה מימין
            x1 = W - (i + 1) * w3 if i < 2 else 0
            d.rectangle([x1, H - 4, W - i * w3 - 1, H], fill=(*c, 255))
    p = f"{tmp}/overlay.png"
    img.save(p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float)
    ap.add_argument("--credit", default="")
    ap.add_argument("--mode", choices=["fill", "fit"], default="fill")
    ap.add_argument("--bg", choices=["ink", "ivory"], default="ink")
    ap.add_argument("--logo", choices=["bottom", "top", "none"], default="bottom")
    ap.add_argument("--strip", action="store_true"); ap.add_argument("--mute", action="store_true")
    ap.add_argument("--size", default="1080x1350")
    a = ap.parse_args()
    assert features.check("raqm"), "PIL בלי libraqm - הקרדיט העברי ייצא הפוך"
    W, H = map(int, a.size.split("x"))
    with tempfile.TemporaryDirectory() as tmp:
        ov = overlay(a, W, H, tmp)
        if a.mode == "fill":
            v = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
        else:
            bg = "0x141413" if a.bg == "ink" else "0xfaf9f5"
            v = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={bg}"
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(a.start)]
        if a.dur: cmd += ["-t", str(a.dur)]
        cmd += ["-i", a.inp, "-i", ov, "-filter_complex",
                f"[0:v]{v},setsar=1,fps=30[b];[b][1:v]overlay=0:0,format=yuv420p[v]",
                "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-movflags", "+faststart"]
        cmd += ["-an"] if a.mute else ["-map", "0:a?", "-c:a", "aac", "-b:a", "160k"]
        subprocess.run(cmd + [a.out], check=True, stdin=subprocess.DEVNULL)
    poster = os.path.splitext(a.out)[0] + ".poster.jpg"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", a.out, "-frames:v", "1", "-q:v", "2", poster],
                   check=True, stdin=subprocess.DEVNULL)
    print("wrote", a.out, "+", poster)


if __name__ == "__main__":
    main()
