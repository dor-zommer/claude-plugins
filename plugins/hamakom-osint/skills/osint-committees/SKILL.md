---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__list_tables mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__new_since
name: osint-committees
description: מה קורה בוועדות הכנסת ומה השרים לא עונים - עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db. סדר יום של ישיבות ועדה כולל ישיבות עתידיות (knesset_committee_sessions + knesset_session_items), חומרי רקע ופרוטוקולים להורדה כולל מסמכי מרכז המחקר והמידע (knesset_session_documents), וזיהוי ישיבות חסויות. הליד המובנה: שאילתות ח"כים שהמועד לתשובת השר חלף ולא נענו (knesset_queries) - 93 כאלה במאגר. הפעל כשדור כותב "מה על סדר היום בוועדה", "ישיבות ועדת הכספים", "מה נדון בוועדה", "פרוטוקול ועדה", "חומר רקע לישיבה", "ישיבה חסויה", "שאילתות שלא נענו", "מה השר לא ענה", "שאילתה של ח\"כ". כל פריט הוא ליד לבדיקה מול אתר הכנסת, לא ממצא מאומת. להצבעות, פרופיל ח"כ ומסלול חוק ראה osint-knesset.
---

# osint-committees - ועדות הכנסת ושאילתות

סקיל לחמש טבלאות כנסת שאין להן בית: ישיבות ועדה, סדר היום שלהן, המסמכים שהוגשו בהן, רשימת הוועדות, והשאילתות. `osint-knesset` מטפל בהצבעות, בפרופיל ח"כ ובמסלול חוק - כאן העבודה השוטפת של הכנסת.

**קרא קודם `references/db-map.md`.**

## עקרונות יסוד

1. **סדר יום אינו תוצאה.** ישיבה שתוכננה יכולה להתבטל, להידחות או לשנות נושא. `status_desc` ו-`start_date` הם מה שהמאגר יודע ברגע הסריקה. אמת מול אתר הכנסת לפני שאתה כותב "יידון".
2. **ישיבה חסויה אינה סוד.** `type_desc = 'חסויה'` אומר שהדיון סגור לציבור - אבל **חומרי הרקע שלה לעיתים כן במאגר**. עצם הפרסום הרשמי של המסמך אינו הדלפה; הוא פורסם באתר הכנסת. יחד עם זאת, בדוק את תוכן המסמך לפני פרסום ואל תניח שכל מה שנגיש מיועד לפרסום.
3. **חומר רקע הוא מקור, לא ליד.** מסמכי מרכז המחקר והמידע (מ.מ.מ) ומסמכי גורמים חיצוניים מכילים נתונים שאין בשום מקום אחר. זה הדבר הראוי ביותר לקריאה בסקיל הזה.
4. **שאילתה שלא נענתה היא סיפור בפני עצמו** - אבל בדוק שהמועד באמת חלף ושהתשובה לא נרשמה במקום אחר.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.**

## מגבלה מחייבת: אין תרגום למשרדים

`knesset_queries.gov_ministry_id` הוא **קוד מספרי, ואין במאגר טבלת lookup של משרדים.** קוד 1178 אינו מתורגם לשם. אל תנחש. שתי דרכים: הצלב את הקוד מול אתר הכנסת, או קרא את שם המשרד מגוף השאילתה. **אסור לייחס שאילתה לשר מסוים על סמך הקוד לבדו.**

`person_id` בשאילתות מתורגם דרך `knesset_mk_individuals`, אבל `mk_individual_name` שם מחזיק לרוב **שם משפחה בלבד** ("אזולאי", "להב הרצנו"). זהה את הח"כ במלואו לפני שאתה מייחס.

## מצב א - הליד המובנה: שאילתות שהשר לא ענה בזמן

זו נקודת הכניסה החזקה. נבדק: **93 מ-266 השאילתות במאגר** עברו את המועד המתוכנן לתשובה בלי שנרשמה תשובה.

```sql
SELECT q.number, q.name, q.type_desc, q.gov_ministry_id,
       substr(q.submit_date,1,10) submitted,
       substr(q.reply_date_planned,1,10) due,
       m.mk_individual_name
FROM knesset_queries q
LEFT JOIN knesset_mk_individuals m ON m.mk_individual_id = q.person_id
WHERE q.reply_minister_date IS NULL
  AND q.reply_date_planned IS NOT NULL
  AND substr(q.reply_date_planned,1,10) < date('now')
ORDER BY q.reply_date_planned ASC
LIMIT 40
```
`ORDER BY ... ASC` מעלה קודם את האיחורים הארוכים.

