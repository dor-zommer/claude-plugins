---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table
name: osint-donation-patterns
version: 1.2.0
description: סריקת חריגות רוחבית במאגר תרומות הבחירות של מבקר המדינה מעל ה-osint-db (mevaker_donations) - תורמים סדרתיים שפרושים על הרבה מקבלים, תורמים חוצי מפלגות, כסף מחו"ל, תרומות בסכומי תקרה, הלוואות שלא הוחזרו, כיסוי גירעון, וריכוזיות מימון. הפעל כשדור כותב "מה חריג בתרומות", "תורמים סדרתיים", "כסף מחו\"ל בבחירות", "מי תורם לכולם", "לידים מהתרומות", "הלוואות שלא הוחזרו", "מי מממן את כולם", או מבקש סריקה יזומה של המאגר בלי שם ספציפי. התוצר הוא לידים מדורגים לבדיקה, לא ממצאים מאומתים. לתורם בודד ראה osint-donor-profile; למקבל ראה osint-candidate-funding; להצלבה מול כסף ציבורי ראה osint-donations-crossref.
---

# osint-donation-patterns - חריגות במאגר התרומות

סריקה יזומה של `mevaker_donations` לאיתור דפוסים שראויים לבדיקה עיתונאית. **התוצר הוא לידים מדורגים, לא ממצאים.**

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

## פילוח - בשביל המשמעות, לא בשביל הביצועים

אגרגציה על כל הטבלה עובדת (נמדד 20.11.2026: קיבוץ של כל 112 אלף השורות חוזר בפחות משתי שניות). פלח בכל זאת, כי סוגי בחירות שונים הם עולמות שונים, עם תקרות שונות:

1. **לפי `election_type`** - הרץ בנפרד לכל סוג.
2. **לפי שנה** - `WHERE substr(publication_date,1,4) = '2019'` (התאריך הוא טקסט ISO).

אם הפלט חורג מ-500 שורות, צמצם את החלון או העלה את הסף ב-`HAVING`.

## שבעה דפוסים

### 1. תורמים סדרתיים

```sql
SELECT donor_first, donor_last, donor_city, COUNT(DISTINCT recipient) recipients,
       COUNT(*) n, ROUND(SUM(sum)) total
FROM mevaker_donations
WHERE election_type = 'primaries' AND COALESCE(donor_last,'') <> ''
GROUP BY donor_first, donor_last, donor_city
HAVING COUNT(DISTINCT recipient) >= 4
ORDER BY total DESC NULLS LAST
LIMIT 50
```

**קבץ לפי השדות המפורקים (`donor_first`, `donor_last`) + `donor_city`, לא לפי `donor_name`** - סדר השם אינו עקבי. בלי `donor_first` (רק שם משפחה + עיר) "כהן מתל אביב" הופך לאדם אחד, ובלי סינון `donor_last` ריק הקבוצה הגדולה בתוצאה היא שורות בלי שם. השורות של הפריימריז שבהן השם המלא יושב ב-`donor_last` מתקבצות בנפרד - חבר אותן ידנית לליד שעולה. תרומה לחמישה מועמדים ומעלה מעלה שאלה אם מדובר בקניית גישה ולא בתמיכה. זו שאלה לבדיקה, לא מסקנה, ובכתבה היא מנוסחת כשאלה או נשענת על מקור.

### 2. חוצי מפלגות

אותו תורם למקבלים משתי מפלגות יריבות. **הדפוס החזק ביותר** - הוא מעמיד בספק את ההסבר של "תמיכה אידיאולוגית", ומחייב לשאול את התורם.

```sql
SELECT donor_first, donor_last, donor_city, COUNT(DISTINCT party) parties,
       string_agg(DISTINCT party, ' | ') party_list, COUNT(*) n, ROUND(SUM(sum)) total
FROM mevaker_donations
WHERE COALESCE(party,'') <> '' AND COALESCE(donor_last,'') <> ''
GROUP BY donor_first, donor_last, donor_city
HAVING COUNT(DISTINCT party) >= 2
ORDER BY parties DESC, total DESC NULLS LAST
LIMIT 50
```
`party` ריק ברשימות מקומיות רבות. מפלגה שהחליפה שם, או רשימה משותפת, נספרות כשתי מפלגות - בדוק לפני שמכריזים "חוצה מפלגות".

### 3. כסף מחו"ל

```sql
SELECT donor_country, recipient, COUNT(*) n, ROUND(SUM(sum)) total
FROM mevaker_donations
WHERE donor_country NOT IN ('', 'ישראל')
GROUP BY donor_country, recipient
ORDER BY total DESC NULLS LAST
LIMIT 50
```
אחד כתיבים של אותה מדינה ("ארה"ב", "ארה"ב-NY") לפני שמסכמים לפי מדינה. ב-11,816 שורות פריימריז המדינה לא דווחה, והן אינן בתוצאה.

### 4. סכומי תקרה

