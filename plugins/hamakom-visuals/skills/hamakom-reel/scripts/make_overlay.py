# -*- coding: utf-8 -*-
"""אוברליי סטטי אחד לכל מקטעי הריל (HaMakom DS 2026) → $REEL_WORKDIR/overlay.png

בונים פעם אחת ומלבישים על כל מקטע (normalize_segment.sh) — אחיד ומהיר:
  1. גרדיאנט דיו אנכי (#141413) בעצירות ה-DS של הקאבר:
     0@0% → 0.1@40% → 0.5@58% → 0.92@78% → 1@100%  (הקריאות במקום צל)
  2. הלוגו הריבועי הטיפוגרפי, לבן, רוחב ~72px, ממורכז למעלה (y≈48)
  3. HA-MAKOM.CO.IL למטה במרכז — IBM Plex SemiBold 28, letter-spacing ~4px,
     לבן באטימות ~25% (שקיפות 75%)
  4. פס-חתימה תחתון יחיד, דק 4px: ימין טרקוטה #D97757 · אמצע מרווה #788C5D ·
     שמאל אברש #8E6FA8

הלוגו: רסטר מ-SVG עם cairosvg — **לשמור על ערוץ האלפא ולצבוע רק RGB**.
(המרה דרך לומיננס→אלפא שגויה: פיקסלים שקופים הם RGB=0 ומתקבל ריבוע מלא.)
דורש: PIL, cairosvg, numpy. בלי libraqm — אין כאן טקסט עברי.
"""
from PIL import Image, ImageDraw, ImageFont
import os

WORKDIR = os.environ.get("REEL_WORKDIR", "/tmp/vid")
HOME_F  = os.path.expanduser("~/Library/Fonts")
HERE    = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
INK = (20, 20, 19)  # דיו #141413

def _first(*cands):
    for c in cands:
        if c and os.path.exists(c):
            return c
    return cands[-1]

LOGO_CANDS = [f"{WORKDIR}/logo-square.svg",
              os.path.expanduser("~/Documents/המקום/שיווק/hamakom square black.svg"),
              os.path.normpath(f"{HERE}/../../hamakom-carousel/assets/logo-square-black.svg")]
F_UI_SB = _first(f"{WORKDIR}/IBMPlexSansHebrew-SemiBold.ttf",
                 f"{HOME_F}/IBMPlexSansHebrew-SemiBold.ttf")


def gradient():
    """גרדיאנט דיו אנכי — אינטרפולציה לינארית בין עצירות ה-DS."""
    stops = [(0.00, 0.0), (0.40, 0.10), (0.58, 0.50), (0.78, 0.92), (1.00, 1.0)]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    for y in range(H):
        p = y / (H - 1)
        for (p0, a0), (p1, a1) in zip(stops, stops[1:]):
            if p0 <= p <= p1:
                a = a0 + (a1 - a0) * ((p - p0) / (p1 - p0) if p1 > p0 else 0)
                break
        row = (*INK, int(round(a * 255)))
        for x in range(W):
            px[x, y] = row
    return img


def logo_white(width=72):
    """רסטר הלוגו הריבועי → לבן. אלפא נשמר כמות שהוא, צובעים רק RGB."""
    import cairosvg, numpy as np
    src = _first(*LOGO_CANDS)
    png = f"{WORKDIR}/_logo_sq_raw.png"
    cairosvg.svg2png(url=src, write_to=png, output_width=width * 4)  # x4 לחדות
    a = np.array(Image.open(png).convert("RGBA"))
    a[..., 0] = 255; a[..., 1] = 255; a[..., 2] = 255   # לבן, אלפא לא נגעים
    im = Image.fromarray(a, "RGBA")
    ys, xs = (a[..., 3] > 8).nonzero()
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    return im.resize((width, int(width * im.height / im.width)), Image.LANCZOS)


def main():
    os.makedirs(WORKDIR, exist_ok=True)
    ov = gradient()
    # לוגו ריבועי לבן ~72px ממורכז למעלה
    logo = logo_white(72)
    ov.alpha_composite(logo, ((W - logo.width) // 2, 48))
    # URL תחתון — IBM Plex SemiBold 28, letter-spacing ~4px, לבן 25% אטימות
    d = ImageDraw.Draw(ov)
    uf = ImageFont.truetype(F_UI_SB, 28)
    text, ls = "HA-MAKOM.CO.IL", 4
    tw = sum(d.textlength(c, font=uf) for c in text) + ls * (len(text) - 1)
    x = (W - tw) / 2
    uy = H - 96
    for c in text:
        d.text((x, uy), c, font=uf, fill=(255, 255, 255, 64))   # ~25% אטימות
        x += d.textlength(c, font=uf) + ls
    # פס-חתימה תחתון יחיד 4px: ימין טרקוטה · אמצע מרווה · שמאל אברש
    seg = W // 3
    for i, col in enumerate([(142, 111, 168), (120, 140, 93), (217, 119, 87)]):
        d.rectangle([i * seg, H - 4, (i + 1) * seg if i < 2 else W, H], fill=(*col, 255))
    ov.save(f"{WORKDIR}/overlay.png")
    print("overlay.png")


if __name__ == "__main__":
    main()
