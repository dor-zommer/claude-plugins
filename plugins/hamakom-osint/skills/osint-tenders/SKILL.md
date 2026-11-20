---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__new_since mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-tenders
version: '0.2.0'
description: >-
  מכרזים פומביים של משרדי הממשלה ויחידות הסמך עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db - gov_tenders (22,330 מכרזים מ-mr.gov.il, משרדיים ומרכזיים, ארכיון ופעיל), gov_tender_awards (10,652 שורות: 39 זוכים רשמיים, והשאר ספקים ששולם להם מכוח מפתח המכרז), ומכרזי משרד הביטחון (mod_tenders, ראה osint-money). מה פורסם, מה בוטל, מי קיבל כסף מכוח מכרז ואצל איזה מפרסם. הפעל כשדור כותב "מכרזים של משרד X", "איזה מכרזים פורסמו", "מכרז שבוטל", "מי זכה במכרז", "מי קיבל כסף מהמכרז", "מכרז מרכזי", "מכרזים פתוחים", "באיזה מכרזים הספק הזה". כל פריט הוא ליד לבדיקה מול דף המכרז ב-mr.gov.il, לא ממצא מאומת. לפטורים ממכרז ראה osint-exemptions; להתקשרויות בפועל ראה osint-money.
---

# osint-tenders - מכרזי הממשלה

סקיל לשתי טבלאות שנטענו ב-8.11.2026 ואין להן סקיל: המכרזים הפומביים של כל משרדי הממשלה מלבד הביטחון (`gov_tenders`), והחיבור שלהם לספקים (`gov_tender_awards`). מכרזי משרד הביטחון בטבלה נפרדת, `mod_tenders`, ומטופלים ב-osint-money (מצב ד).

- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.

## עקרונות יסוד

1. **מכרז פומבי הוא הדרך התקינה.** מכרז שפורסם אינו ליד. הסיפור הוא בחריגה: מכרז שבוטל ואחריו התקשרות בלי מכרז, מכרז שנתפר (תנאי סף צרים, מועד הגשה קצר), או מכרז שהכסף מכוחו זורם לספק אחד לאורך שנים.
2. **באתר אין זוכה, ולכן גם במאגר כמעט אין.** `gov_tender_awards.basis` אומר מאיפה השורה:
   - `official`: 39 זוכים שמינהל הרכש פרסם בדוח המכרזים של data.gov.il (עודכן לאחרונה ב-2021). בלי סכום.
   - `paid_under_key`: 10,613 שורות (4,300 מכרזים, 4,281 ספקים). ספק ששולם לו בהתקשרות ב-`budget_contracts` שה-`tender_key` שלה מצביע על המכרז, לפי מספר רשם בלבד ובלי גופי ממשל. **זה אינו "זכה במכרז"**: מכרז מסגרת או מכרז מרכזי משמש עשרות ספקים, וחלק מהקישורים שגויים במקור. כותבים "שולם לו בהתקשרות מכוח המכרז".
3. **`amount_ils` ב-`paid_under_key` כבר בש"ח**, לפי השער היציג ביום ההזמנה, ובלי שורות שהוחלפו (`superseded`). אין צורך להמיר שוב. הסכום הוא היקף ההזמנות ולא מה ששולם בפועל.
4. **התאמה לפי מספר רשם, לא לפי שם.** `supplier_reg` הוא מספר תאגיד בן 9 ספרות.

## כלי קודם

- לספק או לגוף בשמו: `search_entity("שם")` ואחריו `entity_profile(id)`. במודל הישויות המכרז הוא `mr.tender.{publication_id}`, והזוכים הרשמיים מופיעים בפרופיל תחת "זכייה במכרז, כפי שפורסמה". `paid_under_key` **אינו** בפרופיל, כי הכסף כבר נספר שם בהתקשרויות. לכן "באיזה מכרזים שולם לספק" נשאל ב-`query_db` (מצב ב).
- מה חדש: `new_since("gov_tenders", "2026-11-01")` מחזיר לפי `first_seen_at`. אחרי הטעינה הראשונה ב-8.11.2026 כל המכרזים ההיסטוריים נושאים את אותו יום, ולכן "מה פורסם" נשאל לפי `publication_date` (מצב א).
- `query_db` לכל השאר.

**טריות:** לפני מסקנה של "אין במאגר", בדוק שהמקור רץ:
```sql
SELECT source, max(started_at) last_run FROM scrape_runs
WHERE status IN ('ok','warn') AND source IN ('gov_tenders','gov_tenders_full','gov_tenders_awards')
GROUP BY 1
```
הקרון: כל שש שעות (`gov_tenders`), מלא בשבת, והזוכים ביום ראשון.

