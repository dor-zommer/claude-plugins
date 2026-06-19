# hamakom-plugins — מרקטפלייס פלאגינים פנימי של "המקום הכי חם בגיהנום"

ריפו זה הוא Claude Code plugin marketplace פנימי לעבודת המערכת של ha-makom.co.il.

## מבנה הריפו

```
hamakom-claude-plugins/
├── .claude-plugin/
│   └── marketplace.json        ← הגדרת המרקטפלייס (hamakom-plugins)
├── plugins/
│   ├── hamakom-leads/          ← בריף לידים ועורך בוקר מ-osint-db (hamakom-leads)
│   ├── hamakom-factcheck/      ← אימות: תוכן ויראלי, נתונים, ציטוטים, גיאו, פורנזיקה, אימות כתבה
│   ├── hamakom-osint/          ← תחקיר מעל osint-db (פטורים/כנסת/תכנון/מבקר) + חיבור MCP
│   ├── hamakom-editorial/      ← ניתוח דוחות, עריכה לשונית, עריכה ישירה, Yoast, הכנה לפרסום
│   ├── hamakom-desk/           ← ניהול מערכת: investigations-sync, weekly-lineup, weekly-newsletter, site-strategist
│   ├── hamakom-visuals/        ← מדיה: גרפיקות כתבה, קרוסלות אינסטגרם, רילים
│   └── searchfit-seo/          ← ערכת SEO לעברית/חדשות, מותאמת ל-ha-makom.co.il
├── servers/
│   └── osint-db/               ← שרת MCP מרוחק למסד ה-OSINT (פריסה על VM)
├── README.md
└── .gitignore
```

כל פלאגין מכיל `.claude-plugin/plugin.json` + תיקיות `skills/`, `commands/`, `agents/` לפי הצורך.

## איך מפרסמים (פעם אחת, ע"י דור)

1. צרו ריפו **פרטי** ב-GitHub, למשל `ha-makom/claude-plugins`.
2. מתוך תיקיית הריפו המקומית:

```bash
cd hamakom-claude-plugins
git init
git add .
git commit -m "Marketplace: 4 internal plugins (newsroom, research, visuals, seo) + osint-db server"
git branch -M main
git remote add origin git@github.com:ha-makom/claude-plugins.git
git push -u origin main
```

עדכון בהמשך: עורכים קבצים → `git add` → `git commit` → `git push`. חברי הצוות מקבלים את העדכון עם `/plugin marketplace update hamakom-plugins`.

## איך כל חבר/ת צוות מתקין/ה

בתוך Claude Code (צריך גישה לריפו הפרטי, כלומר להיות מחוברים ל-GitHub עם הרשאה):

```
/plugin marketplace add ha-makom/claude-plugins
```

ואז התקנת פלאגינים, למשל:

```
/plugin install hamakom-leads@hamakom-plugins
/plugin install hamakom-factcheck@hamakom-plugins
/plugin install hamakom-osint@hamakom-plugins
/plugin install hamakom-editorial@hamakom-plugins
/plugin install hamakom-desk@hamakom-plugins
/plugin install hamakom-visuals@hamakom-plugins
/plugin install searchfit-seo@hamakom-plugins
```

או דרך התפריט: `/plugin` → Browse marketplaces → hamakom-plugins → Enable.

## ל-Enterprise עם MDM (התקנה מנוהלת לכל הצוות)

אפשר לחלק את המרקטפלייס והפלאגינים אוטומטית דרך `managed-settings.json` (ב-macOS: `/Library/Application Support/ClaudeCode/managed-settings.json`):

```json
{
  "extraKnownMarketplaces": {
    "hamakom-plugins": {
      "source": {
        "source": "github",
        "repo": "ha-makom/claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "hamakom-leads@hamakom-plugins": true,
    "hamakom-factcheck@hamakom-plugins": true,
    "hamakom-osint@hamakom-plugins": true,
    "hamakom-editorial@hamakom-plugins": true,
    "hamakom-desk@hamakom-plugins": true,
    "hamakom-visuals@hamakom-plugins": true,
    "searchfit-seo@hamakom-plugins": true
  }
}
```

כך כל מחשב מנוהל מקבל את המרקטפלייס והפלאגינים מופעלים, בלי התקנה ידנית.

## osint-db — שרת MCP מרוחק

מסד ה-OSINT הממשלתי (osint.db) מוגש לכל הצוות משרת MCP מרוחק שרץ על VM. הפלאגין `hamakom-osint` מתחבר אליו אוטומטית — כל משתמש/ת רק מגדיר/ה בפרופיל השל:

```bash
export OSINT_DB_MCP_URL=https://<vm-host>/mcp
export OSINT_DB_TOKEN=<token>
```

קוד השרת, הוראות פריסה (docker compose), אימות טוקן ב-nginx, חלופת Tailscale ועדכון המסד עם `sync-db.sh` — הכל ב-[`servers/osint-db/README.md`](servers/osint-db/README.md).

## סודות ומפתחות — לא בריפו

**אין בריפו הזה אף מפתח API.** כל משתמש/ת מגדיר/ה סודות בסביבה המקומית שלו/ה — למשל `OSINT_DB_MCP_URL` ו-`OSINT_DB_TOKEN` שלמעלה (מומלץ ב-`~/.zshrc`). חיבורי Notion / Gmail / Drive / Calendar / Figma נעשים דרך ה-connectors של Claude/Cowork לכל משתמש בנפרד. אל תוסיפו מפתחות, טוקנים או קבצי `.env` לריפו.
