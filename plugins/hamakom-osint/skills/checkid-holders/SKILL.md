---
name: checkid-holders
description: שליפת בעלי שליטה, מחזיקי מניות ודירקטורים של חברה פרטית מ-checkid.co.il, פר-ח.פ, דרך דפדפן אמיתי (השמות הגלויים חינם, לא הנסח בתשלום). הפעל כשדור נותן ח.פ או שם חברה ומבקש "מי הבעלים של", "מי מחזיק ב", "בעלי המניות של", "מי עומד מאחורי החברה X", "מי הדירקטורים", "checkid", או כשבתחקיר צריך לדעת מי שולט בחברה שאין עליה בעלי מניות בדאטה הפתוח. משלים את החוליה החסרה: רשם החברות (ica_companies ב-osint-db) לא מפרסם בעלי מניות. נקודתי בלבד - לא לבאלק.
---

# checkid — בעלי שליטה ומניות פר-ח.פ

## מה זה פותר

רשם החברות הפתוח (`ica_companies` ב-osint-db) נותן חברות, סטטוס, כתובת - אבל **לא בעלי מניות ולא דירקטורים**. הם קיימים רק בנסח בתשלום. `checkid.co.il` (של גיידליין גרופ) מציג **חינם בעמוד הציבורי** את שמות בעלי השליטה, מחזיקי המניות והדירקטורים - וזה מה שהסקיל הזה מחלץ, נקודתית, לתחקיר על חברה ספציפית.

## הגבול - חובה לקרוא

- **נקודתי בלבד, פר-ח.פ.** לא לרוץ בלולאה על אלפי חברות.
- **רק דרך דפדפן אמיתי** (ה-MCP browser / Claude in Chrome). checkid מגן על עמודי הפרטים באתגר Cloudflare מנוהל ("רק רגע...").
- **אסור לבנות סקריפט Playwright/headless שמהונדס לעבור את האתגר** - זו עקיפת זיהוי-בוטים. צפייה בעמוד ציבורי בדפדפן אמיתי = לגיטימי; כלי אוטומטי שמנצח את החסימה = לא. אם צריך אוטומציה אמיתית, המסלול הוא ה-API הרשמי בתשלום (`/exApi/v1/CheckId/GetData/CompanyDetailsDataModel`, ~2.5₪), שדורש חשבון+key שדור פותח.
- **המידע ציבורי אך לא מאומת** - checkid מסייגים ("יתכנו טעויות"). כל שם הוא **ליד לבדיקה מול הנסח הרשמי**, לא ממצא. אסור לפרסם "X הוא בעל השליטה" על סמך checkid בלבד.

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

### 6. הצלבה למאגר
עם השמות ביד, מצליבים ב-osint-db (Supabase, פרויקט Hamakom-Osint-DB): החברה ב-`ica_companies` (סטטוס, מפרה, שעבודים ב-`ica_changes`), והשם כתורם ב-`mevaker_donations`, כספק ב-`exemptions`/`mod_tenders`, או כמקבל ב-`budget_supports`. שם ← חברה ← מה עוד יש עליו.

## פלט לדור
טבלה קצרה: שם · תפקיד · (הצלבות אם נמצאו). בסוף: "מקור: <URL> · ציבורי ולא מאומת, ליד לבדיקה מול הנסח."
