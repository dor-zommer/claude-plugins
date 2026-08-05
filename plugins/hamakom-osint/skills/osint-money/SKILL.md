---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__list_tables mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__new_since
name: osint-money
description: מעקב אחרי כסף ציבורי עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db - התקשרויות בפועל (budget_contracts, מיליון שורות ממפתח התקציב), תמיכות ומענקים (budget_supports, 330 אלף), עמותות ודוחותיהן הכספיים (amutot מגיידסטאר, 75 אלף), ומכרזי משרד הביטחון (mod_tenders). היכולת המרכזית: הצלבת תמיכה ממשלתית עם הדוח הכספי של מקבלת התמיכה לפי מזהה תאגיד (recipient_entity_id = amuta_id), ולא לפי שם. הפעל כשדור כותב "מי מקבל כסף מ", "כמה תמיכות קיבלה", "התקשרויות של משרד X", "מפתח התקציב", "תמיכות לעמותות", "כמה המדינה שילמה ל", "מי הספק הגדול של", "עמותה שמקבלת תמיכות", "מכרזי משרד הביטחון". כל פריט הוא ליד לבדיקה מול המקור הרשמי, לא ממצא מאומת. לפטורים ממכרז ראה osint-exemptions; לתיק חוצה-תחומים ראה osint-entity-dossier.
---

# osint-money - מעקב כסף ציבורי

סקיל לתחקיר תזרים הכסף מהמדינה: מי מקבל, מכמה משרדים, באיזה מסלול, ומה מצבו הכספי המדווח. ארבע טבלאות שאף סקיל אחר לא נוגע בהן, וביניהן ההצלבה החזקה ביותר במאגר.

**חובה לקרוא קודם: `references/db-map.md`.** הטבלאות כאן הן הגדולות במאגר, ורוב השאילתות האינטואיטיביות עליהן נקטעות. המפה קובעת מה מותר.

## עקרונות יסוד

1. **תמיכה או התקשרות אינן עוולה.** המדינה קונה שירותים ומתמכת בגופים לפי מסלולים מוסדרים. הסיפור אינו "קיבלה כסף" אלא הפער: סכום שלא מתיישב עם היקף הפעילות, ריכוז אצל גוף אחד, מסלול שלא מתאים לתוכן, או דוח כספי שלא מסתדר עם התמיכה.
2. **המאגר מחזיר רשומות גולמיות.** `budget_contracts` ו-`budget_supports` הן שיקוף של מפתח התקציב; `amutot` שיקוף של גיידסטאר. כל שורה היא ליד עד לאימות מול המקור.
3. **`volume` אינו `executed`.** ב-`budget_contracts`, `volume` הוא היקף ההתקשרות ו-`executed` מה שבוצע בפועל. אל תכתוב "שילמה" על `volume`. אותו דבר ב-`budget_supports`: `amount_approved` מול `amount_paid` - ורבות מהשורות עם `amount_paid` ריק (אומת).
4. **ההצלבה לפי מזהה, לא לפי שם.** `budget_supports.recipient_entity_id` תואם ל-`amutot.amuta_id` כשמקבלת התמיכה היא עמותה (מזהים שמתחילים ב-58). זה מה שהופך התאמת שם להתאמת זהות. עיריות ותאגידים מקבלים מזהים בפורמטים אחרים (`500…`, `510…`) ואינם ב-`amutot`.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ליד עדיפות + מה הראיה החסרה.

## מלכודת השאילתות - קרא לפני שאתה כותב SQL

זו הטבלה הגדולה במאגר וההתנהגות שלה לא אינטואיטיבית. כל השורות כאן אומתו בהרצה:

