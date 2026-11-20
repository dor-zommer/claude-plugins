---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__legislation_history mcp__plugin_hamakom-osint_osint-db__search_exemption_documents mcp__plugin_hamakom-osint_osint-db__read_exemption_documents mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-entity-dossier
version: '1.4.0'
description: בניית תיק מאוחד על אדם, חברה או משרד ממשלתי חוצה כל ה-osint-db עבור דסק "המקום הכי חם בגיהנום". מצליב שם אחד על פני החלטות ממשלה (decisions), מבקר המדינה (mevaker_chapters), תכנון ובנייה (mavat_plans, yosh_plans), חקיקה (legislation, knesset_bills), התקשרויות, פטורים ותמיכות (budget_contracts, exemptions, budget_supports), רשם החברות (ica_companies, ica_changes), נושאי משרה בחברות ציבוריות (maya_officers) ותרומות לבחירות (mevaker_donations). הנתיב הראשי הוא search_entity(name) לבחירת הישות, ואחריו entity_profile(id) שמחזיר את כל מה שמודל הישויות מקשר אליה, כולל סכומים; query_db רק למה שהפרופיל לא מחזיר. הפעל כשדור כותב "תבנה תיק על X", "מה יש לנו על חברת Y", "תצליב את השם הזה", "dossier", "מה הקשר של X לממשלה", "איפה השם הזה מופיע במאגר", "תעשה לי תחקיר רקע על". התוצר הוא תיק לפי סדר העניין (פעולות המדינה קודם), עם קישורי מקור ורשימת "מה לאמת בהמשך". התאמת שם אינה אישור זהות - כל פריט הוא ליד לבדיקה. לסריקת פטורים ייעודית ראה osint-exemptions; לפרופיל ח"כ מעמיק ראה osint-knesset.
---

# osint-entity-dossier - תיק ישות חוצה-מאגר

סקיל לבניית תיק רקע על ישות (אדם / חברה / משרד) על פני כל osint-db בבת אחת. התוצר אינו "פרופיל מאומת" אלא **תיק לידים לבדיקה**, מסודר לפי מה שמעניין, שכל פריט בו מקושר למקור הרשמי שלו וטעון אימות לפני שהוא נכנס לכתבה.

**סדר הכלים: כלי קודם, SQL אחרון.** `search_entity` כדי לבחור את הישות, `entity_profile` כדי לקבל את כל מה שמקושר אליה, הכלים הייעודיים (`legislation_history`, `search_exemption_documents`) לחוק או למסמכי פטור, ו-`query_db` רק למה שאלה לא מחזירים.

