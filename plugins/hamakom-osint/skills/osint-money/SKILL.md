---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table
name: osint-money
version: 1.2.0
description: >-
  מעקב אחרי כסף ציבורי עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db - התקשרויות בפועל (budget_contracts, מיליון שורות ממפתח התקציב), תמיכות ומענקים (budget_supports, 330 אלף), עמותות וחל"צים ודוחותיהם הכספיים (amutot מגיידסטאר, 76 אלף), ומכרזי משרד הביטחון (mod_tenders). היכולת המרכזית: הצלבת תמיכה ממשלתית עם הדוח הכספי של מקבלת התמיכה לפי מזהה תאגיד (recipient_entity_id = amuta_id), ולא לפי שם. הפעל כשדור כותב "מי מקבל כסף מ", "כמה תמיכות קיבלה", "התקשרויות של משרד X", "מפתח התקציב", "תמיכות לעמותות", "כמה המדינה שילמה ל", "מי הספק הגדול של", "עמותה שמקבלת תמיכות", "מכרזי משרד הביטחון". כל פריט הוא ליד לבדיקה מול המקור הרשמי, לא ממצא מאומת. לפטורים ממכרז ראה osint-exemptions; לתיק חוצה-תחומים ראה osint-entity-dossier.
---

# osint-money - מעקב כסף ציבורי

סקיל לתחקיר תזרים הכסף מהמדינה: מי מקבל, מכמה משרדים, באיזה מסלול, ומה מצבו הכספי המדווח. ארבע טבלאות שאף סקיל אחר לא נוגע בהן, וביניהן ההצלבה החזקה ביותר במאגר.

## עקרונות יסוד

1. **תמיכה או התקשרות אינן עוולה.** המדינה קונה שירותים ומתמכת בגופים לפי מסלולים מוסדרים. הסיפור אינו "קיבלה כסף" אלא הפער: סכום שלא מתיישב עם היקף הפעילות, ריכוז אצל גוף אחד, מסלול שלא מתאים לתוכן, או דוח כספי שלא מסתדר עם התמיכה.
2. **המאגר מחזיר רשומות גולמיות.** `budget_contracts` ו-`budget_supports` הן שיקוף של מפתח התקציב; `amutot` שיקוף של גיידסטאר. כל שורה היא ליד עד לאימות מול המקור.
3. **`volume` אינו `executed`.** ב-`budget_contracts`, `volume` הוא היקף ההתקשרות ו-`executed` מה שבוצע בפועל. אל תכתוב "שילמה" על `volume`. אותו דבר ב-`budget_supports`: `amount_approved` מול `amount_paid` - ו-`amount_paid` ריק ב-79,807 מתוך 329,580 שורות.
4. **ההצלבה לפי מזהה, לא לפי שם.** `budget_supports.recipient_entity_id` תואם ל-`amutot.amuta_id` כשמקבלת התמיכה היא עמותה (מזהה שמתחיל ב-58, 74,046 מתוך 76,188 השורות ב-`amutot`) או חברה לתועלת הציבור (`kind = 'חל"צ'`, 1,500 שורות, מזהה שמתחיל לרוב ב-51). זה מה שהופך התאמת שם להתאמת זהות. עיריות וחברות רגילות אינן ב-`amutot`.
5. **`volume` אינו בשקלים, ושורה שהוחלפה אינה נספרת.** `volume` ב-`budget_contracts` הוא במטבע של `currency` (ביין: במאות ין); 11,248 שורות הן במטבע זר. הסכום בש"ח של שורה הוא `b.volume * FX`, כש-FX הוא השער היציג של בנק ישראל ביום `order_date`:
   ```
   FX = (CASE WHEN b.currency IS NULL OR b.currency = 'ILS' THEN 1.0 ELSE boi_fx_rate(b.currency, b.order_date) * (CASE b.currency WHEN 'JPY' THEN 100 ELSE 1 END) END)
   ```
   כל סכום, ספירה או דירוג של התקשרויות: `SUM(b.volume * FX)` עם `b.superseded IS NOT TRUE AND FX IS NOT NULL`, **לעולם לא `SUM(volume)`**. שורה `superseded` (29,102 שורות) הוחלפה בדיווח מאוחר יותר של אותו `order_id`, והסכום שלה כבר בשורה החדשה. ל-1,675 שורות במטבע זר אין FX (מטבע שאינו קוד בן שלוש אותיות - שורת מקור שזזה בעמודות - או מטבע שבנק ישראל אינו מפרסם לו שער): שורה כזו לא נספרת, ומציינים אותה. `executed` כבר בש"ח במקור, גם בשורה זרה, ואינו מומר. הנוסחה מופיעה גם בתיאור של `query_db`.
6. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ליד עדיפות + מה הראיה החסרה.

## כלי קודם

לגוף מסוים בשמו - `search_entity("שם")` ואחריו `entity_profile(id)` (או `entity_profile` ישירות עם מספר תאגיד בן 9 ספרות). הפרופיל מחזיר את ההתקשרויות, התמיכות והפטורים של הישות, עם סכומים לפי תפקיד ומטבע, מאושר ושולם בנפרד ובלי שורות שהוחלפו. זו הדרך הקצרה והנכונה ל"כמה המדינה שילמה ל-X". `query_db` - לסריקה לפי משרד, שנה או סף, ולהצלבה מול `amutot`.

**טריות:** לפני מסקנה של "אין במאגר", בדוק שהמקור רץ:
```sql
SELECT source, max(started_at) FROM scrape_runs
WHERE status IN ('ok','warn') AND source IN ('budget_contracts','budget_supports','amutot','mod_sapakim_scraper')
GROUP BY 1
```
(`mod_sapakim_scraper` הוא המקור של `mod_tenders`.) מפת המאגר המלאה, שנבנית מהמאגר: `references/db-map.md` בתיקיית התוסף.

## מלכודת השאילתות - קרא לפני שאתה כותב SQL

הגבול הוא 10 שניות לשאילתה, 500 שורות ו-50 אלף תווים בפלט. `query_db` מחזיר 100 שורות כברירת מחדל, ו-`LIMIT` בתוך ה-SQL לא מעלה את התקרה הזו. ליותר שורות מעבירים לכלי את הפרמטר `limit` (עד 500). `budget_contracts` (1,020,934 שורות) היא הטבלה היחידה כאן שבה זה מורגש. כל השורות נמדדו ב-20.11.2026:

| מה שרוצים | מה קורה | מה עושים |
|---|---|---|
| `WHERE supplier_name LIKE '%ספק%'` ב-`budget_contracts` | **עובד, אבל על הגבול** - אין אינדקס על העמודה, וכל שאילתה סורקת את כל הטבלה (2.5-8.5 שניות במדידות) | עדיף `entity_id = '<מספר תאגיד>'` (מאונדקס, כשנייה) או `entity_profile`. אם בכל זאת LIKE - בלי פונקציות נוספות בשאילתה, ואם חרגה, הוסף `publisher_name =` |
| `GROUP BY supplier_name` או `GROUP BY publisher_name` על כל `budget_contracts` | **עובד, על הגבול** (7-8.5 שניות) | צמצם ב-`publisher_name =` ואז קבץ (כ-2 שניות) |
| `SELECT DISTINCT publisher_name` | עובד (83 גופים) | כך מקבלים את השמות המדויקים |
| `WHERE recipient_entity_name LIKE` / `GROUP BY recipient_entity_name` ב-`budget_supports` | עובד (2-3 שניות) | עדיין עדיף לעבור למזהה מהר ככל האפשר |
| `JOIN` של `budget_supports` ל-`amutot` | עובד גם בלי `WHERE` (כ-2.5 שניות) | |
| `new_since` על טבלאות התקציב | מחזיר בעיקר השלמות | ב-`budget_contracts` נקלטו 33,114 שורות מאוגוסט 2026, רובן התקשרויות משנים קודמות (`order_date` של 2015-2025); `budget_supports` גדלה ב-2 שורות בלבד מאז הטעינה ביולי. "מה חדש" כאן הוא "מה נקלט", לא "מה נחתם" - בדוק `order_date` |

**נקודות הכניסה המאונדקסות:** ב-`budget_contracts`: `publisher_name`, `entity_id`, `volume`, `order_id`. ב-`budget_supports`: `year`, `supporting_ministry`, `recipient_entity_id`, `amount_approved`.

