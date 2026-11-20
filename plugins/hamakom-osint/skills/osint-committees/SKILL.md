---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table
name: osint-committees
version: 1.3.0
description: >-
  מה קורה בוועדות הכנסת ומה השרים לא עונים - עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db. סדר יום של ישיבות ועדה כולל ישיבות עתידיות (knesset_committee_sessions + knesset_session_items), חומרי רקע ופרוטוקולים להורדה כולל מסמכי מרכז המחקר והמידע (knesset_session_documents), וזיהוי ישיבות חסויות. הליד המובנה: שאילתות ח"כים שהמועד לתשובת השר חלף ולא נענו (knesset_queries), עם שם המשרד מ-gov_ministers; המספר נמדד בכל ריצה. הפעל כשדור כותב "מה על סדר היום בוועדה", "ישיבות ועדת הכספים", "מה נדון בוועדה", "פרוטוקול ועדה", "חומר רקע לישיבה", "ישיבה חסויה", "שאילתות שלא נענו", "מה השר לא ענה", "שאילתה של ח\"כ". כל פריט הוא ליד לבדיקה מול אתר הכנסת, לא ממצא מאומת. להצבעות, פרופיל ח"כ ומסלול חוק ראה osint-knesset.
---

# osint-committees - ועדות הכנסת ושאילתות

סקיל לחמש טבלאות כנסת שאין להן בית: ישיבות ועדה, סדר היום שלהן, המסמכים שהוגשו בהן, רשימת הוועדות, והשאילתות. `osint-knesset` מטפל בהצבעות, בפרופיל ח"כ ובמסלול חוק - כאן העבודה השוטפת של הכנסת.

**כלי קודם.** שאלה על ח"כ מסוים (מה שאל, באילו דיונים השתתף): `search_entity("שם")` ואז `entity_profile("knesset.person.<PersonID>")` - בקבוצה legislative יש "שאילתות ששאל" ו"דיונים בוועדות". השאילתות כאן ב-`query_db` הן לתמונה הרוחבית: כל האיחורים, סדר היום, המסמכים.

**חוקי המאגר.** המפה המלאה היא `references/db-map.md` בשורש התוסף (`../../references/db-map.md` מתיקיית הסקיל). יש סביבות שטוענות רק את SKILL.md, ולכן העיקר כאן:
- את העמודות של טבלה נותן `describe_table(name)`. לא מנחשים שם עמודה.
- **חוק הזהב:** אין אגרגציה ואין `LIKE` על טבלה גדולה בלי `WHERE` על עמודה מאונדקסת. שאילתה שנקטעה אינה "אין תוצאות".
- **שורה שירדה מהמקור מסומנת ב-`gone_at`.** ב-`knesset_queries`, `knesset_committee_sessions`, `knesset_committees`, `knesset_session_items` ו-`knesset_session_documents` סנן תמיד `gone_at IS NULL`, אחרת שאילתה שבוטלה או ישיבה שהוסרה נספרות.
- **התאריכים הם טקסט ISO עם שעה ואזור זמן** (`2026-11-23T09:15:00+02:00`), ולכן משווים את `substr(col,1,10)` למחרוזת `YYYY-MM-DD`.
- **טריות - לפני כל "אין במאגר":**
  ```sql
  SELECT source, max(started_at) AS last_ok FROM scrape_runs
  WHERE status IN ('ok','warn')
    AND source IN ('knesset_queries','knesset_committee_sessions','knesset_session_items',
                   'knesset_session_documents','knesset_committees','gov_ministers')
  GROUP BY 1
  ```
  ריצה מוצלחת אינה בהכרח נתונים חדשים: בדוק גם `max(first_seen_at)` בטבלה עצמה (נמדד 20.11.2026: `knesset_queries` רץ בהצלחה ב-20.11.2026, והשורה החדשה ביותר בה מ-9.11.2026). מקור שלא רץ הוא "לא נאסף", לא "אין".

## עקרונות יסוד

