---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__list_tables mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__new_since
name: osint-yosh-planning
description: לידים מתכנון ובנייה ביהודה ושומרון (יו"ש) מעל ה-osint-db (טבלת yosh_plans, 2,570 תוכניות) עבור דסק "המקום הכי חם בגיהנום". מסנן לפי מרחב/התנחלות (plan_county_name, ja_concat), מחוז (district_name) ומגזר (sector), תוכניות שהופקדו לאחרונה (depositing_date / first_seen_at), תוכניות גדולות בשטח (pl_area_dunam), ויחידות דיור מתוכננות (quantity_delta_120). יש lat/lng למיפוי. הפעל כשדור כותב "תוכניות בנייה ביו\"ש", "בנייה בהתנחלויות", "מה הופקד ביו\"ש", "תוכניות ב<התנחלות>", "כמה יח\"ד אושרו בשטחים", "תכנון מעבר לקו הירוק". נושא רגיש עריכתית - דווח עובדתית מהרשומה הרשמית, ייחס לרשות המתכננת, הימנע ממסגור טעון, ואמת מול pl_url. כל תוכנית היא ליד לבדיקה, לא ממצא מאומת. לתכנון בתוך הקו הירוק ראה osint-planning; לתיק על יזם ראה osint-entity-dossier.
---

# osint-yosh-planning - לידים מתכנון ובנייה ביו"ש

סקיל לזיהוי לידים תחקיריים בטבלת `yosh_plans` שב-osint-db (תכנון ובנייה ביהודה ושומרון). המנגנון זהה ל-`osint-planning`, אך **הנושא רגיש עריכתית** ויש לו הנחיות הקשר נפרדות (ראה למטה). התוצר הוא **לידים לבדיקה** - אימות מול `pl_url` הרשמי קודם לכל פרסום.

## עקרונות יסוד

1. **המאגר מחזיר רשומות גולמיות.** כל שורה ב-`yosh_plans` היא רישום תכנוני של הרשות המתכננת, לא סיפור מאומת. תוכנית בולטת היא ליד; אימות מול `pl_url` הופך אותה לבסיס לכתבה.
2. **"הופקד" ≠ "אושר" ≠ "נבנה".** `depositing_date` הוא שלב בהליך. אל תכתוב "נבנו X יח"ד" כשהתוכנית רק הופקדה - תאר את השלב המדויק.
3. **יחידות דיור הן אומדן מתוכנן.** `quantity_delta_120` היא הערכת יח"ד, לא דירות שנמסרו. ציין שזה מתוכנן.
4. **דווח עובדתית, ייחס לרשות.** רשום מה נמצא ברשומה ומי הרשות המתכננת. הימנע ממונחים טעונים; תן לעובדה לדבר ולעורך להחליט על המסגור.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ליד תן עדיפות + מה הראיה החסרה (שלב, מגזר, יזם).

## הקשר ואתיקה (קרא לפני שמתחילים)

בנייה ביו"ש היא נושא פוליטי טעון. כדי לשמור על אמינות הדסק:

- **דווח מהרשומה הרשמית בלבד.** הצמד לעובדות שב-`yosh_plans` ול-`pl_url`: מספר תוכנית, שלב, שטח, יח"ד, מיקום, רשות מתכננת. אל תוסיף פרשנות פוליטית לדוח הלידים.
- **ייחס תמיד לרשות המתכננת** (מנהל אזרחי / הרשות הרלוונטית). אל תציג נתון תכנוני כמדיניות מוצהרת בלי מקור.
- **הימנע ממסגור טעון.** השתמש בשמות המקומות והמונחים כפי שהם ברשומה הרשמית; אל תכניס מילות עמדה לליד. בחירת המסגור היא החלטה עריכתית, לא חלק מהשליפה.
- **אמת מול pl_url לפני פרסום.** ברשומה רגישה, התאמה במאגר אינה מספיקה - חובה לראות את המקור הרשמי.
- **שמור איזון.** הצג את העובדות (מה, איפה, כמה, איזה שלב) בלי להכריע את משמעותן; השאר את ההקשר לכתבה ולעורך.

## שלב 1 - מיפוי הטבלה

```
describe_table("yosh_plans")
```
עמודות מפתח: `pl_number, pl_name, station_desc, district_name, plan_county_name, ja_concat, pl_area_dunam, depositing_date, pl_url, mp_id, lat, lng, quantity_delta_120, first_seen_at, sector`.

> **מלכודת מחייבת: `depositing_date` כאן הוא `DD/MM/YYYY`, לא ISO.** בניגוד ל-`mavat_plans` (שם הוא ISO). לכן `WHERE depositing_date >= '2026-05-01'` ו-`ORDER BY depositing_date DESC` **מחזירים זבל** - ההשוואה לקסיקוגרפית והיום קודם לשנה. אומת: שאילתה על "90 הימים האחרונים" החזירה תוכניות מ-2014.
>
> חובה להמיר בכל שאילתה שנוגעת בתאריך:
> ```sql
> substr(depositing_date,7,4)||'-'||substr(depositing_date,4,2)||'-'||substr(depositing_date,1,2) AS dep_iso
> ```
> ואז למיין ולסנן על `dep_iso`. ראה `references/db-map.md`.

## שלב 2 - הרצת דפוסי הלידים (SQL מול העמודות האמיתיות)

הרץ את הדפוסים עם `query_db`. לעדכניות לפי כניסה למאגר אפשר גם `new_since("yosh_plans", since)`, אבל `query_db` נותן סינון לפי מרחב, מגזר, שטח ויח"ד.

**לפי מרחב / התנחלות / מגזר:**
```sql
SELECT pl_number, pl_name, plan_county_name, sector, pl_area_dunam, quantity_delta_120,
       substr(depositing_date,7,4)||'-'||substr(depositing_date,4,2)||'-'||substr(depositing_date,1,2) AS dep_iso,
       pl_url
FROM yosh_plans
WHERE plan_county_name LIKE '%שם המקום%' OR ja_concat LIKE '%שם%' OR sector LIKE '%מגזר%'
ORDER BY dep_iso DESC
```

**הופקד לאחרונה** (עם ההמרה - בלעדיה השאילתה מחזירה תוכניות מלפני עשר שנים):
```sql
SELECT pl_number, pl_name, district_name, plan_county_name, sector,
       pl_area_dunam, quantity_delta_120,
       substr(depositing_date,7,4)||'-'||substr(depositing_date,4,2)||'-'||substr(depositing_date,1,2) AS dep_iso,
       pl_url
FROM yosh_plans
WHERE depositing_date <> ''
  AND substr(depositing_date,7,4)||'-'||substr(depositing_date,4,2)||'-'||substr(depositing_date,1,2) >= date('now','-90 days')
ORDER BY dep_iso DESC
LIMIT 50
```
שים לב שיש תוכניות עם תאריך הפקדה **עתידי** (מועד הפקדה שנקבע) - הן יעלו ראשונות וזה תקין; תאר אותן כמועד מתוכנן ולא כהפקדה שבוצעה.

חלופה לפי כניסה למאגר (ולא לפי תאריך ההפקדה): `new_since("yosh_plans", "<תאריך ISO>")`.

**תוכניות גדולות בשטח** (כאן אין תלות בתאריך ולכן אין צורך בהמרה):
```sql
SELECT pl_number, pl_name, district_name, plan_county_name, sector,
       pl_area_dunam, depositing_date, pl_url
FROM yosh_plans
WHERE pl_area_dunam IS NOT NULL
ORDER BY pl_area_dunam DESC
LIMIT 30
```

**הרבה יחידות דיור מתוכננות:**
```sql
SELECT pl_number, pl_name, plan_county_name, sector,
       quantity_delta_120, depositing_date, pl_url
FROM yosh_plans
WHERE quantity_delta_120 IS NOT NULL
ORDER BY quantity_delta_120 DESC
LIMIT 30
```

**גיאו - תוכניות עם קואורדינטות למיפוי:**
```sql
SELECT pl_number, pl_name, lat, lng, pl_area_dunam, quantity_delta_120, sector, pl_url
FROM yosh_plans
WHERE lat IS NOT NULL AND lng IS NOT NULL
```
ה-`lat/lng` מאפשרים מיפוי הלידים.

## שלב 3 - סינון רעש ודירוג

הורד עדיפות לתוכנית תשתית/שטח פתוח בלי דיור. העלה עדיפות לריכוז יח"ד גבוה, תוכנית גדולה שהופקדה זה עתה, או מיקום בולט. דרג: גבוהה / בינונית / נמוכה - לפי היקף תכנוני, לא לפי עמדה.

## שלב 4 - העשרה ואימות מול pl_url

לכל ליד גבוה/בינוני פתח את `pl_url` (אם חסום - Claude in Chrome) ואמת: השלב בהליך, מספר יח"ד ושטח, הרשות המתכננת, והמיקום המדויק. ייחס כל נתון לרשות. רק אז הליד הופך לבסיס לסיפור.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה רחבה נקטעת | הוסף WHERE על county/sector, ORDER BY ממוקד, limit קטן |
| depositing_date ריק | השתמש ב-first_seen_at; ציין שתאריך ההפקדה חסר |
| התוכניות "האחרונות" יוצאות מלפני עשר שנים | לא המרת את התאריך. `depositing_date` הוא DD/MM/YYYY - ראה המלכודת בשלב 1 |
| quantity_delta_120 ריק | התייחס כאומדן; ציין שזו הערכה מתוכננת, לא דירות שנמסרו |
| שם מקום לא תפס | נסה ja_concat / plan_county_name / כתיב אחר |
| pl_url לא נפתח | נסה Claude in Chrome; אם חסום - סמן "לא אומת מול מקור", אל תפרסם |

**אסור:** לכתוב "נבנו/אושרו X יח"ד" על סמך רשומת מאגר בלבד, ולהוסיף מסגור פוליטי לליד. בלי אימות מול pl_url וייחוס לרשות - זה ליד עובדתי, לא סיפור.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): מיפוי הטבלה, הרצת דפוסי הלידים, סינון ודירוג, אימות מול pl_url וייחוס לרשות (ומיפוי lat/lng אם רלוונטי).

## דוח הדסק - מבנה קבוע

```markdown
# לידים - תכנון ובנייה ביו"ש

## טווח הסריקה
[מרחב/התנחלות/מגזר/חלון זמן, ומספר התוכניות]

## לידים מדורגים (עובדתי, מיוחס לרשות)
לכל ליד:
- **התוכנית:** [pl_number + שם + מיקום + מגזר]
- **המהות:** [שטח (דונם), יח"ד מתוכננות]
- **שלב ההליך:** [הופקד / אחר - לפי depositing_date]
- **למה זה ליד:** [היקף תכנוני - בלי מסגור עמדה]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [pl_url + השאילתה; קואורדינטות אם רלוונטי]

## מה לאמת לפני פרסום
[לכל ליד גבוה: שלב מדויק, יח"ד ושטח, הרשות המתכננת, מיקום]

**שורה תחתונה לדסק:** [התוכנית אחת שהכי בשלה לסיפור, ולמה - עובדתית]

Sources: [שאילתות osint-db + קישורי pl_url שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר, עובדתי ומיוחס לרשות. הדוח צריך לאפשר לעורך לבחור תוך דקה איזו תוכנית שווה תחקיר - עם השלב המדויק בהליך, בלי מסגור טעון ובלי להציג "מתוכנן" כ"נבנה".
