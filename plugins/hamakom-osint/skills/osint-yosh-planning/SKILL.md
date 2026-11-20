---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__new_since mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-yosh-planning
version: '1.4.0'
description: לידים מתכנון ובנייה ביהודה ושומרון (יו"ש) מעל ה-osint-db (טבלת yosh_plans) עבור דסק "המקום הכי חם בגיהנום". מסנן לפי מרחב/התנחלות (plan_county_name, ja_concat), מחוז (district_name) ומגזר (sector), תוכניות שהופקדו לאחרונה או שעברו שלב (depositing_date, yosh_status_history), תוכניות גדולות בשטח (pl_area_dunam), ויחידות דיור מתוכננות (quantity_delta_120). יש lat/lng למיפוי. הפעל כשדור כותב "תוכניות בנייה ביו\"ש", "בנייה בהתנחלויות", "מה הופקד ביו\"ש", "תוכניות ב<התנחלות>", "כמה יח\"ד אושרו בשטחים", "תכנון מעבר לקו הירוק". נושא רגיש עריכתית - דווח עובדתית מהרשומה הרשמית, ייחס לרשות המתכננת, הימנע ממסגור טעון, ואמת מול pl_url. כל תוכנית היא ליד לבדיקה, לא ממצא מאומת. לתכנון בתוך הקו הירוק ראה osint-planning; לתיק על יזם ראה osint-entity-dossier.
---

# osint-yosh-planning - לידים מתכנון ובנייה ביו"ש

סקיל לזיהוי לידים תחקיריים בטבלת `yosh_plans` שב-osint-db (תכנון ובנייה ביהודה ושומרון, 2,632 תוכניות, נמדד 20.11.2026). המנגנון זהה ל-`osint-planning`, אך **הנושא רגיש עריכתית** ויש לו הנחיות הקשר נפרדות (ראה למטה). התוצר הוא **לידים לבדיקה** - אימות מול `pl_url` הרשמי קודם לכל פרסום.

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

**חוקי המאגר.** המפה המלאה היא `references/db-map.md` בשורש התוסף (`../../references/db-map.md` מתיקיית הסקיל). יש סביבות שטוענות רק את SKILL.md, ולכן העיקר כאן:
- **כלי קודם.** לשם (אדם, חברה, רשות, מקום, תוכנית) - `search_entity(name)`, אחריו `entity_profile(<המזהה שחזר>)`, ו-`query_db` רק למה שהכלים לא מחזירים.
- את העמודות נותן `describe_table("<טבלה>")`, ואת רשימת הטבלאות `describe_table()` בלי שם. לא מנחשים שם עמודה.
- **חוק הזהב:** אין אגרגציה ואין `LIKE` על טבלה גדולה בלי `WHERE` על עמודה מאונדקסת. שאילתה שנקטעה או שחרגה מהזמן (10 שניות) אינה "אין תוצאות".
- **תאריכים.** רוב עמודות התאריך במאגר הן טקסט. `osint_date(col)` מחזיר מהן ISO (`YYYY-MM-DD`) בכל הפורמטים שבמאגר (ISO, `DD/MM/YYYY`, גם עם שעה), ומשווים מול `to_char(CURRENT_DATE - 90,'YYYY-MM-DD')`. `date('now', ...)` הוא SQLite: השרת מתרגם אותו בשקט, אבל מול המאגר ישירות הוא נכשל (`function date(unknown, unknown) does not exist`), ולכן כותבים את הצורה המפורשת שעובדת בכל מסלול. השוואה של עמודת טקסט ל-`CURRENT_DATE` נכשלת בכל מסלול (`operator does not exist: text >= date`).
- **טריות:** לפני מסקנה של "אין במאגר" בודקים שהמקור רץ: `SELECT source, max(started_at) FROM scrape_runs WHERE status IN ('ok','warn') AND source = '<מקור>' GROUP BY 1`. מקור שלא רץ הוא "לא נאסף", לא "אין". המקור של `yosh_plans` הוא `source = 'yosh'`.
- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.

```
describe_table("yosh_plans")
```
עמודות מפתח: `pl_number, pl_name, station_desc, district_name, plan_county_name, ja_concat, pl_area_dunam, depositing_date, pl_url, mp_id, lat, lng, quantity_delta_120, first_seen_at, last_seen_at, sector, land_use_category`.

**ליזם, לחברה או ליישוב** - קודם `search_entity("<שם>")`, שמחזיר גם שורות תכנון מיו"ש, ואחריו `entity_profile` על המזהה שחזר. השאילתות למטה הן לסריקה לפי מקום, זמן והיקף.

> **מלכודת מחייבת: `depositing_date` כאן הוא `DD/MM/YYYY`, לא ISO** (2,626 מתוך 2,632 התוכניות; 6 ריקות, נמדד 20.11.2026). בניגוד ל-`mavat_plans` (שם הוא ISO). לכן `ORDER BY depositing_date DESC` **מחזיר זבל** - המיון לקסיקוגרפי והיום קודם לשנה - והשוואה ל-`CURRENT_DATE` נכשלת (`text >= date`).
>
> חובה לעבור דרך `osint_date` בכל שאילתה שנוגעת בתאריך. יש עליו אינדקס:
> ```sql
> osint_date(depositing_date) AS dep_iso
> ```
> ואז למיין ולסנן על `dep_iso` או על `osint_date(depositing_date)`.

> **`sector` הוא הסיווג שלנו, לא נתון של מבא"ת.** הוא היסק משם התוכנית והיישוב, וטעה במקרי קצה. הערכים (נמדד 20.11.2026): `jewish` (1,895), `palestinian` (413), `infrastructure_regional` (174), `unknown` (148), ושתי שורות NULL. מסננים בשוויון (`sector = 'palestinian'`), ולא כותבים "תוכנית ליהודים" או "לפלסטינים" על סמך העמודה הזו בלבד.

## שלב 2 - הרצת דפוסי הלידים (SQL מול העמודות האמיתיות)

הרץ את הדפוסים עם `query_db`. לעדכניות לפי כניסה למאגר אפשר גם `new_since("yosh_plans", since)` (לפי `first_seen_at`), אבל `query_db` נותן סינון לפי מרחב, מגזר, שטח ויח"ד.

**לפי מרחב / התנחלות / מגזר:**
```sql
SELECT pl_number, pl_name, plan_county_name, sector, station_desc,
       pl_area_dunam, quantity_delta_120,
       osint_date(depositing_date) AS dep_iso, pl_url
FROM yosh_plans
WHERE plan_county_name LIKE '%אריאל%' OR ja_concat LIKE '%אריאל%'
ORDER BY dep_iso DESC NULLS LAST
LIMIT 50
```
לסינון לפי מגזר: `WHERE sector = 'palestinian'` (או ערך אחר מהרשימה למעלה).

**עבר שלב לאחרונה** - הדפוס החשוב לעדכניות. מעברי שלב (אישור, הפקדה, דחייה) נרשמים ב-`yosh_status_history` (114 מעברים מאז 29.7.2026, נמדד 20.11.2026). **לא** `last_seen_at`: הוא מתעדכן בכל סריקה (ב-20.11.2026 עודכן בשבוע האחרון ב-2,627 מתוך 2,632 התוכניות), ולכן "מה זז לפי last_seen_at" מחזיר את כל הטבלה.
```sql
SELECT h.pl_number, p.pl_name, p.plan_county_name, p.sector,
       h.old_status, h.new_status, h.changed_at, p.pl_url
FROM yosh_status_history h
JOIN yosh_plans p USING (pl_number)
WHERE h.changed_at >= to_char(CURRENT_DATE - 30,'YYYY-MM-DD')
ORDER BY h.changed_at DESC
LIMIT 50
```
`changed_at` הוא טקסט ISO, ולכן ההשוואה מול `to_char(...)` עובדת. כמה דחיות או אישורים ביום אחד, מול הקצב הרגיל, הם ליד בפני עצמם.

**הופקד לאחרונה** (דרך `osint_date` - בלעדיו השאילתה נכשלת או מחזירה תוכניות מלפני עשר שנים):
```sql
SELECT pl_number, pl_name, district_name, plan_county_name, sector,
       pl_area_dunam, quantity_delta_120,
       osint_date(depositing_date) AS dep_iso, pl_url
FROM yosh_plans
WHERE osint_date(depositing_date) >= to_char(CURRENT_DATE - 90,'YYYY-MM-DD')
ORDER BY dep_iso DESC
LIMIT 50
```
אם יופיע תאריך הפקדה **עתידי** (מועד שנקבע), תאר אותו כמועד מתוכנן ולא כהפקדה שבוצעה. נכון ל-20.11.2026 אין כאלה.

חלופה לפי כניסה למאגר (ולא לפי תאריך ההפקדה): `new_since("yosh_plans", "<תאריך ISO>")`.

**תוכניות גדולות בשטח** (כאן אין תלות בתאריך):
```sql
SELECT pl_number, pl_name, district_name, plan_county_name, sector,
       pl_area_dunam, depositing_date, pl_url
FROM yosh_plans
WHERE pl_area_dunam IS NOT NULL
ORDER BY pl_area_dunam DESC NULLS LAST
LIMIT 30
```
**שטח הוא ליד גס.** `pl_area_dunam` גדול מצדיק מבט, אבל אינו דרמה כשלעצמו (חקלאות, שטח פתוח), והעמודה לא תמיד אמינה. מצליבים עם `land_use_category` ועם מטרות התוכנית ב-`pl_url` לפני שמסיקים משהו.

**הרבה יחידות דיור מתוכננות:**
```sql
SELECT y.pl_number, y.pl_name, y.plan_county_name, y.sector,
       y.quantity_delta_120, y.pl_area_dunam,
       ROUND(CAST(y.quantity_delta_120 AS numeric) / NULLIF(CAST(y.pl_area_dunam AS numeric), 0), 1) AS units_per_dunam,
       r.verify_status, y.depositing_date, y.pl_url
FROM yosh_plans y
LEFT JOIN yosh_plan_rights_latest r ON r.mp_id = y.mp_id
WHERE y.quantity_delta_120 IS NOT NULL
ORDER BY y.quantity_delta_120 DESC NULLS LAST
LIMIT 30
```
**המספר הזה הוא של מבא"ת, ומבא"ת טועה בו לפעמים** - למשל רושם שטח רצפה (מ"ר) תחת קוד יחידות הדיור 120. לכן הדירוג מציג גם `units_per_dunam`: מעל 50 יח"ד לדונם זה כמעט תמיד נתון שגוי (נכון ל-20.11.2026 אין ב-`yosh_plans` תוכנית כזו; ב-`mavat_plans` יש 267). **אסור לצטט מספר יחידות דיור בלי לפתוח את מסמך התוכנית** (`pl_url`).

**טבלת הזכויות מהוראות התוכנית** (`yosh_plan_rights_latest`) נקראה מהמסמך עצמו, ורק `verify_status = 'verified'` בה הוא עובדה. נכון ל-20.11.2026 זה 22 מתוך 2,623 הרשומות; השאר `pending_transcription` (1,782), `no_provisions` (621), `unverified` (170) או `conflict_*` (28). כל סטטוס אחר, וכל מספר מ-`yosh_plans`, הוא ליד.

**גיאו - תוכניות עם קואורדינטות למיפוי:**
```sql
SELECT pl_number, pl_name, lat, lng, pl_area_dunam, quantity_delta_120, sector, pl_url
FROM yosh_plans
WHERE lat IS NOT NULL AND lng IS NOT NULL
LIMIT 500
```
ה-`lat/lng` מאפשרים מיפוי הלידים.

## שלב 3 - סינון רעש ודירוג

הורד עדיפות לתוכנית תשתית/שטח פתוח בלי דיור. העלה עדיפות לריכוז יח"ד גבוה, תוכנית גדולה שהופקדה או עברה שלב זה עתה, או מיקום בולט. דרג: גבוהה / בינונית / נמוכה - לפי היקף תכנוני, לא לפי עמדה.

## שלב 4 - העשרה ואימות מול pl_url

לכל ליד גבוה/בינוני פתח את `pl_url` (אם חסום - Claude in Chrome) ואמת: השלב בהליך, מספר יח"ד ושטח, הרשות המתכננת, והמיקום המדויק. ייחס כל נתון לרשות. רק אז הליד הופך לבסיס לסיפור.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה רחבה נקטעת | הוסף WHERE על county/sector, ORDER BY ממוקד, limit קטן |
| `operator does not exist: text >= date` | השווית את `depositing_date` (טקסט) לתאריך. `osint_date(depositing_date) >= to_char(CURRENT_DATE - N,'YYYY-MM-DD')` |
| `function date(unknown, unknown) does not exist` | `date('now','-N days')` הוא SQLite, ומחוץ לשרת אין לו תרגום. השתמש ב-`to_char(CURRENT_DATE - N,'YYYY-MM-DD')` |
| התוכניות "האחרונות" יוצאות מלפני עשר שנים | מיינת על `depositing_date` הגולמי (DD/MM/YYYY). מיין על `osint_date(depositing_date)` |
| "מה זז השבוע" מחזיר את כל הטבלה | סיננת לפי `last_seen_at`. מעברי שלב - `yosh_status_history` |
| depositing_date ריק | 6 תוכניות. השתמש ב-first_seen_at; ציין שתאריך ההפקדה חסר |
| סינון `sector` בעברית מחזיר אפס | הערכים באנגלית: `jewish`, `palestinian`, `infrastructure_regional`, `unknown` |
| quantity_delta_120 ריק | התייחס כאומדן; ציין שזו הערכה מתוכננת, לא דירות שנמסרו |
| שם מקום לא תפס | נסה ja_concat / plan_county_name / כתיב אחר, או `search_entity` |
| אין תוכניות חדשות | בדוק ב-`scrape_runs` (`source = 'yosh'`) שהמקור רץ, לפני "אין" |
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
- **שלב ההליך:** [הופקד / עבר שלב / אחר - לפי station_desc, depositing_date, yosh_status_history]
- **למה זה ליד:** [היקף תכנוני - בלי מסגור עמדה]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [pl_url + השאילתה; קואורדינטות אם רלוונטי]

## מה לאמת לפני פרסום
[לכל ליד גבוה: שלב מדויק, יח"ד ושטח, הרשות המתכננת, מיקום]

**שורה תחתונה לדסק:** [התוכנית אחת שהכי בשלה לסיפור, ולמה - עובדתית]

Sources: [שאילתות osint-db + קישורי pl_url שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר, עובדתי ומיוחס לרשות. הדוח צריך לאפשר לעורך לבחור תוך דקה איזו תוכנית שווה תחקיר - עם השלב המדויק בהליך, בלי מסגור טעון ובלי להציג "מתוכנן" כ"נבנה".