1. **סדר יום אינו תוצאה.** ישיבה שתוכננה יכולה להתבטל, להידחות או לשנות נושא. `status_desc` ו-`start_date` הם מה שהמאגר יודע ברגע הסריקה. אמת מול אתר הכנסת לפני שאתה כותב "יידון".
2. **ישיבה חסויה אינה סוד.** `type_desc = 'חסויה'` אומר שהדיון סגור לציבור - אבל **חומרי הרקע שלה לעיתים כן במאגר**. עצם הפרסום הרשמי של המסמך אינו הדלפה; הוא פורסם באתר הכנסת. יחד עם זאת, בדוק את תוכן המסמך לפני פרסום ואל תניח שכל מה שנגיש מיועד לפרסום.
3. **חומר רקע הוא מקור, לא ליד.** מסמכי מרכז המחקר והמידע (מ.מ.מ) ומסמכי גורמים חיצוניים מכילים נתונים שאין בשום מקום אחר. זה הדבר הראוי ביותר לקריאה בסקיל הזה.
4. **שאילתה שלא נענתה היא סיפור בפני עצמו** - אבל בדוק שהמועד באמת חלף ושהתשובה לא נרשמה במקום אחר.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.**

## המשרד והשר של שאילתה

`knesset_queries.gov_ministry_id` הוא קוד, ושם המשרד נמצא ב-`gov_ministers` (`ministry_id`, `ministry_name`). נמדד 20.11.2026: כל 1,580 השאילתות של הכנסת ה-25 מתורגמות, ולאף קוד אין שני שמות (למשל 1178 הוא משרד הביטחון). ב-`gov_ministers` יש שורה לכל כהונת שר, ולכן מתרגמים בתת-שאילתה ולא ב-JOIN, שהיה מכפיל שורות:
```sql
(SELECT string_agg(DISTINCT g.ministry_name, ' / ') FROM gov_ministers g WHERE g.ministry_id = q.gov_ministry_id) AS ministry
```
**המשרד אינו השר.** כדי לייחס שאילתה לשר, מצא מי כיהן במשרד במועד שבו התשובה הייתה אמורה להינתן:
```sql
SELECT full_name, position_desc, government, substr(start_date,1,10) AS start_d, substr(finish_date,1,10) AS finish_d
FROM gov_ministers
WHERE ministry_id = <gov_ministry_id>
  AND substr(start_date,1,10) <= '<due>'
  AND (finish_date IS NULL OR substr(finish_date,1,10) >= '<due>')
ORDER BY start_date
```
יותר משורה אחת (שר ושר נוסף במשרד, או חילופי שרים; נמדד: למשרד הביטחון ביוני 2024 חוזרות שתי שורות) - הכרע מול אתר הכנסת. ובכל מקרה אמת את הייחוס מול דף השאילתה לפני פרסום.

`person_id` בשאילתות הוא PersonID של הכנסת, והשם נלקח מ-`knesset_persons` (`id` = PersonID): `LEFT JOIN knesset_persons p ON p.id = q.person_id`. לא מהמרשם `knesset_mk_individuals`: `mk_individual_id` שם הוא לרוב מרחב מזהים אחר שמתנגש על אנשים אמיתיים (`mk_individual_id`=528 הוא מוחמד נפאע, PersonID 528 הוא יעקב ליצמן), ובחלק משורותיו השם העברי נדרס בשם של ח"כ אחר.

## מצב א - הליד המובנה: שאילתות שהשר לא ענה בזמן

**קודם: איזו כנסת יש במאגר.** שאילתה שלא נענתה בכנסת שהתפזרה פקעה עם הפיזור: היא סיפור על הממשלה הקודמת ("לא נענתה עד תום הכנסת"), לא ליד על השר הנוכחי.
```sql
SELECT (SELECT max(knesset_num) FROM knesset_queries WHERE gone_at IS NULL) AS queries_knesset,
       (SELECT max(knesset_num) FROM knesset_mk_positions WHERE is_current = 1) AS current_knesset,
       (SELECT max(first_seen_at) FROM knesset_queries) AS newest_query_row
```
נמדד 20.11.2026: `queries_knesset` = 25, `current_knesset` = 26 (הכנסת ה-26 התחילה לעבוד ב-11.11.2026, לפי הישיבה הראשונה שלה במאגר). כל עוד אין במאגר שאילתות של הכנסת הנוכחית, הרשימה היא של הכנסת הקודמת, וכך היא מוצגת לדסק.

