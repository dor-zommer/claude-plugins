---
allowed-tools: Read Write Edit Bash Grep Glob WebSearch WebFetch TaskCreate TaskUpdate
name: hamakom-update-card
description: >-
  בונה כרטיס עדכון חי של "המקום הכי חם בגיהנום" ב-Figma — 3 פורמטים
  (update-whatsapp-1080x1080, update-instagram-1080x1350, update-story-1080x1920)
  עם תמונה full-bleed, pill טרקוטה, שורת עדכון חדה, שורת משנה, byline בטרקוטה
  ווורדמרק "עיתונות עצמאית. בלי פחד". הפעל כשדור אומר "כרטיס עדכון",
  "עדכון לרשתות", "כרטיס חי", "יום X למצור/למבצע", "תעשה כזה" עם רפרנס של הכרטיס,
  או כשצריך לדווח התפתחות בסיפור מתגלגל שאין לה עדיין כתבה חדשה.
  **זה לא גרפיקת כתבה** — לכותרת h1 של כתבה שפורסמה ראה hamakom-graphic;
  לקרוסלה רב-שקפית ראה hamakom-carousel.
---

# כרטיס עדכון חי — המקום הכי חם בגיהנום

בונה עמוד Figma אחד עם **3 פורמטים** של כרטיס עדכון לסיפור מתגלגל:
`update-whatsapp-1080x1080` · `update-instagram-1080x1350` · `update-story-1080x1920`.

התוצר הוא קובץ Figma שדור עורך ומייצא ממנו. **לא מייצרים PNG ב-Pillow.**

---

## חוק 0 — זה לא `hamakom-graphic`

שני הטמפלייטים מתקיימים במקביל ואסור לערבב ביניהם. הבחנה עורכית, לא טעם:

| | `hamakom-graphic` | **כרטיס עדכון (כאן)** |
|---|---|---|
| מתי | כתבה פורסמה באתר | התפתחות בסיפור מתגלגל, לפני/בלי כתבה חדשה |
| כותרת | **h1 verbatim** — אסור לשנות | **שורת עדכון שנכתבת מחדש**, חדה וקצרה |
| קיקר | אסור | **pill טרקוטה** ("עכשיו ב<מקום>") |
| שורת משנה | אסורה | **קיימת** — סטטוס במשפט אחד |
| byline | ink-soft `#6b6a63` | **טרקוטה `#D97757`** |
| חתימה תחתונה | לוגו ריבועי + `HA-MAKOM.CO.IL` | **וורדמרק + "עיתונות עצמאית. בלי פחד"** |

אם דור ביקש גרפיקה לכתבה שפורסמה — זה הסקיל הלא נכון.

---

## ⚠️ אזהרה עורכית — הכותרת כאן אינה מצוטטת

בניגוד לכל שאר סקילי הוויז'ואלס, הכותרת בכרטיס הזה **נכתבת**, לא מצוטטת. לכן:

1. **כל טענה בכרטיס חייבת מקור.** אם היא לא מגובה בכתבה קיימת של המקום, לומר
   את זה במפורש במסירה: "השורה הזו לא מגובה בכתבה — לא אימתתי אותה."
2. **בלי דרמטיזציה.** "האמבולנס בדרכו לבתים הנצורים" — עובדתי. לא "הרגע הדרמטי
   שבו...". זה גוף תקשורת, לא קרקס.
3. **תיאור שלילי של אדם מזוהה — רק כציטוט מיוחס במפורש לדובר.**
4. **מספרים וסטטוסים** ("יום שלישי למצור", "שלוש משפחות") נספרים מהמקור, לא
   מהזיכרון. יום ראשון ← שני ← שלישי = היום השלישי.

---

## ארבעת שדות הטקסט

```
pill    "עכשיו בקוסרא"                    ← מיקום/הקשר, 2-3 מילים. לא כותרת.
head    "האמבולנס בדרכו לבתים הנצורים"     ← ההתפתחות. שורה אחת, ~28-34 תווים.
sub     "יום שלישי למצור. שלוש משפחות      ← סטטוס. עד ~65 תווים.
         עדיין כלואות, המתנחלים עדיין בשטח"
byline  "סיון תהל | חדשות"                 ← שם | סוג. בלי "מאת:".
```

**`head` בשורה אחת.** אם הוא נשבר לשתיים — לקצר את הטקסט, לא להקטין את הפונט.
הכוח של הכרטיס הוא בשורה אחת שנקראת בחצי שנייה.

---

## פלטה ופונטים — HaMakom DS 2026

