---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table
name: osint-donor-profile
version: 1.2.0
description: >-
  תיק על תורם בודד מעל ה-osint-db - מאגר תרומות הבחירות של מבקר המדינה (mevaker_donations: פריימריז, רשויות מקומיות, מפלגות ארציות, מועצות אזוריות). למי הוא תרם, כמה, מתי, ולאורך כמה מערכות בחירות. הפעל כשדור כותב "תבדוק תרומות של X", "למי X תרם", "כמה X תרם", "תיק תרומות על", "האם X תורם", או כששם עולה בתחקיר וצריך לדעת אם הוא מופיע במאגר התרומות. כל פריט הוא ליד לבדיקה מול הפרסום הרשמי של מבקר המדינה, לא ממצא מאומת. לפרופיל מקבל ראה osint-candidate-funding; לחריגות רוחביות ראה osint-donation-patterns; להצלבה מול כסף ציבורי ראה osint-donations-crossref.
---

# osint-donor-profile - תיק על תורם

בונה תיק על אדם או גוף שתרם למערכות בחירות בישראל, מתוך `mevaker_donations`.

## חוקי המאגר - קרא לפני השאילתה הראשונה

- **כלי קודם, SQL אחר כך.** `search_entity("שם")` מחפש ב-`mevaker_donations` בעמודות `donor_name`, `recipient`, `candidate_name` ו-`party`, ובאותה קריאה בכל שאר המאגר; אחריו `entity_profile(id)` על הישות שהשאלה עליה. `search_entity` מחזיר עד 10 שורות לטבלה כברירת מחדל (עד 100 עם `per_table_limit`), ולכן היסטוריה מלאה של תורם או מקבל נשלפת ב-`query_db`. טבלה שמופיעה בתשובה עם `note` או `error` לא נבדקה - זה לא "אין".
- את העמודות נותן `describe_table("mevaker_donations")`. לא מנחשים שם עמודה.
- **הגבול הוא פלט, לא זמן.** הטבלה (112,396 שורות) מהירה: גם אגרגציה על כולה חוזרת בפחות משתי שניות, ויש אינדקס טריגרם על `donor_name`, `recipient`, `candidate_name` ו-`party`. מה שנחתך הוא הפלט: `query_db` מחזיר 100 שורות כברירת מחדל, ו-`LIMIT` בתוך ה-SQL לא מעלה את התקרה הזו. ליותר שורות מעבירים לכלי את הפרמטר `limit` (עד 500). ו-50 אלף התווים נגמרים לפני 500 השורות - שורה של 12 עמודות מהטבלה היא כ-280 תווים בממוצע, כך שבערך 175 שורות ממלאות את הפלט. "כהן" לבדו תואם 2,593 שורות.
- **טריות:** לפני מסקנה של "אין במאגר", בדוק שהמקור רץ: `SELECT source, max(started_at) FROM scrape_runs WHERE status IN ('ok','warn') AND source = 'mevaker_donations_scraper' GROUP BY 1`. מקור שלא רץ הוא "לא נאסף", לא "אין".
- **הערכים בפועל** (נמדד 20.11.2026): `election_type` - `primaries` (51,835), `local` (46,078), `parties` (10,357), `regional` (3,818), `special` (308). `publication_type` - `תרומה` (107,898), `הלוואה` (3,557), `ערבות` (941). `is_deficit_coverage` הוא טקסט: `'True'` (1,289), `'False'`, או ריק. `publication_date` הוא טקסט ISO (YYYY-MM-DD), מ-2007 עד 2026.
- **מלכודות:**
  - סדר השם ב-`donor_name` אינו עקבי ("כהן יצחק" מול "יצחק כהן").
  - בפריימריז, ב-11,816 שורות `donor_first` ריק ו-`donor_last` מחזיק את השם המלא, לרוב בסדר פרטי-משפחה (ב"כהן": 186 שורות "<פרטי> כהן" מול 2 "כהן <פרטי>"). קיבוץ לפי `donor_last` לא יחבר אותן לשאר השורות של אותו אדם. באותן שורות גם `donor_country` הוא מחרוזת ריקה.
  - `donor_country` הוא `''` כשלא דווח, לא `NULL`, ויש כמה כתיבים לאותה מדינה ("ארה"ב", "ארה"ב-NY", "ארה"ב-ניו יורק").
  - ב-441 שורות יש ישויות HTML ב-`donor_city` (`&quot;`, `&#039;`).
  - `election_date` ריק בכל שורות הפריימריז ובכל שורות המפלגות; `election_period_name` ריק כמעט תמיד.
  - שורות זהות: 1,013 קבוצות של שורות זהות בתורם, מקבל, סכום ותאריך (2,128 שורות, 1,115 מהן עודפות). זו יכולה להיות תרומה שחזרה או כפילות בדיווח.

מפת המאגר המלאה, שנבנית מהמאגר: `references/db-map.md` בתיקיית התוסף.

## נקודות שחייבות להיות בראש

1. **סדר השם אינו עקבי.** חפש לפי שם משפחה בלבד, ורק אחר כך סנן. קבץ לפי `donor_last` + `donor_city`, וזכור את השורות של הפריימריז שבהן השם המלא יושב ב-`donor_last` (למעלה).
2. **התאמת שם אינה אישור זהות.** בשם נפוץ - הצלב עיר וטווח שנים. בשם נדיר ההתאמה חזקה בהרבה, אבל עדיין ליד.
3. **תרומה מדווחת אינה עבירה.** הסיפור הוא בדפוס ובהקשר, לא בעצם קיומה.
4. **שורות זהות.** לפני כל סה"כ - בדוק אותן בנפרד והצג אותן, אל תסכום בשקט.
5. **פרטיות.** רוב התורמים הם אנשים פרטיים. תורם קטן בלי תפקיד ציבורי ובלי קשר לכסף ציבורי לא נכנס לכתבה בשמו. **אין העשרה ב-`population_search`** בלי אישור של דור ועניין ציבורי ברור.

## הרצף

### 1. איתור רחב

קודם `search_entity("<שם>")`: אם התורם הוא חברה או אדם שיש לו ישות במודל, `entity_profile` מחזיר באותה קריאה גם את התרומות שלו וגם את כל השאר (התקשרויות, פטורים, דירקטוריונים). אחר כך ההיסטוריה המלאה:

```sql
SELECT id, donor_name, donor_first, donor_last, donor_city, donor_country, recipient, party,
       publication_type, sum, publication_date, election_type
FROM mevaker_donations
WHERE donor_name LIKE '%<שם משפחה>%'
ORDER BY sum DESC NULLS LAST
LIMIT 150
```
העבר `limit=150` לכלי. גם שם משפחה בינוני חורג מ-50 אלף התווים (שם שתואם 232 שורות הוא כ-66 אלף תווים), ובשם נפוץ (כהן, לוי) הרבה יותר - צמצם מראש ב-`AND donor_city = '<עיר>'`, התחל בסיכום של שלב 3, או דפדף לפי `sum` / `publication_date`.

בדיקת שורות זהות לפני סיכום:
```sql
SELECT donor_name, recipient, sum, publication_date, COUNT(*) AS n
FROM mevaker_donations
WHERE donor_name LIKE '%<שם משפחה>%'
GROUP BY donor_name, recipient, sum, publication_date
HAVING COUNT(*) > 1
```

### 2. איחוד וריאנטים

בנה טבלת איותים: איזה איות, מאיזו עיר, באיזה טווח שנים. הכרע מי מהם אותו אדם, **וסמן במפורש אילו וריאנטים אוחדו ועל סמך מה**. עיר זהה מחזקת מאוד; עיר שונה מחייבת זהירות.

### 3. סיכום

- סה"כ, מספר תרומות, טווח שנים
- פילוח לפי מקבל - מי קיבל הכי הרבה
- פילוח לפי `election_type` - פריימריז מול מוניציפלי מול ארצי
- **חוצה מפלגות?** תורם שנותן לשני צדדים הוא סיפור אחר מתורם נאמן. זו השאלה הכי חזקה בתיק
- הלוואות וערבויות בנפרד מתרומות. הלוואה עם `loan_return_sum` ריק או אפס שקולה כלכלית לתרומה
- `is_deficit_coverage = 'True'` בנפרד

```sql
SELECT recipient, party, election_type, publication_type, COUNT(*) AS n, ROUND(SUM(sum)) AS total,
       MIN(publication_date) AS first_d, MAX(publication_date) AS last_d
FROM mevaker_donations
WHERE donor_name LIKE '%<שם משפחה>%' AND donor_city = '<עיר>'
GROUP BY recipient, party, election_type, publication_type
ORDER BY total DESC NULLS LAST
```

### 4. הצלבה פנימית

לכל מקבל מרכזי: `knesset_mk_individuals` (האם ח"כ; `mk_individual_name` הוא שם משפחה בלבד, והשם הפרטי ב-`mk_individual_first_name`), `wp_articles` (מה כבר פרסמנו, `title` / `excerpt LIKE`). אם התורם נראה מעניין - העבר ל-`osint-donations-crossref` לבדיקה מה הוא קיבל מהמדינה.

## פורמט הפלט

```
## <שם התורם>

**זיהוי:** [וריאנטים שאוחדו + על סמך מה] | **עיר:** [] | **טווח:** [שנים]

| מקבל | תפקיד | סה"כ | מס' תרומות | טווח | סוג בחירות |

**סה"כ:** [] ש"ח ב-[] תרומות
**חוצה מפלגות:** [כן/לא + פירוט]
**הלוואות/ערבויות:** []
**שורות זהות:** [כמה, ואם נספרו]
**מה לאמת:** [רשימה]
```

**מה לאמת לפני פרסום:** הפרסום המקורי באתר מבקר המדינה לכל תרומה שנכנסת לכתבה; זהות התורם מול מקור עצמאי; ותגובת התורם והמקבל.

כתוב בעברית, בלי אימוג'ים, חד וקצר. אל תציג התאמת שם כעובדה, ואל תקבע שסכום חרג מהתקרה בלי אימות מול נוסח החוק לאותה מערכת בחירות.
