---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__legislation_history mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-lobby-footprint
version: '0.2.0'
description: >-
  טביעת הרגל של ארגון, חברה או לוביסט בחקיקה עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db - מי הוזמן לדיוני ועדות הכנסת ובשם מי (knesset_protocol_attendees, 547,650 שורות מתוך הפרוטוקולים של 22,957 ישיבות, הכנסות 20 עד 25), באיזה דיונים על איזו הצעת חוק (knesset_session_items, knesset_bills), ומי הגיש הערות לתזכירי חוק (legislation_comments). הפעל כשדור כותב "מי הופיע בוועדה", "מי הוזמן לדיון על החוק", "כמה פעמים X הופיע בכנסת", "לוביסטים בוועדה", "מי לחץ על החוק", "מי הגיש הערות לתזכיר", "טביעת רגל בכנסת", "מי נוכח בדיון". כל פריט הוא ליד לבדיקה מול הפרוטוקול באתר הכנסת, לא ממצא מאומת. נוכחות בדיון אינה השפעה. לסדר יום של ועדה ראה osint-committees; לתזכיר עצמו ראה osint-memo-watch; למסלול החוק ראה osint-legislation-history.
---

# osint-lobby-footprint - מי היה בחדר

שלושה מקורות שאין להם סקיל: הנוכחים בפרוטוקולי ועדות הכנסת, כפי שנקראו מהפרוטוקול עצמו (`knesset_texts_scraper.py`), סדר היום של הישיבות, וההערות הציבוריות לתזכירי החוק.

- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.

## עקרונות יסוד

1. **הופעה בדיון היא זכות, לא חשד.** ועדות מזמינות ארגונים כדי לשמוע אותם. הסיפור הוא בדפוס: אותו ארגון בכל דיון על חוק אחד, לוביסט בשם לקוח שאינו מוצהר, או ארגון שהופיע בוועדה והחוק השתנה בדיוק בסעיף שלו. רק את האחרון אפשר לבדוק, ורק בפרוטוקול.
2. **השורה היא מה שנכתב בפרוטוקול.** `raw_line` היא השורה המקורית, ו-`name` ו-`affiliation` נגזרו ממנה במפרק (`parser_version`). שגיאות פירוק קיימות. שם ושיוך הם טקסט, לא זהות. **שם לבדו אינו מקשר לאדם.**
3. **הכיסוי חלקי, ונמדד ב-20.11.2026:** ישיבות ועדה בלבד (`doc_set = 'committee'`), מ-31.3.2015 עד 25.10.2026. רוב השורות מהכנסת ה-20 (233,233) ומה-25 (226,593). הכנסות 21 ו-22 דלות (2,442 ו-2,732 שורות). היעדר שם אינו היעדר הופעה.
4. **`section`:** `invitee` (מוזמנים, 351,907 שורות, כמעט כולן עם שיוך), `committee_member`, `other_mk`, `legal_advisor`, `committee_manager`, `recorder`, `committee_staff`. טביעת רגל של ארגון היא `section = 'invitee'`.
5. **לוביסט מוצהר:** 1,258 שורות שבשיוך שלהן מופיעה המילה "לוביסט". בפרוטוקול כתוב בדרך כלל המשרד, ולא תמיד הלקוח.

## כלי קודם

- `legislation_history("<שם החוק או מספר ההצעה>")`: היוזמים, ההצבעות והחוקים שהצעה תיקנה. מכאן מקבלים את מספר ההצעה (`knesset.bill.<id>`) לשאילתות של מצב ב.
- `search_entity("שם הארגון")` ואחריו `entity_profile(id)`: הכסף, החוזים והכהונות של הארגון. הנוכחות בוועדות **אינה** בפרופיל.
- `query_db` לנוכחים ולהערות.

**טריות:**
```sql
SELECT source, max(started_at) last_run FROM scrape_runs
WHERE status IN ('ok','warn') AND source IN ('knesset_texts','legislation_texts')
GROUP BY 1
```

## מלכודות - קרא לפני שאתה כותב SQL

| מלכודת | מה עושים |
|---|---|
| `affiliation` בלי אינדקס. `LIKE` על 547 אלף שורות הוא סריקה מלאה: "התאחדות התעשיינים" חזר ב-1 שנייה (2,539 שורות) | לפעמים חוזר מהר מהקאש. אם חרג, צמצם לפי `session_id` (מאונדקס) דרך מצב ב |
| `name` מאונדקס ב-btree בלבד | שוויון מדויק מהיר. `LIKE '%...%'` סורק |
| אותו ארגון בכמה כתיבים ("לובי99", "לובי 99") | חפש את החלק היציב בשם, ובדוק את הכתיבים בתוצאה |
| `knesset_session_items` ו-`knesset_committee_sessions` מסמנות שורה שירדה מהמקור ב-`gone_at` | תמיד `gone_at IS NULL` |
| `item_type_id = 2` הוא הצעת חוק (`item_id` = `knesset_bills.id`). 11 שאילתה, 4 הצעה לסדר, 6000 חקיקת משנה | מסננים לפי הסוג לפני ה-JOIN |
| `start_date` של ישיבה הוא טקסט ISO עם אזור זמן | `substr(start_date,1,10)` לתאריך |

## מצב א - ארגון: איפה הופיע