| מה שרוצים | מה קורה | מה עושים במקום |
|---|---|---|
| `GROUP BY supplier_name` ב-`budget_contracts` | **נקטע** | צמצם ב-`publisher_name=` ואז קבץ |
| `WHERE supplier_name LIKE '%ספק%'` | **נקטע** - אין אינדקס על העמודה | אין נתיב ישיר לחיפוש ספק. עבור דרך `publisher_name=` של המשרדים הרלוונטיים וסנן בפלט |
| `WHERE recipient_entity_name LIKE '%שם%'` ב-`budget_supports` | **נקטע** - האינדקס על ה-`recipient_entity_id`, לא על השם | הוסף `year = <שנה>` או `supporting_ministry = '<משרד>'` לפני ה-`LIKE` |
| `GROUP BY recipient_entity_name` | **נקטע** | צמצם ב-`year=` ואז קבץ |
| `GROUP BY publisher_name` ב-`budget_contracts` | **נקטע בכל סף** - גם עם `WHERE volume >= 1000000000` | `SELECT DISTINCT publisher_name` (בלי תנאי) לרשימה, ואז שאילתה נפרדת לכל משרד |
| `SELECT DISTINCT publisher_name ... WHERE publisher_name IS NOT NULL` | **נקטע** - התנאי שובר את השימוש באינדקס | `SELECT DISTINCT publisher_name FROM budget_contracts LIMIT 100` נקי |
| `COUNT(*)` על כל `budget_contracts` | נקטע לפעמים | הסתמך על `list_tables()` לספירה |
| `new_since` על טבלאות התקציב | חסר משמעות | ה-`first_seen_at` הוא שניות רצות של import חד-פעמי מ-24.07.2026. אין "מה חדש" כאן |

**החוק:** ב-`budget_contracts` נכנסים רק דרך `publisher_name`, `entity_id` או `volume`. ב-`budget_supports` רק דרך `year`, `supporting_ministry`, `recipient_entity_id` או `amount_approved`.

## מצב א - התקשרויות של משרד (budget_contracts)

זו נקודת הכניסה הבטוחה היחידה לטבלה:

```sql
SELECT supplier_name, publisher_name, purchasing_unit, volume, executed,
       purpose, purchase_method, exemption_reason, start_date, end_date, tender_key
FROM budget_contracts
WHERE publisher_name = 'משרד התחבורה והבטיחות בדרכים'
ORDER BY volume DESC
LIMIT 40
```

ריכוז ספקים בתוך משרד:
```sql
SELECT supplier_name, COUNT(*) deals, SUM(volume) total_volume, SUM(executed) total_executed
FROM budget_contracts
WHERE publisher_name = '<שם המשרד המדויק>'
GROUP BY supplier_name
ORDER BY total_volume DESC
LIMIT 25
```

**`purchase_method` ו-`exemption_reason`** הם השדות התחקיריים: הם אומרים איך ההתקשרות נעשתה. התקשרות גדולה בשיטה שאינה מכרז פומבי היא ליד. `tender_key` מאפשר לחזור למכרז.

**לקבלת שמות המשרדים המדויקים** - `DISTINCT` נקי, בלי שום תנאי (הוא רץ על האינדקס; הוספת `WHERE publisher_name IS NOT NULL` דווקא שוברת אותו):
```sql
SELECT DISTINCT publisher_name FROM budget_contracts LIMIT 100
```
העתק את השם משם בדיוק - יש כמה גרסאות היסטוריות לאותו גוף ("המשרד לביטחון הפנים" מול "המשרד לביטחון לאומי"), וכל אחת מחזיקה שורות אחרות.

**ההתקשרויות הגדולות בכל הממשלה** (ללא `GROUP BY` - הוא נקטע גם עם צמצום על `volume`):
```sql
SELECT publisher_name, supplier_name, volume, executed, purchase_method, purpose
FROM budget_contracts
WHERE volume >= 1000000000
ORDER BY volume DESC
LIMIT 40
```
זה הדפוס שמצא את עמידר ב-1.82 מיליארד בשיטת "פטור ממכרז", ואת דן בהיקף 6.5 מיליארד שממנו בוצעו 199 מיליון. **`GROUP BY publisher_name` על הטבלה הזאת נקטע בכל סף שנבדק** - קבץ את הפלט בצד שלך.

