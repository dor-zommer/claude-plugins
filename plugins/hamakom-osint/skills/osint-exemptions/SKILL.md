---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_exemption_documents mcp__plugin_hamakom-osint_osint-db__read_exemption_documents mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__new_since
name: osint-exemptions
version: 1.3.0
description: סריקה תחקירנית של פטורים ממכרז (התקשרויות ללא מכרז) עבור דסק "המקום הכי חם בגיהנום", מעל ה-osint-db (טבלת exemptions ומסמכי הפטורים המצורפים). מאתר את ההתקשרויות שראויות לבדיקה - ספק שחוזר שוב ושוב אצל אותו משרד או בכמה משרדים, ריכוז התקשרויות אצל מפרסם אחד, סכומים גדולים ביחס לגוף ולתקופה, ונימוק שלא מתיישב עם ההתקשרות. הפעל כשדור כותב "תבדוק פטורים", "פטור ממכרז חשוד", "מי הספק שחוזר", "כמה X קיבל בפטור", "פטורים גדולים החודש", "תסרוק פטורים של משרד Y", "מי מקבל הכי הרבה בלי מכרז". התוצר הוא לידים לבדיקה עם עדיפות - לא ממצא מאומת. כל ליד חייב אימות מול detail_url הרשמי לפני שהוא הופך לסיפור. לתיק מאוחד על ישות חוצה-מאגר ראה osint-entity-dossier; לדייג'סט יומי של פטורים חדשים ראה osint-daily-leads.
---

# osint-exemptions - סריקת פטורים ממכרז ללידים תחקיריים

סקיל לאיתור התקשרויות שראויות לבדיקה בטבלת `exemptions` שב-osint-db (התקשרויות בפטור ממכרז, כוונות להתקשרות ומיזמים משותפים של משרדי ממשלה וגופים ציבוריים). התוצר אינו "שערורייה" - הוא רשימת **לידים לבדיקה** מדורגת לפי עדיפות, שכל אחד מהם דורש אימות מול הרשומה הרשמית לפני פרסום.

## עקרונות יסוד

1. **פטור ממכרז לגיטימי ברוב המקרים.** ספק יחיד, התקשרות המשך, גוף ממשלתי אחר, סודיות - אלה מסלולים שהחוק קבע. **אסור לכתוב "פטור חשוד"**, לא בדוח לדסק ולא בכתבה, ולא לתאר פטור כ"מפוקפק" על סמך המאגר.
2. **ההתקשרות היא הסיפור, לא מנגנון הפטור.** מה שראוי לבדיקה הוא מי הספק, כמה כסף, כמה פעמים זה חוזר, ואצל איזה מוסד. פטור הוא רק הדרך שבה ההתקשרות נעשתה. ליד טוב נשמע כמו "משרד X התקשר עם ספק Y שש פעמים בשלוש שנים ב-40 מיליון", לא כמו "עוד פטור ממכרז".
3. **המאגר מחזיר רשומות גולמיות, לא עובדות מפורסמות.** כל שורה היא ליד. הפוך ליד לסיפור רק אחרי שפתחת את `detail_url` (או את המסמך המצורף) ואימתת מול הפרסום הרשמי.
4. **סכומים יכולים להיות עצומים.** `amount_ils` הוא מספר שלם בשקלים; הסכם מסגרת תחבורתי בודד במאגר רשום ב-53.6 מיליארד. בדוק אם הסכום חריג ביחס לגודל הגוף, לתקופת ההתקשרות ולמספר הגופים שהיא משרתת, לא כמספר בפני עצמו.
5. **נימוק דליל הוא ליד, לא הוכחה.** `reasoning` / `regulation_text` קצר מעלה שאלה - אבל ייתכן שהפירוט המלא במסמך המצורף או ב-`detail_url`. בדוק שם לפני שאתה כותב "ללא הסבר".
6. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ליד תן עדיפות (גבוהה/בינונית/נמוכה) + מה הראיה החסרה שתכריע. אל תציג דפוס סטטיסטי כאשמה.

## חוקי המאגר - קרא לפני השאילתה הראשונה

