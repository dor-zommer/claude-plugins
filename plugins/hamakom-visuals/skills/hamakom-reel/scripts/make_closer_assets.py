# -*- coding: utf-8 -*-
"""נכסי סגיר מותאם (HaMakom DS 2026) — קונספט "המניפסט".

**הסגיר הקנוני הוא closer_v3.mp4 מתיקיית החומרים הקבועה
(`/Users/dorzommer/Desktop/חומרים להכנת וידאו לרילז ` — רווח בסוף!) —
משתמשים בו כמות שהוא. את הסקריפט הזה מריצים רק כשצריך טקסט CTA אחר
מזה שצרוב ב-closer_v3.**

טקסט ה-CTA לפי סוג הכתבה: "התחקיר המלא באתר" רק לתחקיר אמיתי; לדיווח —
"הסיפור המלא באתר" (או "הדיווח של [כתב/ת] באתר" / "כל הפרטים באתר").
מגדירים במשתנה סביבה REEL_CTA.

מייצר ל-$REEL_WORKDIR:
  fA.png fB.png fC.png  — פריימי מכות המניפסט (טקסט אטום על דיו, מצטבר):
      "בלי בעלי הון" → +"בלי פרסומות" → +"בלי בולשיט" (השלישית בטרקוטה)
  fD.png               — פריים הנעילה: לוגו מרובע (שנהב) + פס-חתימה טריקולור +
                         CTA (Suez One) + סלוגן + URL טרקוטה
  sting.wav            — פס-קול מסונתז (drone עולה + 3 מכות מתגברות + boom נעילה)

ffmpeg מרכיב מהם את הסגיר ב-make_closer.sh (cut+shake+flash+grain+vignette).

**מלכודת קואורדינטות:** פריים הנעילה fD נבנה בקואורדינטות המקור של lock()
(לוגו 470px ב-y=640, פס 560×12, CTA 60 ב-cy=1530, סלוגן 1625, URL 1710).
אסור למדוד קואורדינטות מפריים פלט — שרשרת הרעד ב-make_closer.sh מגדילה פי 1.12
וחותכת (crop 65,115); מדידה מהפלט מחילה את הטרנספורם פעמיים וה-URL נחתך.

דורש: PIL + python-bidi (אין libraqm במק של דור — get_display, לא direction='rtl'),
cairosvg, numpy. גרש בעברית — גרש עברי ׳ (U+05F3), לא אפוסטרוף לטיני.
הלוגו: SVG מרובע — מחפש ב-WORKDIR ואז בנכסי הפלאגין (ראה LOGO_CANDS).
"""
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import os, wave

WORKDIR = os.environ.get("REEL_WORKDIR", "/tmp/vid")
HOME_F  = os.path.expanduser("~/Library/Fonts")
HERE    = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920

def _first(*cands):
    for c in cands:
        if c and os.path.exists(c):
            return c
    return cands[-1]

# פונט התצוגה של הסגיר = Publico Headline Hebrew ExtraBold — זה הפונט הצרוב
# ב-closer_v3 הקנוני (מניפסט + CTA). Suez One הוא fallback בלבד; אם משתמשים בו
# הסגיר יוצא דק מדי ולא תואם את הקנוני.
F_DISPLAY = _first(f"{WORKDIR}/publicoheadlinehebrew-extrabold.otf",
                   os.path.normpath(f"{HERE}/../../../design-system/assets/fonts/publicoheadlinehebrew-extrabold.otf"),
                   f"{HOME_F}/PublicoHeadlineHebrew-Black.ttf",
                   f"{WORKDIR}/SuezOne-Regular.ttf", f"{HOME_F}/SuezOne-Regular.ttf")
F_UI      = _first(f"{WORKDIR}/IBMPlexSansHebrew-Regular.ttf", f"{HOME_F}/IBMPlexSansHebrew-Regular.ttf")
F_UI_SB   = _first(f"{WORKDIR}/IBMPlexSansHebrew-SemiBold.ttf", f"{HOME_F}/IBMPlexSansHebrew-SemiBold.ttf", F_UI)
LOGO_CANDS = [f"{WORKDIR}/logo-square.svg",
              os.path.expanduser("~/Documents/המקום/שיווק/hamakom square black.svg"),
              os.path.normpath(f"{HERE}/../../hamakom-carousel/assets/logo-square-black.svg")]

# פלטת DS 2026
INK    = (20, 20, 19)       # דיו #141413
IVORY  = (250, 249, 245)    # שנהב #faf9f5
TERRA  = (232, 144, 111)    # טרקוטה מובהרת לווידאו #E8906F
MUTED  = (200, 198, 189)    # שנהב-מעומעם
HEATHER = (142, 111, 168)   # אברש #8E6FA8
SAGE    = (120, 140, 93)    # מרווה #788C5D
TERRA_S = (217, 119, 87)    # טרקוטה חתימה #D97757


def _center(d, img, text, font, cy, fill):
    """שורה ממורכזת אופקית, cy = מרכז אנכי. RTL דרך bidi (אין libraqm)."""
    vis = get_display(text)
    bbox = d.textbbox((0, 0), vis, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) // 2 - bbox[0]
    y = cy - th // 2 - bbox[1]
    d.text((x, y), vis, font=font, fill=fill)


def manifesto(name, lines):
    """פריים אטום: דיו + שורות המניפסט (מצטברות). השלישית בטרקוטה."""
    f = ImageFont.truetype(F_DISPLAY, 130)
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    cys = [800, 980, 1160]                     # מרכזי שלוש שורות, בלוק ~980
    for i, (txt, terra) in enumerate(lines):
        _center(d, img, txt, f, cys[i], TERRA if terra else IVORY)
    img.save(f"{WORKDIR}/{name}.png")
    print(name)


