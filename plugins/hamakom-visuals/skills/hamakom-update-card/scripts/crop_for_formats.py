#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""חיתוך תמונת בסיס לשלושת פורמטי כרטיס העדכון, עם עיגון הנושא בשליש העליון.

למה לא לתת ל-Figma לחתוך: `scaleMode:"FILL"` חותך מהמרכז, ואז הנושא (רכבים,
אנשים, מבנה) נוחת באמצע הפריים — בדיוק איפה שגוש הטקסט יושב. חותכים מראש,
פר-פורמט, ומעלים שלוש תמונות נפרדות.

שימוש:
    python3 crop_for_formats.py base.png <YV> [outdir]

YV = מרכז הנושא בפיקסלים של **המקור** (נמדד בעין מפריים; לא אחוזים).
פלט: sq.png (1080x1080) · feed.png (1080x1350) · story.png (1080x1920)
"""
import sys, os
from PIL import Image

# name, out_w, out_h, crop_h, frac  ← frac = איפה הנושא בגובה הפריים המוגמר
SPECS = [
    ("sq",    1080, 1080, 464, 0.33),
    ("feed",  1080, 1350, 580, 0.30),
    ("story", 1080, 1920, 600, 0.28),
]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, yv = sys.argv[1], float(sys.argv[2])
    outdir = sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(src)) or "."
    os.makedirs(outdir, exist_ok=True)

    im = Image.open(src).convert("RGB")
    sw, sh = im.size
    print(f"source {sw}x{sh}  YV={yv:g}")
    if sw < 1080:
        print(f"  ⚠ המקור צר מ-1080 ({sw}px) — הסטורי ייצא רך. לציין לדור, לא להתעלם.")

    for name, ow, oh, ch, frac in SPECS:
        ch = min(ch, sh)
        cw = min(int(round(ch * ow / oh)), sw)
        top = max(0, min(sh - ch, int(round(yv - frac * ch))))
        left = max(0, min(sw - cw, (sw - cw) // 2))
        out = im.crop((left, top, left + cw, top + ch)).resize((ow, oh), Image.LANCZOS)
        path = os.path.join(outdir, f"{name}.png")
        out.save(path)
        landed = (yv - top) / ch
        flag = "" if 0.18 <= landed <= 0.48 else "   ⚠ הנושא לא בשליש העליון — לכוונן YV"
        print(f"  {name:6s} crop=({left},{top},{cw},{ch}) -> {ow}x{oh}  נושא ב-{landed:.0%}{flag}")


if __name__ == "__main__":
    main()
