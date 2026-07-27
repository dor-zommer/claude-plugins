#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watch_published.py — הטריגר. מזהה שכתבה פורסמה, מכין את הקרקע, ומוסר לסקילים הקיימים.

**הסקריפט הזה לא מעצב כלום.** אין כאן רינדור, אין פונטים, אין פלטה — כל זה חי
ב-hamakom-graphic / hamakom-carousel / hamakom-reel, והם מקור-האמת היחיד.
תפקיד הטריגר: (1) לזהות כתבה חדשה, (2) לפתוח תיקיית עבודה, (3) לאסוף את הדאטה
ואת התמונות שדור הכין, (4) להדפיס את רשימת ההפעלה של הסקילים.

הרצה:
  python3 watch_published.py             # כל מה שחדש מאז ההרצה הקודמת
  python3 watch_published.py --latest    # הכתבה האחרונה
  python3 watch_published.py --slug X    # כתבה ספציפית
  DEST=~/Desktop/הפצה python3 watch_published.py
"""
import json, os, re, sys, html, glob, datetime, urllib.request, ssl

try:
    import certifi
    _CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _CTX = ssl.create_default_context()

BASE = "https://www.ha-makom.co.il/wp-json/wp/v2"
UA = {"User-Agent": "Mozilla/5.0 hamakom-publish-trigger"}
FIELDS = "slug,link,title,excerpt,date,categories,jetpack_featured_media_url,yoast_head_json"
DEST = os.path.expanduser(os.environ.get("DEST", "~/Desktop/הפצה"))
STATE = os.path.join(DEST, ".state.json")

# קודי צלמים בשמות קבצי פלאש 90 (F<YYMMDD><XX><NNN>.jpg) — מ-hamakom-carousel חוק 5
SHOOTERS = {"CG": "חיים גולדברג", "YS": "יונתן סינדל", "TN": "תומר נויברג",
            "FFSS": "שרה שומאן", "MG": "מרים אלסטר", "SD": "שריה דיאמנט",
            "DP": "דור פזואלו", "NI": "נאסר אשתיה", "WH": "ואיל חסן"}


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                timeout=30, context=_CTX) as r:
        return json.load(r)


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).replace("\xa0", " ").strip()


def to_article(p):
    y = p.get("yoast_head_json", {}) or {}
    return {"slug": p.get("slug", ""), "link": p.get("link", ""),
            "title": strip(p.get("title", {}).get("rendered", "")),
            "excerpt": strip(p.get("excerpt", {}).get("rendered", "")),
            "date": p.get("date", "")[:10],
            "img": p.get("jetpack_featured_media_url") or "",
            "author": y.get("author", "") or ""}


def article_images(slug, featured=""):
    """**המקור העיקרי: התמונות של הכתבה עצמה.** לא תלוי בתיקיית ההורדות של דור.
    שולף את ה-og/featured + כל התמונות בגוף הכתבה, עם הקרדיט שמופיע לצידן."""
    out = []
    if featured:
        out.append({"src": "article", "url": featured, "role": "featured", "credit": ""})
    try:
        posts = _get(f"{BASE}/posts?slug={slug}&_fields=content")
        html_body = (posts[0].get("content", {}) or {}).get("rendered", "") if posts else ""
    except Exception as e:
        print("  שליפת גוף הכתבה נכשלה:", e)
        return out
    seen = {featured}
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', html_body):
        u = re.sub(r"-\d+x\d+(\.\w+)$", r"\1", m.group(1))
        if "uploads" not in u or u in seen:
            continue
        seen.add(u)
        # קרדיט: הטקסט שאחרי התמונה עד 400 תווים
        tail = html_body[m.end():m.end() + 400]
        cm = re.search(r"צילום[^<|]{0,60}", strip(tail))
        out.append({"src": "article", "url": u, "role": "inline",
                    "credit": cm.group(0).strip() if cm else ""})
    return out


def recent_downloads(hours=36):
    """**משני**: קבצי פלאש 90 טריים ש דור הכין (`F<YYMMDD><XX><NNN>.jpg`).
    מסונן לפי טריות — קבצים ישנים שייכים לכתבה קודמת ואסור להציג אותם כמקור."""
    import time
    cutoff = time.time() - hours * 3600
    found = []
    for pat in ("F[0-9][0-9][0-9][0-9][0-9][0-9]*.jpg", "F[0-9][0-9][0-9][0-9][0-9][0-9]*.JPG"):
        found += glob.glob(os.path.expanduser(f"~/Downloads/{pat}"))
    out = []
    for f in sorted(found, key=os.path.getmtime, reverse=True):
        if os.path.getmtime(f) < cutoff:
            continue
        m = re.match(r"F\d{6}([A-Z]{2,4})", os.path.basename(f))
        code = m.group(1) if m else ""
        out.append({"src": "downloads", "file": f,
                    "credit": f"צילום: {SHOOTERS.get(code, '___')} / פלאש 90"})
    return out


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {"done": []}


def process(art, imgs):
    folder = os.path.join(DEST, f"{art['date'] or datetime.date.today().isoformat()}-{art['slug']}")
    os.makedirs(folder, exist_ok=True)
    json.dump(art, open(os.path.join(folder, "article.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(imgs, open(os.path.join(folder, "images.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return folder


def main():
    args = sys.argv[1:]
    st = load_state()
    if "--slug" in args:
        posts = _get(f"{BASE}/posts?slug={args[args.index('--slug')+1]}&_fields={FIELDS}")
    elif "--latest" in args:
        posts = _get(f"{BASE}/posts?per_page=1&_fields={FIELDS}")
    else:
        posts = [p for p in _get(f"{BASE}/posts?per_page=10&orderby=date&order=desc&_fields={FIELDS}")
                 if p.get("slug") not in st["done"]]
    if not posts:
        print("אין כתבות חדשות."); return

    for p in posts:
        art = to_article(p)
        if not art["slug"]:
            continue
        imgs = article_images(art["slug"], art.get("img", "")) + recent_downloads()
        folder = process(art, imgs)
        st["done"] = list(dict.fromkeys(st["done"] + [art["slug"]]))
        print(f"\n{'='*62}\n▸ {art['title'][:60]}\n  מאת {art['author']} · {art['date']}")
        print(f"  תיקייה: {folder}")
        art_i = [i for i in imgs if i["src"] == "article"]
        dl_i  = [i for i in imgs if i["src"] == "downloads"]
        print(f"  תמונות מהכתבה ({len(art_i)}) — המקור העיקרי:")
        for i in art_i[:8]:
            print(f"     {i['url'].split('/')[-1]}  ·  {i.get('credit','') or i['role']}")
        if dl_i:
            print(f"  + קבצי פלאש 90 טריים ב-Downloads ({len(dl_i)}):")
            for i in dl_i[:6]:
                print(f"     {os.path.basename(i['file'])}  ·  {i['credit']}")
        if not art_i and not dl_i:
            print("  ⚠ לא נמצאו תמונות — לבדוק מול דור.")
        print("""
  הפעל את הסקילים הקיימים על התיקייה הזו, בסדר הזה:
     1. hamakom-graphic    ← 3 גרפיקות (וואטסאפ / פיד / סטורי)
     2. hamakom-carousel   ← קרוסלה 8-10 שקפים
     3. hamakom-reel       ← ריל (דורש חומרי גלם)""")

    os.makedirs(DEST, exist_ok=True)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