```sql
SELECT substr(s.start_date,1,10) session_date, c.name committee, a.name, a.affiliation, a.session_id, s.session_url
FROM knesset_protocol_attendees a
JOIN knesset_committee_sessions s ON s.id = a.session_id AND s.gone_at IS NULL
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE a.section = 'invitee' AND a.affiliation LIKE '%<שם הארגון>%'
ORDER BY s.start_date DESC
LIMIT 100
```

לפי ועדה ושנה, כדי לראות דפוס:
```sql
SELECT c.name committee, substr(s.start_date,1,4) yr, count(DISTINCT a.session_id) sessions
FROM knesset_protocol_attendees a
JOIN knesset_committee_sessions s ON s.id = a.session_id AND s.gone_at IS NULL
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE a.section = 'invitee' AND a.affiliation LIKE '%<שם הארגון>%'
GROUP BY 1,2 ORDER BY 2 DESC, 3 DESC
```

לוביסטים מוצהרים בישיבות של החודשים האחרונים:
```sql
SELECT substr(s.start_date,1,10) session_date, c.name committee, a.name, a.affiliation, s.session_url
FROM knesset_protocol_attendees a
JOIN knesset_committee_sessions s ON s.id = a.session_id AND s.gone_at IS NULL
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE a.affiliation LIKE '%לוביסט%' AND s.start_date >= '2026-06-01'
ORDER BY s.start_date DESC
LIMIT 100
```

## מצב ב - הצעת חוק: מי היה בכל הדיונים עליה

הישיבות שבהן הצעה הייתה על סדר היום (`<מספר הצעת חוק>` מ-`legislation_history`; למשל 2168881, חוק שירות ביטחון, 124 ישיבות):
```sql
SELECT s.id session_id, substr(s.start_date,1,10) session_date, c.name committee, i.name item, s.session_url
FROM knesset_session_items i
JOIN knesset_committee_sessions s ON s.id = i.session_id AND s.gone_at IS NULL
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE i.item_type_id = 2 AND i.item_id = <מספר הצעת חוק> AND i.gone_at IS NULL
ORDER BY s.start_date
```

הארגונים שהוזמנו הכי הרבה לדיונים על ההצעה:
```sql
WITH sess AS (
  SELECT DISTINCT i.session_id FROM knesset_session_items i
  WHERE i.item_type_id = 2 AND i.item_id = <מספר הצעת חוק> AND i.gone_at IS NULL)
SELECT a.affiliation, count(DISTINCT a.session_id) sessions, count(*) appearances,
       string_agg(DISTINCT a.name, ', ') names
FROM knesset_protocol_attendees a JOIN sess ON sess.session_id = a.session_id
WHERE a.section = 'invitee' AND a.affiliation IS NOT NULL
GROUP BY 1 ORDER BY 2 DESC
LIMIT 50
```
ישיבה עוסקת לפעמים בכמה נושאים, ולכן מוזמן לישיבה לא בהכרח דיבר על ההצעה. בודקים בפרוטוקול.

## מצב ג - הערות לתזכירי חוק

ב-`legislation_comments` יש 159,465 הערות ל-3,245 תזכירים (מ-6.3.2020). רק ב-2,663 יש `affiliation`; לרוב הגוף כתוב ב-`header` אחרי פסיק, או ב-`author_name`. יש אינדקס טריגרם על `body_text` בלבד:
```sql
SELECT c.legislation_id, l.title, l.ministry, c.comment_date, c.author_name, c.header, c.affiliation, c.body_chars
FROM legislation_comments c JOIN legislation l ON l.id = c.legislation_id
WHERE c.removed_at IS NULL AND (c.header LIKE '%<שם הארגון>%' OR c.affiliation LIKE '%<שם הארגון>%')
ORDER BY c.comment_date DESC
LIMIT 60
```
ההצלבה החזקה היא ארגון שהעיר על התזכיר והוזמן אחר כך לוועדה על ההצעה שנולדה ממנו. את הקשר בין תזכיר להצעה מביא `legislation_history`, לא שם.

## שלב האימות

- **ישיבה:** `session_url` באתר הכנסת, ובו הפרוטוקול. שם, תפקיד ושיוך נבדקים בפרוטוקול ולא ב-`affiliation`.
- **הערה:** עמוד התזכיר בפורטל תזכירי החוק.
- **לוביסט:** פנקס בעלי רישיון שדלן של הכנסת, ללקוח שעליו הוצהר.

## אתיקה

הופעה בוועדה והגשת הערה הן השתתפות דמוקרטית. אל תכתוב "לחץ" או "השפיע" בלי ראיה שהנוסח השתנה בעקבותיו. אנשים פרטיים שהגישו הערה בשמם אינם נושא לרשימות.

## דוח הדסק - מבנה קבוע

```markdown
# טביעת רגל - <ארגון / הצעת חוק>

## טווח הסריקה
[ארגון או הצעה, כנסות ותקופה, ומה לא מכוסה (כנסות 21-22, מליאה)]

## ממצאים
- **הופעות:** [ישיבות, ועדות, תאריכים, מי הופיע בשם הארגון]
- **הערות לתזכירים:** [תזכיר, תאריך, מי הגיש]
- **הדפוס:** [מה חוזר, ומה לא מתיישב]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה (בדרך כלל: מה השתנה בנוסח)
- **המקור:** [session_url / עמוד התזכיר + השאילתה]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר.
