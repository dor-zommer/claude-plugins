---
allowed-tools: mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__query_db
name: checkid-holders
version: 1.2.0
description: >-
  שליפת בעלי שליטה, מחזיקי מניות ודירקטורים של חברה פרטית מ-checkid.co.il, פר-ח.פ, דרך דפדפן אמיתי (השמות הגלויים חינם, לא הנסח בתשלום). הפעל כשדור נותן ח.פ או שם חברה ומבקש "מי הבעלים של", "מי מחזיק ב", "בעלי המניות של", "מי עומד מאחורי החברה X", "מי הדירקטורים", "checkid", או כשבתחקיר צריך לדעת מי שולט בחברה שאין עליה בעלי מניות בדאטה הפתוח. משלים את החוליה החסרה: רשם החברות (ica_companies ב-osint-db) לא מפרסם בעלי מניות. אחרי השליפה מחבר את החברה ואת השמות לתיק הישות ב-osint-db (entity_profile לח.פ, search_entity לכל שם). נקודתי בלבד - לא לבאלק.
---

# checkid - בעלי שליטה ומניות פר-ח.פ

## מה זה פותר

רשם החברות הפתוח (`ica_companies` ב-osint-db) נותן חברות, סטטוס, כתובת - אבל **לא בעלי מניות ולא דירקטורים**. הם קיימים רק בנסח בתשלום. `checkid.co.il` (של גיידליין גרופ) מציג **חינם בעמוד הציבורי** את שמות בעלי השליטה, מחזיקי המניות והדירקטורים - וזה מה שהסקיל הזה מחלץ, נקודתית, לתחקיר על חברה ספציפית.

## הגבול - חובה לקרוא

- **נקודתי בלבד, פר-ח.פ.** לא לרוץ בלולאה על אלפי חברות.
- **רק דרך דפדפן אמיתי** (ה-MCP browser / Claude in Chrome). checkid מגן על עמודי הפרטים באתגר Cloudflare מנוהל ("רק רגע...").
- **אסור לבנות סקריפט Playwright/headless שמהונדס לעבור את האתגר** - זו עקיפת זיהוי-בוטים. צפייה בעמוד ציבורי בדפדפן אמיתי = לגיטימי; כלי אוטומטי שמנצח את החסימה = לא. אם צריך אוטומציה אמיתית, המסלול הוא ה-API הרשמי בתשלום (`/exApi/v1/CheckId/GetData/CompanyDetailsDataModel`, ~2.5₪), שדורש חשבון+key שדור פותח.
- **המידע ציבורי אך לא מאומת** - checkid מסייגים ("יתכנו טעויות"). כל שם הוא **ליד לבדיקה מול הנסח הרשמי**, לא ממצא. אסור לפרסם "X הוא בעל השליטה" על סמך checkid בלבד.

## חוקי המאגר כשמצליבים את החברה