- **פטורים:** בכל סכום או דירוג של `exemptions.amount_ils` מסננים `amount_kind IS NULL`. שורה עם `amount_kind` (הקצאות ותמורות של רמ"י) היא תמורה שהמדינה מקבלת, לא הוצאה.
- **שורה שירדה מהמקור** מסומנת ב-`gone_at` (כנסת) או ב-`removed_at` (רשם החברות, מאיה). מסננים `IS NULL`.

## מצב א - התקשרויות של משרד (budget_contracts)

```sql
SELECT b.supplier_name, b.publisher_name, b.purchasing_unit, b.currency, b.volume,
       b.volume * (CASE WHEN b.currency IS NULL OR b.currency = 'ILS' THEN 1.0 ELSE boi_fx_rate(b.currency, b.order_date) * (CASE b.currency WHEN 'JPY' THEN 100 ELSE 1 END) END) AS volume_ils,
       b.executed, b.purpose, b.purchase_method, b.exemption_reason, b.start_date, b.end_date,
       b.tender_key, b.order_id
FROM budget_contracts b
WHERE b.publisher_name = 'משרד התחבורה והבטיחות בדרכים' AND b.superseded IS NOT TRUE
ORDER BY volume_ils DESC NULLS LAST
LIMIT 40
```
`volume_ils` ריק = שורה שאין לה שער (עקרון 5). היא בתחתית ולא נספרת.

ריכוז ספקים בתוך משרד:
```sql
SELECT b.supplier_name, COUNT(*) deals,
       SUM(b.volume * (CASE WHEN b.currency IS NULL OR b.currency = 'ILS' THEN 1.0 ELSE boi_fx_rate(b.currency, b.order_date) * (CASE b.currency WHEN 'JPY' THEN 100 ELSE 1 END) END)) AS total_volume_ils,
       SUM(b.executed) total_executed
FROM budget_contracts b
WHERE b.publisher_name = '<שם המשרד המדויק>' AND b.superseded IS NOT TRUE
  AND (CASE WHEN b.currency IS NULL OR b.currency = 'ILS' THEN 1.0 ELSE boi_fx_rate(b.currency, b.order_date) * (CASE b.currency WHEN 'JPY' THEN 100 ELSE 1 END) END) IS NOT NULL
GROUP BY b.supplier_name
ORDER BY total_volume_ils DESC NULLS LAST
LIMIT 25
```
במשרד גדול (משרד הבריאות, 138 אלף שורות) הריצה הראשונה נמדדה פעם אחת מעל 10 שניות, ובהרצה חוזרת כ-2 שניות: הנתונים נקראים מהדיסק בפעם הראשונה. אם חרגה, הרץ שוב, או הוסף `AND b.volume >= 100000`.

**`purchase_method` ו-`exemption_reason`** הם השדות התחקיריים: הם אומרים איך ההתקשרות נעשתה. התקשרות גדולה בשיטה שאינה מכרז פומבי היא ליד לבדיקה, לא ממצא. `tender_key` מאפשר לחזור למכרז.

**לקבלת שמות המשרדים המדויקים:**
```sql
SELECT DISTINCT publisher_name FROM budget_contracts LIMIT 100
```
העתק את השם משם בדיוק - יש כמה גרסאות היסטוריות לאותו גוף ("המשרד לביטחון הפנים" מול "המשרד לביטחון לאומי"), וכל אחת מחזיקה שורות אחרות.

**ספק מסוים לפי מספר תאגיד** (אחרי `search_entity`, או מ-`ica_companies.company_id`; ברשם החברות "בע"מ" כתוב "בע~מ"):
```sql
SELECT b.publisher_name, b.supplier_name,
       b.volume * (CASE WHEN b.currency IS NULL OR b.currency = 'ILS' THEN 1.0 ELSE boi_fx_rate(b.currency, b.order_date) * (CASE b.currency WHEN 'JPY' THEN 100 ELSE 1 END) END) AS volume_ils,
       b.executed, b.purchase_method, b.order_date
FROM budget_contracts b
WHERE b.entity_id = '<מספר תאגיד>' AND b.superseded IS NOT TRUE
ORDER BY volume_ils DESC NULLS LAST
LIMIT 50
```

**ההתקשרויות הגדולות בכל הממשלה:**
```sql
SELECT b.publisher_name, b.supplier_name, b.currency, b.volume,
       b.volume * (CASE WHEN b.currency IS NULL OR b.currency = 'ILS' THEN 1.0 ELSE boi_fx_rate(b.currency, b.order_date) * (CASE b.currency WHEN 'JPY' THEN 100 ELSE 1 END) END) AS volume_ils,
       b.executed, b.purchase_method, b.purpose
FROM budget_contracts b
WHERE b.volume >= 1000000000 AND b.superseded IS NOT TRUE
ORDER BY volume_ils DESC NULLS LAST
LIMIT 40
```
זה הדפוס שמצא את עמידר בהיקף 1.82 מיליארד בשיטת "פטור ממכרז" (משרד הבינוי והשיכון), ואת דן בהיקף 6.5 מיליארד שממנו בוצעו 199 מיליון. הסינון `volume >= 1000000000` הוא על הסכום הגולמי כדי לרוץ על האינדקס: שורה במטבע זר שערכה בש"ח גבוה מהסף אבל ה-`volume` שלה נמוך ממנו (דולר, יורו) לא תיתפס כאן, ושורה ביין עם `volume` גבוה עלולה להיתפס ולהתברר קטנה. הדירוג הוא לפי `volume_ils`.

## מצב ב - תמיכות ומענקים (budget_supports)

המקבלים הגדולים בשנה:
```sql
SELECT recipient_entity_name, recipient_entity_id, supporting_ministry,
       amount_approved, amount_paid, purpose, request_type, item_url
FROM budget_supports
WHERE year = 2024
ORDER BY amount_paid DESC NULLS LAST
LIMIT 30
```
(השנים בטבלה: 2004-2025. 2025 חלקית - 6,769 שורות מול 17-21 אלף בשנה מלאה בעשור האחרון. 2004-2006 דלות.)

גוף מסוים, לאורך שנים - קודם מצא את המזהה, ואז עבוד דרכו:
```sql
SELECT recipient_entity_id, recipient_entity_name FROM budget_supports
WHERE year = 2024 AND recipient_entity_name LIKE '%שם הגוף%' LIMIT 5
```
```sql
SELECT year, supporting_ministry, amount_approved, amount_paid, purpose
FROM budget_supports WHERE recipient_entity_id = '<מזהה>' ORDER BY year DESC
```
המסלול דרך המזהה מדויק יותר: אותו גוף מופיע בכמה איותים של שם.

תמיכות של משרד מסוים:
```sql
SELECT recipient_entity_name, year, amount_approved, amount_paid, purpose
FROM budget_supports
WHERE supporting_ministry = '<שם המשרד>'
ORDER BY amount_paid DESC NULLS LAST LIMIT 40
```
שמות המשרדים כאן (53 ערכים) שונים מאלה של `budget_contracts` ושל `exemptions` ("מ.האוצר - מנהלת הגמלאות"). הוצא אותם ב-`SELECT DISTINCT supporting_ministry FROM budget_supports`.

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

**מה לחפש בפלט:**
- **תמיכה שהיא חלק גדול מהמחזור** (`amount_paid` מול `revenue`) - גוף שתלוי כמעט כולו בכספי מדינה.
- **`nihul_takin` שאינו "נחתם אישור"** בגוף שמקבל תמיכה גדולה - אישור ניהול תקין הוא תנאי סף בחלק מהמסלולים. הערכים: "נחתם אישור", "אין אישור", "מסורב", "מבוטל", "בטיפול" ועוד; ריק ב-41,275 שורות, וריק אינו "אין אישור".
- **`status` שאינו "רשומה"/"פעילה"** - למשל "נמחקה" (33,527 שורות) או בהליכי פירוק, אצל גוף שמופיע כמקבל תמיכה.
- **`last_report_year` מיושן** - גוף שלא דיווח לאחרונה וממשיך לקבל.
- **פער בין `employees`/`volunteers` להיקף התמיכה.**

**מלכודת:** `expenses = 0` ב-67,260 מתוך 76,188 שורות. זה כמעט תמיד "לא דווח", לא הוצאות אפס. אל תבנה ליד על `expenses` בלי לבדוק את הדוח בגיידסטאר.

הפער הוא הליד, לא הסכום.

## מצב ד - מכרזי משרד הביטחון (mod_tenders)

מכרזים שבוטלו:
```sql
SELECT title, type, category, status, publish_date, submission_date, url
FROM mod_tenders
WHERE is_cancelled = 1
ORDER BY submission_date DESC NULLS LAST
LIMIT 40
```
מכרזים שמועד ההגשה שלהם חלף ולא בוטלו (שאילתה נפרדת: `OR` בשאילתה אחת מחזיר כמעט כל מכרז שהגשתו חלפה, כלומר את רוב הטבלה):
```sql
SELECT title, type, category, status, publish_date, submission_date, url
FROM mod_tenders
WHERE is_cancelled = 0
  AND substr(submission_date,1,10) < to_char(CURRENT_DATE,'YYYY-MM-DD')
ORDER BY submission_date DESC NULLS LAST
LIMIT 40
```
"חלף בלי המשך" אינו עמודה: את ההמשך (זוכה, ביטול מאוחר, הארכה) בודקים בדף המכרז (`url`). רק זה הופך מכרז שהגשתו חלפה לליד. הטבלה קטנה (3,693 שורות; `status`: finished 3,460, active 142, cancelled 91) ומועדי ההגשה בה מתחילים בדצמבר 2025, כך שאין בה היסטוריה ישנה. מכרזים פתוחים: `substr(submission_date,1,10) >= to_char(CURRENT_DATE,'YYYY-MM-DD')`.

## שלב האימות - מול המקור הרשמי

- **תמיכות:** `item_url` מוביל למפתח התקציב. אמת את הסכום, המסלול והשנה.
- **התקשרויות:** ב-`budget_contracts` אין URL לשורה. אמת דרך מפתח התקציב לפי `order_id`/`tender_key`, או מול הפרסום במנהל הרכש.
- **עמותות:** אמת מול גיידסטאר ורשם העמותות לפי `amuta_id`. הדוח הכספי ב-`amutot` הוא שיקוף של דיווח, לא ביקורת.
- **מכרזי ביטחון:** `url` לדף המכרז.

בלי אימות מול המקור - זה ליד, לא ממצא. אל תפרסם סכום שלא ראית ברשומה הרשמית.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה חרגה מ-10 שניות | כמעט תמיד `LIKE` או `GROUP BY` על כל `budget_contracts`. ראה טבלת המלכודות למעלה; עבור ל-`entity_id` או צמצם ב-`publisher_name` |
| `amount_paid` ריק בהרבה שורות | צפוי - התמיכה אושרה ולא שולמה, או טרם דווחה. השתמש ב-`amount_approved` וציין את ההבחנה |
| `entity_name` ריק ב-`budget_contracts` | קורה ב-249,112 שורות (24%). ב-238,996 מהן `supplier_name` מלא - השתמש בו כשם הספק |
| ה-JOIN ל-`amutot` לא מחזיר את הגוף | המזהה אינו של עמותה או חל"צ (עירייה/חברה). חפש ברשם החברות או ב-`entity_profile`; אל תניח שאין דיווח |
| שם משרד לא תפס | השמות שונים בין הטבלאות. הוצא את הרשימה ב-`SELECT DISTINCT` על העמודה של אותה טבלה |
| רוצים "מה חדש" | אין "מה נחתם השבוע" כאן: הטבלאות מתעדכנות במנות, ורוב מה שנקלט הוא השלמה של עבר. לדייג'סט יומי יש `osint-daily-leads` על טבלאות אחרות |

**אסור:** להציג תמיכה או התקשרות כ"העברת כספים חשודה" על סמך סכום. הפער בין התמיכה לדוח הכספי הוא שאלה לגוף ולמשרד המתמך, לא מסקנה.

## אתיקה

עמותות וחברות שמקבלות כספי ציבור הן נושא לגיטימי לתחקור, וכך גם המשרד שהעביר. יחד עם זאת: `nihul_takin` חסר אינו הכרח עוולה (יכול להיות עיכוב מנהלי), מחזור גדול אינו בזבוז, ותלות בכספי מדינה היא מודל מקובל בשירותי רווחה. פנה לגוף לתגובה לפני פרסום, ייחס כל נתון למקור, ואל תקבע מניע. אל תגלוש לפרטים על אנשים פרטיים שמופיעים כאנשי קשר.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): בדיקת טריות המקור, `search_entity` / `entity_profile` לגוף בשמו, שליפה מצומצמת, הצלבה ל-`amutot` לפי מזהה, זיהוי הפער, אימות מול המקור הרשמי.

## דוח הדסק - מבנה קבוע

```markdown
# לידים - כסף ציבורי

## טווח הסריקה
[אילו טבלאות, איזה משרד/שנה/סף סכום, מתי המקור רץ לאחרונה, ומה נשאר מחוץ לסריקה]

## לידים מדורגים
לכל ליד:
- **הגוף:** [שם + מזהה תאגיד]
- **הכסף:** [סכום מאושר מול שולם / היקף בש"ח מול בוצע, שנה, משרד, מסלול]
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
