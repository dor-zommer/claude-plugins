# -*- coding: utf-8 -*-
"""כרטיסי טקסט לריל — טקסט ישירות על הווידאו, בלי קוביות רקע.
שימוש: ערכו את רשימת הכרטיסים בתחתית הקובץ והריצו. דורש PIL עם libraqm.
הפונטים: ראו references/brand-assets.md. ציפייה: הקבצים הועתקו ל-WORKDIR."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

WORKDIR = os.environ.get("REEL_WORKDIR", "/tmp/vid")
HOME_F  = os.path.expanduser("~/Library/Fonts")

def _font(*cands):
    """הפונט הראשון שקיים — WORKDIR ואז ~/Library/Fonts (Mac / VM)."""
    for c in cands:
        if c and os.path.exists(c):
            return c
    return cands[-1]

# ציטוט עריכתי בגוף הריל — נשאר Narkiss Shimshon (חתך הכותרות של המותג)
F_QUOTE   = _font(f"{WORKDIR}/NarkissShimshon-Extended.otf",
                  f"{HOME_F}/NarkissShimshon-Extended.otf",
                  os.path.expanduser("~/Desktop/NarkissShimshon-Extended.otf"))
# תצוגה ב-DS (כותרת הסגיר) — Suez One
F_DISPLAY = _font(f"{WORKDIR}/SuezOne-Regular.ttf", f"{HOME_F}/SuezOne-Regular.ttf")
# גוף/UI ב-DS — IBM Plex Sans Hebrew (שורות "בתיעוד:", סלוגן, URL — יש גליפים לטיניים)
F_UI      = _font(f"{WORKDIR}/IBMPlexSansHebrew-Regular.ttf", f"{HOME_F}/IBMPlexSansHebrew-Regular.ttf")
F_LATIN   = F_UI
W = 1080
IVORY = (250, 249, 245, 255)   # שנהב DS #faf9f5
TERRA = (232, 144, 111, 255)   # טרקוטה DS מובהרת לווידאו #E8906F
MUTED = (200, 198, 189, 255)   # שנהב-מעומעם לסלוגן/משנה

def wrap(d, text, font, maxw):
    words = text.split(); lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def card(name, quote, qsize=56, explainer=None, kicker=None, qcolor=IVORY,
         qfont=None, slogan=None):
    """כרטיס אחד. quote=ציטוט מילה-במילה מהכתבה. kicker=תג קצר בטרקוטה.
    explainer=שורת 'בתיעוד:' (עברית) או URL (לטינית, ייצבע טרקוטה אוטומטית).
    qfont=חריגה מפונט הציטוט (למשל F_DISPLAY/Suez One בסגיר).
    slogan=שורת סלוגן קטנה (IBM Plex, שנהב-מעומעם) — לסגיר."""
    qfont = qfont or F_QUOTE
    tmp = Image.new("RGBA", (W, 10)); d = ImageDraw.Draw(tmp)
    pad_x = 60; maxw = W - 2 * pad_x
    blocks = []
    if kicker:
        kf = ImageFont.truetype(F_QUOTE, 40)
        blocks.append((wrap(d, kicker, kf, maxw), kf, TERRA, 54, 14, 'rtl'))
    qf = ImageFont.truetype(qfont, qsize)
    blocks.append((wrap(d, quote, qf, maxw), qf, qcolor, int(qsize * 1.34), 18, 'rtl'))
    if slogan:
        sf = ImageFont.truetype(F_UI, 34)
        blocks.append((wrap(d, slogan, sf, maxw), sf, MUTED, 46, 16, 'rtl'))
    if explainer:
        if all(ord(c) < 1024 for c in explainer):   # לטיני → DejaVu, כיוון LTR
            ef = ImageFont.truetype(F_LATIN, 52)
            blocks.append(([explainer], ef, TERRA, 64, 0, 'ltr'))
        else:
            ef = ImageFont.truetype(F_UI, 38)
            blocks.append((wrap(d, explainer, ef, maxw), ef, MUTED, 50, 0, 'rtl'))
    total = 30
    for lines, f, fill, lh, gap, _ in blocks: total += len(lines) * lh + gap
    total += 16
    sh = Image.new("RGBA", (W, total), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    img = Image.new("RGBA", (W, total), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y = 12
    for lines, f, fill, lh, gap, dirn in blocks:
        for ln in lines:
            tw = d.textlength(ln, font=f)
            x = W - pad_x - tw                      # יישור לימין (RTL)
            ds.text((x + 3, y + 3), ln, font=f, fill=(0, 0, 0, 200), direction=dirn)
            d.text((x, y), ln, font=f, fill=fill, direction=dirn)
            y += lh
        y += gap
    sh = sh.filter(ImageFilter.GaussianBlur(6))     # צל רך לקריאות
    os.makedirs(f"{WORKDIR}/cards", exist_ok=True)
    Image.alpha_composite(sh, img).save(f"{WORKDIR}/cards/{name}.png")
    print(name)

# ============ ערכו מכאן: הכרטיסים של הריל הנוכחי ============
# ריל פוגרום חווארה 6.6.2026 — ציטוטים מילה-במילה מהכתבה
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
    # סגיר DS: כותרת Suez One + שורת סלוגן (IBM Plex) + URL טרקוטה
    card("CTA", "התחקיר המלא באתר", qsize=48, qfont=F_DISPLAY,
         slogan="בלי בעלי הון · בלי פרסומות · בלי בולשיט",
         explainer="ha-makom.co.il")