## מצב ב - תמיכות ומענקים (budget_supports)

המקבלים הגדולים בשנה:
```sql
SELECT recipient_entity_name, recipient_entity_id, supporting_ministry,
       amount_approved, amount_paid, purpose, request_type, item_url
FROM budget_supports
WHERE year = 2024
ORDER BY amount_paid DESC
LIMIT 30
```
(השנים בטבלה: 2020-2025. 2025 חלקית - 6,769 שורות מול ~19 אלף בשנה מלאה.)

גוף מסוים, לאורך שנים - קודם מצא את המזהה בתוך שנה אחת, ואז עבוד דרכו:
```sql
SELECT recipient_entity_id, recipient_entity_name FROM budget_supports
WHERE year = 2024 AND recipient_entity_name LIKE '%שם הגוף%' LIMIT 5;

SELECT year, supporting_ministry, amount_approved, amount_paid, purpose
FROM budget_supports WHERE recipient_entity_id = '<id>' ORDER BY year DESC
```
המסלול דרך המזהה הוא גם מדויק יותר וגם לא נקטע.

תמיכות של משרד מסוים:
```sql
SELECT recipient_entity_name, year, amount_approved, amount_paid, purpose
FROM budget_supports
WHERE supporting_ministry = '<שם המשרד>'
ORDER BY amount_paid DESC LIMIT 40
```

## מצב ג - ההצלבה: תמיכה מול הדוח הכספי (זו הליבה)

זה מה שאין בשום סקיל אחר: לקחת מקבלת תמיכה ולראות את מצבה המדווח בגיידסטאר באותה שורה.

```sql
SELECT s.recipient_entity_name, s.supporting_ministry, s.amount_paid,
       a.status, a.classification, a.revenue, a.expenses,
       a.employees, a.volunteers, a.nihul_takin, a.last_report_year, a.city
FROM budget_supports s
JOIN amutot a ON a.amuta_id = s.recipient_entity_id
WHERE s.year = 2024 AND s.amount_paid > 20000000
ORDER BY s.amount_paid DESC
LIMIT 25
```

ה-`WHERE` על `year` ועל `amount_paid` הוא מה שמאפשר ל-`JOIN` הזה לרוץ. בלעדיו הוא נקטע.

**מה לחפש בפלט:**
- **תמיכה שהיא חלק גדול מהמחזור** (`amount_paid` מול `revenue`) - גוף שתלוי כמעט כולו בכספי מדינה.
- **`nihul_takin` שאינו "נחתם אישור"** בגוף שמקבל תמיכה גדולה - אישור ניהול תקין הוא תנאי סף בחלק מהמסלולים.
- **`status` שאינו "רשומה"/"פעילה"** - עמותה שנמחקה או מוגבלת שמופיעה כמקבלת תמיכה.
- **`last_report_year` מיושן** - גוף שלא דיווח לאחרונה וממשיך לקבל.
- **פער בין `employees`/`volunteers` להיקף התמיכה.**

הפער הוא הליד, לא הסכום.

## מצב ד - מכרזי משרד הביטחון (mod_tenders)

```sql
SELECT title, type, category, status, is_cancelled, publish_date,
       submission_date, url
FROM mod_tenders
WHERE submission_date >= date('now')
ORDER BY submission_date ASC
LIMIT 40
```
מכרזים שבוטלו (`is_cancelled`) ומכרזים שמועד ההגשה שלהם חלף בלי המשך הם הלידים כאן. הטבלה קטנה (2,967) וסובלנית לשאילתות.

## שלב האימות - מול המקור הרשמי

