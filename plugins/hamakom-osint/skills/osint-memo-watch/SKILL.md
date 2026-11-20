---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__legislation_history mcp__plugin_hamakom-osint_osint-db__new_since mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-memo-watch
version: '0.2.0'
description: >-
  מעקב אחרי תזכירי חוק וטיוטות תקנות בפורטל תזכירי החוק עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db - legislation (7,499 תזכירים), legislation_details (מועד ההערות כתאריך, קיצור זמן ההערות והנימוק, היעדר RIA והנימוק, סטטוס, תקציר), legislation_comments (159,465 הערות ציבור) ו-legislation_files (טיוטות, RIA וקבצי הערות, עם טקסט). מה פתוח להערות עכשיו, איפה קיצרו את זמן ההערות, מה עבר בלי דוח השפעת רגולציה, ואיזה תזכיר קיבל אלפי הערות. הפעל כשדור כותב "תזכירי חוק", "מה פתוח להערות", "תזכיר חדש", "קיצרו את זמן ההערות", "בלי RIA", "כמה הערות היו לתזכיר", "מה כתוב בטיוטה", "טיוטת תקנות של משרד X", "מועד ההערות נגמר". כל פריט הוא ליד לבדיקה מול עמוד התזכיר בפורטל, לא ממצא מאומת. תזכיר אינו כותרת ואינו חוק. להיסטוריה של חוק ראה osint-legislation-history; למי הגיש הערות ראה osint-lobby-footprint.
---

# osint-memo-watch - תזכירי החוק

תזכיר הוא השלב שבו הממשלה מפרסמת נוסח לפני הכנסת ומבקשת הערות. ארבע טבלאות: `legislation` (השורה הבסיסית, מ-`legislation_scraper.py` כל שעה), ו-`legislation_details`, `legislation_comments` ו-`legislation_files` (`tazkirim_texts_collector.py`, בלילה).

- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.

## עקרונות יסוד

1. **תזכיר אינו כותרת.** תזכיר הוא טיוטה של משרד. רוב התזכירים לא הופכים לחוק בנוסח שלהם, וחלק נעצרים (134 בסטטוס "נעצרה"). אל תכתוב "הממשלה מחוקקת" על תזכיר.
2. **הליד הוא בהליך, לא בעצם הפרסום:**
   - **קיצור זמן ההערות** (`is_short_time`, 3,083 מתוך 7,496), עם `shortening_days` ו-`shortening_reason`. הנימוק הנפוץ הוא "השלכות מינימליות על הציבור". נימוק כזה על תזכיר משמעותי הוא שאלה.
   - **בלי RIA** (דוח השפעת רגולציה): `no_ria_reason` מלא ב-3,411.
   - **חלון הערות פתוח:** 22 תזכירים שמועד ההערות שלהם לא חלף (נמדד 20.11.2026).
   - **היקף הערות חריג:** שלושה תזכירים קיבלו 14,835, 12,575 ו-9,255 הערות.
3. **תאריכים:** `legislation_details.pub_date` ו-`comment_deadline_date` הם `date` אמיתי ומאונדקס. ב-`legislation` מיינים לפי `pub_date_iso` ולא לפי `pub_date` (DD/MM/YYYY). `comment_deadline` בטבלה הבסיסית הוא טקסט עם שעה. התאריך נאמן למקור גם כשהמקור שגוי: יש תזכירים מהייבוא של 8.2.2024 עם השנים 1905, 1993 ו-1998.
4. **שורה שירדה מהמקור** מסומנת ב-`removed_at` (הערות וקבצים). מסננים `IS NULL`.

## כלי קודם

- `legislation_history("<מזהה התזכיר>")` (מזהה כמו `a13Wn00000EhBubIAF`): התזכיר כמרכז, עם החוקים שהוא מתקן ומכוחם הוא מותקן, וההצעות שנולדו ממנו. גם `legislation_history("<שם החוק>")` מחזיר את התזכירים של חוק.
- `new_since("legislation", "2026-11-13")`: מה נכנס מאז. אחרי טעינה מרוכזת `first_seen_at` אינו תאריך פרסום, ולכן לבדוק גם `pub_date_iso`.
- `search_entity("שם המשרד")` לגוף המפרסם, אם צריך את שאר הפעולות שלו.
- `query_db` לכל השאר.

**טריות:**
```sql
SELECT source, max(started_at) last_run FROM scrape_runs
WHERE status IN ('ok','warn') AND source IN ('legislation','legislation_texts')
GROUP BY 1
```

## מלכודות

| מלכודת | מה עושים |
|---|---|
| `legislation_details.ministry` ושמות המשרדים משתנים בין תקופות | `SELECT DISTINCT ministry` קודם |
| `legislation_comments` גדולה (159 אלף), ו-`header` ו-`affiliation` בלי אינדקס | מסננים לפי `legislation_id` (מאונדקס) או לפי `comment_date` (מאונדקס) |
| חיפוש בטקסט הטיוטה: `legislation_files.text` עם אינדקס טריגרם. חלק מהקבצים סרוקים (`ocr_text`) | `text LIKE '%...%'`. שורה סרוקה נבדקת גם ב-`ocr_text`. גופן שבולע את האות נ (U+F8FF) נמדד ב-`pua_chars` |
| `role` של קובץ: `draft` 8,439, `comment` 5,617, `ria` 948 | מסננים לפי `role` |

## מצב א - מה פתוח עכשיו

