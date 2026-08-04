# -*- coding: utf-8 -*-
"""כתוביות קריוקי לריל — מילים שנצבעות בקצב קריאה מוסכם (נוסף 02.08.2026).

במקום כרטיס סטטי: המשפט מוצג בלבן, והמילים נצבעות ב-sc-terra (#E8906F)
במצטבר, משמאל התודעה של הקורא — מילה אחרי מילה, בקצב קריאה קבוע.

למה לא ASS/libass: ה-ffmpeg של דור בנוי בלי libass, וקריוקי RTL ב-libass
ממילא שביר (סדר מילים). כאן הציור ב-PIL + python-bidi — אותו מנוע של
make_cards.py — והתוצר הוא MOV שקוף (qtrle) שמולבש כמו כרטיס רגיל.

קצב הקריאה המוסכם (מקור: Netflix Hebrew TTSG — תקרה 17 CPS למבוגרים;
אנחנו שמרנים יותר כי הטקסט יושב על וידאו):
  CPS = 15  תווים/שנייה  ·  מינימום 0.25 שנ' למילה  ·  lead-in 0.4 שנ'
  לפני שהצביעה מתחילה  ·  hold של ≥1 שנ' אחרי המילה האחרונה.
  ⇒ אורך מקטע מומלץ: ceil(len(text)/15 + 1.6) שניות.

פונטים: ציטוט/משפט — Publico Headline (לבן→terra). קיקר — Graphik Medium.
שימוש:
  python3 make_karaoke.py "הטקסט מילה במילה" DURATION OUT_NAME [--size 52] [--kicker "..."]
פלט: $REEL_WORKDIR/karaoke/OUT_NAME.mov (RGBA, 1080 רוחב, שקוף)
החלפה ב-normalize: input הכרטיס הופך ל-MOV הזה (בלי -loop), שאר השרשרת זהה.
"""
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import os, sys, subprocess, math

WORKDIR = os.environ.get("REEL_WORKDIR", "/tmp/vid")
F_DISPLAY = f"{WORKDIR}/publicoheadlinehebrew-roman.otf"
F_UI_BOLD = f"{WORKDIR}/graphikhlar-medium.otf"
F_UI = f"{WORKDIR}/graphikhlar-regular.otf"
W = 1080
WHITE = (255, 255, 255, 255)
TERRA = (232, 144, 111, 255)   # sc-terra — צבע ההדגשה על וידאו
SC_TERRA = TERRA

CPS = 15.0          # קצב הקריאה המוסכם (עברית, טקסט על וידאו)
MIN_WORD = 0.25     # שנ' מינימום למילה
LEAD_IN = 0.4       # שנ' לפני תחילת הצביעה
FPS_HOLD = "30"

def word_durations(words):
    return [max(MIN_WORD, len(w) / CPS) for w in words]

SOFT = (183, 181, 172, 255)   # on-dark-soft — שורת "בתיעוד:"/קרדיט

def layout(words, qsize, kicker):
    """שובר את המילים לשורות (RTL) ומחזיר לכל מילה (line, index_in_line)."""
    tmp = Image.new("RGBA", (W, 10)); d = ImageDraw.Draw(tmp)
    pad_x = 150; maxw = W - 2 * pad_x   # שוליים רחבים — הנחיית דור 02.08.2026
    qf = ImageFont.truetype(F_DISPLAY, qsize)
    lines, cur = [], []
    for w in words:
        t = " ".join(cur + [w])
        if d.textlength(get_display(t), font=qf) <= maxw: cur.append(w)
        else:
            if cur: lines.append(cur)
            cur = [w]
    if cur: lines.append(cur)
    return lines, qf, pad_x

def render_frame(lines, qf, pad_x, n_colored, kicker, out_path, explainer=None):
    lh = int(qf.size * 1.34)
    kf = ImageFont.truetype(F_UI_BOLD, 30) if kicker else None
    kick_h = 58 if kicker else 0
    ef = ImageFont.truetype(F_UI, 34) if explainer else None
    exp_h = 62 if explainer else 0
    H = 30 + kick_h + len(lines) * lh + exp_h + 28
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = 12
    if kicker:
        vis = get_display(kicker)
        tw = d.textlength(vis, font=kf) + 3 * max(len(vis) - 1, 0)
        x = W - pad_x - tw
        for ch in vis:
            d.text((x, y), ch, font=kf, fill=SC_TERRA)
            x += d.textlength(ch, font=kf) + 3
        y += kick_h
    idx = 0
    space = d.textlength(" ", font=qf)
    for line in lines:
        # RTL: המילה הראשונה בשורה יושבת הכי ימינה. מציירים מילה-מילה
        # כדי לצבוע כל אחת בנפרד; bidi מוחל פר-מילה (מילה עברית = יחידה שלמה).
        x = W - pad_x
        for w in line:
            vis = get_display(w)
            tw = d.textlength(vis, font=qf)
            x -= tw
            color = TERRA if idx < n_colored else WHITE
            d.text((x, y), vis, font=qf, fill=color)
            x -= space
            idx += 1
        y += lh
    if explainer:
        y += 16
        vis = get_display(explainer)
        tw = d.textlength(vis, font=ef)
        d.text((W - pad_x - tw, y), vis, font=ef, fill=SOFT)
    img.save(out_path)
    return H

def main():
    text = sys.argv[1]; duration = float(sys.argv[2]); name = sys.argv[3]
    qsize = 52; kicker = None; explainer = None
    if "--size" in sys.argv: qsize = int(sys.argv[sys.argv.index("--size") + 1])
    if "--kicker" in sys.argv: kicker = sys.argv[sys.argv.index("--kicker") + 1]
    if "--explainer" in sys.argv: explainer = sys.argv[sys.argv.index("--explainer") + 1]
    words = text.split()
    durs = word_durations(words)
    total_paint = LEAD_IN + sum(durs)
    if total_paint + 1.0 > duration:
        print(f"WARNING: paint time {total_paint:.1f}s + 1s hold > segment {duration}s — "
              f"recommended duration: {math.ceil(total_paint + 1.6)}s", file=sys.stderr)
    outdir = f"{WORKDIR}/karaoke/{name}"; os.makedirs(outdir, exist_ok=True)
    lines, qf, pad_x = layout(words, qsize, kicker)
    # פריים 0 = הכל לבן; פריים k = k מילים צבועות
    for k in range(len(words) + 1):
        render_frame(lines, qf, pad_x, k, kicker, f"{outdir}/f{k:03d}.png", explainer)
    # concat list עם משכי פריימים: f0 מוצג LEAD_IN, f_k מוצג durs[k-1], אחרון עד סוף המקטע
    hold = max(0.1, duration - total_paint)
    lst = f"{outdir}/list.txt"
    with open(lst, "w") as f:
        f.write(f"file 'f000.png'\nduration {LEAD_IN}\n")
        for k, dur in enumerate(durs, start=1):
            f.write(f"file 'f{k:03d}.png'\nduration {dur}\n")
        f.write(f"file 'f{len(words):03d}.png'\nduration {hold}\n")
        f.write(f"file 'f{len(words):03d}.png'\n")   # concat demuxer דורש כפילות אחרונה
    out = f"{WORKDIR}/karaoke/{name}.mov"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-vsync", "vfr", "-pix_fmt", "argb", "-c:v", "qtrle",
                    "-t", str(duration), out], check=True)
    print(out)

if __name__ == "__main__":
    main()