def logo_ivory(width=470):
    """רסטר הלוגו המרובע → שנהב. **אלפא נשמר כמות שהוא, צובעים רק RGB.**
    (ההמרה הישנה לומיננס→אלפא שגויה: פיקסלים שקופים הם RGB=0 ומתקבל ריבוע מלא.)"""
    import cairosvg, numpy as np
    src = _first(*LOGO_CANDS)
    png = f"{WORKDIR}/_logo_raw.png"
    cairosvg.svg2png(url=src, write_to=png, output_width=width * 2)   # x2 לחדות
    a = np.array(Image.open(png).convert("RGBA"))
    a[..., 0], a[..., 1], a[..., 2] = 250, 249, 245                  # שנהב, אלפא לא נגעים
    ys, xs = np.where(a[..., 3] > 20)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray(a, "RGBA")
    im = im.resize((width, int(width * im.height / im.width)), Image.LANCZOS)
    return im


def lock(name="fD"):
    """פריים נעילה: לוגו + פס-חתימה טריקולור + CTA + סלוגן + URL."""
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    logo = logo_ivory(470)
    lw, lh = logo.size
    ly = 640                                    # ראש הלוגו
    img.paste(logo, ((W - lw) // 2, ly), logo)
    # פס-חתימה טריקולור מתחת ללוגו (אברש·מרווה·טרקוטה, שמאל→ימין)
    sw, sh, sy = 560, 12, ly + lh + 40
    sx = (W - sw) // 2
    seg = sw // 3
    for i, col in enumerate((HEATHER, SAGE, TERRA_S)):
        d.rectangle([sx + i * seg, sy, sx + (i + 1) * seg, sy + sh], fill=col)
    # CTA — לפי סוג הכתבה: "התחקיר המלא באתר" רק לתחקיר; לדיווח "הסיפור המלא באתר"
    cta = os.environ.get("REEL_CTA", "הסיפור המלא באתר")
    _center(d, img, cta, ImageFont.truetype(F_DISPLAY, 60), 1530, IVORY)
    _center(d, img, "בלי בעלי הון · בלי פרסומות · בלי בולשיט",
            ImageFont.truetype(F_UI, 38), 1625, MUTED)
    # URL — לטיני, LTR
    uf = ImageFont.truetype(F_UI_SB, 52)
    ub = d.textbbox((0, 0), "ha-makom.co.il", font=uf)
    d.text(((W - (ub[2] - ub[0])) // 2 - ub[0], 1710 - (ub[3] - ub[1]) // 2 - ub[1]),
           "ha-makom.co.il", font=uf, fill=TERRA)
    img.save(f"{WORKDIR}/{name}.png")
    print(name)


def sting(path=None, dur=6.0, sr=44100):
    """פס-קול דרמטי: drone עולה + 3 מכות מתגברות + boom נעילה + זנב."""
    import numpy as np
    path = path or f"{WORKDIR}/sting.wav"
    n = int(sr * dur); t = np.linspace(0, dur, n, endpoint=False)
    rng = np.random.default_rng(7)
    out = np.zeros(n)
    # drone
    de = np.clip(t / 2.0, 0, 1) * 0.22
    de = np.where(t > 2.85, 0.30 * np.exp(-0.5 * (t - 2.85)), de)
    out += np.sin(2 * np.pi * 46 * t) * de

    def kick(t0, amp, f=55, dec=16):
        tau = np.clip(t - t0, 0, None); m = (t - t0) >= 0
        k = np.sin(2 * np.pi * f * tau) * np.exp(-dec * tau)
        click = rng.standard_normal(n) * np.exp(-90 * tau)
        return m * (k * amp + click * amp * 0.35)
    for t0, a in [(0.6, 0.55), (1.3, 0.68), (2.0, 0.82)]:
        out += kick(t0, a)
    # riser
    ramp = np.clip((t - 2.0) / 0.85, 0, 1) ** 2
    out += ((t >= 2.0) & (t < 2.85)) * rng.standard_normal(n) * ramp * 0.28
    # boom נעילה
    tau = np.clip(t - 2.85, 0, None); m = (t - 2.85) >= 0
    out += m * (np.sin(2 * np.pi * 40 * tau) * np.exp(-5 * tau) * 0.95
                + rng.standard_normal(n) * np.exp(-26 * tau) * 0.5)
    # whoosh + זנב
    tw = np.clip(t - 3.4, 0, None); mw = ((t - 3.4) >= 0) & ((t - 3.4) < 0.6)
    out += mw * rng.standard_normal(n) * np.exp(-6 * tw) * 0.22 * np.clip(tw / 0.1, 0, 1)
    out += np.sin(2 * np.pi * 42 * t) * np.where(t > 2.9, 0.12 * np.exp(-0.7 * (t - 2.9)), 0)
    out = np.tanh(out / (np.max(np.abs(out)) + 1e-6) * 0.92 * 1.1)
    pcm = (out * 32767).astype("int16")
    w = wave.open(path, "w"); w.setnchannels(1); w.setsampwidth(2)
    w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
    print("sting.wav")


if __name__ == "__main__":
    os.makedirs(WORKDIR, exist_ok=True)
    L1 = ("בלי בעלי הון", False)
    L2 = ("בלי פרסומות", False)
    L3 = ("בלי בולשיט", True)          # טרקוטה — הפאנצ'ליין
    manifesto("fA", [L1])
    manifesto("fB", [L1, L2])
    manifesto("fC", [L1, L2, L3])
    lock("fD")
    sting()
