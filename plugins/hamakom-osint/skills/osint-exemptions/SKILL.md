---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate
name: osint-exemptions
description: סריקה תחקירנית של פטורים ממכרז (התקשרויות ללא מכרז) עבור דסק "המקום הכי חם בגיהנום", מעל ה-osint-db (טבלת exemptions, 139 אלף רשומות). מאתר דפוסים חשודים - ספק שחוזר שוב ושוב אצל אותו משרד או בכמה משרדים, ריכוז התקשרויות אצל מפרסם אחד, סכומים חריגים בגודלם, ונימוק דליל או גנרי שלא מצדיק פטור. הפעל כשדור כותב "תבדוק פטורים", "פטור ממכרז חשוד", "מי הספק שחוזר", "כמה X קיבל בפטור", "פטורים גדולים החודש", "תסרוק פטורים של משרד Y", "מי מקבל הכי הרבה בלי מכרז". התוצר הוא לידים לבדיקה עם עדיפות - לא ממצא מאומת. כל ליד חייב אימות מול detail_url הרשמי לפני שהוא הופך לסיפור. לתיק מאוחד על ישות חוצה-מאגר ראה osint-entity-dossier; לדייג'סט יומי של פטורים חדשים ראה osint-daily-leads.
---

# osint-exemptions - סריקת פטורים ממכרז ללידים תחקיריים

סקיל לזיהוי דפוסים חשודים בטבלת `exemptions` שב-osint-db (התקשרויות בפטור ממכרז של משרדי ממשלה וגופים ציבוריים). התוצר אינו "שערורייה" - הוא רשימת **לידים לבדיקה** מדורגת לפי עדיפות, שכל אחד מהם דורש אימות מול הרשומה הרשמית לפני פרסום.

## עקרונות יסוד

1. **המאגר מחזיר רשומות גולמיות, לא עובדות מפורסמות.** כל שורה ב-`exemptions` היא ליד. דפוס חשוד (ספק חוזר, סכום עצום, נימוק דליל) הוא סיבה לבדוק - לא מסקנה. הפוך כל ליד לסיפור רק אחרי שפתחת את `detail_url` ואימתת מול הפרסום הרשמי.
2. **פטור ממכרז הוא חוקי כברירת מחדל.** רוב הפטורים תקינים (ספק יחיד, התקשרות המשך, סודיות). הסיפור אינו "פטור" אלא **פטור שלא מסתדר** - נימוק שלא תואם את הסכום, ספק שזוכה שוב ושוב, או ריכוז חריג.
3. **סכומים יכולים להיות עצומים.** `amount_ils` הוא INTEGER בשקלים; התקשרות רכבת בודדת יכולה להיות 5,000,000,000. אל תיבהל ממספר גדול - בדוק אם הוא חריג ביחס לסוג ההתקשרות והמשרד.
4. **נימוק דליל הוא ליד, לא הוכחה.** `reasoning` / `regulation_text` קצר או גנרי מעלה דגל - אבל ייתכן שהפירוט המלא ב-`detail_url`. בדוק שם לפני שאתה כותב "ללא הסבר".
5. **כשאי-אפשר לקבוע - הערך כיוון והסתברות.** לכל ליד תן עדיפות (גבוהה/בינונית/נמוכה) + מה הראיה החסרה שתכריע. אל תציג דפוס סטטיסטי כאשמה.

## שלב 1 - מיפוי שדה החיפוש

**קרא קודם את `references/db-map.md`** - שם הספירות המדויקות, העמודות המאונדקסות, וחוק הזהב של השאילתות. אל תשכפל אותם לכאן.

```
describe_table("exemptions")   → אישור שמות עמודות
```

עמודות מפתח: `title, publisher, exemption_type, status, update_date, deadline, proc_number, detail_url, supplier_names, supplier_ids, regulation_text, amount_ils, first_seen_at, contract_purpose, reasoning, subjects`. שים לב: `pub_date` ריק לעיתים קרובות - לעדכניות השתמש ב-`first_seen_at`.

## שלב 2 - הרצת דפוסי הלידים (SQL מול העמודות האמיתיות)

> **חוק מחייב: אין `GROUP BY` בלי `WHERE` על עמודה מאונדקסת.** אגרגציה על כל הטבלה (139 אלף שורות) נקטעת תמיד בתקרת מיליון צעדי ה-VM. העמודות המאונדקסות: `publisher`, `exemption_type`, `pub_date`, `amount_ils`. **`supplier_names` אינה מאונדקסת** - `LIKE` עליה עובד, `GROUP BY` עליה לא.

