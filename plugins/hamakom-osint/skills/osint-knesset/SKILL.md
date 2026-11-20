---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__legislation_history mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table
name: osint-knesset
version: 1.4.0
description: פרופיילר כנסת מעל ה-osint-db עבור דסק "המקום הכי חם בגיהנום", בשלושה מצבים - (א) פרופיל ח"כ - search_entity(שם) ואז entity_profile("knesset.person.<PersonID>") לתפקידים, סיעות, חוקים שיזם, הצבעות ושאילתות, והעמקה ב-knesset_mk_positions, knesset_bill_initiators ו-knesset_mk_factions; (ב) מסלול הצעת חוק - legislation_history(שם או מספר) ליוזמים, להצבעות, לחוקים שתיקנה ולמסמכים, ו-knesset_bills לקוד הסטטוס; (ג) פירוק הצבעה - knesset_votes לפי תיאור הסעיף + ספירת בעד/נגד/נמנע, ופילוח לכל ח"כ דרך knesset_vote_options (תמיד עם vote_id ספציפי ו-gone_at IS NULL, כדי לא לסרוק כ-2.4 מיליון שורות). מציף הצבעות חוצות-סיעה ומפתיעות. הפעל כשדור כותב "פרופיל ח\"כ", "מה X הצביע", "איזה חוקים X יזם", "תפרק לי את ההצבעה", "מי בעד ומי נגד", "מה הסטטוס של החוק", "מי יזם את ההצעה". כל פריט הוא ליד לבדיקה מול אתר הכנסת - לא ממצא מאומת. לתיק חוצה-תחומים על אותו אדם ראה osint-entity-dossier.
---

# osint-knesset - פרופיילר כנסת

סקיל לתחקיר נתוני הכנסת ב-osint-db בשלושה מצבים: פרופיל ח"כ, מסלול הצעת חוק, ופירוק הצבעה. התוצר הוא **לידים לבדיקה** - כל מספר ושם נבדק מול אתר הכנסת הרשמי לפני פרסום.

**סדר הכלים: כלי קודם, SQL אחרון.** הנתונים של הכנסת נמצאים במאגר, ולכן לא שולפים אותם מאתר הכנסת או מאתרים חיצוניים לפני שהכלים החזירו ריק. ח"כ: `search_entity` ואז `entity_profile`. חוק או הצעה: `legislation_history`. `query_db` למה שהכלים לא מחזירים: רשימה מלאה מעבר ל-20 הפריטים של הפרופיל, הצבעה בודדת, ופילוח סיעתי.

**לפני "אין במאגר"** - בדוק שהמקור רץ. שמות המקורות ב-`scrape_runs` אינם תמיד שמות הטבלאות (ההצבעות: `knesset_votes_v4_scraper`):
```sql
SELECT source, max(started_at) AS last_ok FROM scrape_runs
WHERE status IN ('ok','warn')
  AND source IN ('knesset_bills','knesset_bill_initiators','knesset_persons','knesset_votes_v4_scraper','knesset_mk_factions','knesset_laws_scraper')
GROUP BY 1
```
ריצה מוצלחת אינה בהכרח נתונים חדשים: בדוק גם `max(first_seen_at)` בטבלה עצמה.

## עקרונות יסוד

