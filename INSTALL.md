# התקנה — hamakom-plugins

מדריך התקנה של ה־marketplace `hamakom-plugins` ב־Claude Code, כולל הקמת שרת ה־MCP `osint-db`.

הריפו **פרטי** (`github.com/dor-zommer/claude-plugins`). לכן לפני ההתקנה צריך שהמכונה/החשבון שמתקין יהיה מחובר ל־GitHub עם הרשאת קריאה לריפו.

---

## 1. אימות GitHub (חובה — ריפו פרטי)

על המכונה של היוזר הארגוני, ודאו חיבור ל־GitHub:

```bash
gh auth login          # בחרו github.com → HTTPS → התחברו לחשבון עם גישה לריפו
gh auth status         # לוודא שמחובר
```

בלי זה, `marketplace add` ייכשל עם שגיאת "repository not found".

---

## 2. הוספת ה־marketplace והתקנת הפלאגינים

בתוך Claude Code:

```
/plugin marketplace add dor-zommer/claude-plugins
```

ואז התקינו את הפלאגינים הרצויים (כולם או חלק):

```
/plugin install hamakom-leads@hamakom-plugins
/plugin install hamakom-factcheck@hamakom-plugins
/plugin install hamakom-osint@hamakom-plugins
/plugin install hamakom-desk@hamakom-plugins
/plugin install hamakom-visuals@hamakom-plugins
/plugin install searchfit-seo@hamakom-plugins
```

אפשר גם דרך התפריט האינטראקטיבי: `/plugin` ← Browse marketplaces.

לעדכון בעתיד (אחרי `git push` של גרסה חדשה):

```
/plugin marketplace update hamakom-plugins
```

---

## 3. הקמת שרת ה־MCP `osint-db` (נדרש רק ל־`hamakom-osint`)

הפלאגין `hamakom-osint` מתחבר לשרת MCP מרוחק שמגיש את `osint.db`. שני סקילים נוספים שתלויים בדאטה
(ב־`hamakom-leads` וב־`hamakom-factcheck`) משתמשים בו גם כן. בלי השרת, שאר הפלאגינים יעבדו רגיל — רק
הסקילים שתלויים ב־DB לא יחזירו תוצאות.

### 3א. משתני סביבה (על כל מכונה שמשתמשת ב־DB)

הוסיפו ל־`~/.zshrc` (או `~/.bashrc`):

```bash
export OSINT_DB_MCP_URL='<כתובת ה-endpoint המלאה שקיבלתן מדור, כולל ?key=...>'
```

**משתנה אחד בלבד.** ה-nginx על ה-VM מאמת את פרמטר `?key=` בשאילתה, **לא** כותרת
`Authorization: Bearer` — לכן הטוקן חייב להיות חלק מה-URL, וממילא אין `OSINT_DB_TOKEN`
נפרד. שימו את ה-URL במרכאות בודדות כדי ש-`?` ו-`&` לא יתפרשו ב-shell.

ה־`.mcp.json` של הפלאגין קורא את המשתנה הזה אוטומטית בכל סשן.
**ה-URL כולו הוא סוד** — אל תשמרו אותו בריפו, בנושיין, בוואטסאפ או בכל מקום משותף;
רק במשתנה סביבה מקומי.

### 3ב. פריסת השרת (חד־פעמי, על VM)

הקוד המלא נמצא ב־`servers/osint-db/` עם הוראות מפורטות ב־`servers/osint-db/README.md`. בקצרה:

```bash
sudo mkdir -p /opt/osint-db && cd /opt/osint-db
# העתיקו לכאן: server.py, requirements.txt, Dockerfile, docker-compose.yml + osint.db
docker compose up -d --build
```

השרת קשור ל־`127.0.0.1:8765` בלבד. הגישה מבחוץ עוברת דרך **nginx + בדיקת Bearer token** או דרך
**Tailscale** (פשוט ובטוח יותר לצוות קטן). פירוט מלא של שתי האופציות — ב־README של השרת.

### 3ג. בדיקה

בתוך Claude Code, אחרי התקנת `hamakom-osint`:

> תריץ `list_tables` על osint-db

אם חוזרת רשימת טבלאות — החיבור עובד.

---

## פתרון תקלות

| תקלה | סיבה | פתרון |
|---|---|---|
| `repository not found` ב־`marketplace add` | אין אימות GitHub / אין גישה לריפו הפרטי | `gh auth login` עם חשבון שיש לו גישה |
| הפלאגין מותקן אבל סקילי DB ריקים | חסר `OSINT_DB_MCP_URL`, או שהשרת לא רץ | הגדירו את משתני הסביבה; ודאו שהקונטיינר עלה (`docker compose logs -f osint-db`) |
| `401` מהשרת | הטוקן שגוי, או שנשלח ככותרת Bearer במקום כ־`?key=` בשאילתה | ודאו ש־`OSINT_DB_MCP_URL` כולל `?key=<טוקן>` בסוף, ושהטוקן תואם לזה שב־nginx |

חלופה לציבורי: אם לא רוצים להתעסק עם אימות GitHub בכל מכונה, אפשר להפוך את הריפו לציבורי —
`gh repo edit dor-zommer/claude-plugins --visibility public`. שימו לב שזה חושף את כל מבנה העבודה המערכתי.
