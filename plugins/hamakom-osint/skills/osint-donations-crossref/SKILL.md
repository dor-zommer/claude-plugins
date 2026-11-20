---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__search_exemption_documents mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-donations-crossref
version: '1.3.0'
description: הצלבת תרומות בחירות מול כסף ציבורי ורגולציה מעל ה-osint-db - לוקח תורם או מקבל מ-mevaker_donations ומצליב אותו מול פטורים ממכרז (exemptions), התקשרויות ממשלתיות (budget_contracts), תמיכות (budget_supports), תוכניות בנייה (mavat_plans, yosh_plans), דוחות מבקר, חקיקה, הצבעות וארכיון האתר. זה מה שהופך תרומה לסיפור. הפעל כשדור כותב "תצליב את התרומה", "האם התורם קיבל משהו", "מה הוא קיבל בתמורה", "תרומות מול מכרזים", "תרם וגם זכה", "מה יש לו מול המדינה", או אחרי שסקיל תרומות אחר החזיר שם מעניין. כל פריט הוא ליד לבדיקה מול המקור הרשמי, לא ממצא מאומת. לתורם בודד ראה osint-donor-profile; למקבל ראה osint-candidate-funding; לחריגות רוחביות ראה osint-donation-patterns.
---

# osint-donations-crossref - מתרומה לסיפור

תרומה מדווחת אינה עבירה, ולכן לבדה היא לא כתבה. הסקיל הזה לוקח שם מ-`mevaker_donations` ומחפש **מה עוד יש לו מול המדינה**.

## חוקי המאגר - קרא לפני השאילתה הראשונה

- **כלי קודם, SQL אחר כך.** `search_entity` ו-`entity_profile` עושים את רוב ההצלבה בקריאה אחת (פירוט בשלב 2). `query_db` רק למה שהם לא מחזירים.
- את העמודות של טבלה נותן `describe_table`. לא מנחשים שם עמודה.
- הגבול הוא 10 שניות לשאילתה, 500 שורות ו-50 אלף תווים בפלט. שאילתה שחרגה בזמן אינה "אין תוצאות". `query_db` מחזיר 100 שורות כברירת מחדל, ו-`LIMIT` בתוך ה-SQL לא מעלה את התקרה הזו. ליותר שורות מעבירים לכלי את הפרמטר `limit` (עד 500).
- **כסף בהתקשרויות:** `budget_contracts.volume` הוא במטבע של `currency`, ושורה `superseded` הוחלפה בדיווח מאוחר יותר. כל סכום הוא `SUM(volume * FX)` עם `superseded IS NOT TRUE`, לפי הנוסחה בתיאור של `query_db` (ובסקיל osint-money). לעולם לא `SUM(volume)`.
- **פטורים:** בכל סכום של `exemptions.amount_ils` מסננים `amount_kind IS NULL`. שורה עם `amount_kind` (הקצאות ותמורות של רשות מקרקעי ישראל) היא כסף שהמדינה מקבלת, לא הוצאה.
- **שורה שירדה מהמקור** מסומנת ב-`gone_at` (כנסת) או ב-`removed_at` (רשם החברות). מסננים `IS NULL`.
- **טריות:** לפני "אין במאגר" על מאגר מסוים, בדוק ב-`scrape_runs` שהמקור שלו רץ:
- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.
  ```sql
  SELECT source, max(started_at) FROM scrape_runs
  WHERE status IN ('ok','warn')
    AND source IN ('mevaker_donations_scraper','exemptions','budget_contracts','budget_supports','amutot',
                   'mod_sapakim_scraper','mavat','yosh','knesset_bills','knesset_votes_v4_scraper',
                   'mevaker_library_collector','local_news_wp_api')
  GROUP BY 1
  ```
  מקור שלא רץ הוא "לא נאסף", לא "אין". (`mod_sapakim_scraper` מזין את `mod_tenders`, `mevaker_library_collector` את דוחות המבקר, ו-`local_news_wp_api` את `wp_articles`.)

מפת המאגר המלאה, שנבנית מהמאגר: `references/db-map.md` בתיקיית התוסף.