ריכוז לפי משרד (זכור: הקוד לא מתורגם):
```sql
SELECT gov_ministry_id, COUNT(*) overdue
FROM knesset_queries
WHERE reply_minister_date IS NULL
  AND substr(reply_date_planned,1,10) < date('now')
GROUP BY gov_ministry_id ORDER BY overdue DESC
```
משרד עם ריכוז איחורים גבוה הוא ליד - אבל **חובה לתרגם את הקוד מול אתר הכנסת לפני ייחוס**.

שאילתות דחופות (`type_desc = 'דחופה'`) נענות בימים ולא בשבועות; דחופה שלא נענתה היא ליד חזק יותר.

## מצב ב - מה על סדר היום

ישיבות קרובות ועתידיות:
```sql
SELECT s.start_date, c.name AS committee, s.type_desc, s.status_desc,
       s.location, s.session_url
FROM knesset_committee_sessions s
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE s.start_date >= date('now')
ORDER BY s.start_date ASC
LIMIT 40
```
המאגר מחזיק ישיבות שנקבעו לשבועות קדימה. זה מאפשר לדסק לתכנן סיקור מראש.

הנושאים שיידונו בישיבה מסוימת:
```sql
SELECT ordinal, name, item_type_id
FROM knesset_session_items
WHERE session_id = <session_id>
ORDER BY ordinal
```

ועדה מסוימת לאורך זמן:
```sql
SELECT s.start_date, s.type_desc, s.status_desc, s.session_url,
       (SELECT GROUP_CONCAT(i.name, ' | ') FROM knesset_session_items i
        WHERE i.session_id = s.id) AS agenda
FROM knesset_committee_sessions s
JOIN knesset_committees c ON c.id = s.committee_id
WHERE c.name LIKE '%ועדת הכספים%'
ORDER BY s.start_date DESC
LIMIT 25
```

רשימת הוועדות הפעילות:
```sql
SELECT id, name, category_desc, committee_type_desc, parent_committee_name, is_current
FROM knesset_committees
WHERE is_current = 1
ORDER BY name
```
שים לב: הסקרייפר של `knesset_committees` לא הכניס שורה חדשה מ-07.07.2026 - ועדה שהוקמה מאז לא תופיע.

## מצב ג - ישיבות חסויות

```sql
SELECT s.start_date, c.name AS committee, s.type_desc, s.location, s.session_url,
       (SELECT COUNT(*) FROM knesset_session_documents d WHERE d.session_id = s.id) docs
FROM knesset_committee_sessions s
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE s.type_desc = 'חסויה'
ORDER BY s.start_date DESC
LIMIT 30
```
ישיבה חסויה שיש לה מסמכים במאגר (`docs > 0`) היא הליד: מה שנדון מאחורי דלתיים סגורות, עם חומר הרקע שכן פורסם. ראה עקרון 2 לפני פרסום.

## מצב ד - המסמכים (זה החומר המשמעותי)

```sql
SELECT d.group_type_desc, d.application_desc, d.file_path,
       c.name AS committee, s.start_date, s.type_desc
FROM knesset_session_documents d
JOIN knesset_committee_sessions s ON s.id = d.session_id
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE d.session_id = <session_id>
```

סוגי המסמכים במאגר, לפי שכיחות: **חומר רקע - גורמים חיצוניים** (1,112), **פרוטוקול ועדה** (878), **חומר רקע** (875 PDF + 196 DOC), **מסמך מ.מ.מ ישיבת ועדה** (154), **החלטות ועדה** (244), **נוסח לדיון בוועדה** (152), **הודעה לעיתונות** (66).

מסמכי מרכז המחקר והמידע לבדם:
```sql
SELECT d.file_path, s.start_date, c.name AS committee
FROM knesset_session_documents d
JOIN knesset_committee_sessions s ON s.id = d.session_id
LEFT JOIN knesset_committees c ON c.id = s.committee_id
WHERE d.group_type_desc LIKE '%מ.מ.מ%'
ORDER BY s.start_date DESC LIMIT 30
```
מסמכי מ.מ.מ הם מחקר מוכן עם נתונים מקוריים, והם הפריט הראוי ביותר לקריאה כאן.