מקור-אמת: `../../design-system/HAMAKOM-DS-2026.md`.

| תפקיד | ערך |
|---|---|
| דיו `--ink` | `#141413` ← Figma `{r:0.0784,g:0.0784,b:0.0745}` |
| טרקוטה `--terra` | `#D97757` ← `{r:0.851,g:0.4667,b:0.3412}` — pill + byline |
| מרווה `--sage` | `#788C5D` ← `{r:0.4706,g:0.549,b:0.3647}` |
| אברש `--heather` | `#8E6FA8` ← `{r:0.5569,g:0.4353,b:0.6588}` |
| לבן | `#ffffff` — כותרת, טקסט ה-pill, משנה (אטימות 0.93) |

| שכבה | פונט |
|---|---|
| `head` | **Publico Headline Hebrew Extrabold** |
| `sub` | Graphik HLAR Regular |
| `pill` / `byline` | Graphik HLAR Medium |

**אסור:** אדום `#f70d28`, ענבר `#d4a13a`, NextExit, Narkiss (פלטות/פונטים שבוטלו).

### resolver עם fallback ל-TRIAL

Figma מגיש לפעמים רשימת פונטים ישנה שבה הקבצים המורשים חסרים ורק ה-TRIAL זמין.
נפילה ל-TRIAL כמעט בלתי מורגשת; **נפילה ל-Inter היא כשל** ששובר את הזהות.

```javascript
const fonts = await figma.listAvailableFontsAsync();
const AV = new Set(fonts.map(f => f.fontName.family + "||" + f.fontName.style));
const FB = {family:"Inter", style:"Regular"};
const pick = c => c.find(x => AV.has(x.family+"||"+x.style)) || c[c.length-1] || FB;
const ROLE = {
  dispXB: pick([{family:"Publico Headline Hebrew",style:"Extrabold"},
                {family:"Publico Headline Hebrew Exbold",style:"Regular"},
                {family:"Publico Headline Hebrew TRIAL",style:"Extrabold"}, FB]),
  reg:    pick([{family:"Graphik HLAR",style:"Regular"},
                {family:"Graphik HLAR TRIAL",style:"Regular"}, FB]),
  med:    pick([{family:"Graphik HLAR",style:"Medium"},
                {family:"Graphik HLAR Medium",style:"Regular"},
                {family:"Graphik HLAR TRIAL",style:"Medium"}, FB]),
};
for (const r of Object.values(ROLE)) { try { await figma.loadFontAsync(r); } catch(e){} }
const fontFallback = Object.values(ROLE).some(r => r.family === "Inter");   // כשל
const trialCuts    = Object.values(ROLE).some(r => /TRIAL/.test(r.family)); // לציין בלבד
```

התקנה חד-פעמית של הפונטים:
```bash
DS=$(ls -d ~/.claude/plugins/cache/hamakom-plugins/hamakom-visuals/*/design-system 2>/dev/null | sort -V | tail -1)
DS=${DS:-plugins/hamakom-visuals/design-system}
cp "$DS"/assets/fonts/*.otf "$DS"/assets/fonts/*.ttf ~/Library/Fonts/
```

---

## נכס קבוע — הוורדמרק

```bash
DS=$(ls -d ~/.claude/plugins/cache/hamakom-plugins/hamakom-visuals/*/design-system 2>/dev/null | sort -V | tail -1)
DS=${DS:-plugins/hamakom-visuals/design-system}
WORDMARK="$DS/assets/logo/logo-wordmark-white.png"    # 600×193, יחס 3.109
```

הקובץ הזה **כבר מכיל** את שתי השורות — "המקום הכי חם בגיהנום" + "עיתונות עצמאית.
בלי פחד". מעלים אותו כתמונה ומציבים כ-`scaleMode:"FIT"`.

**חוק ברזל:** לעולם לא `figma.createText("המקום הכי חם בגיהנום")` לבניית הלוגו.

---

## מבנה הכרטיס — מלמטה למעלה

הטקסט מחושב **מהוורדמרק כלפי מעלה**, כדי שגוש הטקסט יישאר נמוך והתמונה תישאר
גלויה. לא מציבים y קבועים לכותרת.