1. **המאגר מחזיר רשומות גולמיות.** טבלאות הכנסת הן שיקוף; ייתכנו עיכובי עדכון או רשומות חלקיות. אמת כל ממצא מול אתר הכנסת לפני שהוא הופך לסיפור. את העמודות של טבלה נותן `describe_table(name)`; לא מנחשים שם עמודה.
2. **אל תסרוק את knesset_vote_options בלי vote_id.** בטבלה 2,401,364 שורות, מתוכן 1,997,774 חיות (נמדד 20.11.2026; הצבעה פר-ח"כ). כל שאילתה עליה חייבת `WHERE vote_id = <מספר>` ספציפי, אחרת היא תיקטע.
3. **סטטוס ומספרים זזים.** סטטוס הצעת חוק, ספירת הצבעה והרכב ועדה משתנים. ציין את תאריך/כנסת ההקשר, והצלב מול האתר הרשמי.
4. **הצבעה חוצת-סיעה היא ליד, לא סקופ.** ח"כ שהצביע נגד הקו הוא נקודת פתיחה לבדיקה (אולי טעות רישום, אולי היעדרות, אולי הצבעה אמיתית) - לא כותרת מוכנה.
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ממצא תן רמת ביטחון + מה הראיה החסרה שתכריע.
6. **בדוק שיש פילוח לפני שאתה מבטיח אותו.** `SELECT COUNT(*) FROM knesset_vote_options WHERE vote_id = <id> AND gone_at IS NULL`. אם 0, להצבעה הזאת אין פילוח במאגר. (נמדד 20.11.2026: הפילוח החי מגיע עד 18.11.2026, כמו ההצבעות עצמן.)
7. **מזהה הח"כ הוא PersonID של הכנסת, ובטבלאות שונות הוא נקרא בשמות שונים.** `knesset_mk_positions.person_id`, `knesset_bill_initiators.person_id`, `knesset_mk_factions.mk_individual_id` ו-`knesset_vote_options.mk_person_id` הם כולם PersonID (ב-`knesset_vote_options` גם `kmmbr_id`, טקסט עם אפסים מובילים לפעמים; `mk_person_id` שווה ל-`ltrim(kmmbr_id,'0')` בכל 65,129 השורות שנבדקו, וחסר בכ-0.02% מהשורות החיות של הכנסת ה-25). במודל הישויות הח"כ הוא `knesset.person.<PersonID>`. **השם לפי PersonID נלקח מ-`knesset_persons` (`id` = PersonID, `first_name`, `last_name`), ורק ממנה.** ב-`knesset_mk_individuals` לעומת זאת `mk_individual_id` הוא מרחב אחר שמתנגש על אנשים אמיתיים (`mk_individual_id`=528 הוא מוחמד נפאע, ו-PersonID 528 הוא יעקב ליצמן), ובמרשם יש שורות שהשם העברי שלהן נדרס בשם של ח"כ אחר בעוד שהשם האנגלי וה-`vip_id` שייכים לאדם אחר (427 "אביגדור ליברמן" עם השם האנגלי Taviv). **לעולם אל תצרף את `knesset_mk_individuals` כדי לקבל שם לפי PersonID**, וגם לא את השורות הגולמיות שלה ש-`search_entity` מחזיר. ב-`knesset_bill_initiators` **אין** עמודת `mk_individual_id`.
8. **ב-knesset_vote_options סנן תמיד `gone_at IS NULL`.** 403,590 שורות הן קולות ישנים שהוחלפו בקולות של OData v4, במרחב מזהים אחר. בלי הסינון כל ח"כ נספר פעמיים (נמדד: בהצבעה 38968, 204 שורות מול 118 חיות).

## מצב א - פרופיל ח"כ

**זיהוי:** `search_entity("שם מלא")` - הכרטיס של הח"כ הוא `knesset.person.<PersonID>` (נמדד: "יעקב ליצמן" מחזיר את `knesset.person.528` ראשון). אם חזרו כמה ישויות `knesset.person` לאותו שם, אלה אנשים שונים (למשל שני ח"כים בשם נפאע); הבחן לפי התפקידים. בלי כלי:
```sql
SELECT id AS person_id, first_name, last_name, is_current
FROM knesset_persons
WHERE last_name LIKE '%<שם משפחה>%'
   OR (first_name || ' ' || last_name) LIKE '%<שם מלא>%'
```

**הפרופיל:** `entity_profile("knesset.person.<PersonID>")` מחזיר בקריאה אחת את הקבוצות positions (תפקידים), political (סיעות וועדות) ו-legislative (הצעות חוק שיזם או חתם, הצבעות במליאה, שאילתות ששאל, דיונים בוועדות), כל תת-קבוצה עם 20 הפריטים האחרונים וספירות. זה בסיס הפרופיל; ההעמקה למטה רק למה שחסר.

**כל התפקידים** - סיעה, ועדה, תפקיד, נוכחי או היסטורי:
```sql
SELECT knesset_num, faction_name, committee_name, duty_desc, start_date, finish_date, is_current
FROM knesset_mk_positions
WHERE person_id = <person_id>
ORDER BY is_current DESC, start_date DESC
```