הרץ את הדפוסים הבאים עם `query_db`. היכן ש-`search_entity` מתאים (חיפוש ספק) הוא מהיר יותר - אבל שים לב שהוא נקטע בשקט על מונחים בלי התאמות; ראה `db-map.md`.

**ספק שחוזר אצל משרד מסוים (כמות + סכום מצטבר):**
```sql
SELECT supplier_names, COUNT(*) AS deals, SUM(amount_ils) AS total_ils
FROM exemptions
WHERE publisher = 'משרד התחבורה והבטיחות בדרכים'   -- חובה: צמצום לפני GROUP BY
  AND supplier_names <> ''
GROUP BY supplier_names
HAVING COUNT(*) >= 3
ORDER BY total_ils DESC
LIMIT 20
```
לתמונה רוחבית - הרץ את זה משרד-משרד וחבר את התוצאות בצד שלך. אין קיצור דרך; `GROUP BY supplier_names` על כל הטבלה נקטע.

**ריכוז לפי מפרסם, בתוך טווח סכומים או סוג פטור:**
```sql
SELECT publisher, COUNT(*) AS deals, SUM(amount_ils) AS total_ils
FROM exemptions
WHERE amount_ils >= 10000000        -- חובה: צמצום על עמודה מאונדקסת
GROUP BY publisher
ORDER BY total_ils DESC
LIMIT 25
```
זה נותן את הריכוז בהתקשרויות הגדולות, וזה הליד המעניין בכל מקרה. `GROUP BY publisher` בלי `WHERE` נקטע.

**הסכומים הגדולים ביותר (top N):**
```sql
SELECT id, title, publisher, supplier_names, amount_ils, exemption_type, detail_url
FROM exemptions
WHERE amount_ils IS NOT NULL
ORDER BY amount_ils DESC
LIMIT 30
```

**נימוק/בסיס משפטי דליל ביחס לסכום גדול:**
```sql
SELECT id, title, publisher, supplier_names, amount_ils,
       LENGTH(reasoning) AS reason_len, LENGTH(regulation_text) AS reg_len, detail_url
FROM exemptions
WHERE amount_ils >= 1000000
  AND (LENGTH(COALESCE(reasoning,'')) < 60 OR LENGTH(COALESCE(regulation_text,'')) < 40)
ORDER BY amount_ils DESC
LIMIT 40
```

**אותו ספק חוצה כמה משרדים (ריכוז ממשלתי-רוחבי):**

הדפוס הזה (`COUNT(DISTINCT publisher)` על כל הטבלה) כבד מהשניים שלמעלה ונקטע בוודאות. הדרך שכן עובדת היא הפוכה - קח ספק ובדוק אותו:
```sql
SELECT publisher, COUNT(*) AS deals, SUM(amount_ils) AS total_ils
FROM exemptions
WHERE supplier_names LIKE '%שם הספק%'      -- LIKE על supplier_names עובד
GROUP BY publisher
ORDER BY total_ils DESC
```
כמה משרדים חזרו בפלט = ריכוז רוחבי. את רשימת הספקים המועמדים קבל קודם מהשאילתה של הסכומים הגדולים או מריכוז לפי מפרסם, ואז בדוק אותם אחד-אחד.

**נכנסו לאחרונה (עדכניות לפי first_seen_at):**
```sql
SELECT id, title, publisher, supplier_names, amount_ils, exemption_type, first_seen_at, detail_url
FROM exemptions
WHERE first_seen_at >= date('now','-14 days')
ORDER BY first_seen_at DESC, amount_ils DESC
LIMIT 50
```
השתמש בתאריכים יחסיים (`date('now','-N days')`) ולא בתאריך קשיח - תאריך קשיח בדוגמה מתיישן ומחזיר חלון שגוי. חלופה: `new_since("exemptions", "<תאריך>")`.

**ספק ספציפי (כמה X קיבל בפטור):** עדיף `search_entity("שם הספק")` שמחזיר גם פטורים; חלופת SQL:
```sql
SELECT id, title, publisher, amount_ils, exemption_type, update_date, detail_url
FROM exemptions
WHERE supplier_names LIKE '%שם הספק%'
ORDER BY amount_ils DESC
```

## שלב 3 - סינון רעש ודירוג לידים