- **כלי קודם, SQL אחר כך.** שאלה על מה נקנה, מה אושר או מה נומק - `search_exemption_documents`. ספק או גוף בשמו - `search_entity` ואחריו `entity_profile`. `query_db` רק לאגרגציות ולמה שהכלים לא מחזירים.
- את העמודות נותן `describe_table("exemptions")`. לא מנחשים שם עמודה.
- **כסף:** בכל סכום או דירוג של `amount_ils` מסננים `amount_kind IS NULL`. שורה עם `amount_kind` (43,794 שורות, הקצאות ותמורות של רשות מקרקעי ישראל) היא כסף שהמדינה מקבלת, לא הוצאה.
- **תאריכים:** `pub_date` ו-`update_date` הם טקסט בצורה DD/MM/YYYY. השוואה שלהם למחרוזת ISO היא השוואת טקסט ומחזירה זבל (`update_date >= '2026-11-06'` מחזיר 78,107 שורות), והשוואה ל-`date` נכשלת (`operator does not exist: text >= date`). לחלון זמן משתמשים ב-`pub_date_iso` (טקסט ISO) מול `to_char(CURRENT_DATE - N, 'YYYY-MM-DD')`. `osint_date(update_date)` עובד על שורה בודדת, אבל כתנאי על כל הטבלה הוא חורג מ-10 השניות.
- **כסף בהתקשרויות:** `budget_contracts.volume` הוא במטבע של `currency`, ושורה `superseded` הוחלפה בדיווח מאוחר יותר. כל סכום הוא `SUM(volume * FX)` עם `superseded IS NOT TRUE`, לפי הנוסחה בתיאור של `query_db`. לעולם לא `SUM(volume)`.
- **טריות:** לפני מסקנה של "אין במאגר", בדוק שהמקור רץ: `SELECT source, max(started_at) FROM scrape_runs WHERE status IN ('ok','warn') AND source = 'exemptions' GROUP BY 1`. מקור שלא רץ הוא "לא נאסף", לא "אין".
- **שאילתה שנכשלה בזמן אינה "אין תוצאות".** הגבול הוא 10 שניות לשאילתה, 500 שורות ו-50 אלף תווים בפלט. `query_db` מחזיר 100 שורות כברירת מחדל, ו-`LIMIT` בתוך ה-SQL לא מעלה את התקרה הזו. ליותר שורות מעבירים לכלי את הפרמטר `limit` (עד 500).

(נמדד 20.11.2026 על 212,875 שורות.) מפת המאגר המלאה, שנבנית מהמאגר: `references/db-map.md` בתיקיית התוסף.

## שלב 1 - מיפוי שדה החיפוש

```
describe_table("exemptions")   → אישור שמות עמודות
```

עמודות מפתח: `title, publisher, exemption_type, status, pub_date_iso, update_date, deadline, proc_number, detail_url, supplier_names, supplier_ids, regulation_text, amount_ils, amount_kind, first_seen_at, contract_start, contract_end, contract_purpose, reasoning, subjects`.

`exemption_type`: `פטור` (152,749), `כוונה להתקשרות` (57,647), `מיזם משותף` (2,462), `הודעת מכר` (17).

**תאריך הפרסום הוא `pub_date_iso`, והוא חסר ב-140,508 מתוך 212,875 שורות** (`NULL` או מחרוזת ריקה). כל השורות בלי תאריך פרסום הן רשומות ישנות שתאריך העדכון שלהן עד 29.09.2020; מאז כל שורה נושאת `pub_date_iso`, ולכן חלון זמן עדכני לפיו שלם. לשורה ישנה בלי תאריך פרסום, `update_date` ("תאריך עדכון" באתר) הוא התאריך היחיד, ומציגים אותו כ"עודכן ב-", לא כ"פורסם ב-". `first_seen_at` אומר מתי סרקנו, לא מתי זה קרה.

## שלב 2 - מסמכים וישויות (הכלים)

