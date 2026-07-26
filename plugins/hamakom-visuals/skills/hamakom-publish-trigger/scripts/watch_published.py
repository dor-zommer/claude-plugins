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
            "FFSS": "שרה שומאן", "MG": "מרים אלסטר"}


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


def local_images():
    """**בדיקת ~/Downloads חוסמת** (חוק 5 ב-hamakom-carousel): דור מכין תמונות
    פלאש 90 מראש — הן המקור. לא להוריד מהאתר לפני שבודקים כאן."""
    found = []
    for pat in ("F[0-9][0-9][0-9][0-9][0-9][0-9]*.jpg", "F[0-9][0-9][0-9][0-9][0-9][0-9]*.JPG"):
        found += glob.glob(os.path.expanduser(f"~/Downloads/{pat}"))
    out = []
    for f in sorted(found, key=os.path.getmtime, reverse=True)[:12]:
        m = re.match(r"F\d{6}([A-Z]{2,4})", os.path.basename(f))
        code = m.group(1) if m else ""
        out.append({"file": f, "credit": f"צילום: {SHOOTERS.get(code, '___')} / פלאש 90"})
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

    imgs = local_images()
    for p in posts:
        art = to_article(p)
        if not art["slug"]:
            continue
        folder = process(art, imgs)
        st["done"] = list(dict.fromkeys(st["done"] + [art["slug"]]))
        print(f"\n{'='*62}\n▸ {art['title'][:60]}\n  מאת {art['author']} · {art['date']}")
        print(f"  תיקייה: {folder}")
        if imgs:
            print(f"  תמונות שדור הכין ב-Downloads ({len(imgs)}) — **אלה המקור**:")
            for i in imgs[:6]:
                print(f"     {os.path.basename(i['file'])}  ·  {i['credit']}")
        else:
            print("  ⚠ אין קבצי פלאש 90 ב-Downloads — לבדוק מול דור לפני הורדה מהאתר.")
        print("""
  הפעל את הסקילים הקיימים על התיקייה הזו, בסדר הזה:
     1. hamakom-graphic    ← 3 גרפיקות (וואטסאפ / פיד / סטורי)
     2. hamakom-carousel   ← קרוסלה 8-10 שקפים
     3. hamakom-reel       ← ריל (דורש חומרי גלם)""")

    os.makedirs(DEST, exist_ok=True)
    json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