סכום עגול וחוזר מרמז על תרומה בגובה התקרה. ראוי לבדיקה במיוחד: כמה בני משפחה מאותה עיר שכל אחד תורם בדיוק באותו סכום לאותו מקבל:
```sql
SELECT donor_last, donor_city, recipient, sum, COUNT(DISTINCT donor_first) givers,
       MIN(publication_date) first_d, MAX(publication_date) last_d
FROM mevaker_donations
WHERE publication_type = 'תרומה' AND COALESCE(donor_last,'') <> ''
GROUP BY donor_last, donor_city, recipient, sum
HAVING COUNT(DISTINCT donor_first) >= 3
ORDER BY sum DESC
LIMIT 50
```
**התקרה משתנה לפי סוג הבחירות, מספר התורמים והשנה - אל תקבע חריגה בלי אימות מול נוסח החוק.**
**קרבה משפחתית היא ליד בלבד.** שם משפחה ועיר משותפים לא מוכיחים קשר. בני משפחה פרטיים לא מוזכרים בכתבה בשמם, ואין העשרה ב-`population_search`, בלי אימות ובלי אישור של דור.

### 5. הלוואות שלא הוחזרו

```sql
SELECT donor_name, donor_city, recipient, election_type, sum, loan_return_sum, publication_date
FROM mevaker_donations
WHERE publication_type = 'הלוואה'
  AND (loan_return_sum IS NULL OR loan_return_sum = 0)
ORDER BY sum DESC NULLS LAST
LIMIT 50
```

1,669 מתוך 3,557 ההלוואות במאגר רשומות בלי החזר (נמדד 20.11.2026). הלוואה שלא הוחזרה שקולה כלכלית לתרומה, ולעיתים עוקפת את מגבלותיה - אבל ייתכן שההחזר פשוט לא דווח עדיין. בדוק גם `publication_type = 'ערבות'`.

### 6. כיסוי גירעון

```sql
SELECT recipient, COUNT(*) n, ROUND(SUM(sum)) total
FROM mevaker_donations
WHERE is_deficit_coverage = 'True'
GROUP BY recipient
ORDER BY total DESC NULLS LAST
LIMIT 30
```
כסף שנכנס אחרי הבחירות (1,289 שורות). קטגוריה נפרדת שלעיתים מסתירה את התורמים המעניינים.

### 7. ריכוזיות

מקבל שחמשת תורמיו הגדולים מהווים מעל 50% מהגיוס תלוי בהם:
```sql
WITH d AS (
  SELECT recipient, donor_name, SUM(sum) s
  FROM mevaker_donations
  WHERE election_type = 'primaries' AND publication_type = 'תרומה'
  GROUP BY recipient, donor_name),
r AS (
  SELECT recipient, s,
         ROW_NUMBER() OVER (PARTITION BY recipient ORDER BY s DESC) rk,
         SUM(s) OVER (PARTITION BY recipient) tot
  FROM d)
SELECT recipient, COUNT(*) donors, ROUND(tot) total,
       ROUND(100.0 * SUM(s) FILTER (WHERE rk <= 5) / NULLIF(tot,0)) top5_pct
FROM r
GROUP BY recipient, tot
HAVING tot >= 200000 AND COUNT(*) >= 20
ORDER BY top5_pct DESC
LIMIT 40
```
הסף `COUNT(*) >= 20` מוציא מקבלים עם קומץ תורמים, שאצלם 100% הוא מובן מאליו. תורם שנכתב בשני סדרי שם נספר פעמיים ומוריד את האחוז.

## הרצף

1. בדוק טריות המקור, ובחר חתך: סוג בחירות, שנה, או שניהם
2. הרץ את שבעת הדפוסים
3. **סנן זיהויים שגויים ושמות נפוצים** - זה השלב שבו נופלים
4. לכל ליד שורד: `search_entity` על השם (האם יש לו ישות במודל, ומה עוד מחובר אליה), ואז `osint-donor-profile` על התורם, `osint-candidate-funding` על המקבל, `osint-donations-crossref` להצלבה
5. הצלב מול `wp_articles` ו-`knesset_mk_individuals`
6. דרג לפי סכום, רוחב פריסה, וזהות המקבל

## פורמט הפלט

```
## לידים מהמאגר - [חתך]

### ליד 1: [כותרת]
- **הדפוס:** [איזה מהשבעה]
- **התורם:** [שם + עיר + וריאנטים שאוחדו]
- **המקבלים:** []
- **הסכום:** [] ש"ח ב-[] תרומות, [טווח שנים]
- **למה זה מעניין:** []
- **עדיפות:** [גבוהה/בינונית/נמוכה] + מה הראיה החסרה
- **מה לאמת:** []
```

**מה לאמת לפני פרסום:** הפרסום המקורי אצל מבקר המדינה; זהות התורם; ותגובת הצדדים.

כתוב בעברית, בלי אימוג'ים, חד וקצר. תרומה חוקית ומדווחת אינה עבירה - הסיפור הוא בדפוס ובהקשר.