**מה נקנה, מה אושר, מה נומק:** `search_exemption_documents(query, since, until, types)` מחפש בתוך המסמכים המצורפים (בקשות פטור, פרוטוקולי ועדות, חוות דעת) ובשדות. חפש כמה ניסוחים מופרדים ב-`|` - המסמכים כמעט אף פעם לא משתמשים במילים של הקורא. `read_exemption_documents(id)` נותן את הטקסט המלא של פטור אחד וקישור הורדה לשעה. טקסט שנקרא ב-OCR או בתעתוק מודל (`text_source`) הוא ליד: לעולם לא מצטטים ממנו סכום, מספר חברה או שם בלי לפתוח את הקובץ.

**ספק או גוף מסוים:** `search_entity("שם הספק")` ואחריו `entity_profile(id)`, שמחזיר את כל ההתקשרויות והפטורים של הישות, עם סכומים לפי תפקיד ומטבע. `entity_profile` מקבל גם מספר חברה בן 9 ספרות - ו-`supplier_ids` בפטור הוא בדיוק זה. טבלה שמופיעה בתשובה של `search_entity` עם `note` או `error` לא נבדקה; אין להסיק ממנה "אין".

## שלב 3 - הרצת דפוסי הלידים (SQL)

האגרגציות על הטבלה כולה עובדות היום: `GROUP BY publisher`, `GROUP BY supplier_names` ו-`COUNT(DISTINCT publisher)` לכל ספק חזרו כולן בפחות מ-5 שניות (נמדד 20.11.2026). צמצום ב-`WHERE` עדיין עדיף כשהשאלה ממוקדת, כי הוא מקצר את הפלט.

**ספק שחוזר אצל משרד מסוים (כמות + סכום מצטבר):**
```sql
SELECT supplier_names, COUNT(*) AS deals, SUM(amount_ils) AS total_ils
FROM exemptions
WHERE publisher = 'משרד התחבורה והבטיחות בדרכים'
  AND supplier_names <> '' AND supplier_names <> 'ללא'
  AND amount_kind IS NULL
GROUP BY supplier_names
HAVING COUNT(*) >= 3
ORDER BY total_ils DESC NULLS LAST
LIMIT 20
```
את אותה שאילתה בלי תנאי ה-`publisher` אפשר להריץ על כל הממשלה.

**ריכוז לפי מפרסם:**
```sql
SELECT publisher, COUNT(*) AS deals, SUM(amount_ils) AS total_ils
FROM exemptions
WHERE amount_kind IS NULL
GROUP BY publisher
ORDER BY total_ils DESC NULLS LAST
LIMIT 25
```
לריכוז בהתקשרויות הגדולות בלבד הוסף `AND amount_ils >= 10000000`.

**הסכומים הגדולים ביותר (top N):**
```sql
SELECT id, title, publisher, supplier_names, amount_ils, exemption_type, pub_date_iso, detail_url
FROM exemptions
WHERE amount_ils IS NOT NULL AND amount_kind IS NULL
ORDER BY amount_ils DESC NULLS LAST
LIMIT 30
```

**נימוק/בסיס משפטי דליל ביחס לסכום גדול:**
```sql
SELECT id, title, publisher, supplier_names, amount_ils,
       LENGTH(reasoning) AS reason_len, LENGTH(regulation_text) AS reg_len, detail_url
FROM exemptions
WHERE amount_ils >= 1000000 AND amount_kind IS NULL
  AND (LENGTH(COALESCE(reasoning,'')) < 60 OR LENGTH(COALESCE(regulation_text,'')) < 40)
ORDER BY amount_ils DESC NULLS LAST
LIMIT 40
```
לפני שמסמנים נימוק כדליל - `read_exemption_documents(id)`: הנימוק המלא יושב לרוב במסמך המצורף.