```sql
SELECT q.number, q.knesset_num, q.name, q.type_desc, q.gov_ministry_id,
       (SELECT string_agg(DISTINCT g.ministry_name, ' / ') FROM gov_ministers g
         WHERE g.ministry_id = q.gov_ministry_id) AS ministry,
       substr(q.submit_date,1,10) AS submitted,
       substr(q.reply_date_planned,1,10) AS due,
       p.first_name || ' ' || p.last_name AS mk
FROM knesset_queries q
LEFT JOIN knesset_persons p ON p.id = q.person_id
WHERE q.gone_at IS NULL
  AND q.knesset_num = <queries_knesset>
  AND q.reply_minister_date IS NULL
  AND q.reply_date_planned IS NOT NULL
  AND substr(q.reply_date_planned,1,10) < to_char(CURRENT_DATE,'YYYY-MM-DD')
ORDER BY q.reply_date_planned ASC
LIMIT 40
```
`ORDER BY ... ASC` מעלה קודם את האיחורים הארוכים. את מספר האיחורים מודדים בכל ריצה (`COUNT(*)` באותו `WHERE`), לא מצטטים מכאן.

ריכוז לפי משרד:
```sql
SELECT q.gov_ministry_id,
       (SELECT string_agg(DISTINCT g.ministry_name, ' / ') FROM gov_ministers g
         WHERE g.ministry_id = q.gov_ministry_id) AS ministry,
       COUNT(*) AS overdue
FROM knesset_queries q
WHERE q.gone_at IS NULL
  AND q.knesset_num = <queries_knesset>
  AND q.reply_minister_date IS NULL
  AND substr(q.reply_date_planned,1,10) < to_char(CURRENT_DATE,'YYYY-MM-DD')
GROUP BY q.gov_ministry_id ORDER BY overdue DESC
```
משרד עם ריכוז איחורים גבוה הוא ליד - אבל לפני ייחוס לשר, ראה "המשרד והשר של שאילתה".

שאילתות דחופות (`type_desc = 'דחופה'`) נענות בימים ולא בשבועות; דחופה שלא נענתה היא ליד חזק יותר. (נמדד בכנסת ה-25: לשאילתות הדחופות אין `reply_date_planned`, ולכן הן לא נכנסות לשאילתה למעלה; כל 202 כאלה נענו.)

## מצב ב - מה על סדר היום

ישיבות קרובות ועתידיות:
```sql
SELECT s.id AS session_id, s.start_date, c.name AS committee, s.type_desc, s.status_desc,
       s.location, s.session_url
FROM knesset_committee_sessions s
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE s.gone_at IS NULL
  AND substr(s.start_date,1,10) >= to_char(CURRENT_DATE,'YYYY-MM-DD')
ORDER BY s.start_date ASC
LIMIT 40
```
המאגר מחזיק ישיבות שנקבעו קדימה (נמדד 20.11.2026: 12 ישיבות עתידיות, האחרונה ב-8.12.2026). זה מאפשר לדסק לתכנן סיקור מראש.

הנושאים שיידונו בישיבה מסוימת:
```sql
SELECT ordinal, name, item_type_id
FROM knesset_session_items
WHERE session_id = <session_id> AND gone_at IS NULL
ORDER BY ordinal
```