## מלכודות - קרא לפני שאתה כותב SQL

| מלכודת | מה עושים |
|---|---|
| `publication_date` שגוי במקור: מכרז אחד ב-2203, אחד ב-1016, 43 ריקים (נמדד 20.11.2026) | כל סינון לפי תאריך עם גבול עליון `<= CURRENT_DATE` |
| שורות בדיקה של המערכת ("TEST 19/11 - לא להתייחס"), 3 שורות | `title NOT ILIKE 'TEST%'` |
| `status` הוא טקסט חופשי של האתר: "סגור", "חלף מועד הגשה", "מבוטל", "עודכן", "פורסם", "חדש", "עתידי", "התקשרות בתוקף", ופעם אחת "Published" | סופרים לפי `status` מדויק, ומציגים אותו כמו שהוא |
| `tender_type`: מכרז פומבי 20,911, RFI 1,011, מכרז מרכזי 252, רשימת מציעים 156 | RFI הוא בקשה לקבלת מידע, לא מכרז |
| `submission_deadline` הוא טקסט (`2026-12-29T10:00`) | משווים ב-`substr(submission_deadline,1,10)` מול `to_char(CURRENT_DATE,'YYYY-MM-DD')` |
| שם המפרסם משתנה: "משרד הבריאות - המרכז הרפואי ע"ש חיים שיבא, תל השומר" ו"...עש חיים שיבא..." הם שני ערכים | הוצא את הרשימה המדויקת (למטה), ואחד את הכתיבים בעצמך |
| `title` בלי אינדקס | `LIKE` על 22 אלף שורות מהיר מספיק. אם מצמצמים, `publisher =` מאונדקס |

**עמודות מאונדקסות:** `publication_id` (מפתח), `publisher`, `status`, `publication_date`, `update_date`. ב-`gov_tender_awards`: `(publication_id, supplier_reg, basis)` ו-`supplier_reg`.

## מצב א - מה פורסם ומה בוטל

שמות המפרסמים המדויקים:
```sql
SELECT publisher, count(*) n FROM gov_tenders GROUP BY 1 ORDER BY 2 DESC LIMIT 200
```

מה פורסם בחודש האחרון:
```sql
SELECT publication_id, tender_kind, tender_type, title, publisher, status,
       publication_date, submission_deadline, detail_url
FROM gov_tenders
WHERE publication_date BETWEEN CURRENT_DATE - 30 AND CURRENT_DATE
  AND title NOT ILIKE 'TEST%'
ORDER BY publication_date DESC
LIMIT 60
```

מכרזים של משרד אחד:
```sql
SELECT publication_id, tender_type, title, status, publication_date, submission_deadline, detail_url
FROM gov_tenders
WHERE publisher = '<שם המפרסם המדויק>' AND publication_date <= CURRENT_DATE
ORDER BY publication_date DESC NULLS LAST
LIMIT 60
```

מכרזים שבוטלו (254 בסך הכל):
```sql
SELECT publication_id, publisher, title, tender_type, publication_date, update_date, detail_url
FROM gov_tenders
WHERE status = 'מבוטל' AND publication_date <= CURRENT_DATE
ORDER BY update_date DESC NULLS LAST
LIMIT 60
```

מכרזים פתוחים להגשה:
```sql
SELECT publication_id, publisher, title, tender_type, publication_date, submission_deadline, detail_url
FROM gov_tenders
WHERE substr(submission_deadline,1,10) >= to_char(CURRENT_DATE,'YYYY-MM-DD')
  AND status <> 'מבוטל' AND title NOT ILIKE 'TEST%'
ORDER BY submission_deadline
LIMIT 60
```
**חלון הגשה קצר** הוא שאלה, לא ממצא: `submission_deadline` פחות שבועיים אחרי `publication_date` במכרז פומבי גדול מצדיק לפתוח את המסמכים בדף המכרז.

מכרז לפי נושא:
```sql
SELECT publication_id, publisher, title, tender_type, status, publication_date, detail_url
FROM gov_tenders
WHERE title LIKE '%שמירה%' AND publication_date <= CURRENT_DATE
ORDER BY publication_date DESC NULLS LAST
LIMIT 60
```

## מצב ב - מי קיבל כסף מכוח מכרז

הספקים ששולם להם מכוח מכרז מסוים:
```sql
SELECT a.supplier_reg, a.supplier_name, a.basis, a.contracts, a.amount_ils,
       a.first_order_date, a.last_order_date, t.title, t.publisher, t.detail_url
FROM gov_tender_awards a
LEFT JOIN gov_tenders t ON t.publication_id = a.publication_id
WHERE a.publication_id = '<publication_id>'
ORDER BY a.amount_ils DESC NULLS LAST
```