**כל החוקים שיזם או חתם:**
```sql
SELECT b.id, b.knesset_num, b.name, b.type_desc, b.sub_type_desc, b.status_id, b.publication_date, i.is_initiator
FROM knesset_bill_initiators i
JOIN knesset_bills b ON b.id = i.bill_id
WHERE i.person_id = <person_id>
ORDER BY b.publication_date DESC NULLS LAST
```

**סיעה וגוש (קואליציה/אופוזיציה):**
```sql
SELECT DISTINCT knesset_num, faction_name, alignment, is_current, start_date, finish_date
FROM knesset_mk_factions
WHERE mk_individual_id = <person_id>   -- כאן העמודה נקראת mk_individual_id, והערך הוא PersonID
ORDER BY is_current DESC, start_date DESC
```
`alignment` הוא `coalition` או `opposition` - זה השדה שמאפשר לזהות הצבעה חוצת-גוש בלי לנחש מהרכב הסיעה. `DISTINCT` כי לחלק מהח"כים יש שורות כפולות לאותה תקופה.

**הצבעה של הח"כ בהצבעה מסוימת** - תמיד לפי vote_id ספציפי:
```sql
SELECT o.vote_id, o.kmmbr_name, trim(o.faction_name) AS faction, t.result_type_name AS result
FROM knesset_vote_options o
LEFT JOIN knesset_vote_result_types t ON t.result_type_id = o.vote_result
WHERE o.vote_id = <vote_id> AND o.mk_person_id = <person_id> AND o.gone_at IS NULL
```
`vote_result` הוא קוד; `knesset_vote_result_types` מתרגם אותו (1 בעד, 2 נגד, 3 נמנע, 4 לא הצביע, 0 בוטל). אם `mk_person_id` ריק בשורה ישנה, `ltrim(kmmbr_id,'0') = '<person_id>'`. `mk_individual_id` **אינה קיימת** בטבלה הזאת.

## מצב ב - מסלול הצעת חוק

**הכלי:** `legislation_history("<שם ההצעה או החוק>")`, או לפי מזהה: `legislation_history("knesset.bill.<id>")`. שם עמום מחזיר רשימת מועמדים, לא ניחוש: בחר מזהה וקרא שוב. להצעה הוא מחזיר (נמדד על `knesset.bill.477119`): פרטי ההצעה (שם, סוג, כנסת, תאריך פרסום, האם עברה, הוועדה המטפלת), החוקים שההצעה חוקקה, תיקנה או ביטלה, היוזמים, ההצבעות עם בעד/נגד/נמנע, פילוח לפי סיעה של ההצבעה האחרונה, תזכירי חוק קשורים ומסמכים, וכל פריט עם קישור למקור. לחוק הוא מחזיר את כל ההיסטוריה: החקיקה המקורית, התיקונים, הביטולים, התקנות וההצעות שנגעו בו (`part`, `from_year`, `to_year` לחוק ארוך). הצבעות קיימות מ-2003 בלבד.

