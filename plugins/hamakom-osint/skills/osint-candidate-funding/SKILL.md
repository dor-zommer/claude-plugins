---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table
name: osint-candidate-funding
version: 1.2.0
description: מי מימן מועמד, ח"כ, ראש רשות, רשימה מקומית או מפלגה - פרופיל המימון מעל ה-osint-db, מתוך מאגר תרומות הבחירות של מבקר המדינה (mevaker_donations). מפלח לפי מערכות בחירות, מזהה תורמים גדולים וחוזרים, מפריד מימון עצמי, ומחשב ריכוזיות. הפעל כשדור כותב "מי מימן את X", "מי תרם ל-X", "תרומות שקיבל", "מאיפה הכסף של X", "פרופיל מימון", "כמה גייס", "מי מממן את הרשימה". כל פריט הוא ליד לבדיקה מול הפרסום הרשמי של מבקר המדינה, לא ממצא מאומת. לתיק על תורם בודד ראה osint-donor-profile; לחריגות רוחביות ראה osint-donation-patterns; להצלבה מול כסף ציבורי ראה osint-donations-crossref.
---

# osint-candidate-funding - מי מימן את המועמד

בונה פרופיל מימון של מקבל תרומות מתוך `mevaker_donations`.

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

## המלכודת המבנית שחייבים להכיר

**`election_date` ריק בכל שורות הפריימריז והמפלגות, ו-`election_period_name` ריק כמעט תמיד.** אי אפשר לשייך תרומה למערכת בחירות דרכם. **יש לגזור את הקמפיין מאשכולות `publication_date`** - ולהציג את המיפוי במפורש בפלט. ברשויות המקומיות ובמועצות האזוריות `election_date` מלא.

וזכור: **תרומות ממשיכות להתפרסם חודשים אחרי הבחירות.** תרומה מאוחרת אינה בהכרח שייכת לקמפיין הבא - היא יכולה להיות דיווח מאוחר או כיסוי גירעון. בדוק `is_deficit_coverage`.

## הרצף

### 1. איתור המקבל

קודם `search_entity("<שם>")`: מחפש גם ב-`recipient`, `candidate_name` ו-`party`, ומביא את הח"כ, המפלגה והישויות הקשורות מהמודל. אחר כך:

```sql
SELECT recipient, election_type, COUNT(*) n, ROUND(SUM(sum)) total
FROM mevaker_donations
WHERE recipient LIKE '%<שם>%'
GROUP BY recipient, election_type ORDER BY total DESC NULLS LAST
```

LIKE רחב יאסוף אנשים אחרים ("ביטן" מחזיר גם "אביטן", כולל רשימות מקומיות שנקראות על שם מועמד). הצג את הווריאנטים והכרע לפני שממשיכים. אותו מקבל יכול להופיע בסדר שם הפוך, וגם תחת `candidate_name` או `party`.

### 2. שליפה מלאה

```sql
SELECT donor_name, donor_city, donor_country, sum, publication_date,
       election_type, publication_type, is_deficit_coverage
FROM mevaker_donations
WHERE recipient = '<שם מדויק>'
ORDER BY publication_date
```
העבר `limit=500` לכלי. שורה כאן היא כ-200 תווים, כך שכ-250 שורות ממלאות את 50 אלף התווים: מעבר לזה - שלוף לפי חלון של `publication_date` (קמפיין אחד בכל פעם).

### 3. פילוח לקמפיינים

מיין לפי תאריך, זהה פערים של חודשים, קבע גבולות אשכול, **ואמת כל אשכול מול לוח הבחירות בפועל** - מתי נערכו הפריימריז ומתי הבחירות. אם אשכול נמשך מעבר למועד הבחירות, אמור זאת במפורש. הפערים הגדולים:

```sql
SELECT publication_date,
       publication_date::date - lag(publication_date) OVER (ORDER BY publication_date)::date AS gap_days
FROM mevaker_donations
WHERE recipient = '<שם מדויק>'
ORDER BY gap_days DESC NULLS LAST
LIMIT 10
```

בדוק גם: האם למקבל יש רשומות ב-`election_type='local'` בנוסף ל-`primaries`? מועמד יכול לרוץ בשתי זירות (השאילתה בשלב 1 מפלחת לפי סוג).

### 4. ניתוח

- **חמשת התורמים הגדולים** ואיזה אחוז מהסך הם מהווים. מעל 50% = תלות:
  ```sql
  WITH d AS (
    SELECT donor_name, SUM(sum) AS s
    FROM mevaker_donations
    WHERE recipient = '<שם מדויק>' AND publication_type = 'תרומה'
    GROUP BY donor_name)
  SELECT donor_name, s, ROUND(100.0 * s / SUM(s) OVER ()) AS pct
  FROM d ORDER BY s DESC LIMIT 5
  ```
  הקיבוץ לפי `donor_name` מפצל תורם שנכתב בשני סדרים; אחד את הווריאנטים לפני שמחשבים אחוז.
- **תורמים חוזרים** - מי תרם ביותר ממערכת אחת. אלה הקשרים העמידים
- **גיאוגרפיה** - כמה מהעיר של המועמד, כמה מבחוץ
- **חו"ל** - `donor_country NOT IN ('', 'ישראל')`. מחרוזת ריקה היא "לא דווח", ובפריימריז היא נפוצה - אל תכתוב "אין תרומות מחו"ל" על סמך הסינון הזה בלבד
- **מימון עצמי** - המועמד מופיע כתורם לעצמו, לרוב בסדר שם הפוך (המקבל "<משפחה> <פרטי>", התורם "<פרטי> <משפחה>"). שורה נפרדת בדוח
- **הלוואות וערבויות** בנפרד

### 5. הצלבה

לכל תורם משמעותי - `osint-donor-profile` (למי עוד תרם) ו-`osint-donations-crossref` (מה קיבל מהמדינה). הצלב מול `wp_articles` ו-`knesset_mk_individuals` (`mk_individual_name` הוא שם משפחה בלבד - התאם גם לפי `mk_individual_first_name`).

**פרטיות:** תורם פרטי קטן, בלי תפקיד ציבורי ובלי קשר לכסף ציבורי, לא נכנס לכתבה בשמו. כל שורה בטבלת הפלט היא ליד לבדיקה, לא ממצא.

## פורמט הפלט

```
## מימון <שם המקבל>

### קמפיין [שנה] - [מערכת הבחירות]
תאריכים: [] | תרומות: [] | סה"כ: [] ש"ח

| תורם | עיר | סכום | תאריך | סוג |

**חמשת הגדולים:** [] = []% מהגיוס
**תורמים חוזרים בין קמפיינים:** []
**מימון עצמי:** []
**מחו"ל:** []
**מה לאמת:** []
```

**מה לאמת לפני פרסום:** שיוך כל אשכול למערכת הבחירות הנכונה מול לוח הבחירות; הפרסום המקורי אצל מבקר המדינה; ותגובת המקבל.

כתוב בעברית, בלי אימוג'ים, חד וקצר. תרומה חוקית ומדווחת אינה עבירה - הסיפור הוא בדפוס, בריכוזיות, ובמה שהתורם צריך.