ועדה מסוימת לאורך זמן:
```sql
SELECT s.id AS session_id, s.start_date, s.type_desc, s.status_desc, s.session_url,
       (SELECT string_agg(i.name, ' | ' ORDER BY i.ordinal) FROM knesset_session_items i
         WHERE i.session_id = s.id AND i.gone_at IS NULL) AS agenda
FROM knesset_committee_sessions s
JOIN knesset_committees c ON c.id = s.committee_id
WHERE c.name LIKE '%ועדת הכספים%' AND s.gone_at IS NULL
ORDER BY s.start_date DESC
LIMIT 25
```
בתחילת כנסת הוועדות הקבועות עוד לא הוקמו, ובמקומן פועלות ועדות זמניות ("הוועדה הזמנית לענייני כספים"). חפש גם את השם הזמני.

רשימת הוועדות של הכנסת הנוכחית:
```sql
SELECT id, name, category_desc, committee_type_desc, parent_committee_name
FROM knesset_committees
WHERE is_current = 1 AND gone_at IS NULL
  AND knesset_num = (SELECT max(knesset_num) FROM knesset_mk_positions WHERE is_current = 1)
ORDER BY name
```
**חובה לסנן לפי `knesset_num`:** `is_current = 1` לבדו מחזיר גם ועדות מכנסות ישנות (נמדד 20.11.2026: 423 שורות, מהכנסת ה-1 ועד ה-26). בכנסת ה-26 היו באותו יום 7 ועדות.

## מצב ג - ישיבות חסויות

```sql
SELECT s.id AS session_id, s.start_date, c.name AS committee, s.type_desc, s.location, s.session_url,
       (SELECT COUNT(*) FROM knesset_session_documents d
         WHERE d.session_id = s.id AND d.gone_at IS NULL) AS docs
FROM knesset_committee_sessions s
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE s.type_desc = 'חסויה' AND s.gone_at IS NULL
ORDER BY s.start_date DESC
LIMIT 30
```
ישיבה חסויה שיש לה מסמכים במאגר (`docs > 0`) היא הליד: מה שנדון מאחורי דלתיים סגורות, עם חומר הרקע שכן פורסם. (נמדד 20.11.2026: 71 מתוך 1,551 הישיבות החסויות במאגר.) ראה עקרון 2 לפני פרסום.

## מצב ד - המסמכים (זה החומר המשמעותי)

```sql
SELECT d.group_type_desc, d.application_desc, d.file_path,
       c.name AS committee, s.start_date, s.type_desc
FROM knesset_session_documents d
JOIN knesset_committee_sessions s ON s.id = d.session_id
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE d.session_id = <session_id> AND d.gone_at IS NULL
```

סוגי המסמכים במאגר, לפי שכיחות (נמדד 20.11.2026, שורות חיות): **פרוטוקול ועדה** (141,712), **חומר רקע** (42,485), **החלטות ועדה** (7,428), **הודעה לעיתונות** (2,204), **חומר רקע - גורמים חיצוניים** (2,185), **מסקנות ועדה** (1,377), **נוסח לדיון בוועדה** (1,339), **תשובת השר** (1,328), **מסמך מ.מ.מ ישיבת ועדה** (1,084).

מסמכי מרכז המחקר והמידע לבדם:
```sql
SELECT d.file_path, s.start_date, c.name AS committee
FROM knesset_session_documents d
JOIN knesset_committee_sessions s ON s.id = d.session_id
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE d.group_type_desc LIKE '%מ.מ.מ%' AND d.gone_at IS NULL AND s.gone_at IS NULL
ORDER BY s.start_date DESC LIMIT 30
```
מסמכי מ.מ.מ הם מחקר מוכן עם נתונים מקוריים, והם הפריט הראוי ביותר לקריאה כאן.

`file_path` הוא URL ישיר ל-`fs.knesset.gov.il`. **קרא את המסמך במלואו לפני שאתה מסתמך עליו** - אל תסיק מהשם. פרוטוקולים הם DOC ודורשים המרה.

## שלב האימות - מול אתר הכנסת

