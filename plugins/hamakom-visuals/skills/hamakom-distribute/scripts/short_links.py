#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
short_links.py - הקישורים הקצרים של המקום לכתבה: ha-makom.co.il/{fb|x|wa|tg}/<key>.

כל קישור קצר הוא הפניה בתוסף Redirection באתר (קבוצה 1, קוד 302) לכתובת הכתבה עם
תגיות UTM של הרשת. כך הקורא רואה קישור קצר, ו-Google Analytics עדיין יודע מאיפה הגיע.
(wp.me לא מתאים: הוא מוחק את פרמטרי ה-UTM. נבדק 2.11.2026.)

ברירת המחדל היא בדיקה בלבד: מה קיים, מה חסר, ולאן כל אחד מפנה. --create יוצר את
החסרים. הפניה קיימת שמפנה למקום אחר לא נדרסת: הסקריפט עוצר ומדווח.

הרצה:
  python3 short_links.py <תיקיית-ההפצה>/article.json <key>            # בדיקה
  python3 short_links.py <תיקיית-ההפצה>/article.json <key> --create   # יצירת החסרים

הפלט: short_links.json באותה תיקייה, ש-write_posts.py קורא.
פרטי הגישה מ-~/.claude/.env (WP_BASE_URL, WP_APP_USERNAME, WP_APP_PASSWORD), לא מודפסים.
"""
import base64, json, os, re, ssl, sys, urllib.request
from urllib.parse import urlencode

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from write_posts import tagged  # noqa: E402

# רשת -> (קידומת בכתובת הקצרה, utm_source)
NETS = {"facebook": ("fb", "facebook"), "x": ("x", "x"),
        "whatsapp": ("wa", "whatsapp"), "telegram": ("tg", "telegram")}

try:
    import certifi
    _CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _CTX = ssl.create_default_context()


def env(key):
    for line in open(os.path.expanduser("~/.claude/.env"), encoding="utf-8"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit(f"חסר {key} ב-~/.claude/.env")


def api(path, body=None):
    base = env("WP_BASE_URL").rstrip("/")
    base = base[:-len("/wp-json")] if base.endswith("/wp-json") else base
    auth = base64.b64encode(f"{env('WP_APP_USERNAME')}:{env('WP_APP_PASSWORD')}".encode()).decode()
    req = urllib.request.Request(
        f"{base}/wp-json/redirection/v1/{path}", method="POST" if body else "GET",
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0"})  # בלי UA האתר מחזיר 403
    with urllib.request.urlopen(req, context=_CTX, timeout=30) as r:
        return json.load(r)


# פייסבוק ואינסטגרם מוסיפים לכל קישור ?fbclid= / ?igsh=, ויש אפליקציות שמוסיפות לוכסן בסוף.
# בלי שתי ההגדרות האלה ההפניה מחזירה 404, והמטמון של LiteSpeed ו-Cloudflare שומר את ה-404
# (11.11.2026, הקישורים של ad-kan-rahat-election). flag_query=ignore: התוספת נזרקת, וה-UTM
# שביעד נשמר; flag_trailing: /wa/key/ מזוהה כמו /wa/key.
MATCH_DATA = {"source": {"flag_query": "ignore", "flag_case": True,
                         "flag_trailing": True, "flag_regex": False}}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit("שימוש: short_links.py article.json <key> [--create]")
    create = "--create" in sys.argv
    art = json.load(open(args[0], encoding="utf-8"))
    key = args[1].strip("/")
    if not re.fullmatch(r"[a-z0-9-]+", key):
        raise SystemExit("ה-key: אותיות לטיניות קטנות, ספרות ומקף בלבד (למשל carlson)")

    existing = {i["url"]: i for i in api("redirect?" + urlencode(
        {"filterBy[url]": f"/{key}", "per_page": 100})).get("items", [])}
    out, problems, missing = {}, [], 0
    for net, (prefix, source) in NETS.items():
        path, target = f"/{prefix}/{key}", tagged(art, source)
        cur = existing.get(path)
        if cur:
            dest = (cur.get("action_data") or {}).get("url", "")
            if dest != target:
                problems.append(f"{path} כבר קיים ומפנה ל-{dest}")
                continue
            src = ((cur.get("match_data") or {}).get("source") or {})
            if any(src.get(k) != MATCH_DATA["source"][k] for k in ("flag_query", "flag_trailing")):
                if create:
                    api(f"redirect/{cur['id']}", {
                        "url": path, "action_type": cur["action_type"],
                        "action_code": cur["action_code"], "match_type": cur["match_type"],
                        "group_id": cur["group_id"], "action_data": cur["action_data"],
                        "match_data": {"source": {**src, "flag_query": "ignore",
                                                  "flag_trailing": True}}})
                    state = "קיים, תוקן"
                else:
                    state, missing = "קיים בהגדרה ישנה (--create יתקן)", missing + 1
            else:
                state = "קיים"
        elif create:
            api("redirect", {"url": path, "action_type": "url", "action_code": 302,
                             "match_type": "url", "group_id": 1, "regex": False,
                             "match_data": MATCH_DATA,
                             "action_data": {"url": target}})
            state = "נוצר"
        else:
            state, missing = "חסר (להריץ עם --create)", missing + 1
        out[net] = f"ha-makom.co.il{path}"
        print(f"  {state:<26} ha-makom.co.il{path}  ->  {target}")

    if problems:
        raise SystemExit("עצירה, לא נדרס כלום:\n  " + "\n  ".join(problems)
                         + "\nלבחור key אחר או לבדוק עם דור.")
    if missing:
        return
    p = os.path.join(os.path.dirname(os.path.abspath(args[0])), "short_links.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  ✓ {p}")


if __name__ == "__main__":
    main()