## מתי להפעיל

אחרי ש-`osint-donor-profile`, `osint-candidate-funding` או `osint-donation-patterns` העלו שם. או ישירות, כששם מהתחקיר צריך בדיקת "תרם וגם קיבל".

## הרצף

### 1. נקודת המוצא

בסס קודם את התרומה: מי, למי, כמה, מתי, ומאיזו עיר. **`donor_city` הוא מפתח ההצלבה** - הוא מקשר לרשות המקומית שבה עשויים להיות לו אינטרסים.

### 2. הצלבה מהירה - הכלים

`search_entity(name)` מחזיר בקריאה אחת התאמות מהמודל האחיד ומהטבלאות: פטורים, רשם החברות והשותפויות, נושאי משרה במאיה, תרומות, מבא"ת ויו"ש, החלטות ממשלה, חקיקה, דוחות המבקר וח"כים. כל טבלה מקבלת עד דקה; טבלה שנכשלה מסומנת בתשובה בשמה (`note` / `error`) ואינה "אין התאמות".

אחר כך `entity_profile(id)` על הישות הנכונה (או ישירות עם מספר תאגיד בן 9 ספרות): כל מה שמחובר אליה, לפי סוג קשר - התקשרויות ופטורים (כספק או כגוף מתקשר), תמיכות, תרומות, דירקטוריונים, הצבעות, תכנון ומסמכים - עם סכומים לפי תפקיד ומטבע, בלי שורות שהוחלפו, ועם `sourceUrl` לכל פריט. זה הכלי שעונה על "מה יש לו מול המדינה". ה-`id` לא נבחר בשבילך: כשחוזרים כמה מועמדים, בחר לפי מזהה קשיח, לא לפי שם.

לפטורים, `search_exemption_documents("שם התורם|שם החברה")` מחפש גם בתוך המסמכים המצורפים לפטור - שם שמופיע בבקשת הפטור או בפרוטוקול הוועדה ולא בשדה הספק.

### 3. מאגר-מאגר (כשצריך יותר ממה שהכלים החזירו)