`file_path` הוא URL ישיר ל-`fs.knesset.gov.il`. **קרא את המסמך במלואו לפני שאתה מסתמך עליו** - אל תסיק מהשם. פרוטוקולים הם DOC ודורשים המרה.

## שלב האימות - מול אתר הכנסת

`session_url` מוביל לדף הישיבה, `file_path` למסמך עצמו. לכל ליד:
- אמת שהישיבה התקיימה ובאיזה תאריך בפועל (סדר יום מתעדכן).
- לשאילתה שלא נענתה: בדוק בדף הח"כ ובדף השאילתה אם נרשמה תשובה שלא נסרקה.
- תרגם `gov_ministry_id` לשם משרד מול האתר.
- קרא את המסמך המלא, לא את שם הקובץ.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| `committee` יוצא null ב-JOIN | ה-`committee_id` לא קיים ב-`knesset_committees` (הסקרייפר עצר ביולי 2026). קח את השם מ-`session_url` באתר |
| שם ח"כ הוא שם משפחה בלבד | צפוי. זהה במלואו מול `knesset_mk_individuals` או אתר הכנסת לפני ייחוס |
| `gov_ministry_id` לא מתורגם | אין טבלת lookup. תרגם מול אתר הכנסת; אל תנחש |
| שאילתה בלי `reply_date_planned` | לרוב דחופה שנענתה (`reply_minister_date` מלא). אל תספור אותה כאיחור |
| ישיבה עתידית שלא התקיימה | סדר היום מתעדכן. אמת מול האתר לפני שכותבים "יידון" |
| `docs` יוצא 0 בישיבה שהתקיימה | המסמכים לא נסרקו או לא פורסמו. בדוק בדף הישיבה |

**אסור:** לייחס שאילתה לשר על סמך `gov_ministry_id` בלבד, לכתוב "השר סירב לענות" (איחור אינו סירוב), או לפרסם תוכן ממסמך שלא נקרא במלואו.

## אתיקה

פעילות פרלמנטרית היא נתון ציבורי מובהק. יחד עם זאת: איחור בתשובה לשאילתה הוא כשל מנהלי ולא בהכרח הסתרה - בקש תגובת המשרד. בישיבה חסויה, הישיבה סגורה מסיבה שהוועדה קבעה; חומר הרקע שפורסם רשמית הוא ציבורי, אבל שקול את תוכנו ואת ההקשר הביטחוני לפני פרסום, ופנה לוועדה בשאלה כשיש ספק. אל תהפוך שאילתה של ח"כ לעמדה עיתונאית - היא כלי פרלמנטרי.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): איתור השאילתות באיחור, סדר היום הקרוב, זיהוי ישיבות חסויות עם מסמכים, שליפת מסמכי מ.מ.מ וקריאתם, אימות מול אתר הכנסת ותרגום קודי המשרדים.

## דוח הדסק - מבנה קבוע

```markdown
# כנסת - ועדות ושאילתות

## מה נסרק
[איזו ועדה / טווח תאריכים / סוג מסמך, וכמה רשומות. ציין את מגבלת קודי המשרדים]

## שאילתות באיחור
לכל אחת: [מספר, נושא, מי הגיש, מתי הוגשה, מתי הייתה אמורה להיענות, כמה זמן חלף]
**קוד המשרד:** [הקוד + האם תורגם מול אתר הכנסת]

## סדר היום הקרוב
[ישיבות עתידיות עם ועדה, תאריך, נושאים, וסימון פתוחה/חסויה]

## מסמכים ששווה לקרוא
[מ.מ.מ / חומר רקע / פרוטוקול - עם קישור ישיר, ומה יש בו]

## מה לאמת מול אתר הכנסת
[קיום הישיבה, תשובה לשאילתה, תרגום קוד המשרד, קריאת המסמך במלואו]

**שורה תחתונה לדסק:** [הליד אחד שהכי בשל, ולמה]

Sources: [שאילתות osint-db + session_url ו-file_path שנפתחו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הבחן תמיד בין ישיבה שנקבעה לישיבה שהתקיימה, ובין איחור בתשובה לסירוב.
