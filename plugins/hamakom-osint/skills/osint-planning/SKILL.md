---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__list_tables mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__new_since
name: osint-planning
description: לידים מתכנון ובנייה (מנהל התכנון / מבא"ת) בכל ישראל, מעל ה-osint-db (טבלת mavat_plans, 36 אלף תוכניות) עבור דסק "המקום הכי חם בגיהנום". מסנן לפי מחוז (district_name) ורשות/מרחב (plan_county_name), לפי תוכן מטרות (pl_objectives, pl_landuse_string), תוכניות שהופקדו לאחרונה (depositing_date / first_seen_at), תוכניות גדולות בשטח (pl_area_dunam), ומספר יחידות דיור מתוכננות (quantity_delta_120/60/75/80). יש lat/lng למיפוי. הפעל כשדור כותב "תוכניות בנייה ב<מקום>", "מה הופקד לאחרונה", "תוכניות גדולות", "כמה יח\"ד מתוכננות ב", "מה מתוכנן ב<עיר>", "תוכניות דיור באזור". זהו תכנון בתוך הקו הירוק - לתכנון ביו"ש/התנחלויות ראה osint-yosh-planning. כל תוכנית היא ליד לבדיקה מול pl_url הרשמי - לא ממצא מאומת. לתיק על יזם/חברה ראה osint-entity-dossier.
---

# osint-planning - לידים מתכנון ובנייה (כל ישראל)

סקיל לזיהוי לידים תחקיריים בטבלת `mavat_plans` שב-osint-db (תוכניות תכנון ובנייה בכל ישראל, בתוך הקו הירוק). התוצר הוא **לידים לבדיקה** - תוכנית שעלתה בסריקה היא נקודת פתיחה, ואימותה מול `pl_url` הרשמי קודם לכל פרסום.

> **תיחום:** סקיל זה לתכנון בתוך הקו הירוק בלבד. לתוכניות ביהודה ושומרון/התנחלויות - `osint-yosh-planning` (טבלת yosh_plans), שהוא רגיש עריכתית ויש לו הנחיות הקשר נפרדות.

## עקרונות יסוד

1. **המאגר מחזיר רשומות גולמיות.** כל שורה ב-`mavat_plans` היא רישום תכנוני, לא סיפור. תוכנית גדולה או הפקדה חדשה היא ליד; אימות מול `pl_url` (מנהל התכנון) הופך אותה לבסיס לכתבה.
2. **"הופקד" ≠ "אושר" ≠ "נבנה".** `depositing_date` הוא שלב בהליך. `pl_rejection_date` מציין דחייה. אל תכתוב "ייבנו X יח"ד" כשהתוכנית רק הופקדה - תאר את השלב המדויק.
3. **יחידות דיור הן הערכת דלתא.** `quantity_delta_120/60/75/80` הן יח"ד מתוכננות לפי חתכים; הן אומדן תכנוני, לא דירות שנמסרו. ציין שזה מתוכנן.
4. **גודל שטח הוא ליד גס.** `pl_area_dunam` גדול מצדיק מבט, אבל שטח אינו דרמה כשלעצמו (יער, חקלאות). הצלב עם `pl_landuse_string` ו-`pl_objectives`.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ליד תן עדיפות + מה הראיה החסרה (שלב ההליך, ייעוד, יזם).

## שלב 1 - מיפוי הטבלה

**קרא קודם `references/db-map.md`** - העמודות המאונדקסות וחוק הזהב של השאילתות. נקודות הכניסה כאן: `district_name`, `plan_county_name`, `station_desc`, `depositing_date`.

```
describe_table("mavat_plans")
```
עמודות מפתח: `pl_number, pl_name, station_desc, district_name, plan_county_name, plan_area_name, ja_concat, pl_area_dunam, pl_landuse_string, pl_objectives, depositing_date, pl_rejection_date, pl_url, quantity_delta_120/60/75/80, mp_id, lat, lng, geom_geojson, first_seen_at`.

## שלב 2 - הרצת דפוסי הלידים (SQL מול העמודות האמיתיות)

הרץ את הדפוסים עם `query_db`. לעדכניות לפי כניסה למאגר אפשר גם `new_since("mavat_plans", since)`, אבל `query_db` נותן סינון לפי מחוז, שטח, יח"ד ותוכן מטרות.

**לפי מקום (מחוז / רשות):**
```sql
SELECT pl_number, pl_name, plan_county_name, station_desc, pl_area_dunam,
       quantity_delta_120, depositing_date, pl_url
FROM mavat_plans
WHERE district_name LIKE '%מחוז%' OR plan_county_name LIKE '%שם הרשות%'
ORDER BY depositing_date DESC
```

**הופקד לאחרונה:**
```sql
SELECT pl_number, pl_name, district_name, plan_county_name, pl_area_dunam,
       quantity_delta_120, depositing_date, pl_url
FROM mavat_plans
WHERE depositing_date >= date('now','-90 days')
ORDER BY depositing_date DESC
LIMIT 50
```
כאן `depositing_date` הוא ISO (`2026-07-08`) וההשוואה עובדת ישירות. **שים לב:** ב-`yosh_plans` הפורמט שונה (`DD/MM/YYYY`) ומחייב המרה - ראה `osint-yosh-planning`. השתמש בתאריכים יחסיים ולא בתאריך קשיח.

חלופה לפי כניסה למאגר: `new_since("mavat_plans", "<תאריך ISO>")`.

**תוכניות גדולות בשטח** - חובה לצמצם למחוז או לרשות. `pl_area_dunam` **אינה מאונדקסת**, ומיון עליה על כל 36,796 השורות נקטע (אומת):
```sql
SELECT pl_number, pl_name, plan_county_name, pl_area_dunam,
       pl_landuse_string, pl_objectives, pl_url
FROM mavat_plans
WHERE district_name = 'מרכז'          -- חובה: צמצום על עמודה מאונדקסת
  AND pl_area_dunam IS NOT NULL
ORDER BY pl_area_dunam DESC
LIMIT 30
```
עבור מחוז-מחוז (`מרכז`, `תל אביב`, `חיפה`, `ירושלים`, `צפון`, `דרום`) וחבר.

> **בדיקת סבירות ל-`pl_area_dunam`.** הערכים בעמודה אינם אמינים כיחידות דונם: התוכנית הגדולה במחוז מרכז רשומה כ-56,611,000 "דונם" - יותר משטח המדינה כולה, בתוכנית שכל עניינה הוראות לבניית מרתפים בראשון לציון. **אל תדווח שטח מהעמודה הזאת בלי לאמת ב-`pl_url`.** השתמש בה למיון גס בלבד, והצלב עם `pl_objectives` כדי לראות במה התוכנית עוסקת בפועל.

**הרבה יחידות דיור מתוכננות:**
```sql
SELECT pl_number, pl_name, district_name, plan_county_name,
       quantity_delta_120, quantity_delta_80, depositing_date, pl_url
FROM mavat_plans
WHERE quantity_delta_120 IS NOT NULL
ORDER BY quantity_delta_120 DESC
LIMIT 30
```

**לפי תוכן מטרות/ייעוד:**
```sql
SELECT pl_number, pl_name, district_name, pl_objectives, pl_landuse_string,
       pl_area_dunam, depositing_date, pl_url
FROM mavat_plans
WHERE pl_objectives LIKE '%מילת מפתח%' OR pl_landuse_string LIKE '%ייעוד%'
ORDER BY depositing_date DESC
```

**גיאו - תוכניות עם קואורדינטות למיפוי באזור:**
```sql
SELECT pl_number, pl_name, lat, lng, pl_area_dunam, quantity_delta_120, pl_url
FROM mavat_plans
WHERE lat IS NOT NULL AND lng IS NOT NULL
  AND district_name LIKE '%מחוז%'
```
ה-`lat/lng` (ו-`geom_geojson`) מאפשרים מיפוי הלידים על מפה.

## שלב 3 - סינון רעש ודירוג

הורד עדיפות כשהשטח הגדול הוא יער/חקלאות/תשתית בלי דיור, או כשהתוכנית כבר נדחתה (`pl_rejection_date`). העלה עדיפות כש: ריכוז יח"ד גבוה באזור רגיש, תוכנית גדולה שהופקדה זה עתה, ייעוד שנוי במחלוקת, או תוכנית סמוכה לשטח פתוח/רגיש. דרג: גבוהה / בינונית / נמוכה.

## שלב 4 - העשרה ואימות מול pl_url

לכל ליד גבוה/בינוני פתח את `pl_url` (מנהל התכנון; אם חסום - Claude in Chrome) ואמת: השלב המדויק בהליך, מספר יח"ד ושטח, ייעוד, מגיש התוכנית, והאם הופקד/אושר/נדחה. רק אז הליד הופך לבסיס לסיפור.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה רחבה נקטעת | הוסף WHERE על district/county, ORDER BY ממוקד, limit קטן |
| depositing_date ריק | השתמש ב-first_seen_at לעדכניות; ציין שתאריך ההפקדה חסר |
| quantity_delta ריק/שונה בין חתכים | התייחס כאומדן; השתמש בחתך הזמין; ציין שזו הערכה מתוכננת |
| שם רשות לא תפס | נסה plan_area_name / ja_concat / כתיב אחר |
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
- **שלב ההליך:** [הופקד / נדחה / אחר - לפי depositing_date / pl_rejection_date]
- **למה זה ליד:** [גודל / ריכוז דיור / ייעוד / מיקום רגיש]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [pl_url + השאילתה; קואורדינטות אם רלוונטי]

## מה לאמת לפני פרסום
[לכל ליד גבוה: שלב מדויק, יח"ד ושטח, ייעוד, מגיש התוכנית]

**שורה תחתונה לדסק:** [התוכנית אחת שהכי בשלה לסיפור, ולמה]

Sources: [שאילתות osint-db + קישורי pl_url שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הדוח צריך לאפשר לעורך לבחור תוך דקה איזו תוכנית שווה תחקיר - עם השלב המדויק בהליך, בלי להציג "מתוכנן" כ"ייבנה".