**מה הכלי לא נותן - קוד הסטטוס הנוכחי:**
```sql
SELECT id, knesset_num, name, type_desc, sub_type_desc, private_number,
       committee_id, status_id, publication_date, last_updated
FROM knesset_bills
WHERE name LIKE '%שם החוק%'      -- או: WHERE id = <מספר>
ORDER BY last_updated DESC LIMIT 20
```
אין במאגר טבלת תרגום ל-`status_id`: תרגם אותו מול דף ההצעה באתר הכנסת (טרומית / ועדה / קריאה ראשונה וכו'), ואל תמציא ניסוח שלב.

**היוזמים בלי הכלי** (למשל לסדר החתימה המלא):
```sql
SELECT i.person_id, i.is_initiator, i.ordinal,
       p.first_name || ' ' || p.last_name AS name
FROM knesset_bill_initiators i
LEFT JOIN knesset_persons p ON p.id = i.person_id
WHERE i.bill_id = <id>
ORDER BY i.ordinal
```
השם נגזר מ-PersonID דרך `knesset_persons` (עקרון 7). צירוף למרשם `knesset_mk_individuals` היה מחזיר אדם אחר.

## מצב ג - פירוק הצבעה

**איתור ההצבעה והספירה הכוללת:**
```sql
SELECT vote_id, knesset_num, session_id, sess_item_dscr, vote_item_dscr,
       vote_date, vote_type, is_accepted, total_for, total_against, total_abstain
FROM knesset_votes
WHERE vote_item_dscr LIKE '%נושא ההצבעה%' OR sess_item_dscr LIKE '%נושא ההצבעה%'
ORDER BY vote_date DESC LIMIT 20
```
להצבעות על הצעה מסוימת, `legislation_history` כבר מחזיר אותן עם המזהים.

**פילוח פר-ח"כ - תמיד עם vote_id מההצבעה שמצאת:**
```sql
SELECT o.kmmbr_name, trim(o.faction_name) AS faction, t.result_type_name AS result
FROM knesset_vote_options o
LEFT JOIN knesset_vote_result_types t ON t.result_type_id = o.vote_result
WHERE o.vote_id = <vote_id> AND o.gone_at IS NULL
ORDER BY faction, result
```
**אין צורך ב-JOIN לסיעות.** הטבלה מכילה כבר את `kmmbr_name` ואת `faction_name` (לפעמים עם רווח בסוף, ולכן `trim`).

**זיהוי חוצי-סיעה.** `faction_name` מאוכלס בשורות החיות, גם בכנסת ה-25 (נמדד 20.11.2026: ריק ב-90 מ-526,567 השורות החיות שלה):
```sql
SELECT trim(o.faction_name) AS faction, t.result_type_name AS result, COUNT(*) n,
       string_agg(o.kmmbr_name, ', ' ORDER BY o.kmmbr_name) AS who
FROM knesset_vote_options o
LEFT JOIN knesset_vote_result_types t ON t.result_type_id = o.vote_result
WHERE o.vote_id = <vote_id> AND o.gone_at IS NULL
GROUP BY trim(o.faction_name), t.result_type_name
ORDER BY faction, n DESC
```
סיעה שמופיעה בשתי שורות `result` שונות = פיצול, וה-`who` נותן את השמות.

כשהשדה ריק - קבל את הפילוח הגולמי (זה עובד תמיד):
```sql
SELECT t.result_type_name AS result, COUNT(*) n,
       string_agg(o.kmmbr_name, ', ' ORDER BY o.kmmbr_name) AS who
FROM knesset_vote_options o
LEFT JOIN knesset_vote_result_types t ON t.result_type_id = o.vote_result
WHERE o.vote_id = <vote_id> AND o.gone_at IS NULL
GROUP BY t.result_type_name
```
ואת השיוך הסיעתי השלם לח"כים שבפלט; אל תסתמך על JOIN אוטומטי. `LEFT JOIN knesset_mk_factions f ON f.mk_individual_id = o.mk_person_id AND f.is_current = 1` **מכפיל ח"כים**: ל-5 ח"כים יש יותר משורת סיעה נוכחית אחת (נמדד 20.11.2026; בהצבעה האחרונה של הכנסת ה-26 ה-JOIN החזיר 12 שורות ל-9 ח"כים). אם השתמשת בו - ספור `COUNT(DISTINCT o.mk_person_id)` ואל תדווח את ה-`COUNT(*)` שלו כמספר ח"כים.

`GROUP BY` כאן מותר רק כי ה-`WHERE vote_id=` מצמצם להצבעה אחת. אם השאילתה חוזרת ריקה - להצבעה הזאת אין פילוח במאגר (עקרון 6).

## שלב משותף - העשרה ואימות