```sql
SELECT d.legislation_id, d.title, d.ministry, d.doc_type, d.pub_date, d.comment_deadline_date,
       d.is_short_time, d.shortening_days, d.shortening_reason, d.no_ria_reason, d.comments_total, d.url
FROM legislation_details d
WHERE d.comment_deadline_date >= CURRENT_DATE
ORDER BY d.comment_deadline_date
LIMIT 60
```

מה פורסם בשבועיים האחרונים:
```sql
SELECT d.legislation_id, d.title, d.ministry, d.pub_date, d.comment_deadline_date,
       d.is_short_time, d.shortening_reason, d.no_ria_reason, d.last_status, d.url
FROM legislation_details d
WHERE d.pub_date BETWEEN CURRENT_DATE - 14 AND CURRENT_DATE
ORDER BY d.pub_date DESC
LIMIT 60
```

## מצב ב - הליך מקוצר ובלי RIA

```sql
SELECT d.legislation_id, d.title, d.ministry, d.pub_date, d.comment_deadline_date,
       d.shortening_days, d.shortening_reason, d.no_ria_reason, d.comments_total, d.url
FROM legislation_details d
WHERE d.is_short_time AND d.no_ria_reason IS NOT NULL AND d.no_ria_reason <> ''
  AND d.pub_date BETWEEN CURRENT_DATE - 90 AND CURRENT_DATE
ORDER BY d.pub_date DESC
LIMIT 60
```

אילו משרדים מקצרים הכי הרבה (מכנה: כל התזכירים של המשרד בשנה):
```sql
SELECT ministry, count(*) memos, count(*) FILTER (WHERE is_short_time) shortened,
       round(100.0 * count(*) FILTER (WHERE is_short_time) / count(*)) pct
FROM legislation_details
WHERE pub_date BETWEEN CURRENT_DATE - 365 AND CURRENT_DATE
GROUP BY 1 HAVING count(*) >= 10
ORDER BY pct DESC
LIMIT 40
```
הנימוקים לקיצור:
```sql
SELECT shortening_reason, count(*) n FROM legislation_details WHERE is_short_time
GROUP BY 1 ORDER BY 2 DESC LIMIT 20
```

## מצב ג - ההערות

התזכירים עם הכי הרבה הערות:
```sql
SELECT c.legislation_id, l.title, l.ministry, count(*) comments, min(c.comment_date) first_c, max(c.comment_date) last_c
FROM legislation_comments c JOIN legislation l ON l.id = c.legislation_id
WHERE c.removed_at IS NULL AND c.comment_date >= CURRENT_DATE - 365
GROUP BY 1,2,3 ORDER BY 4 DESC
LIMIT 30
```

ההערות על תזכיר אחד:
```sql
SELECT comment_id, comment_date, author_name, header, affiliation, body_chars, files_count, left(body_text, 400) body_start
FROM legislation_comments
WHERE legislation_id = '<מזהה תזכיר>' AND removed_at IS NULL
ORDER BY comment_date
LIMIT 100
```
**הערה של אדם פרטי היא שלו.** מצטטים גופים, לא אזרחים שהגישו בשמם.

## מצב ד - מה כתוב בטיוטה

```sql
SELECT f.legislation_id, l.title, l.ministry, f.role, f.display_name, f.text_method, f.pages, f.pua_chars, f.download_url
FROM legislation_files f JOIN legislation l ON l.id = f.legislation_id
WHERE f.removed_at IS NULL AND f.role = 'draft' AND f.text LIKE '%פטור ממכרז%'
ORDER BY l.pub_date_iso DESC NULLS LAST
LIMIT 40
```
לטקסט המלא של קובץ אחד:
```sql
SELECT role, display_name, text_chars, left(coalesce(nullif(text,''), ocr_text), 20000) text
FROM legislation_files
WHERE legislation_id = '<מזהה תזכיר>' AND removed_at IS NULL AND role = 'draft'
```
חיפוש בטקסט כל הטיוטות נמדד ב-4.4 שניות (20.11.2026), קרוב לגבול של 10 שניות בקאש קר. אם חרג, צמצם ב-`l.ministry =` או בטווח של `l.pub_date_iso`. התשובה של `query_db` נחתכת ב-50 אלף תווים. לטיוטה ארוכה, קוראים במנות לפי `substr(text, ...)`.

## שלב האימות

- `url` של התזכיר בפורטל: הנוסח, מועד ההערות, הנימוק לקיצור ול-RIA.
- הקובץ: `download_url`. טקסט שחולץ מ-PDF (ובמיוחד OCR) אינו ציטוט. מצטטים מהקובץ.

## אתיקה

תזכיר הוא טיוטה. ייחס אותו למשרד המפרסם, ציין שהוא בשלב הערות הציבור, ואל תכתוב עליו כחוק. פנה למשרד לפני פרסום על קיצור זמנים או היעדר RIA.

## דוח הדסק - מבנה קבוע

```markdown
# תזכירים - <תקופה / משרד>

## טווח הסריקה
[תקופה, משרדים, מתי המקור רץ]

## לידים מדורגים
לכל ליד:
- **התזכיר:** [כותרת, משרד, תאריך פרסום, מועד הערות]
- **ההליך:** [קיצור וימים ונימוק / בלי RIA ונימוק / סטטוס]
- **ההערות:** [כמה, ומי הגופים הבולטים]
- **למה זה חשוב:** [מה התזכיר משנה, בשורה]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [url + השאילתה]

**שורה תחתונה לדסק:** [התזכיר שהכי בשל, ולמה]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר.