- **תמיכות:** `item_url` מוביל למפתח התקציב. אמת את הסכום, המסלול והשנה.
- **התקשרויות:** ב-`budget_contracts` אין URL לשורה. אמת דרך מפתח התקציב לפי `order_id`/`tender_key`, או מול הפרסום במנהל הרכש.
- **עמותות:** אמת מול גיידסטאר ורשם העמותות לפי `amuta_id`. הדוח הכספי ב-`amutot` הוא שיקוף של דיווח, לא ביקורת.
- **מכרזי ביטחון:** `url` לדף המכרז.

בלי אימות מול המקור - זה ליד, לא ממצא. אל תפרסם סכום שלא ראית ברשומה הרשמית.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה נקטעת | כמעט תמיד `LIKE`/`GROUP BY` בלי צמצום. ראה טבלת המלכודות למעלה |
| `amount_paid` ריק בהרבה שורות | צפוי - התמיכה אושרה ולא שולמה, או טרם דווחה. השתמש ב-`amount_approved` וציין את ההבחנה |
| `entity_name` ריק ב-budget_contracts | קיים בזנב הטבלה. סנן `WHERE supplier_name <> ''` |
| ה-JOIN ל-amutot לא מחזיר את הגוף | המזהה אינו של עמותה (עירייה/חברה). חפש ידנית ברשם החברות; אל תניח שאין דיווח |
| שם משרד לא תפס | השמות ב-budget שונים מ-exemptions ("מ.האוצר - מנהלת הגמלאות"). הוצא את הרשימה בשאילתת ה-`GROUP BY publisher_name` המצומצמת |
| רוצים "מה חדש" | אין. הטבלאות נטענו ב-import. לדייג'סט יומי יש `osint-daily-leads` על טבלאות אחרות |

**אסור:** להציג תמיכה או התקשרות כ"העברת כספים חשודה" על סמך סכום. הפער בין התמיכה לדוח הכספי הוא שאלה לגוף ולמשרד המתמך, לא מסקנה.

## אתיקה

עמותות וחברות שמקבלות כספי ציבור הן נושא לגיטימי לתחקור, וכך גם המשרד שהעביר. יחד עם זאת: `nihul_takin` חסר אינו הכרח עוולה (יכול להיות עיכוב מנהלי), מחזור גדול אינו בזבוז, ותלות בכספי מדינה היא מודל מקובל בשירותי רווחה. פנה לגוף לתגובה לפני פרסום, ייחס כל נתון למקור, ואל תקבע מניע. אל תגלוש לפרטים על אנשים פרטיים שמופיעים כאנשי קשר.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): בחירת נקודת הכניסה המותרת, שליפה מצומצמת, הצלבה ל-amutot לפי מזהה, זיהוי הפער, אימות מול המקור הרשמי.

## דוח הדסק - מבנה קבוע

```markdown
# לידים - כסף ציבורי

## טווח הסריקה
[אילו טבלאות, איזה משרד/שנה/סף סכום, ומה נשאר מחוץ לסריקה בגלל מלכודת שאילתה]

## לידים מדורגים
לכל ליד:
- **הגוף:** [שם + מזהה תאגיד]
- **הכסף:** [סכום מאושר מול שולם / היקף מול בוצע, שנה, משרד, מסלול]
- **מצב הגוף:** [מחזור, עובדים, ניהול תקין, שנת דיווח אחרונה - אם יש התאמה ב-amutot]
- **הפער:** [מה לא מתיישב - תלות, ניהול תקין, סטטוס, מסלול]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [item_url / tender_key / amuta_id + השאילתה]

## מה לאמת לפני פרסום
[לכל ליד גבוה: אישור הסכום במפתח התקציב, הדוח בגיידסטאר, תגובת המשרד והגוף]

**שורה תחתונה לדסק:** [הליד אחד שהכי בשל, ולמה]

Sources: [שאילתות osint-db + קישורי מקור שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. תמיד הבחן בין מאושר לשולם ובין היקף לבוצע, ואל תציג סכום כעובדה בלי אימות.