אתר הכנסת הוא מקור האמת לאימות: דף ההצעה, פרוטוקול ההצבעה, ודף הח"כ. כל סטטוס, ספירה ויוזם - אמת מולו לפני פרסום. ציין את הכנסת ומספר ההצבעה/ההצעה כדי שהעורך יוכל לאמת בעצמו.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה על knesset_vote_options נקטעת | חובה `WHERE vote_id = <מספר>`; אל תסרוק את כל הטבלה (כ-2.4 מיליון שורות) |
| `column "mk_individual_id" does not exist` | ב-knesset_vote_options המזהה הוא `mk_person_id` (או `kmmbr_id`); ב-knesset_bill_initiators הוא `person_id` |
| `function group_concat does not exist` | המאגר הוא Postgres: `string_agg(col, ', ')` |
| הפילוח פר-ח"כ חוזר ריק | להצבעה הזאת אין שורות חיות במאגר (עקרון 6) |
| כל ח"כ מופיע פעמיים, או יותר מ-120 מצביעים | חסר `gone_at IS NULL` (עקרון 8) |
| faction_name ריק בפילוח | בדוק שסיננת `gone_at IS NULL`; אם עדיין ריק, השלם שיוך סיעתי ידנית |
| שם ח"כ לא נמצא | נסה שם חלקי או כתיב אחר ב-`search_entity` וב-`knesset_persons` |
| כמה ח"כים עם שם דומה | הבחן לפי person_id (עקרון 7); ציין במפורש איזה זוהה |
| ח"כ "יזם" חוקים של סיעה אחרת לגמרי | השם נלקח מהמרשם `knesset_mk_individuals` במקום מ-`knesset_persons` (עקרון 7) |
| `legislation_history` מחזיר רשימת מועמדים | השם עמום. בחר מזהה וקרא שוב |
| status_id לא ברור | תרגם מול אתר הכנסת; אל תמציא ניסוח שלב |
| total_for+against+abstain לא מסתדר | ייתכנו נעדרים/נמנעים שלא נספרו; אמת מול פרוטוקול ההצבעה |
| publication_date ריק | השתמש ב-last_updated או first_seen_at לעדכניות |

**אסור:** להציג הצבעה חוצת-סיעה או סטטוס חוק כעובדה בלי אימות מול אתר הכנסת. רשומת המאגר היא ליד.

## אתיקה

ח"כים ופעילותם הפרלמנטרית הם נתון ציבורי מובהק וניתן לתחקור. עם זאת, הצבעה בודדת אינה עמדה מלאה, והיעדרות אינה תמיד התנגדות. ייחס לרשומה הרשמית, אל תקבע מניע, ותן לח"כ הקשר (תפקיד, סיעה, מועד) במקום מספר ערום.

## ניהול העבודה

פתח רשימת משימות (TaskCreate) לפי המצב: זיהוי הח"כ/החוק/ההצבעה, הכלי (entity_profile / legislation_history), השלמות ב-query_db, הצלבה וזיהוי החריגים, אימות מול אתר הכנסת. ציין את הכנסת ומספרי הזיהוי לאורך הדרך.

## דוח הדסק - מבנה קבוע

```markdown
# כנסת - [פרופיל ח"כ / מסלול חוק / פירוק הצבעה]

## מה נבדק
[שם הח"כ + PersonID / שם ומספר החוק / נושא ומספר ההצבעה + הכנסת]

## הממצאים
[מצב א: פרטי הח"כ, תפקידים נוכחיים/היסטוריים, חוקים שיזם, הצבעות בולטות.
מצב ב: שלב נוכחי, יוזמים, הצבעות, החוקים שנגעה בהם, ציר זמן.
מצב ג: ספירת בעד/נגד/נמנע, מי בצד המיעוט, חוצי-סיעה]

## הלידים המעניינים
[הצבעה חוצת-סיעה / סטטוס מפתיע / ריכוז יוזמות - כל אחד עם
רמת ביטחון ומה שיכריע]

## מה לאמת מול אתר הכנסת
[רשימת בדיקות: דף ההצעה, פרוטוקול ההצבעה, דף הח"כ]

**שורה תחתונה לדסק:** [הליד הכי מעניין כאן ומה חוסם אותו מסיפור]

Sources: [הקריאות לכלים + שאילתות osint-db עם ה-vote_id/bill_id + קישורי אתר הכנסת]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הדוח צריך לאפשר לעורך להבין תוך דקה את התמונה הפרלמנטרית - בלי להגיש אף מספר או הצבעה כעובדה לפני אימות מול הכנסת.
