# osint-db — שרת MCP מרוחק למסד ה-OSINT הממשלתי

שרת MCP (FastMCP 2.x, טרנספורט HTTP) שמגיש את `osint.db` — מסד SQLite עם דאטה ממשלתי ישראלי (exemptions, knesset_bills, knesset_votes, mavat_plans, legislation, mevaker_reports, police_announcements ועוד) — לכל חברי הצוות דרך הפלאגין `hamakom-research`.

חמישה כלים, כולם קריאה-בלבד:

| כלי | מה עושה |
|---|---|
| `list_tables()` | כל הטבלאות + מספר שורות |
| `describe_table(name)` | עמודות הטבלה (PRAGMA table_info) |
| `query_db(sql, limit)` | SELECT/WITH בלבד; limit עד 500; פלט עד 50,000 תווים; חיתוך אחרי ~מיליון צעדי VM או 10 שניות |
| `search_entity(name, per_table_limit)` | חיפוש שם אדם/חברה במקביל בכל הטבלאות (ספקים בפטורים, ח"כים, חקיקה, מבקר, תכנון, החלטות). חיבור-מוגן נפרד לכל טבלה כדי שטבלה כבדה לא תרעיב את השאר |
| `new_since(table, since, limit)` | שורות שנקלטו מאז תאריך (לפי first_seen_at), לסריקת לידים יומית |

המסד נפתח read-only (`mode=ro`) וממופה לקונטיינר כ-volume לקריאה בלבד — אין שום דרך לכתוב אליו דרך השרת.

## פריסה על VM

```bash
# על ה-VM:
sudo mkdir -p /opt/osint-db && cd /opt/osint-db
# העתיקו לכאן את: server.py, requirements.txt, Dockerfile, docker-compose.yml
# והניחו את osint.db באותה תיקייה (או הריצו sync-db.sh מהמק — ראו בהמשך)
docker compose up -d --build
docker compose logs -f osint-db   # לוודא שעלה על פורט 8765
```

הקונטיינר קשור ל-`127.0.0.1:8765` בלבד — הוא לא חשוף לאינטרנט ישירות. הגישה מבחוץ עוברת דרך nginx (עם בדיקת טוקן) או דרך Tailscale.

## אימות טוקן — nginx reverse proxy

לשרת אין אימות מובנה; nginx בודק את כותרת ה-Authorization לפני שהבקשה מגיעה אליו. ב-server block של הדומיין (עם TLS — חובה, הטוקן עובר בכותרת):

```nginx
location /mcp {
    # בדיקת Bearer token — החליפו את REPLACE_WITH_LONG_RANDOM_TOKEN
    if ($http_authorization != "Bearer REPLACE_WITH_LONG_RANDOM_TOKEN") {
        return 401;
    }

    proxy_pass http://127.0.0.1:8765;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # MCP over HTTP משתמש ב-streaming — בלי buffering ועם timeout נדיב
    proxy_buffering off;
    proxy_read_timeout 300s;
}
```

יצירת טוקן חזק: `openssl rand -hex 32`. אחרי עדכון הקונפיג: `sudo nginx -t && sudo systemctl reload nginx`.

נתיב ה-MCP של FastMCP בטרנספורט HTTP הוא `/mcp`, ולכן ה-URL החיצוני הוא `https://<vm-host>/mcp`.

## חלופה: Tailscale במקום חשיפה פומבית

אם לא רוצים לחשוף את השרת לאינטרנט בכלל:

1. מתקינים Tailscale על ה-VM ועל המחשבים של חברי הצוות (כולם באותו tailnet).
2. ב-docker-compose.yml אפשר להשאיר את הקשירה ל-localhost ולהשתמש ב-`tailscale serve` להפניית הפורט, או לקשור ל-IP של ה-tailnet.
3. ה-URL הופך ל-`http://<שם-המכונה-ב-tailnet>:8765/mcp` (או https דרך tailscale serve), והרשת עצמה היא שכבת האימות — אפשר אז להגדיר `OSINT_DB_TOKEN` לערך דמה.

זו האופציה הפשוטה והבטוחה יותר לצוות קטן; nginx + טוקן מתאים כשצריך גישה ממכונות שלא ב-tailnet.

## עדכון המסד — sync-db.sh

המסד נבנה ומתעדכן אצל דור במק. כדי לדחוף גרסה טרייה ל-VM:

```bash
cd servers/osint-db/scripts
# עריכה חד-פעמית של המשתנים בראש הקובץ: VM_HOST, VM_PATH, LOCAL_DB
./sync-db.sh
```

הסקריפט מעלה את הקובץ ב-scp בשם זמני, מחליף אטומית ל-`osint.db`, ומריץ `docker compose restart osint-db` כדי שהשרת ייפתח מול הקובץ החדש.

## איך חברי צוות מתחברים

כל חבר/ת צוות מוסיף/ה לפרופיל השל (`~/.zshrc` או `~/.bashrc`):

```bash
export OSINT_DB_MCP_URL=https://<vm-host>/mcp
export OSINT_DB_TOKEN=<הטוקן שקיבלתם מדור>
```

זהו. הפלאגין `hamakom-research` (דרך ה-`.mcp.json` שלו) מחבר את שרת ה-osint-db אוטומטית בכל סשן Claude Code — בלי קונפיגורציה נוספת. בדיקה מהירה: בתוך Claude Code לבקש "תריץ list_tables על osint-db".

אל תשמרו את הטוקן בריפו או בקבצים משותפים — רק במשתני סביבה מקומיים.
