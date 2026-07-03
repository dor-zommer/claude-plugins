# -*- coding: utf-8 -*-
"""כרטיסי טקסט לריל — טקסט ישירות על הווידאו, בלי קוביות רקע ובלי צל.
הקריאות מגיעה מגרדיאנט הדיו שב-overlay.png (ראו make_overlay.py) — לא מצל.
שימוש: ערכו את רשימת הכרטיסים בתחתית הקובץ והריצו.

רינדור עברית: אין libraqm במק של דור — משתמשים ב-python-bidi
(bidi.algorithm.get_display) ולא ב-direction='rtl'. גרש בעברית: גרש עברי ׳
(U+05F3), לא אפוסטרוף לטיני.
הפונטים: ראו references/brand-assets.md. ציפייה: הקבצים הועתקו ל-WORKDIR."""
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import os

WORKDIR = os.environ.get("REEL_WORKDIR", "/tmp/vid")
HOME_F  = os.path.expanduser("~/Library/Fonts")

def _font(*cands):
    """הפונט הראשון שקיים — WORKDIR ואז ~/Library/Fonts (Mac / VM)."""
    for c in cands:
        if c and os.path.exists(c):
            return c
    return cands[-1]

# ציטוטים — Suez One בלבן בלבד (Narkiss ירד, לא בשימוש לציטוטים)
F_DISPLAY = _font(f"{WORKDIR}/SuezOne-Regular.ttf", f"{HOME_F}/SuezOne-Regular.ttf")
# גוף/UI ב-DS — IBM Plex Sans Hebrew (קיקר, "בתיעוד:", סלוגן, URL — יש גליפים לטיניים)
F_UI      = _font(f"{WORKDIR}/IBMPlexSansHebrew-Regular.ttf", f"{HOME_F}/IBMPlexSansHebrew-Regular.ttf")
F_UI_BOLD = _font(f"{WORKDIR}/IBMPlexSansHebrew-Bold.ttf", f"{HOME_F}/IBMPlexSansHebrew-Bold.ttf", F_UI)
F_LATIN   = F_UI
W = 1080
WHITE   = (255, 255, 255, 255)  # ציטוטים — לבן #ffffff בלבד
SC_TERRA = (232, 144, 111, 255) # sc-terra #E8906F — קיקר (טרקוטה מובהרת לווידאו)
SOFT    = (183, 181, 172, 255)  # on-dark-soft #b7b5ac — "בתיעוד:" ומשנה

def wrap(d, text, font, maxw):
    words = text.split(); lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(get_display(t), font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def _draw_tracked(d, xy, text, font, fill, tracking=0):
    """ציור עם letter-spacing (PIL לא תומך נטיבית) — תו-תו בסדר ויזואלי."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tracking

def card(name, quote, qsize=56, explainer=None, kicker=None, qcolor=WHITE,
         qfont=None, slogan=None):
    """כרטיס אחד. quote=ציטוט מילה-במילה מהכתבה (Suez One לבן).
    kicker=תג קצר — IBM Plex Bold 30, sc-terra, letter-spacing ~3px.
    explainer=שורת 'בתיעוד:' (IBM Plex Regular 34, #b7b5ac) או URL (לטינית).
    slogan=שורת סלוגן קטנה (IBM Plex, on-dark-soft) — לסגיר."""
    qfont = qfont or F_DISPLAY
    tmp = Image.new("RGBA", (W, 10)); d = ImageDraw.Draw(tmp)
    pad_x = 60; maxw = W - 2 * pad_x
    blocks = []   # (lines, font, fill, line_h, gap, tracking)
    if kicker:
        kf = ImageFont.truetype(F_UI_BOLD, 30)
        blocks.append((wrap(d, kicker, kf, maxw), kf, SC_TERRA, 44, 14, 3))
    qf = ImageFont.truetype(qfont, qsize)
    blocks.append((wrap(d, quote, qf, maxw), qf, qcolor, int(qsize * 1.34), 18, 0))
    if slogan:
        sf = ImageFont.truetype(F_UI, 34)
        blocks.append((wrap(d, slogan, sf, maxw), sf, SOFT, 46, 16, 0))
    if explainer:
        if all(ord(c) < 1024 for c in explainer):   # לטיני → LTR כמו שהוא
            ef = ImageFont.truetype(F_LATIN, 52)
            blocks.append(([explainer], ef, SC_TERRA, 64, 0, 0))
        else:
            ef = ImageFont.truetype(F_UI, 34)
            blocks.append((wrap(d, explainer, ef, maxw), ef, SOFT, 46, 0, 0))
    total = 30
    for lines, f, fill, lh, gap, _ in blocks: total += len(lines) * lh + gap
    total += 16
    img = Image.new("RGBA", (W, total), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = 12
    for lines, f, fill, lh, gap, tracking in blocks:
        for ln in lines:
            vis = get_display(ln)                   # bidi — סדר ויזואלי
            tw = d.textlength(vis, font=f) + tracking * max(len(vis) - 1, 0)
            x = W - pad_x - tw                      # יישור לימין (RTL)
            if tracking:
                _draw_tracked(d, (x, y), vis, f, fill, tracking)
            else:
                d.text((x, y), vis, font=f, fill=fill)
            y += lh
        y += gap
    os.makedirs(f"{WORKDIR}/cards", exist_ok=True)
    img.save(f"{WORKDIR}/cards/{name}.png")
    print(name)

# ============ ערכו מכאן: הכרטיסים של הריל הנוכחי ============
# דוגמה (ריל חווארה 6.6.2026) — ציטוטים מילה-במילה מהכתבה; משפט סביל בלי עושה
# מומר לפעיל שממנה את העושה (ראו SKILL.md שלב 2).
if __name__ == "__main__":
    card("A", "עשרות מתנחלים פשטו עם טנדרים בצהרי שבת על חווארה",
         qsize=60, kicker="פוגרום דוחה שבת")
    card("B", "במשך שעות תקפו תושבים ורכוש באופן אקראי")
    card("C", "הותקפו תושבים, בתים, נופצו כלי רכב ומבני ציבור")
    card("D", "התוקפים מכים ובועטים בשניים כשהם פצועים ושרועים על הקרקע",
         qsize=54,
         explainer="בתיעוד: תקיפת שני הפלסטינים, שלקח בה חלק גם חייל על ציוד מלא")
    card("E", "אחד מהם איבד את הכרתו ופונה לבית החולים במצב קשה")
    card("F", "הציתו שטחים חקלאיים, וגנבו עשרות בעלי חיים מעדרי צאן")
    card("G", "אחת מההצתות שהתפשטה לשריפה, הוסיפה לבעור שעות לאחר תחילת האירוע",
         qsize=54)
    card("H", "לפחות תשעה פלסטינים שנפלו קורבן למסע האלימות נפצעו")