**חוקי המאגר.** המפה המלאה היא `references/db-map.md` בשורש התוסף (`../../references/db-map.md` מתיקיית הסקיל). יש סביבות שטוענות רק את SKILL.md, ולכן העיקר כאן:
- את העמודות של טבלה נותן `describe_table(name)`. לא מנחשים שם עמודה.
- **חוק הזהב:** אין אגרגציה ואין `LIKE` על טבלה גדולה בלי `WHERE` על עמודה מאונדקסת. שאילתה שנקטעה אינה "אין תוצאות".
- **כסף בהתקשרויות:** `budget_contracts.volume` הוא במטבע של `currency`, ושורה `superseded` הוחלפה בדיווח מאוחר יותר. כל סכום הוא `SUM(volume * FX)` עם `superseded IS NOT TRUE`, לפי הנוסחה בתיאור של `query_db`. לעולם לא `SUM(volume)`.
- **פטורים:** בכל סכום או דירוג של `exemptions.amount_ils` מסננים `amount_kind IS NULL`. שורה עם `amount_kind` (הקצאות ותמורות של רמ"י) היא תמורה שהמדינה מקבלת, לא הוצאה.
- **שורה שירדה מהמקור** מסומנת ב-`gone_at` (כנסת) או ב-`removed_at` (רשם החברות, מאיה). מסננים `IS NULL`.
- **תאריכים טקסטואליים:** `yosh_plans.depositing_date` ו-`exemptions.update_date` הם DD/MM/YYYY; ממיינים ומשווים דרך `osint_date(col)` או העמודה ה-ISO (`exemptions.pub_date_iso`, `legislation.pub_date_iso`). `mavat_plans.depositing_date` הוא ISO (וריק ברוב השורות).
- **טריות - לפני כל "אין במאגר":** בודקים שהמקור רץ. שמות המקורות ב-`scrape_runs` אינם שמות הטבלאות:
- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.
  ```sql
  SELECT source, max(started_at) AS last_ok FROM scrape_runs
  WHERE status IN ('ok','warn')
    AND source IN ('exemptions','mavat','yosh','decisions','legislation','mevaker_library_collector',
                   'ica_scraper','maya_scraper','mevaker_donations_scraper','budget_contracts',
                   'budget_supports','amutot','knesset_bills')
  GROUP BY 1
  ```
  ריצה מוצלחת אינה בהכרח נתונים חדשים: בדוק גם `max(first_seen_at)` בטבלה עצמה. מקור שלא רץ הוא "לא נאסף", לא "אין".

## עקרונות יסוד

1. **התאמת שם אינה אישור זהות.** "ישראל ישראלי" ב-`exemptions` ו-"ישראל ישראלי" בכנסת אינם בהכרח אותו אדם. כל פגיעה היא ליד; הקישור בין שתי פגיעות הוא השערה לבדיקה - לא עובדה. אמת זהות מול מזהים (ח"פ / `supplier_ids`, PersonID של הכנסת) והמקור הרשמי לפני שאתה מחבר. גם המודל אומר זאת: "ייתכן שזו אותה ישות" אינו איחוד, ולא מאחדים בלי מזהה קשיח.
2. **המאגר מחזיר רשומות גולמיות.** כל שורה היא רישום ראשוני. הופך לסיפור רק אחרי פתיחת ה-URL הרשמי (`sourceUrl` בפרופיל, `detail_url` / `url` / `pl_url` / אתר הכנסת) ואימות.
3. **תיק אינו האשמה.** קשר במודל פירושו "קשור ל": שתי הישויות מופיעות יחד ברשומה רשמית. ריבוי הופעות אינו מעיד על עוולה. נסח את התיק כמפה של קשרים-לבדיקה, לא כתב אישום.
4. **הבחן ציבורי מפרטי.** חברה, משרד, ח"כ, בכיר ציבורי - לגיטימי לתחקר. אדם פרטי שצף בהתאמה אקראית - אל תבנה עליו תיק; ציין שזו התאמת שם בלבד.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל קשר בין-תחומי תן רמת ביטחון (גבוהה/בינונית/נמוכה) שזו אותה ישות, ומה יכריע.
6. **ישויות חבויות תחת כתיב אחר או שם-גג.** גוף מופיע לעיתים בכתיב חסר, בשם הרשום שלו או תחת ארגון-האם. דוגמה מדודה (20.11.2026): "החטיבה להתיישבות" יושבת במודל כאשכול אחד עם 3,420 קשרים, בכתיב "החטיבה להתישבות" ובשם הרשום "ההסתדרות הציונית/החטיבה להתישבות". חיפוש השם בכתיב המלא מוצא אותה רק דרך "כל חלקי השם", אחרי רסיסים קטנים (ראה שלב 1). כשנפתח דרך שם-גג רחב (למשל "ההסתדרות הציונית העולמית"), ייכללו גם זרועות אחרות של הארגון: סמן כל פריט אם הוא באמת הישות המבוקשת, ותן ביטחון לכל ייחוס.
7. **מה שמעניין קודם.** בתיק, פעולות של המדינה כלפי הישות או בידיה (החלטות ממשלה, דוחות מבקר, תוכניות, חקיקה, תמיכות והתקשרויות מהותיות) באות לפני רכש שגרתי, הודעות דוברים וכותרות. מאות פטורים קטנים או אזכורים בהודעות לעיתונות הם שורה מסכמת, לא פרק.

## שלב 1 - בחירת הישות: search_entity

```
search_entity("שם הישות")
```
התשובה היא טקסט, בסדר הזה:
1. **כרטיסי ישות** (עד 3) מהמודל האחיד: שם, `id`, סוג, שורת סיכום (מקורות, מספר קשרים, כסף לפי תפקיד ומטבע, שנים), צדדים שניים מובילים וקישור לאתר. כשאין לשם ישות במודל, במקומם בא **כרטיס זמני מתוך אזכורים** (הכותרות שמזכירות את השם והישויות שסביבן).
2. **מועמדים נוספים במודל** - שורות JSON (`"table": "ftm_names"`) עם `id`, `incoming_links` והפניה ל-`entity_profile`. `possibly_same_as` מסמן מועמד שאולי זהה לכרטיס הראשון; `"relation": "מזכיר את השם"` מסמן מסמך, כתבה או אירוע שרק מזכירים את השם.
3. **ראיות** - שורות גולמיות מ-12 טבלאות (exemptions, knesset_mk_individuals, legislation, mevaker_reports, mevaker_chapters, ica_companies, ica_partnerships, maya_officers, mevaker_donations, mavat_plans, yosh_plans, decisions), כל אחת עם `model`: הישות שהיא שייכת לה, או "אין ישות במודל".

> **בוחרים לפי מספר הקשרים, לא לפי הסדר.** הכרטיסים נבנים לשלושת המועמדים הראשונים מסוג צד (אדם, חברה, ארגון, גוף ציבורי) שיש להם קשרים, בסדר המועמדים, ולא לפי גודל. נמדד 20.11.2026 על "החטיבה להתיישבות": שלושת הכרטיסים הלכו לרסיסים עם 19, 1 ו-1 קשרים, והאשכול הקנוני עם 3,420 קשרים הופיע רק ברשימת המועמדים הנוספים (חמישי בה). לכן: עבור גם על הכרטיסים וגם על שורות `ftm_names`, דלג על מה שמסומן "מזכיר את השם", ובחר את הצד עם `incoming_links` הגבוה ביותר שמתאים לישות. אם הוא לא נראה, `entity_profile("<שם>")` מחזיר רשימה קצרה של מועמדים (בלי פרופיל), ומשם בוחרים `id`.

> **ח"כ:** השורות הגולמיות מ-`knesset_mk_individuals` הן מרחב מזהים אחר (`mk_individual_id`=528 הוא מוחמד נפאע, PersonID 528 הוא יעקב ליצמן). המזהה הנכון הוא ישות המודל `knesset.person.<PersonID>`, ולא `mk_individual_id` מהשורות.

> **תשובה חלקית:** כשטבלה לא הושלמה, התשובה נפתחת ב"## התשובה חלקית" ובשורה כמו `{"table":"exemptions","note":"scan too broad (aborted)"}`. על הטבלה הזאת **אין מסקנה**, וזה לא "אין התאמות"; צמצם את השם או השלם ב-`entity_profile` / `query_db`.

השתמש בשם מדויק ככל האפשר. `per_table_limit` מרחיב את השורות לטבלה: `search_entity("שם", 50)` (עד 100; תקרה של 60 שורות גולמיות בתשובה).

## שלב 2 - התיק עצמו: entity_profile

```
entity_profile("<id>")          # מזהה מודל: il-reg.520043027, knesset.person.528, NK-...
entity_profile("520043027")     # ח"פ / מספר רשם בן 9 ספרות - פרופיל ישיר
```
מחזיר סיכום בעברית ואחריו JSON, מקובץ לפי סוג הקשר:
- **contracts** - פטורים ממכרז והתקשרויות (כספק וכגוף מתקשר), מכרזים שפרסם, זכיות במכרז, התקשרויות מכוח פטור או מכרז.
- **payments** - תמיכות (שקיבל ושנתן), תשלומים, תרומות, הלוואות וערבויות.
- **positions** - נושאי משרה, כהונות ותפקידים. **political** - מפלגות, רשימות וסיעות.
- **legislative** - הצעות חוק (יוזם או חתום), הצבעות במליאה, שאילתות, דיונים בוועדות, תזכירים.
- **planning** - תוכניות ושינויי סטטוס. **events** - אירועי רשם החברות, פעולות שהישות מוזכרת בהן. **documents** - מסמכים ופרקי דוחות.

בכל תת-קבוצה: 20 הפריטים האחרונים לפי תאריך, ספירות וסכומים לפי מטבע. כל פריט נושא את טבלת המקור, את מפתח השורה ו-`sourceUrl` כשיש. בסיכום, כסף לפי תפקיד ומטבע: ששולם ואושר בנפרד, שורות `superseded` מוחרגות. **לא מחברים בין מטבעות, בין תפקידים, ובין אושר לשולם**, ולא מחברים פטור לחוזים שנחתמו מכוחו.

מזהה של אשכול (`NK-...`) או של כל חבר באשכול מחזיר את הפרופיל של **כל האשכול** (`cluster.members`): משרד ששינה שם, גוף עם כמה רישומים.

**מה הפרופיל לא נותן (ולכן שלב 4):** יותר מ-20 פריטים בתת-קבוצה; חיפוש טקסט חופשי בתוך דוחות המבקר או בגוף החלטות; נושאי משרה ממאיה כשהם לא מקושרים לחברה (שם החברה במאיה מקוצר; נמדד: בפרופיל של `il-reg.520043027`, אלביט מערכות, יש contracts, payments ו-events ואין positions); ושם שאין לו ישות במודל.

## שלב 3 - הכלים הייעודיים

- **חוק, הצעת חוק או תזכיר** שקשורים לישות: `legislation_history("<שם החוק או מזהה>")` - החקיקה המקורית, כל התיקונים, התקנות, ההצעות עם היוזמים ותוצאות ההצבעה. לפירוט ראה osint-knesset.
- **מה כתוב במסמכי הפטורים** (בקשות, פרוטוקולים, חוות דעת): `search_exemption_documents("<שם>|<כתיב אחר>", since="YYYY-MM-DD")`, ואז `read_exemption_documents("<id>")` לפטור אחד. טקסט OCR הוא קריאת מכונה: לא מצטטים ממנו מספר, סכום, מזהה או שם לפני פתיחת הקובץ דרך `download_link_1h`.

## שלב 4 - העמקה ב-query_db (רק למה שחסר)

כל השאילתות כאן נבדקו מול המאגר (20.11.2026). החלף את הערכים בשם או במזהה שלך.

**מבקר המדינה - שם בתוך הדוח.** קודם הפרקים (קל), ואז הטקסט המלא בחלון שנים צר (כבד: `LIKE` על הטקסט רץ קרוב לתקרת 10 השניות, ושאילתה שנקטעה פירושה "לא נבדק", לא "לא מוזכר"):
```sql
SELECT chapter_key, title, main_audited, publication_title, library_pub_date, url
FROM mevaker_chapters
WHERE main_audited LIKE '%שם%' OR title LIKE '%שם%' OR audited_bodies::text LIKE '%שם%'
ORDER BY library_pub_date DESC NULLS LAST
```
```sql
SELECT chapter_key, title, publication_title, library_pub_date, url
FROM mevaker_chapter_texts
WHERE library_pub_date >= '2020-01-01' AND text LIKE '%שם%'
ORDER BY library_pub_date DESC LIMIT 30
```
`mevaker_reports` היא תצוגת תאימות, לא לחיפוש בגוף. לעומק - ראה `osint-comptroller`.

**החלטות ממשלה** (שם בכותרת או בתקציר; `source` הוא המשרד המפרסם, ולא כל שורה היא החלטת ממשלה):
```sql
SELECT id, title, decision_number, decision_date, source, url
FROM decisions
WHERE title LIKE '%שם%' OR summary LIKE '%שם%'
ORDER BY decision_date DESC NULLS LAST LIMIT 50
```

**תכנון ובנייה:**
```sql
SELECT pl_number, pl_name, district_name, plan_county_name, pl_area_dunam, depositing_date, pl_url
FROM mavat_plans
WHERE pl_name LIKE '%שם%' OR ja_concat LIKE '%שם%'
ORDER BY depositing_date DESC LIMIT 50
```
ביו"ש אותו דבר על `yosh_plans`, אבל התאריך שם DD/MM/YYYY: `ORDER BY osint_date(depositing_date) DESC NULLS LAST`.

**חקיקה ותזכירים:**
```sql
SELECT id, title, ministry, type, pub_date_iso, url FROM legislation
WHERE title LIKE '%שם%' OR ministry LIKE '%שם%'
ORDER BY pub_date_iso DESC NULLS LAST LIMIT 100
```

**כסף מעבר ל-20 הפריטים של הפרופיל.** התקשרויות - רק לפי `entity_id` (ח"פ) או `publisher_name`, עם נוסחת ה-FX; `LIKE` על `supplier_name` נקטע. ראה `osint-money`. תמיכות - ב-`budget_supports` האינדקס הוא על `recipient_entity_id`, ולכן `LIKE` על השם **חייב** צמצום ב-`year` (בטבלה 2004-2025, נמדד) או ב-`supporting_ministry`:
```sql
SELECT recipient_entity_id, recipient_entity_name, supporting_ministry, year, amount_approved, amount_paid, purpose
FROM budget_supports
WHERE year = 2024 AND recipient_entity_name LIKE '%שם%'
ORDER BY amount_paid DESC NULLS LAST LIMIT 50
```
ומשם דרך המזהה, בלי צמצום: `SELECT year, supporting_ministry, amount_approved, amount_paid, purpose FROM budget_supports WHERE recipient_entity_id = '<id>' ORDER BY year DESC`.

**עמותה:**
```sql
SELECT amuta_id, name_he, status, classification, revenue, expenses, employees, nihul_takin, last_report_year
FROM amutot WHERE name_he LIKE '%שם%' LIMIT 50
```

**פטורים לפי שם** (כשהפרופיל לא מצא ספק במודל; אם נקטע - `search_exemption_documents`):
```sql
SELECT id, title, publisher, supplier_names, supplier_ids, amount_ils, amount_kind,
       exemption_type, contract_purpose, pub_date_iso, detail_url
FROM exemptions
WHERE supplier_names LIKE '%שם%' OR contact_name LIKE '%שם%'
ORDER BY (amount_kind IS NULL) DESC, amount_ils DESC NULLS LAST LIMIT 50
```
שורה עם `amount_kind` היא הקצאה או תמורה של רמ"י: הגוף שילם למדינה, לא קיבל ממנה.

**רשם החברות** (`company_id` הוא מספר ב-`ica_companies` וטקסט ב-`ica_changes`):
```sql
SELECT c.company_id, c.name_he, c.status, c.company_type, c.registration_date,
       (SELECT COUNT(*) FROM ica_changes ch WHERE ch.company_id = c.company_id::text) AS changes
FROM ica_companies c
WHERE c.name_he LIKE '%שם%' AND c.removed_at IS NULL
LIMIT 20
```
```sql
SELECT request_type, status_date, lien_id FROM ica_changes
WHERE company_id = '<ח"פ>' ORDER BY status_date DESC NULLS LAST LIMIT 50
```
בעלי מניות ודירקטורים של חברה פרטית אינם ברשם הפתוח - `checkid-holders`.

**נושאי משרה בחברה ציבורית** (מאיה; שם החברה מקוצר, "אלביט הדמיה" ולא השם ברשם):
```sql
SELECT name, position, company_name, start_date, end_date, proof_url
FROM maya_officers
WHERE (company_name LIKE '%שם%' OR name LIKE '%שם%') AND removed_at IS NULL
ORDER BY start_date DESC NULLS LAST LIMIT 40
```

**תרומות לבחירות** (אדם שאין לו ישות במודל):
```sql
SELECT donor_name, donor_city, recipient, party, sum, publication_date, election_type
FROM mevaker_donations
WHERE donor_name LIKE '%שם%'
ORDER BY sum DESC NULLS LAST LIMIT 100
```
סדר השם ב-`donor_name` אינו עקבי (משפחה-פרטי או פרטי-משפחה). לעומק - `osint-donor-profile`. תורם פרטי בלי תפקיד ציבורי ובלי קשר לכסף ציבורי לא נכנס לתיק בשמו.

**כנסת:** לח"כ - `entity_profile("knesset.person.<PersonID>")`; המזהה והשם מ-`knesset_persons` (`id` = PersonID), לעולם לא מ-`knesset_mk_individuals`. פרופיל כנסת מלא - osint-knesset.

## שלב 5 - הצלבה וזיהוי קשרים בין-תחומיים

הנקודה התחקירנית: אותה ישות שמופיעה, למשל, כ**מקבלת תמיכה** + **נושא בדוח מבקר** + **צד להחלטת ממשלה** + **יזם תוכנית**. כשהפרופיל כבר מאחד אותם תחת ישות אחת, החיבור נעשה במודל (לפי מזהה); כשהחיבור הוא שלך, משתי ישויות או משורות בלי ישות:
- בדוק שזו אותה ישות (ח"פ זהה? שם מלא תואם? הקשר גיאוגרפי/תחומי מתיישב?).
- תן רמת ביטחון לזהות (גבוהה/בינונית/נמוכה).
- ציין מה יאשש או יפריך (ח"פ, PersonID, מסמך רשמי).

## שלב 6 - אימות מול המקור הרשמי

לכל פריט בתיק שמדורג לפרסום, פתח את ה-`sourceUrl` או ה-URL הרשמי (`detail_url` לפטור, `pl_url` לתכנון, `url` למבקר/חקיקה/החלטות, אתר הכנסת) ואמת את הרשומה. רק פריט שעבר אימות נכנס כ"מאומת"; השאר "ליד לבדיקה".

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| search_entity מחזיר כרטיס של רסיס קטן | בחר לפי `incoming_links` מתוך הכרטיסים ושורות `ftm_names`; או `entity_profile("<שם>")` לרשימת המועמדים |
| search_entity מחזיר "כרטיס זמני מתוך אזכורים" | לשם אין ישות במודל. נסה כתיב אחר, שם רשום או שם-גג (עיקרון 6), ואז שלב 4 |
| "התשובה חלקית" / "scan too broad" | אין מסקנה על הטבלה שנקטעה. הוסף מילה מזהה או השלם ב-`query_db` |
| יותר מדי התאמות (שם נפוץ) | סנן לפי הקשר (משרד, מחוז, תקופה); ציין במפורש שזה שם נפוץ |
| התאמה ב-exemptions אבל supplier_ids ריק | אמת זהות מול detail_url; בלי ח"פ - סמן "זהות לא אומתה" |
| `entity_profile` מחזיר רשימת מועמדים ולא פרופיל | נתת שם. בחר `id` וקרא שוב |
| שתי ישויות שנראות אותה ישות ("ייתכן שזו אותה ישות") | אל תאחד; תעד כשתי רשומות עם הערת ביטחון |
| אין תוצאות בטבלה | בדוק ב-`scrape_runs` שהמקור רץ (ראה חוקי המאגר). לא רץ = "לא נאסף" |

**אסור:** לחבר רשומות מטבלאות שונות לישות אחת על סמך שם בלבד ולהציג את החיבור כעובדה; לחבר סכומים בין מטבעות או בין תפקידים.

## אתיקה

הפרד בין דמות/חברה ציבורית (שניתן לתחקר) לאדם פרטי (שאינו נושא לתיק). שם נפוץ מחייב זהירות כפולה - ציין במפורש כשהתאמה היא שם בלבד. אל תייחס מניע, אל תקבע קשר אישי, ואל תפרסם פרטים מזהים של אדם פרטי שצף בהתאמה אקראית.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): בחירת הישות (search_entity), הפרופיל (entity_profile), הכלים הייעודיים, השלמות ב-query_db, הצלבה, אימות זהות ו-URL רשמי. עדכן רמת ביטחון לכל קשר תוך כדי.

## דוח הדסק - מבנה קבוע

הסדר הוא סדר העניין: מה שהמדינה עשתה קודם, הכסף אחר כך, השגרה בסוף.

```markdown
# תיק: [שם הישות]

## הישות והיקף החיפוש
[אדם / חברה / משרד; ה-id שנבחר ומספר הקשרים שלו; אשכול אם יש; מה נסרק; אם שם נפוץ - אזהרה מפורשת]

## פעולות של המדינה
### החלטות ממשלה ורגולטורים
[החלטות + מספר + url]
### מבקר המדינה
[פרקים + url]
### תכנון ובנייה
[תוכניות + מחוז + pl_url]
### חקיקה וכנסת
[חוקים, הצעות, תזכירים, יוזמות + קישור]

## כסף ציבורי
[תמיכות, התקשרויות ופטורים מהותיים: סכומים לפי תפקיד ומטבע, בלי חיבור ביניהם, עם sourceUrl]

## רשם החברות ומאיה
[סטטוס, שעבודים, נושאי משרה]

## תרומות לבחירות
[למי, כמה, מתי - רק אם רלוונטי לעניין הציבורי]

## קשרים בין-תחומיים (הלידים החזקים)
[כל חיבור: אילו שני מקורות, האם המודל איחד או שזה חיבור שלך, רמת ביטחון, מה יכריע]

## שגרה (שורה מסכמת)
[רכש שגרתי, הודעות דוברים, אזכורים בכותרות - ספירה ודוגמה אחת, אלא אם יש בהם חריג]

## מה לאמת בהמשך
[רשימת בדיקות: ח"פ/זהות, פתיחת URL-ים, הצלבות נוספות, מקורות שלא רצו]

**שורה תחתונה לדסק:** [האם יש כאן תחקיר, מה הקשר המעניין ביותר,
ומה חוסם אותו מלהיות סיפור]

Sources: [search_entity + entity_profile + כל שאילתות query_db + קישורי המקור שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. התיק צריך לתת לעורך תמונת קשרים תוך דקה - עם הבחנה ברורה בין מה שאומת לבין מה שהוא עדיין התאמת שם.