לא כל דפוס הוא סיפור. הורד עדיפות כש: ספק יחיד מובהק בתחומו (תוכנה ייעודית, תרופה), התקשרות המשך לחוזה קיים, או גוף ביטחוני שבו פטור הוא הנורמה. העלה עדיפות כש: סכום חריג מול סוג ההתקשרות, ספק לא-מוכר שמרכז התקשרויות, נימוק שלא תואם את הסכום, או ריכוז אצל מפרסם אחד שלא מוסבר.

דרג כל ליד: **עדיפות גבוהה** (חריגה ברורה שראויה לתחקיר), **בינונית** (דורש בדיקה אבל ייתכן הסבר), **נמוכה** (כנראה תקין, לתיעוד).

## שלב 4 - העשרה ואימות מול המקור הרשמי

לכל ליד שמדורג גבוה/בינוני, פתח את `detail_url` (web_fetch; אם חסום - Claude in Chrome) ובדוק: הנימוק המלא, הבסיס בתקנות חובת המכרזים, זהות הספק (`supplier_ids` לחברה רשומה), היקף וטווח החוזה (`contract_start/contract_end`, `contract_purpose`), ואיש הקשר (`contact_name`). רק אחרי שהרשומה הרשמית מאשרת - הליד הופך לבסיס לסיפור.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| השאילתה נקטעת (>1M opcodes / 10s) | כמעט תמיד `GROUP BY` בלי `WHERE`. הוסף צמצום על `publisher` / `amount_ils` / `exemption_type` והרץ מחדש |
| `search_entity` החזיר `note: scan too broad (aborted)` על exemptions | אין מסקנה על פטורים - זה לא "אין התאמות". חזור עם `query_db` ו-`LIKE` על `supplier_names` |
| amount_ils ריק/אפס בהרבה שורות | סנן `WHERE amount_ils IS NOT NULL AND amount_ils > 0`; ציין בדוח שחלק מהרשומות בלי סכום |
| supplier_names מכיל כמה ספקים במחרוזת אחת | התייחס כמחרוזת; אמת זהות מדויקת מול detail_url, לא מול ההתאמה הגולמית |
| pub_date ריק | השתמש ב-first_seen_at או update_date לעדכניות |
| detail_url לא נפתח | נסה Claude in Chrome; אם עדיין חסום - סמן "לא אומת מול מקור" ואל תפרסם |

**אסור:** להציג ספק כ"מקורב" או התקשרות כ"מפוקפקת" על סמך דפוס במאגר בלבד. בלי אימות מול detail_url - זה ליד, לא ממצא.

## אתיקה

ספקים וחברות הם גופים ציבוריים-כלכליים שניתן לתחקר. עם זאת, התאמת שם אינה אישור זהות: ייתכנו חברות חד-שמיות. נימוק דליל אינו שחיתות; ריכוז התקשרויות אינו בהכרח קנוניה. נסח כל ליד כהשערה לבדיקה, ייחס נתונים למקור הרשמי, ואל תקבע מניע.

## ניהול העבודה

פתח רשימת משימות (TaskCreate): מיפוי הטבלה, הרצת דפוסי הלידים, סינון ודירוג, העשרה ואימות מול detail_url. עדכן עדיפות לכל ליד תוך כדי.

## דוח הדסק - מבנה קבוע

```markdown
# לידים - פטורים ממכרז

## טווח הסריקה
[מה נסרק: כל הטבלה / מפרסם מסוים / ספק מסוים / חלון זמן, ומספר הרשומות]

## לידים מדורגים
לכל ליד:
- **הליד:** [המשרד, הספק, הסכום, סוג הפטור]
- **למה זה ליד:** [הדפוס שאיתר אותו - ספק חוזר / סכום חריג / נימוק דליל / ריכוז]
- **עדיפות:** [גבוהה / בינונית / נמוכה] - ומה הראיה החסרה שתכריע
- **הרשומה:** [proc_number + detail_url + השאילתה]

## מה לאמת לפני פרסום
[לכל ליד גבוה: מה לבדוק ב-detail_url - נימוק מלא, בסיס בתקנות,
זהות הספק, היקף החוזה, איש קשר]

**שורה תחתונה לדסק:** [איזה ליד אחד הכי בשל לתחקיר, ולמה]

Sources: [שאילתות osint-db + קישורי detail_url שנבדקו]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הדוח צריך לאפשר לעורך לבחור תוך דקה איזה ליד שווה תחקיר - בלי להציג אף דפוס כעובדה מאומתת.