כל המכרזים שספק אחד מופיע בהם, לפי מספר רשם:
```sql
SELECT a.publication_id, a.basis, a.contracts, a.amount_ils, a.first_order_date, a.last_order_date,
       t.title, t.publisher, t.tender_type, t.detail_url
FROM gov_tender_awards a
LEFT JOIN gov_tenders t ON t.publication_id = a.publication_id
WHERE a.supplier_reg = '<מספר רשם>'
ORDER BY a.amount_ils DESC NULLS LAST
LIMIT 60
```

מכרזים שהכסף מכוחם הלך כמעט כולו לספק אחד (ריכוז). ליד לבדיקה, לא ממצא: מכרז שנועד מראש לספק אחד הוא מצב תקין:
```sql
WITH s AS (
  SELECT publication_id, count(*) suppliers, sum(amount_ils) total, max(amount_ils) top
  FROM gov_tender_awards WHERE basis = 'paid_under_key' AND amount_ils > 0
  GROUP BY 1)
SELECT s.publication_id, s.suppliers, round(s.total) total_ils, round(100 * s.top / s.total) top_pct,
       t.title, t.publisher, t.tender_type, t.detail_url
FROM s JOIN gov_tenders t ON t.publication_id = s.publication_id
WHERE s.total >= 50000000
ORDER BY s.total DESC
LIMIT 40
```

הזוכים הרשמיים:
```sql
SELECT a.publication_id, a.supplier_reg, a.supplier_name, t.title, t.publisher, t.publication_date
FROM gov_tender_awards a LEFT JOIN gov_tenders t ON t.publication_id = a.publication_id
WHERE a.basis = 'official'
ORDER BY t.publication_date DESC NULLS LAST
```

## מצב ג - מכרז שבוטל, ואחריו פטור אצל אותו מפרסם

שני המקורות מגיעים מ-mr.gov.il ושמות המפרסמים זהים (147 מפרסמים משותפים). השאילתה מחזירה פטורים מהחודשים שאחרי ביטול, אצל אותו מפרסם. הקשר בין השניים נבדק בקריאה: נושא, ספק ונימוק:
```sql
WITH c AS (
  SELECT publication_id, title, publisher, update_date AS cancelled_on
  FROM gov_tenders
  WHERE status = 'מבוטל' AND publisher = '<שם המפרסם המדויק>')
SELECT c.publication_id, c.title tender_title, c.cancelled_on,
       e.id exemption_id, e.title exemption_title, e.supplier_names, e.pub_date_iso, e.amount_ils, e.detail_url
FROM c
JOIN exemptions e ON e.publisher = c.publisher
 AND e.pub_date_iso BETWEEN to_char(c.cancelled_on,'YYYY-MM-DD') AND to_char(c.cancelled_on + 180,'YYYY-MM-DD')
 AND e.amount_kind IS NULL
ORDER BY c.cancelled_on DESC, e.pub_date_iso
LIMIT 60
```
באותו מפרסם יש עשרות פטורים בכל חודש, ולכן רוב השורות אינן קשורות לביטול. רק פטור על אותו נושא, בנימוק שמזכיר את המכרז או את הדחיפות, הוא ליד.

## שלב האימות

- **מכרז:** `detail_url` לדף ב-mr.gov.il: מסמכי המכרז, תנאי הסף, ההבהרות והסטטוס.
- **ספק מכוח מכרז:** `paid_under_key` נגזר מ-`budget_contracts`. אמת את ההתקשרות במפתח התקציב לפי הספק והמשרד, ואת הזכייה עצמה מול המשרד.
- **זוכה רשמי:** דוח המכרזים של מינהל הרכש ב-data.gov.il.

## אתיקה

ספק שזכה במכרז או שולם לו מכוח מכרז לא עשה דבר פסול. אל תכתוב "זכה" על `paid_under_key`, ואל תקבע מניע לביטול מכרז. פנה למשרד ולספק לתגובה לפני פרסום.

## דוח הדסק - מבנה קבוע

```markdown
# לידים - מכרזי הממשלה

## טווח הסריקה
[מפרסם, תקופה, סוג מכרז, מתי המקור רץ לאחרונה]

## לידים מדורגים
לכל ליד:
- **המכרז:** [כותרת, מפרסם, publication_id, סוג, סטטוס, תאריכים]
- **הכסף:** [ספקים מכוח המכרז, בסיס (official / paid_under_key), היקף בש"ח]
- **החריגה:** [ביטול ואחריו פטור / ריכוז / חלון הגשה קצר / אחר]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [detail_url + השאילתה]

**שורה תחתונה לדסק:** [הליד שהכי בשל, ולמה]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר.
