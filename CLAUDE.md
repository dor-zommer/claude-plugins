# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## מה הריפו הזה

**Claude Code plugin marketplace פנימי** של "המקום הכי חם בגיהנום" (ha-makom.co.il). לא אפליקציה — אוסף פלאגינים שחברי המערכת מתקינים ב-Claude Code כדי לעבוד. אין "build" ואין "test suite"; היחידה הרצה היחידה היא שרת ה-MCP תחת `servers/osint-db/`. רוב התוכן הוא Markdown של סקילים, commands ו-agents.

הריפו הפרטי הקנוני: `github.com/dor-zommer/claude-plugins` (marketplace בשם `hamakom-plugins`).

## ארכיטקטורה

```
.claude-plugin/marketplace.json   ← הרשומה שמגדירה את המרקטפלייס ומונה את כל הפלאגינים
plugins/<name>/
  .claude-plugin/plugin.json      ← מניפסט הפלאגין (name, version, description)
  .mcp.json                       ← (רק hamakom-osint) חיבור לשרת MCP מרוחק
  skills/<skill>/SKILL.md         ← סקיל = תיקייה עם SKILL.md + frontmatter
  commands/*.md                   ← slash commands (searchfit-seo)
  agents/*                        ← subagents (searchfit-seo בלבד)
servers/osint-db/                 ← קוד שרת ה-MCP (FastMCP/Python) + Docker + sync
```

שרשרת הטעינה: `marketplace.json` מונה כל פלאגין דרך `source: ./plugins/<name>` → כל `plugin.json` מצהיר על עצמו → Claude Code מגלה `skills/`, `commands/`, `agents/` אוטומטית לפי קונבנציה (לא נדרשת הצהרה מפורשת של כל סקיל, אם כי חלק מהמניפסטים מוסיפים `"skills": [...]`).

### עמוד השדרה: osint-db

זה החוט שמחבר בין הפלאגינים, ולא ברור מקריאת פלאגין בודד:

- **`hamakom-osint`** הוא הבעלים של החיבור. ה-`.mcp.json` שלו מגדיר שרת HTTP MCP בשם `osint-db` שקורא משתנה סביבה אחד: `${OSINT_DB_MCP_URL}`. **האימות הוא `?key=` בשאילתה, לא `Authorization: Bearer`** — ה-nginx על ה-VM בודק רק את `$arg_key`, ולכן הטוקן חייב להיות חלק מה-URL (תוקן 29.07.2026; קודם לכן נשלח Bearer וכל בקשה חטפה 401). הסקילים שלו קוראים ל-5 כלים: `list_tables`, `describe_table`, `query_db`, `search_entity`, `new_since` (מופיעים ב-frontmatter כ-`mcp__osint-db__*`).
- **שלושה פלאגינים נוספים תלויים באותו שרת ולא מגדירים אותו:** `hamakom-factcheck` (6 סקילים), `hamakom-desk` (4), `hamakom-leads` (1) — סה"כ 11 סקילים שקוראים ל-`mcp__osint-db__*`. **שרתי MCP הם per-plugin ועולים רק כשהפלאגין שלהם מופעל** (מתועד), ולכן התקנה של אחד מהם לבדו לא מביאה את השרת. **הפתרון (19.07.2026): כל ארבעתם מכריזים `"dependencies": ["hamakom-osint"]` ב-`plugin.json`**, כדי שההתקנה תגרור את השרת אוטומטית. בלי השרת שאר הסקילים עובדים; רק אלה שתלויים ב-DB מחזירים ריק.
- **אין דרך להכריז MCP ברמת המרקטפלייס.** שורש `marketplace.json` לא תומך ב-`mcpServers` (רק רשומת פלאגין בודדת יכולה). **לא לשכפל את אותו `.mcp.json` לכמה פלאגינים** — התנהגות ה-dedupe לפי שם שרת אינה מתועדת.
- השרת עצמו (`servers/osint-db/server.py`) הוא FastMCP קריא-בלבד מעל SQLite (`mode=ro`), עם תקרות קשיחות: `MAX_LIMIT=500`, `MAX_OUTPUT_CHARS=50_000`, `QUERY_TIMEOUT_SEC=10`. טבלאות: `exemptions`, `knesset_bills`, `knesset_votes`, `mavat_plans`, `legislation`, `mevaker_reports`, `police_announcements` ועוד. אימות נעשה **לפני** השרת (nginx Bearer או Tailscale), לא בתוכו.

### מוסכמת SKILL.md

כל `SKILL.md` נפתח ב-frontmatter עם:
- `name` + `description` בעברית שכולל **ביטויי הפעלה מפורשים** ("הפעל כשדור כותב …") — זה מה שמפעיל את הסקיל, אז שינוי ניסוח משנה התנהגות.
- `allowed-tools` — רשימת הכלים המותרים, כולל כלי ה-`mcp__osint-db__*` בסקילים שתלויים ב-DB.

### עיצוב ויזואלי — מקור אמת יחיד

כל סקילי `hamakom-visuals` (graphic/carousel/reel) נשענים על `plugins/hamakom-visuals/design-system/HAMAKOM-DS-2026.md`. זה מקור-האמת למותג: שנהב `#faf9f5` / דיו `#141413` / טרקוטה `#D97757`, Publico Headline Hebrew + Graphik HLAR, פסי-חתימה טריקולור. שינוי מותג = עריכת הקובץ הזה, לא כל סקיל בנפרד.

## משמעת גרסאות (חשוב)

בכל שינוי מהותי בפלאגין צריך **שני** עדכוני גרסה:
1. `version` ב-`plugins/<name>/.claude-plugin/plugin.json`.
2. `metadata.version` ב-`.claude-plugin/marketplace.json` (גרסת המרקטפלייס הכוללת).

בלי bump, `/plugin marketplace update` לא מושך את השינוי אצל הצוות. ראה `git log` — יש commit ייעודי "bump גרסאות" אחרי סנכרונים.

## פרסום ועדכון

```bash
# עדכון (התהליך הרגיל)
git add . && git commit -m "…" && git push        # ל-github.com/dor-zommer/claude-plugins
# הצוות מקבל: /plugin marketplace update hamakom-plugins
```

התקנה אצל חבר צוות: `/plugin marketplace add dor-zommer/claude-plugins` → `/plugin install <name>@hamakom-plugins`. פירוט + הקמת שרת MCP + פתרון תקלות ב-`INSTALL.md`.

## פריסת שרת ה-MCP (חד-פעמי, על VM)

```bash
cd servers/osint-db && docker compose up -d --build   # קשור ל-127.0.0.1:8765
```

עדכון הנתונים: `servers/osint-db/scripts/sync-db.sh`. פרטי nginx/Tailscale/token — ב-`servers/osint-db/README.md`.

## סודות — לא בריפו

אין בריפו אף מפתח API. `osint.db`, `.env`, `__pycache__` מוחרגים ב-`.gitignore`. משתני `OSINT_DB_*` מוגדרים ב-`~/.zshrc` של כל משתמש/ת; חיבורי Notion/Gmail/Drive/Figma דרך ה-connectors האישיים של Claude. אל תוסיף טוקנים, `.env`, או את קובץ ה-DB.
