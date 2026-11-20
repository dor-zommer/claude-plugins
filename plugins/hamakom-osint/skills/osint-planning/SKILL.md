---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__new_since mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-planning
version: '1.4.0'
description: לידים מתכנון ובנייה (מנהל התכנון / מבא"ת) בכל ישראל, מעל ה-osint-db (טבלת mavat_plans) עבור דסק "המקום הכי חם בגיהנום". מסנן לפי מחוז (district_name) ורשות/מרחב (plan_county_name), לפי תוכן מטרות (pl_objectives, pl_landuse_string), תוכניות שהופקדו לאחרונה או שעברו שלב (depositing_date, mavat_status_history), תוכניות גדולות בשטח (pl_area_dunam), ומספר יחידות דיור מתוכננות (quantity_delta_120/60/75/80). יש lat/lng למיפוי. הפעל כשדור כותב "תוכניות בנייה ב<מקום>", "מה הופקד לאחרונה", "תוכניות גדולות", "כמה יח\"ד מתוכננות ב", "מה מתוכנן ב<עיר>", "תוכניות דיור באזור". זהו התכנון של מוסדות התכנון בישראל (מבא"ת), כולל מזרח ירושלים ורמת הגולן - לתכנון ביו"ש/התנחלויות ראה osint-yosh-planning. כל תוכנית היא ליד לבדיקה מול pl_url הרשמי - לא ממצא מאומת. לתיק על יזם/חברה ראה osint-entity-dossier.
---

# osint-planning - לידים מתכנון ובנייה (כל ישראל)

סקיל לזיהוי לידים תחקיריים בטבלת `mavat_plans` שב-osint-db (תוכניות תכנון ובנייה של מוסדות התכנון בישראל, 37,576 תוכניות, נמדד 20.11.2026). התוצר הוא **לידים לבדיקה** - תוכנית שעלתה בסריקה היא נקודת פתיחה, ואימותה מול `pl_url` הרשמי קודם לכל פרסום.

> **תיחום:** סקיל זה לתוכניות של מוסדות התכנון בישראל (מבא"ת). **מבא"ת כולל גם תוכניות במזרח ירושלים וברמת הגולן** (נבדק 20.11.2026: קצרין, נאות גולן, שער הגולן ומרום גולן ב-`plan_county_name`; בית חנינא, שועפט, ג'בל מוכבר וסילוואן בשמות תוכניות במחוז ירושלים), שאינם "בתוך הקו הירוק" - בדיווח מציינים את המיקום במדויק ולא כותבים "בתוך הקו הירוק". לתוכניות ביהודה ושומרון/התנחלויות - `osint-yosh-planning` (טבלת yosh_plans), שהוא רגיש עריכתית ויש לו הנחיות הקשר נפרדות.

## עקרונות יסוד

1. **המאגר מחזיר רשומות גולמיות.** כל שורה ב-`mavat_plans` היא רישום תכנוני, לא סיפור. תוכנית גדולה או הפקדה חדשה היא ליד; אימות מול `pl_url` (מנהל התכנון) הופך אותה לבסיס לכתבה.
2. **"הופקד" ≠ "אושר" ≠ "נבנה".** `depositing_date` הוא שלב בהליך, `station_desc` הוא השלב הנוכחי, ו-`pl_rejection_date` מציין דחייה. אל תכתוב "ייבנו X יח"ד" כשהתוכנית רק הופקדה - תאר את השלב המדויק.
3. **יחידות דיור הן הערכת דלתא.** `quantity_delta_120/60/75/80` הן יח"ד מתוכננות לפי חתכים; הן אומדן תכנוני, לא דירות שנמסרו. ציין שזה מתוכנן.
4. **גודל שטח הוא ליד גס.** `pl_area_dunam` גדול מצדיק מבט, אבל שטח אינו דרמה כשלעצמו (יער, חקלאות). הצלב עם `pl_landuse_string` ו-`pl_objectives`.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ליד תן עדיפות + מה הראיה החסרה (שלב ההליך, ייעוד, יזם).

## שלב 1 - מיפוי הטבלה

**חוקי המאגר.** המפה המלאה היא `references/db-map.md` בשורש התוסף (`../../references/db-map.md` מתיקיית הסקיל). יש סביבות שטוענות רק את SKILL.md, ולכן העיקר כאן:
- **כלי קודם.** לשם (אדם, חברה, רשות, מקום, תוכנית) - `search_entity(name)`, אחריו `entity_profile(<המזהה שחזר>)`, ו-`query_db` רק למה שהכלים לא מחזירים.
- את העמודות נותן `describe_table("<טבלה>")`, ואת רשימת הטבלאות `describe_table()` בלי שם. לא מנחשים שם עמודה.
- **חוק הזהב:** אין אגרגציה ואין `LIKE` על טבלה גדולה בלי `WHERE` על עמודה מאונדקסת. שאילתה שנקטעה או שחרגה מהזמן (10 שניות) אינה "אין תוצאות".
- **תאריכים.** רוב עמודות התאריך במאגר הן טקסט. `osint_date(col)` מחזיר מהן ISO (`YYYY-MM-DD`) בכל הפורמטים שבמאגר (ISO, `DD/MM/YYYY`, גם עם שעה), ומשווים מול `to_char(CURRENT_DATE - 90,'YYYY-MM-DD')`. `date('now', ...)` הוא SQLite: השרת מתרגם אותו בשקט, אבל מול המאגר ישירות הוא נכשל (`function date(unknown, unknown) does not exist`), ולכן כותבים את הצורה המפורשת שעובדת בכל מסלול. השוואה של עמודת טקסט ל-`CURRENT_DATE` נכשלת בכל מסלול (`operator does not exist: text >= date`).
- **טריות:** לפני מסקנה של "אין במאגר" בודקים שהמקור רץ: `SELECT source, max(started_at) FROM scrape_runs WHERE status IN ('ok','warn') AND source = '<מקור>' GROUP BY 1`. מקור שלא רץ הוא "לא נאסף", לא "אין". המקור של `mavat_plans` הוא `source = 'mavat'`.
- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.

נקודות הכניסה המאונדקסות כאן: `district_name`, `plan_county_name`, `station_desc`, `osint_date(depositing_date)`.

```
describe_table("mavat_plans")
```
עמודות מפתח: `pl_number, pl_name, station_desc, district_name, plan_county_name, plan_area_name, ja_concat, pl_area_dunam, pl_landuse_string, pl_objectives, depositing_date, pl_rejection_date, pl_url, quantity_delta_120/60/75/80, mp_id, lat, lng, geom_geojson, first_seen_at`.

ערכי `district_name` (נמדד 20.11.2026): `צפון`, `מרכז`, `דרום`, `ירושלים`, `חיפה`, `תל-אביב` (**עם מקף**), ו-`מטה`.

**ליזם, לחברה או לרשות** - קודם `search_entity("<שם>")`, שמחזיר גם שורות תכנון (מבא"ת ויו"ש) של השם, ואחריו `entity_profile` על המזהה שחזר. השאילתות למטה הן לסריקה לפי מקום, זמן והיקף.

## שלב 2 - הרצת דפוסי הלידים (SQL מול העמודות האמיתיות)

הרץ את הדפוסים עם `query_db`. לעדכניות לפי כניסה למאגר אפשר גם `new_since("mavat_plans", since)` (לפי `first_seen_at`), אבל `query_db` נותן סינון לפי מחוז, שטח, יח"ד ותוכן מטרות.

**לפי מקום (מחוז / רשות):**
```sql
SELECT pl_number, pl_name, plan_county_name, station_desc, pl_area_dunam,
       quantity_delta_120, depositing_date, pl_url
FROM mavat_plans
WHERE district_name = 'מרכז' OR plan_county_name LIKE '%רחובות%'
ORDER BY osint_date(depositing_date) DESC NULLS LAST
LIMIT 50
```

**עבר שלב לאחרונה** - הדפוס החשוב לעדכניות. מעברי שלב נרשמים ב-`mavat_status_history` (743 מעברים מאז 21.8.2026, נמדד 20.11.2026). **לא** `last_seen_at`: הוא מתעדכן בכל סריקה ולכן אינו אומר שתוכנית זזה.
```sql
SELECT h.pl_number, p.pl_name, p.district_name, p.plan_county_name,
       h.old_status, h.new_status, h.changed_at, p.pl_url
FROM mavat_status_history h
JOIN mavat_plans p USING (pl_number)
WHERE h.changed_at >= to_char(CURRENT_DATE - 30,'YYYY-MM-DD')
ORDER BY h.changed_at DESC
LIMIT 50
```
`changed_at` הוא טקסט ISO, ולכן ההשוואה מול `to_char(...)` עובדת. גל של מעברים ביום אחד (כמה הפקדות או דחיות) הוא ליד בפני עצמו.

**הופקד לאחרונה:**
```sql
SELECT pl_number, pl_name, district_name, plan_county_name, pl_area_dunam,
       quantity_delta_120, depositing_date, pl_url
FROM mavat_plans
WHERE osint_date(depositing_date) >= to_char(CURRENT_DATE - 90,'YYYY-MM-DD')
ORDER BY osint_date(depositing_date) DESC
LIMIT 50
```
`depositing_date` כאן הוא ISO (`2026-10-19`) או מחרוזת ריקה, ו-`osint_date` מחזיר NULL לריקה. **ב-23,228 מתוך 37,576 התוכניות (62%) העמודה ריקה** (נמדד 20.11.2026), ובחלון של 90 יום יש רק עשרות תוכניות, ולכן להפקדות טריות השתמש גם בדפוס מעברי השלב למעלה. השוואה ישירה `depositing_date >= CURRENT_DATE - 90` נכשלת (`text >= date`). ב-`yosh_plans` הפורמט הוא `DD/MM/YYYY`, ו-`osint_date` מטפל בשניהם.

חלופה לפי כניסה למאגר: `new_since("mavat_plans", "<תאריך ISO>")`.

**תוכניות גדולות בשטח** - צמצם למחוז או לרשות. בלי צמצום, ראש הרשימה הוא ערכים שגויים מכל הארץ ולא תוכניות גדולות:
```sql
SELECT pl_number, pl_name, plan_county_name, pl_area_dunam,
       pl_landuse_string, pl_objectives, pl_url
FROM mavat_plans
WHERE district_name = 'מרכז'          -- צמצום על עמודה מאונדקסת
  AND pl_area_dunam IS NOT NULL
ORDER BY pl_area_dunam DESC NULLS LAST
LIMIT 30
```
עבור מחוז-מחוז (`מרכז`, `תל-אביב`, `חיפה`, `ירושלים`, `צפון`, `דרום`) וחבר.

> **בדיקת סבירות ל-`pl_area_dunam`.** הערכים בעמודה אינם אמינים כיחידות דונם. נכון ל-20.11.2026 התוכנית הגדולה במחוז מרכז רשומה כ-130,030,417 "דונם" (409-1511195, תוכנית נושאית מרחבית לעמק חפר), והשנייה כ-56,611,000 (413-1493923, הוראות לבניית מרתפים) - כל אחת יותר משטח המדינה כולה. **אל תדווח שטח מהעמודה הזאת בלי לאמת ב-`pl_url`.** השתמש בה למיון גס בלבד, והצלב עם `pl_objectives` כדי לראות במה התוכנית עוסקת בפועל.

**הרבה יחידות דיור מתוכננות:**
```sql
SELECT pl_number, pl_name, district_name, plan_county_name,
       quantity_delta_120, quantity_delta_80, pl_area_dunam,
       ROUND(CAST(quantity_delta_120 AS numeric) / NULLIF(CAST(pl_area_dunam AS numeric), 0), 1) AS units_per_dunam,
       depositing_date, pl_url
FROM mavat_plans
WHERE quantity_delta_120 IS NOT NULL
ORDER BY quantity_delta_120 DESC NULLS LAST
LIMIT 30
```
**המספר הזה הוא של מבא"ת, ומבא"ת טועה בו לפעמים** - למשל רושם שטח רצפה (מ"ר) תחת קוד יחידות הדיור 120. לכן הדירוג מציג גם `units_per_dunam`: מעל 50 יח"ד לדונם זה כמעט תמיד נתון שגוי. נכון ל-20.11.2026 יש 267 תוכניות כאלה, ובראש הרשימה תמל/ 3009 (מתחם חרודי, נס ציונה) עם 231,100 "יח"ד" על 263 דונם. **אסור לצטט מספר יחידות דיור בלי לפתוח את מסמך התוכנית** (`pl_url`).

**לפי תוכן מטרות/ייעוד** (עם צמצום למחוז, לפי חוק הזהב):
```sql
SELECT pl_number, pl_name, district_name, pl_objectives, pl_landuse_string,
       pl_area_dunam, depositing_date, pl_url
FROM mavat_plans
WHERE district_name = 'דרום'
  AND (pl_objectives LIKE '%מלונאות%' OR pl_landuse_string LIKE '%מלונאות%')
ORDER BY osint_date(depositing_date) DESC NULLS LAST
LIMIT 30
```

**גיאו - תוכניות עם קואורדינטות למיפוי באזור:**
```sql
SELECT pl_number, pl_name, lat, lng, pl_area_dunam, quantity_delta_120, pl_url
FROM mavat_plans
WHERE lat IS NOT NULL AND lng IS NOT NULL
  AND district_name = 'חיפה'
LIMIT 500
```
ה-`lat/lng` (ו-`geom_geojson`) מאפשרים מיפוי הלידים על מפה.

## שלב 3 - סינון רעש ודירוג

הורד עדיפות כשהשטח הגדול הוא יער/חקלאות/תשתית בלי דיור, כשהתוכנית כבר נדחתה (`pl_rejection_date`), או כש-`units_per_dunam` חשוד. העלה עדיפות כש: ריכוז יח"ד גבוה באזור רגיש, תוכנית גדולה שהופקדה או עברה שלב זה עתה, ייעוד שנוי במחלוקת, או תוכנית סמוכה לשטח פתוח/רגיש. דרג: גבוהה / בינונית / נמוכה.

## שלב 4 - העשרה ואימות מול pl_url

לכל ליד גבוה/בינוני פתח את `pl_url` (מנהל התכנון; אם חסום - Claude in Chrome) ואמת: השלב המדויק בהליך, מספר יח"ד ושטח, ייעוד, מגיש התוכנית, והאם הופקד/אושר/נדחה. רק אז הליד הופך לבסיס לסיפור.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה רחבה נקטעת או חורגת מהזמן | הוסף WHERE על district/county, ORDER BY ממוקד, limit קטן |
| `operator does not exist: text >= date` | השווית עמודת טקסט לתאריך. `osint_date(col) >= to_char(CURRENT_DATE - N,'YYYY-MM-DD')` |
| `function date(unknown, unknown) does not exist` | `date('now','-N days')` הוא SQLite, ומחוץ לשרת אין לו תרגום. השתמש ב-`to_char(CURRENT_DATE - N,'YYYY-MM-DD')` |
| depositing_date ריק | צפוי ב-62% מהתוכניות. לעדכניות - `mavat_status_history` או first_seen_at; ציין שתאריך ההפקדה חסר |
| quantity_delta ריק/שונה בין חתכים | התייחס כאומדן; השתמש בחתך הזמין; ציין שזו הערכה מתוכננת |
| `תל אביב` לא תפס במחוז | הערך הוא `תל-אביב`, עם מקף |
| שם רשות לא תפס | נסה plan_area_name / ja_concat / כתיב אחר, או `search_entity` |
| אין תוכניות חדשות | בדוק ב-`scrape_runs` (`source = 'mavat'`) שהמקור רץ, לפני "אין" |
| pl_url לא נפתח | נסה Claude in Chrome; אם חסום - סמן "לא אומת מול מקור" |

**אסור:** לכתוב "ייבנו X דירות" על סמך רשומת מאגר בלבד. בלי אימות שלב ההליך ב-pl_url - זה ליד, לא עובדה.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): מיפוי הטבלה, הרצת דפוסי הלידים, סינון ודירוג, אימות מול pl_url (ומיפוי lat/lng אם רלוונטי).

## דוח הדסק - מבנה קבוע

```markdown
# לידים - תכנון ובנייה (כל ישראל)

## טווח הסריקה
[מחוז/רשות/מילת-מטרה/חלון זמן, ומספר התוכניות]

## לידים מדורגים
לכל ליד:
- **התוכנית:** [pl_number + שם + מיקום]
- **המהות:** [שטח (דונם), יח"ד מתוכננות, ייעוד]
- **שלב ההליך:** [הופקד / נדחה / עבר שלב / אחר - לפי station_desc, depositing_date, pl_rejection_date, mavat_status_history]
- **למה זה ליד:** [גודל / ריכוז דיור / ייעוד / מיקום רגיש]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [pl_url + השאילתה; קואורדינטות אם רלוונטי]

## מה לאמת לפני פרסום
[לכל ליד גבוה: שלב מדויק, יח"ד ושטח, ייעוד, מגיש התוכנית]

**שורה תחתונה לדסק:** [התוכנית אחת שהכי בשלה לסיפור, ולמה]

Sources: [שאילתות osint-db + קישורי pl_url שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הדוח צריך לאפשר לעורך לבחור תוך דקה איזו תוכנית שווה תחקיר - עם השלב המדויק בהליך, בלי להציג "מתוכנן" כ"ייבנה".