```
photo         full-bleed, scaleMode FILL
gradient      דיו — שקוף למעלה, מתעבה מעל ה-pill (מוזרק ב-insertChild(1))
                 ↑ מחושב אחרון, לפי מיקום ה-pill בפועל
pill          טרקוטה, radius = h/2, צמוד לימין ב-padX
head          Publico Extrabold לבן, RIGHT, lh 112%
sub           Graphik Regular לבן 0.93, RIGHT, lh 142%
byline        Graphik Medium טרקוטה, RIGHT
wordmark      FIT, ממורכז אופקית, תחתית ב-wmBottom
sig           פס-חתימה טריקולור 6px בקצה התחתון (אברש · מרווה · טרקוטה, שמאל←ימין)
```

### Per-format config (נמדד ואומת מול הרפרנס של דור, 11.08.2026)

| | 1080×1080 | 1080×1350 | 1080×1920 |
|---|---|---|---|
| `padX` | 56 | 56 | 60 |
| `wmW` | 330 | 330 | 370 |
| `wmBottom` | 1032 | 1300 | **1700** |
| `bylineSize` / `bylineGap` | 26 / 34 | 26 / 34 | 30 / 40 |
| `subSize` / `subGap` | 34 / 20 | 34 / 20 | 38 / 24 |
| `headSize` / `headGap` | 62 / 20 | 62 / 20 | 70 / 24 |
| `pillSize` / `pillH` / `pillPadH` / `pillGap` | 26 / 52 / 26 / 22 | 26 / 52 / 26 / 22 | 30 / 60 / 30 / 26 |
| `sigH` | 6 | 6 | 6 |

**`wmBottom` בסטורי הוא 1700 ולא 1870** — 250px התחתונים מוסתרים ע"י ה-UI של
אינסטגרם וטיקטוק. גוש הטקסט כולו חייב לשבת מעל הקו הזה.

### גרדיאנט — מעוגן ב-pill

```javascript
const anchor = pill.y / H;
const p2 = Math.max(0.01, anchor - 0.22);
const p3 = Math.max(p2 + 0.01, anchor + 0.02);
grad.fills = [{ type:"GRADIENT_LINEAR", gradientTransform:[[0,1,0],[-1,0,1]], gradientStops:[
  { position:0.0, color:{...C.ink, a:0.0} },
  { position:p2,  color:{...C.ink, a:0.0} },
  { position:p3,  color:{...C.ink, a:0.78} },
  { position:1.0, color:{...C.ink, a:1.0} },
]}];
```

הרמפה ארוכה (22% מגובה הפריים) בכוונה — מעבר חד יוצר "קו" גלוי לרוחב התמונה.

---

## ⚠️ שלוש מלכודות שיפילו אותך

### 1. רוחב ה-pill — למדוד את הטקסט, לא לנחש

`createText` + `textAutoResize="HEIGHT"` + `resize(600, …)` מחזיר `width === 600`,
ואז ה-pill יוצא ברוחב חצי פריים. חייבים למדוד ברוחב טבעי קודם:

```javascript
pillTxt.textAutoResize = "WIDTH_AND_HEIGHT";       // עכשיו width הוא הרוחב האמיתי
const pillW = Math.ceil(pillTxt.width) + 2 * S.pillPadH;
pill.resize(pillW, S.pillH);
pill.x = W - S.padX - pillW;
pillTxt.textAutoResize = "HEIGHT";
pillTxt.resize(pillW, pillTxt.height);
pillTxt.textAlignHorizontal = "CENTER";
pillTxt.x = pill.x;
pillTxt.y = Math.round(pill.y + (S.pillH - pillTxt.height) / 2);
```

### 2. `upload_assets` משאיר פריימים יתומים ב-Page 1

העלאה **בלי** `nodeId` יוצרת פריים תמונה בעמוד הנוכחי ומחזירה `imageHash`.
משתמשים ב-hash ישירות בסקריפט, ובסוף מנקים:

```javascript
const first = figma.root.children[0];
await figma.setCurrentPageAsync(first);
for (const c of [...first.children]) c.remove();
```

(עם `nodeId` בעמוד שאינו currentPage ההעלאה מחזירה `success:true` אבל **לא** מחילה
את ה-fill — אותה מלכודת שמתועדת ב-`hamakom-graphic`.)

### 3. `use_figma` דורש `description`

בלי הפרמטר הזה הקריאה נופלת ב-validation error לפני שהיא בכלל רצה.

---

## הכנת התמונה — עיגון הנושא בשליש העליון

**זה השלב שקובע אם הכרטיס עובד.** הנושא (רכבים, אנשים, מבנה) חייב לשבת בשליש
העליון, והקרקע/הרקע הריקים מתחתיו נושאים את הטקסט. חיתוך מרכזי אוטומטי של Figma
ישים את הנושא באמצע והטקסט יכסה אותו.

