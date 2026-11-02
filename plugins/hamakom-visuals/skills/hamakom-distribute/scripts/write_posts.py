#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
write_posts.py - מייצר את הקופי לכל פלטפורמה במבנה שדור קבע (2.11.2026):

  ההוק     = ה-h1 של הכתבה, מילה במילה ("תשנה שההוק יהיה הכותרת כלשונה באתר")
  הגוף     = המשנה (excerpt), מילה במילה ("יתר הטקסט בפוסטים - בבקשה את המשנה")
  הסיום    = שורת קרדיט + קישור קצר של הרשת

לא מנסחים תקציר משלנו. הכותרת והמשנה כבר עברו עריכה; הקופי חוזר עליהן כמו שהן.

פלטפורמות:
  אינסטגרם / טיקטוק  h1 · משנה · "כל הפרטים בכתבה של <שם>, עכשיו בביו ובסטורי שלנו" · האשטג
  פייסבוק / X        h1 · משנה · "כל הפרטים בכתבה של <שם>:" + קישור קצר
  וואטסאפ / טלגרם    הפורמט הקבוע של hamakom-whatsapp-item: *h1*, משנה, "הדיווח של <שם> - עכשיו
                     באתר >>", קישור קצר, ופוטר (invest / whatsapp / t.me/ha_makom)
  ריל                h1 · שורת הביו · האשטג

קישורים: אם בתיקייה יש short_links.json (מ-short_links.py), יוצאים הקישורים הקצרים
ha-makom.co.il/{fb|x|wa|tg}/<key>, בלי https. אחרת - הקישור המלא עם UTM של הרשת
(utm_source=<רשת>, utm_medium=social, utm_campaign=<slug>). לעולם לא wp.me: הוא מוחק את ה-UTM.
אינסטגרם וטיקטוק בלי קישור (לא לחיץ שם); ההפניה היא לביו ולסטורי.

קרדיט תמונה: רק לצילום, ורק כלשונו מהכתבה (image_credit ב-article.json). איור בינה
מלאכותית (image_ai: true) - בלי שורת "צילום". אין ברירת מחדל "צילום: פלאש 90".

שדות ב-article.json: title, excerpt, author, link, slug (אופציונלי), genre ("opinion" לטור),
image_ai, image_credit. משנה ריקה נשלפת מה-API הציבורי של האתר לפי ה-slug.