| מאגר | איך נכנסים | מה מחפשים |
|---|---|---|
| `exemptions` | `supplier_ids = '<מספר תאגיד>'`, או `supplier_names LIKE` (מהיר, כשתי שניות) | פטור ממכרז. הסיפור הוא ההתקשרות - ספק, סכום, חזרתיות, מוסד - לא עצם הפטור |
| `budget_contracts` | **`entity_id = '<מספר תאגיד>'`** (מאונדקס). `supplier_name LIKE` עובד אבל סורק מיליון שורות ועומד על גבול 10 השניות | התקשרויות. את מספר התאגיד: `entity_profile`, או `ica_companies.company_id` לפי `name_he` (שם "בע"מ" כתוב "בע~מ") עם `removed_at IS NULL` |
| `budget_supports` | `recipient_entity_id = '<מזהה>'`. `recipient_entity_name LIKE` עובד (2-3 שניות) | תמיכות |
| `mavat_plans` / `yosh_plans` | `pl_name LIKE` או `search_entity`. **אין במאגר עמודת יזם**: שם היזם מופיע במסמכי התוכנית (`pl_url`), לא בשורה | תוכניות בנייה שהשם מופיע בשמן |
| `mevaker_chapters` / `mevaker_chapter_texts` | `main_audited` / `title LIKE` על `mevaker_chapters`; `text LIKE` על `mevaker_chapter_texts` רק **בחלון של שנה** (`library_pub_date`) - הטקסט המלא הוא 445 מיליון תווים בלי אינדקס, וחלון רחב חורג מ-10 השניות | פרקי דוחות המבקר. פרק סרוק או בלי קובץ אינו בטקסט - **אסור לטעון ש"הדוח לא מזכיר"** |
| `mod_tenders` | `title LIKE` | מכרזי ביטחון. אין בטבלה עמודת ספק או זוכה |
| `amutot` | `amuta_id`, או `name_he LIKE` | עמותות וחל"צים |
| `knesset_vote_options` (`kmmbr_id` הוא PersonID כטקסט, זהה ל-`mk_person_id`; תמיד עם `vote_id` ספציפי ו-`gone_at IS NULL`; ראה osint-knesset) / `knesset_bills` | לפי המקבל | איך הצביע בנושא שנוגע לתורם |
| `wp_articles` | `title` / `excerpt LIKE` | מה כבר פרסמנו. קטנה (6,008 כתבות) - OR ארוך מותר |

דוגמה - התקשרויות של התורם לפי מספר תאגיד:
```sql
SELECT b.publisher_name, b.supplier_name,
       b.volume * (CASE WHEN b.currency IS NULL OR b.currency = 'ILS' THEN 1.0 ELSE boi_fx_rate(b.currency, b.order_date) * (CASE b.currency WHEN 'JPY' THEN 100 ELSE 1 END) END) AS volume_ils,
       b.executed, b.purchase_method, b.order_date
FROM budget_contracts b
WHERE b.entity_id = '<מספר תאגיד>' AND b.superseded IS NOT TRUE
ORDER BY b.order_date DESC NULLS LAST
LIMIT 100
```

דוגמה - דוחות המבקר בשנה אחת:
```sql
SELECT chapter_key, title, library_pub_date, url
FROM mevaker_chapter_texts
WHERE library_pub_date >= '2024-01-01' AND library_pub_date < '2025-01-01'
  AND text LIKE '%<שם>%'
LIMIT 20
```

### 4. פרוטוקולי ועדות

במאגר: סדרי יום ומסמכי ישיבות דרך `osint-committees`. אם יש בידך גם תיקיית פרוטוקולים - סרוק לשם התורם ולשם החברה. **הופעת תורם כמוזמן בוועדה שהמקבל מנהל היא הממצא החזק ביותר שהצלבה כזו יכולה לייצר.** סנן זיהויים שגויים בקפדנות - מילים עבריות נפוצות מייצרות המון רעש.

### 5. ציר הזמן - הלב

בנה ציר אחד שמשלב תרומה, מינוי, פטור, מכרז, הצבעה ודיון. **הסמיכות בזמן היא הסיפור.** תרומה בינואר ופטור במרץ אינם ראיה לקשר - הם השאלה שיש לשאול, ולתת לצד השני להשיב. לתאריך הפטור השתמש ב-`pub_date_iso` (ולא ב-`pub_date`, שהוא DD/MM/YYYY ולא ניתן להשוואה), ולהתקשרות ב-`order_date`.

## מלכודות

- **חברה מול אדם.** תורם פרטי והתאגיד שבבעלותו הם שתי ישויות. חפש את שניהם, וציין במפורש מי מהם קיבל את הכסף הציבורי.
- **כיווניות.** תרומה זורמת מהתורם למקבל; כסף ציבורי זורם מהמדינה לתורם. נסח בבירור מי נתן למי.
- **קורלציה אינה סיבתיות.** ספק ממשלתי גדול תורם גם בלי תמורה. הסיפור בחריגות בהליך - נימוק שלא מתיישב עם ההתקשרות, מכרז תפור, שינוי רגולציה - לא בעצם קיומם של השניים. פטור ממכרז לגיטימי ברוב המקרים.
- **"קשור ל" אינו ממצא.** קשר ב-`entity_profile` אומר שהישות מופיעה ברשומה רשמית ליד הישות האחרת, ותו לא.

## פורמט הפלט

```
## הצלבה: <שם>

### ציר זמן
| תאריך | אירוע | מקור | סכום |

### ממצאים
| מאגר | פרט | סכום | קישור-מקור | ודאות זיהוי |

**מה זה כן אומר:** []
**מה זה לא אומר:** []
**מה לאמת:** []
**למי לפנות לתגובה:** [התורם / המקבל / הגוף הציבורי]
```

**מה לאמת לפני פרסום:** מבקר המדינה לתרומות, `detail_url` ב-mr.gov.il לפטורים, מפתח התקציב להתקשרויות - וזהות הישות מול רשם החברות.

כתוב בעברית, בלי אימוג'ים, חד וקצר. אל תציג סמיכות בזמן כקשר סיבתי.