- **כסף בהתקשרויות:** `budget_contracts.volume` הוא במטבע של `currency`, ושורה `superseded` הוחלפה בדיווח מאוחר יותר. כל סכום הוא `SUM(volume * FX)` עם `superseded IS NOT TRUE`, לפי הנוסחה בתיאור של `query_db`. לעולם לא `SUM(volume)`.
- **פטורים:** בכל סכום או דירוג של `exemptions.amount_ils` מסננים `amount_kind IS NULL`. שורה עם `amount_kind` (הקצאות ותמורות של רמ"י) היא תמורה שהמדינה מקבלת, לא הוצאה.
- **שורה שירדה מהמקור** מסומנת ב-`gone_at` (כנסת) או ב-`removed_at` (רשם החברות, מאיה). מסננים `IS NULL`.

## הצעדים (דרך ה-MCP browser)

### 1. פתיחת דפדפן ומעבר Cloudflare
`preview_start` עם `url: "https://www.checkid.co.il/"`. הבית עובר את האתגר הקל לבד. אם נתקע ב"רק רגע..." - `computer{action:"screenshot"}` לוודא, ולהמתין/לטעון שוב. **לא לפתור CAPTCHA ידנית אם מופיע כזה** - לעצור ולדווח.

### 2. איתור החברה לפי ח.פ (או שם)
מריצים את החיפוש הפנימי מאותו origin (עובר עם ה-cookie):
```js
fetch('/api/search-company', {
  method:'POST', headers:{'Content-Type':'application/json'},
  body: JSON.stringify({query: '<ח.פ או שם>'})
}).then(r=>r.text())
```
מחזיר `results[]` עם `id` (ח.פ), `nameHeb`, `nameEng`. בוחרים את זה ש-`id` תואם ל-ח.פ המבוקש.

### 3. מעבר לעמוד החברה
בונים את ה-slug מ-`nameHeb`: מרכאות כפולות (`"`/`״`) → `~`, כל רצף רווחים → מקף בודד. ה-URL:
```
https://www.checkid.co.il/company/<slug>-<ח.פ>
```
דוגמה: `nameHeb = ג'י די אס קריפטו טכנולוג'יז ישראל  בע"מ` (ח.פ 516716016) →
`/company/ג'י-די-אס-קריפטו-טכנולוג'יז-ישראל-בע~מ-516716016`.
`navigate` לשם. (העמוד מרונדר בשרת - Astro - השמות בתוך ה-HTML.)

### 4. חילוץ השמות (מובנה)
כל שם יושב ב-`props` של רכיב `astro-island` (עבור כפתור ההזמנה שלו), עם `name`, `section` (התפקיד), ו-`companyId`:
```js
(function(){var out=[];
document.querySelectorAll('astro-island[props]').forEach(function(el){
  try{var p=JSON.parse(el.getAttribute('props'));
    if(p.name&&p.name[1]) out.push({name:p.name[1],
      section:p.section?p.section[1]:null,
      companyId:p.companyId?p.companyId[1]:null});
  }catch(e){}});
// דדופ + רק החברה המבוקשת
var seen={},res=[];out.forEach(function(o){
  if(o.companyId&&String(o.companyId)!=='<ח.פ>')return;
  var k=o.name+'|'+o.section; if(!seen[k]){seen[k]=1;res.push(o);}});
return JSON.stringify(res);})()
```
אם ריק - לגזור מה-DOM של קטע "בעלי מניות ותפקידים" ישירות (get_page_text / read_page), ולתעד את תאריך העדכון ("מעודכן לתאריך ...").

### 5. מיפוי תפקידים ל-עברית
`ShareHolders`→בעל מניות · `Directors`→דירקטור · `OptionHolders`→מחזיק אופציות · `Signatories`→מורשה חתימה · `Officers`→נושא משרה · `Trustees`→נאמן.

### 6. חיבור לתיק הישות ב-osint-db
כלי קודם, SQL אחרון:

1. **החברה:** `entity_profile("<ח.פ>")` - מספר בן 9 ספרות מחזיר ישירות את הפרופיל של `il-reg.<ח.פ>`: מה שהמודל מקשר לחברה, מקובץ (פטורים והתקשרויות כספק, תמיכות, אירועי רשם החברות, נושאי משרה כשהם מקושרים), עם סכומים לפי מטבע ו-`sourceUrl`. לא מחברים בין מטבעות או בין תפקידים.
2. **כל שם שעלה ב-checkid:** `search_entity("<שם מלא>")`. אם חוזרת ישות מסוג אדם עם קשרים (`incoming_links`), `entity_profile("<id>")` שלה מראה כהונות, תרומות וקשרים אחרים. בחר לפי מספר הקשרים ולא לפי הסדר, והתאמת שם אינה זהות: אדם בשם זהה אינו בהכרח בעל המניות.
3. **רק מה שהכלים לא מחזירים - `query_db`:**
```sql
SELECT company_id, name_he, status, sub_status, company_type, is_violating, registration_date, city
FROM ica_companies WHERE company_id = <ח.פ>
```
```sql
SELECT request_type, status_date, lien_id FROM ica_changes
WHERE company_id = '<ח.פ>' ORDER BY status_date DESC NULLS LAST LIMIT 50
```
(`company_id` הוא מספר ב-`ica_companies` וטקסט ב-`ica_changes`.) התקשרויות מעבר לפרופיל - רק לפי `entity_id = '<ח.פ>'` (חיפוש לפי `supplier_name` נקטע; ראה `osint-money`). תמיכות לפי שם - תמיד עם `year = ...`, אחרת השאילתה נקטעת. חברה ציבורית - גם `maya_officers` לפי `company_name` (שם מקוצר; לא תמיד מקושר לחברה בפרופיל). תורם בשם - `mevaker_donations`, דרך `osint-donor-profile`.

**`mod_tenders` לא מתאים להצלבה הזו:** אלה הודעות מכרז, בלי עמודת זוכה או ספק.

לפני "אין עליה כלום במאגר": בדוק ב-`scrape_runs` שהמקור רץ (`SELECT source, max(started_at) FROM scrape_runs WHERE status IN ('ok','warn') AND source IN ('ica_scraper','maya_scraper','budget_contracts','exemptions') GROUP BY 1`).

לתיק מלא על החברה או על בעל השליטה - `osint-entity-dossier`.

### 7. פרטיות וזהירות משפטית
- **בעלי מניות הם לעיתים קרובות אנשים פרטיים.** שם שעלה ב-checkid לא מועבר ל-`population_search` או להעשרה אחרת בלי אישור של דור, ורק כשיש עניין ציבורי ברור (תפקיד ציבורי, כסף ציבורי, ניגוד עניינים).
- **ייחוס בכתבה:** "לפי נסח רשם החברות", לא "לפי checkid". לפני פרסום מאמתים מול נסח רשמי של רשם החברות.
- נקודתי בלבד, לפי תנאי השימוש של האתר. לא סריקה המונית.

## פלט לדור
טבלה קצרה: שם · תפקיד · (הצלבות אם נמצאו). בסוף: "מקור: <URL> · ציבורי ולא מאומת, ליד לבדיקה מול הנסח."