לכן חותכים **מראש, פר-פורמט**, ומעלים שלוש תמונות נפרדות —
`scripts/crop_for_formats.py`:

```bash
python3 scripts/crop_for_formats.py base.png <YV> [outdir]
# YV = מרכז הנושא בפיקסלים של המקור (נמדד בעין מפריים)
```

- **פריים מסרטון:** `ffmpeg -ss <t> -i clip.mp4 -frames:v 1 base.png`, אחרי שסורקים
  רשת פריימים (`fps=1/N,scale=300:-2,tile=3x3`) ובוחרים את הרגע.
- **מקור קטן מ-1080 רוחב** (למשל וידאו וואטסאפ 464×832) — לציין לדור שהסטורי ייצא
  רך. הגדלה לא מוסיפה פרטים.
- **קרדיט צילום** אינו חלק מהטמפלייט הזה. אם התמונה דורשת קרדיט — לשאול את דור
  איפה להציב אותו, לא להמציא מיקום.

---

## תהליך ההפעלה

1. קורא את הסקיל הזה ואת `../../design-system/HAMAKOM-DS-2026.md`.
2. אוסף את ארבעת שדות הטקסט. אם דור לא נתן — **לשאול**, לא להמציא. אם יש כתבה
   קיימת, לגזור ממנה ולציין מאיזו פסקה.
3. בוחר תמונה ומכין 3 חיתוכים (`scripts/crop_for_formats.py`). מדווח מידות מקור.
4. `whoami` ← `planKey` ← `create_new_file` editorType=`design`.
5. `upload_assets count=4` (sq, feed, story, wordmark) ← POST כל קובץ ל-submitUrl
   שלו (`curl -F "file=@…"`) ← שומר את ארבעת ה-hashes.
6. `use_figma` — בונה עמוד `Update card — 3 פורמטים` עם 3 הפריימים
   (ראה `scripts/build_update_card.md`).
7. תיקון ה-pill (מלכודת 1) — אפשר באותה קריאה או בקריאה שנייה.
8. `get_screenshot` על שלושת הפריימים ל-QA חזותי.
9. מנקה את Page 1 (מלכודת 2).
10. מחזיר לדור: URL, שמות הפריימים, מקור התמונה ומידותיה,
    `font_fallback_used` / `trial_cuts_used`, וכל טענה שלא אומתה מול כתבה.

---

## QA לפני מסירה

- ☐ **ה-pill צמוד לטקסט שלו** ולא נמתח על חצי פריים (מלכודת 1)
- ☐ `head` בשורה **אחת** בשלושת הפורמטים
- ☐ הטקסט זהה תו-בתו בשלושת הפריימים — בדיקה תכנותית, לא בעין
- ☐ הנושא בתמונה בשליש העליון; הטקסט על רקע ריק
- ☐ ~55-60% העליונים של התמונה גלויים; אין "קו" חד בגרדיאנט
- ☐ בסטורי: תחתית הוורדמרק ≤ 1700
- ☐ byline בטרקוטה, בפורמט `שם | סוג`, בלי "מאת:"
- ☐ וורדמרק ממורכז — **מהקובץ, לא מטקסט**
- ☐ פס-חתימה טריקולור תחתון יחיד 6px; אין פס עליון
- ☐ `font_fallback_used: false` (TRIAL בסדר, Inter לא)
- ☐ Page 1 נוקה מפריימי ההעלאה
- ☐ אין אימוג'ים באף פורמט

---

## כשדור עורך פריים אחד ומבקש להחיל על השאר

1. **קרא לפני שאתה כותב** — משוך את כל העץ של הפריים הערוך: fonts, sizes, x/y,
   fills, imageHash, עצירות הגרדיאנט, ומה נמחק. מה שנעלם הוא החלטה, לא תקלה.
2. **אל תיגע בפריים שלו.** מעדכנים רק את האחרים. משהו נראה שגוי — אומרים,
   לא מתקנים.
3. **תרגם, אל תעתיק בעיוורון.** מה שתלוי ברוחב (padX, גודל כותרת) מועתק כמו שהוא;
   מה שתלוי בגובה המסגרת (wmBottom, מרווחים) מקבל סקיילינג ביחס שבטבלת הקונפיג.
4. **הגרדיאנט מתורגם ביחסים** — חלץ את היחס בין העצירות שלו למיקום ה-pill שלו,
   והחל את אותו יחס בפריימים האחרים.
5. **דווח מה נגזר ולמה**, במיוחד איפה לא יכולת להעתיק ישירות.