`session_url` מוביל לדף הישיבה, `file_path` למסמך עצמו. לכל ליד:
- אמת שהישיבה התקיימה ובאיזה תאריך בפועל (סדר יום מתעדכן).
- לשאילתה שלא נענתה: בדוק בדף הח"כ ובדף השאילתה אם נרשמה תשובה שלא נסרקה.
- אמת את המשרד ואת השר מול האתר.
- קרא את המסמך המלא, לא את שם הקובץ.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| `committee` יוצא null ב-JOIN | ה-`committee_id` לא קיים ב-`knesset_committees` (נמדד 20.11.2026: אפס כאלה מ-2,159 ישיבות של 2026). קח את השם מ-`session_url` באתר |
| רשימת הוועדות "הנוכחיות" כוללת ועדות מכנסות ישנות | חסר `knesset_num =` הכנסת הנוכחית (מצב ב) |
| שאילתות באיחור רק מהכנסת הקודמת | שאילתות הכנסת הנוכחית עוד לא במאגר. בדוק `scrape_runs` ו-`max(first_seen_at)`, והצג את הרשימה כהיסטורית |
| `ministry` יוצא null | הקוד לא נמצא ב-`gov_ministers`. תרגם מול אתר הכנסת; אל תנחש |
| שם ח"כ שגוי או של אדם אחר | השם נלקח מ-`knesset_mk_individuals` במקום מ-`knesset_persons` |
| שאילתה בלי `reply_date_planned` | דחופה (בכנסת ה-25 כולן נענו). אל תספור אותה כאיחור |
| ישיבה עתידית שלא התקיימה | סדר היום מתעדכן. אמת מול האתר לפני שכותבים "יידון" |
| `docs` יוצא 0 בישיבה שהתקיימה | המסמכים לא נסרקו או לא פורסמו. בדוק בדף הישיבה |

**אסור:** לייחס שאילתה לשר על סמך הקוד או שם המשרד בלבד, לכתוב "השר סירב לענות" (איחור אינו סירוב), או לפרסם תוכן ממסמך שלא נקרא במלואו.

## אתיקה

פעילות פרלמנטרית היא נתון ציבורי מובהק. יחד עם זאת: איחור בתשובה לשאילתה הוא כשל מנהלי ולא בהכרח הסתרה - בקש תגובת המשרד. בישיבה חסויה, הישיבה סגורה מסיבה שהוועדה קבעה; חומר הרקע שפורסם רשמית הוא ציבורי, אבל שקול את תוכנו ואת ההקשר הביטחוני לפני פרסום, ופנה לוועדה בשאלה כשיש ספק. אל תהפוך שאילתה של ח"כ לעמדה עיתונאית - היא כלי פרלמנטרי.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): בדיקת הכנסת והטריות, איתור השאילתות באיחור, סדר היום הקרוב, זיהוי ישיבות חסויות עם מסמכים, שליפת מסמכי מ.מ.מ וקריאתם, אימות מול אתר הכנסת וייחוס המשרד והשר.

## דוח הדסק - מבנה קבוע

```markdown
# כנסת - ועדות ושאילתות

## מה נסרק
[איזו ועדה / טווח תאריכים / סוג מסמך, וכמה רשומות. איזו כנסת יש במאגר לשאילתות ומה הכנסת הנוכחית]

## שאילתות באיחור
לכל אחת: [מספר, נושא, מי הגיש, מתי הוגשה, מתי הייתה אמורה להיענות, כמה זמן חלף]
**המשרד והשר:** [שם המשרד מ-gov_ministers, השר במועד, והאם אומת מול אתר הכנסת]

## סדר היום הקרוב
[ישיבות עתידיות עם ועדה, תאריך, נושאים, וסימון פתוחה/חסויה]

## מסמכים ששווה לקרוא
[מ.מ.מ / חומר רקע / פרוטוקול - עם קישור ישיר, ומה יש בו]

## מה לאמת מול אתר הכנסת
[קיום הישיבה, תשובה לשאילתה, המשרד והשר, קריאת המסמך במלואו]

**שורה תחתונה לדסק:** [הליד אחד שהכי בשל, ולמה]

Sources: [שאילתות osint-db + session_url ו-file_path שנפתחו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הבחן תמיד בין ישיבה שנקבעה לישיבה שהתקיימה, ובין איחור בתשובה לסירוב.