**אותו ספק חוצה כמה משרדים (ריכוז ממשלתי-רוחבי):**
```sql
SELECT supplier_names, COUNT(DISTINCT publisher) AS publishers, COUNT(*) AS deals, SUM(amount_ils) AS total_ils
FROM exemptions
WHERE supplier_names <> '' AND supplier_names <> 'ללא' AND amount_kind IS NULL
GROUP BY supplier_names
HAVING COUNT(DISTINCT publisher) >= 3
ORDER BY publishers DESC, total_ils DESC NULLS LAST
LIMIT 30
```
ובכיוון ההפוך, לספק אחד - איפה הוא מופיע:
```sql
SELECT publisher, COUNT(*) AS deals, SUM(amount_ils) AS total_ils
FROM exemptions
WHERE supplier_names LIKE '%שם הספק%' AND amount_kind IS NULL
GROUP BY publisher
ORDER BY total_ils DESC NULLS LAST
```
**רעש ב-`supplier_names`:** 20,278 שורות רשומות עם הספק "ללא"; אותו ספק מופיע בכמה איותים ("בע"מ" מול "בעמ"); ושמות ארוכים חתוכים ב-35 תווים (11,546 שורות באורך 35 בדיוק). קבץ איותים בצד שלך, או עבוד לפי `supplier_ids` (מספר חברה, קיים ב-140,382 שורות), שהוא מפתח קשיח.

**פורסמו לאחרונה:**
```sql
SELECT id, title, publisher, supplier_names, amount_ils, exemption_type, pub_date_iso, detail_url
FROM exemptions
WHERE pub_date_iso >= to_char(CURRENT_DATE - 14, 'YYYY-MM-DD')
  AND amount_kind IS NULL
ORDER BY pub_date_iso DESC, amount_ils DESC NULLS LAST
LIMIT 50
```
השתמש בתאריך יחסי (`CURRENT_DATE - N`) ולא בתאריך קשיח, שמתיישן ומחזיר חלון שגוי. `new_since("exemptions", "<תאריך>")` מחזיר לפי זמן קליטה (`first_seen_at`), ולכן גם בתוצאה שלו בדוק את `pub_date_iso` של כל שורה: מה שקדם לחלון הוא השלמה של עבר, לא חדש. פטור ישן שהמפרסם עדכן אינו "פורסם לאחרונה": מתוך 72,367 השורות שיש להן תאריך פרסום, 2,892 עודכנו יותר מ-90 יום אחריו.

**ספק ספציפי (כמה X קיבל בפטור):** קודם `search_entity` / `entity_profile` (למעלה). חלופת SQL, לפי מספר החברה כשהוא ידוע:
```sql
SELECT id, title, publisher, amount_ils, amount_kind, exemption_type, pub_date_iso, update_date, detail_url
FROM exemptions
WHERE supplier_ids = '<מספר תאגיד>'
ORDER BY amount_ils DESC NULLS LAST
LIMIT 100
```
או לפי שם: `WHERE supplier_names LIKE '%שם הספק%'`. שורה עם `amount_kind` היא הקצאה או תמורה של רמ"י, כסף שהמדינה מקבלת. לא מחברים אותה לסכום שהספק "קיבל".

## שלב 4 - סינון רעש ודירוג לידים

לא כל התקשרות היא סיפור. הורד עדיפות כש: ספק יחיד מובהק בתחומו (תוכנה ייעודית, תרופה), התקשרות המשך לחוזה קיים, גוף ביטחוני שבו פטור הוא הנורמה, התקשרות עם גוף ממשלתי או עירוני אחר, או רכש שגרתי של מתכלים אצל גוף גדול (ניקיון, מזון, ציוד משקי וחד־פעמי, ציוד משרדי) - גם במיליונים, כי שב"ס והמשטרה קונים לעשרות אלפי אנשים. העלה עדיפות כש: סכום גדול מול סוג ההתקשרות וגודל הגוף, ספק לא-מוכר שמרכז התקשרויות, אותו ספק שחוזר אצל אותו מוסד שנה אחרי שנה, נימוק שלא מתיישב עם ההתקשרות, או ריכוז אצל מפרסם אחד שלא מוסבר.

דרג כל ליד: **עדיפות גבוהה** (התקשרות שראויה לתחקיר), **בינונית** (דורש בדיקה אבל ייתכן הסבר), **נמוכה** (כנראה תקין, לתיעוד).

## שלב 5 - העשרה ואימות מול המקור הרשמי

לכל ליד שמדורג גבוה/בינוני: `read_exemption_documents(id)` לנימוק המלא ולמסמכים, ואז `detail_url` (web_fetch; אם חסום - Claude in Chrome). בדוק: הנימוק המלא, הבסיס בתקנות חובת המכרזים, זהות הספק (`supplier_ids` → `entity_profile`), היקף וטווח החוזה (`contract_start` / `contract_end`, `contract_purpose`), ואיש הקשר (`contact_name`). רק אחרי שהרשומה הרשמית מאשרת - הליד הופך לבסיס לסיפור.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| השאילתה חרגה מ-10 שניות | בדרך כלל פונקציה על עמודה בתוך `WHERE` (כמו `osint_date(update_date)`) או `LIKE` על טקסט ארוך. החלף ב-`pub_date_iso`, או צמצם ב-`publisher` / `exemption_type` / `amount_ils` |
| `operator does not exist: text >= date` | עמודת התאריך היא טקסט. השווה `pub_date_iso >= to_char(CURRENT_DATE - N, 'YYYY-MM-DD')` |
| `search_entity` החזיר `note: scan too broad (aborted)` על exemptions | הטבלה לא נבדקה - זה לא "אין התאמות". חזור עם `query_db` ו-`LIKE` על `supplier_names`, או לפי `supplier_ids` |
| `amount_ils` ריק/אפס בהרבה שורות | סנן `WHERE amount_ils IS NOT NULL AND amount_ils > 0`; ציין בדוח שחלק מהרשומות בלי סכום |
| `supplier_names` מכיל כמה ספקים במחרוזת אחת | התייחס כמחרוזת; אמת זהות מדויקת מול detail_url, לא מול ההתאמה הגולמית |
| `pub_date_iso` ריק | רשומה מלפני אוקטובר 2020. הצג את `update_date` כ"עודכן ב-", לא כ"פורסם ב-" |
| `detail_url` לא נפתח | נסה Claude in Chrome, או את קישור ההורדה מ-`read_exemption_documents`; אם עדיין חסום - סמן "לא אומת מול מקור" ואל תפרסם |

**אסור:** להציג ספק כ"מקורב", התקשרות כ"מפוקפקת" או פטור כ"חשוד" על סמך המאגר בלבד. בלי אימות מול detail_url - זה ליד, לא ממצא.

## אתיקה

ספקים וחברות הם גופים ציבוריים-כלכליים שניתן לתחקר. עם זאת, התאמת שם אינה אישור זהות: ייתכנו חברות חד-שמיות. נימוק דליל אינו שחיתות; ריכוז התקשרויות אינו בהכרח קנוניה; ופטור ממכרז הוא מסלול חוקי. נסח כל ליד כשאלה על ההתקשרות, ייחס נתונים למקור הרשמי, ואל תקבע מניע.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): בדיקת טריות המקור, חיפוש במסמכים ובישויות, הרצת דפוסי הלידים, סינון ודירוג, העשרה ואימות מול detail_url. עדכן עדיפות לכל ליד תוך כדי.