הרצה: python3 write_posts.py article.json OUT_DIR
"""
import html, json, os, re, ssl, sys, urllib.request
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

HASHTAG = "#המקום_הכי_חם_בגיהנום"
SENSITIVE_NOTE = "למצולמים אין קשר לכתבה"
# מילות-סף לתוכן רגיש -> מוסיפות את שורת ההסתייגות (מוסכמת האתר)
SENSITIVE = ("תקיפה מינית", "אונס", "הטרדה מינית", "התעללות", "פגיעה מינית",
             "אובדנות", "התאבדות", "קטין", "נפגעות", "נפגעי")
FOOTER = ("____________________\n"
          "תמכו בעיתונות עצמאית: ha-makom.co.il/invest\n"
          "עדכונים בוואטסאפ: ha-makom.co.il/whatsapp\n"
          "בטלגרם: t.me/ha_makom")
SITE = "https://www.ha-makom.co.il"


def slug_of(art):
    u = urlsplit(art.get("link") or "")
    return art.get("slug") or ([p for p in u.path.split("/") if p][-1:] or ["home"])[0]


def tagged(art, source):
    """הקישור לכתבה עם תגיות UTM לפלטפורמה. תגית קיימת באותו שם לא נדרסת."""
    link = (art.get("link") or "").strip()
    if not link:
        return ""
    u = urlsplit(link)
    q = dict(parse_qsl(u.query, keep_blank_values=True))
    for k, v in (("utm_source", source), ("utm_medium", "social"), ("utm_campaign", slug_of(art))):
        q.setdefault(k, v)
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), u.fragment))


def link_for(art, short, net):
    """קישור קצר אם נוצר, אחרת הקישור המלא המתויג."""
    return short.get(net) or tagged(art, net)


def proof(s):
    """חוק המקף + ריסון סימני קריאה - רק לשורות שאנחנו מנסחים, לא ל-h1 ולמשנה."""
    s = re.sub("\\s*[\u2014\u2013]\\s*", " - ", s or "")
    s = re.sub(r"!{2,}", "!", s)
    return s.strip()


def fetch_excerpt(art):
    """משנה ריקה ב-article.json (קורה בטיוטה) - שולפים מהאתר החי, קריאה בלבד."""
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        ctx = ssl.create_default_context()
    url = f"{SITE}/wp-json/wp/v2/posts?slug={slug_of(art)}&_fields=excerpt"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=30) as r:
        posts = json.load(r)
    raw = posts[0]["excerpt"]["rendered"] if posts else ""
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).replace("\xa0", " ").strip()


def is_sensitive(art):
    blob = " ".join([art.get("title", ""), art.get("excerpt", "")])
    return any(k in blob for k in SENSITIVE)


def credit_line(art):
    """שורת קרדיט לתמונה - רק לצילום, כלשונה מהכתבה. איור AI: אין."""
    lines = []
    if not art.get("image_ai"):
        lines.append(art.get("image_credit")
                     or "<<< קרדיט הצילום כלשונו מה-figcaption בכתבה, או למחוק את השורה אם זה איור >>>")
    if is_sensitive(art):
        lines.append(SENSITIVE_NOTE)
    return ". ".join(lines)


def who(art):
    a = (art.get("author") or "").strip()
    noun = "בטור" if art.get("genre") == "opinion" else "בכתבה"
    return proof(f"כל הפרטים {noun} של {a}" if a else f"כל הפרטים {noun}")


def head(art):
    return [art["title"].strip(), art["excerpt"].strip()]


def bio_post(art):
    """אינסטגרם וטיקטוק - בלי קישור, הפניה לביו ולסטורי (השורה שדור קבע 2.11.2026)."""
    return "\n\n".join(p for p in head(art) + [
        f"{who(art)}, עכשיו בביו ובסטורי שלנו", credit_line(art), HASHTAG] if p)


def link_post(art, short, net):
    """פייסבוק ו-X - אותו טקסט, קישור קצר לכל רשת."""
    return "\n\n".join(p for p in head(art) + [
        f"{who(art)}:\n{link_for(art, short, net)}", credit_line(art)] if p)


def messenger(art, short, net):
    """וואטסאפ/טלגרם - הפורמט הקבוע (hamakom-whatsapp-item). אין לשנות."""
    a = (art.get("author") or "").strip()
    kind = "הטור המלא של" if art.get("genre") == "opinion" else "הדיווח של"
    return "\n".join([
        f"*{art['title'].strip()}*",
        art["excerpt"].strip(),
        "",
        f"{kind} {a} - עכשיו באתר >>",
        link_for(art, short, net).replace("https://", ""),
        FOOTER,
    ])


def reel_caption(art):
    return "\n\n".join([art["title"].strip(), f"{who(art)}, עכשיו בביו ובסטורי שלנו", HASHTAG])


def main():
    if len(sys.argv) < 3:
        raise SystemExit("שימוש: write_posts.py article.json OUT_DIR")
    src = sys.argv[1]
    art = json.load(open(src, encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if not (art.get("excerpt") or "").strip():
        art["excerpt"] = fetch_excerpt(art)
    if not art.get("excerpt"):
        raise SystemExit("אין משנה לכתבה (excerpt ריק גם באתר). גוף הפוסטים הוא המשנה - להשלים קודם.")
    sl = os.path.join(os.path.dirname(os.path.abspath(src)), "short_links.json")
    short = json.load(open(sl, encoding="utf-8")) if os.path.exists(sl) else {}

    blocks = [
        ("אינסטגרם (פוסט / קרוסלה, גרפיקה 4:5)", bio_post(art)),
        ("פייסבוק (גרפיקה מרובעת)", link_post(art, short, "facebook")),
        ("X (גרפיקה מרובעת)", link_post(art, short, "x")),
        ("טיקטוק (פוסט תמונה מהסטורי; כותרת = h1)", bio_post(art)),
        ("וואטסאפ", messenger(art, short, "whatsapp")),
        ("טלגרם", messenger(art, short, "telegram")),
        ("ריל", reel_caption(art)),
    ]
    md = [f"# קופי הפצה - {art['title'].strip()}", ""]
    md.append(f"**מאת:** {art.get('author','')}  ·  **קישור:** {art.get('link','')}")
    md.append("\n> ההוק הוא ה-h1 והגוף הוא המשנה, מילה במילה. לא לנסח מחדש.")
    md.append("> " + ("הקישורים הקצרים מפנים לכתבה עם UTM של כל רשת."
                      if short else "אין short_links.json: הקישורים המלאים עם UTM. לקיצור - short_links.py."))
    if art.get("image_ai"):
        md.append("> התמונה היא איור בינה מלאכותית, ולכן אין שורת \"צילום\".")
    if is_sensitive(art):
        md.append("> תוכן רגיש זוהה - נוספה שורת ההסתייגות \"למצולמים אין קשר לכתבה\".")
    for name, body in blocks:
        md += [f"\n## {name}\n", "```", body, "```"]

    p = os.path.join(out, "posts.md")
    open(p, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print(f"  ✓ posts.md - {len(blocks)} פלטפורמות" + (" · קישורים קצרים" if short else ""))
    return p


if __name__ == "__main__":
    main()