## דוח הדסק - מבנה קבוע

```markdown
# לידים - פטורים ממכרז

## טווח הסריקה
[מה נסרק: כל הטבלה / מפרסם מסוים / ספק מסוים / חלון זמן, מספר הרשומות, ומתי המקור רץ לאחרונה]

## לידים מדורגים
לכל ליד:
- **ההתקשרות:** [המוסד, הספק, הסכום, כמה פעמים חזרה, סוג ההליך]
- **למה זה ליד:** [מה בהתקשרות דורש בדיקה - חזרתיות / סכום ביחס לגוף / נימוק שלא מתיישב / ריכוז]
- **עדיפות:** [גבוהה / בינונית / נמוכה] - ומה הראיה החסרה שתכריע
- **הרשומה:** [proc_number + detail_url + השאילתה]

## מה לאמת לפני פרסום
[לכל ליד גבוה: מה לבדוק במסמכים וב-detail_url - נימוק מלא, בסיס בתקנות,
זהות הספק, היקף החוזה, איש קשר]

**שורה תחתונה לדסק:** [איזה ליד אחד הכי בשל לתחקיר, ולמה]

Sources: [שאילתות osint-db + קישורי detail_url ומסמכים שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הדוח צריך לאפשר לעורך לבחור תוך דקה איזה ליד שווה תחקיר - בלי להציג אף דפוס כעובדה מאומתת, ובלי המילה "חשוד".
