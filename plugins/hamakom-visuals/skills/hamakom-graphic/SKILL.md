---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate
name: hamakom-graphic
description: >
  בונה את עמוד הגרפיקות הממותג של "המקום הכי חם בגיהנום" — 3 פורמטים בודדים
  לכתבה אחת, ישירות בתוך Figma. סקיל נפרד מ-hamakom-carousel (שמטפל בקרוסלות
  רב-שקפיות). זהו הסקיל לפוסט/תמונה בודדת — לא לקרוסלה.

  הפלט: עמוד Figma אחד עם 3 פריימים ממותגים של אותה כתבה —
  whatsapp-1080x1080 (ריבוע 1:1), instagram-1080x1350 (פיד 4:5),
  ig-story-1080x1920 (סטורי 9:16).
  כל פריים: תמונה full-bleed + gradient + label/title/lede/byline + לוגו
  במרכז התחתון + פס URL אדום. הכותרת = h1 verbatim של הכתבה.

  פלטה קנונית כברירת מחדל. פונטים NextExit + Narkiss Tam + Inter.
  עיצוב זהה לקאבר של hamakom-carousel.

  הפעל כשדור מבקש:
  - "תעשה גרפיקה לכתבה" / "גרפיקת כתבה" / "תכין לי את הגרפיקות לכתבה"
  - "גרפיקה לאינסטגרם / וואטסאפ / סטורי" / "תמונה לפוסט" / "גרפיקה ל-share"
  - URL של כתבה ב-ha-makom + בקשה לתמונה/גרפיקה לפוסט (לא קרוסלה)

  אם דור מבקש קרוסלה רב-שקפית / "carousel" — זה לא הסקיל הזה, אלא hamakom-carousel.
---

# גרפיקות כתבה — המקום הכי חם בגיהנום

בונה עמוד Figma אחד עם **3 פורמטים גרפיים ממותגים** של כתבה בודדת — לוואטסאפ/טלגרם,
פיד אינסטגרם, וסטורי. זה pattern קבוע ב-Figma שעובד היטב; אין צורך לייצר PNG
ב-Pillow. הפלט הוא קובץ Figma שדור עורך ומייצא ממנו.

**סקיל נפרד מ-hamakom-carousel.** הקרוסלה היא רב-שקפית (12-14 שקפים, פסקה
לשקף). כאן — גרפיקה בודדת ל-3 פלטפורמות. אם דור ביקש קרוסלה — זה הסקיל הלא נכון.

---

## חוק ברזל: הכותרת היא h1 verbatim — לא SEO title, לא קיצור

**הכותרת בכל 3 הגרפיקות חייבת להיות ה-h1 של הכתבה — מילה במילה.** הקטנת
fontSize מותרת; שינוי הטקסט אסור.

- ✗ **אסור:** להשתמש ב-`<title>` של ה-HTML או ב-`meta-og:title` (זה SEO title, לרוב שונה מה-h1 ומקוצר).
- ✗ **אסור:** "לחדד" / "לקצר" / "להמציא" כותרת חדשה. גם אם ה-h1 ארוך.
- ✗ **אסור:** להחליף את הכותרת בהאשטאג / שאלה רטורית / סלוגן.
- ✓ **מותר:** להקטין `titleSize` כדי שה-h1 המלא ייכנס.
- ✓ **מותר:** לפצל לשתי-שלוש שורות (Figma עושה את זה אוטומטית עם RTL+RIGHT align).

**איך לחלץ את ה-h1 נכון:** `webfetch` מחזיר את ה-h1 בתוך תוכן הכתבה
(אחרי הכרטיס של הקטגוריה, לפני ה-byline). זה השם המלא והרשמי של
הכתבה. ה-`meta-og:title` הוא לרוב הכותרת המקוצרת ל-social — אל
תשתמש בה.

דוגמה: כתבה על פארקים בערים מעורבות מ-`ha-makom.co.il/parkim-arim-meoravot`:
- ✓ h1 verbatim: "מה מחקר על 17 פארקים בערים מעורבות חושף על המרחב הציבורי בישראל"
- ✗ SEO title: "פארק רק ליהודים? מחקר חושף הדרה בערים מעורבות"

---

## 3 הפורמטים (תמיד, כל הכתבות)

| Frame name | מידות | יחס | שימוש |
|------------|-------|-----|--------|
| `whatsapp-1080x1080` | **1080×1080** | 1:1 | וואטסאפ / טלגרם (כאן ריבוע תקין) |
| `instagram-1080x1350` | **1080×1350** | 4:5 | פוסט פיד אינסטגרם (לא ריבוע) |
| `ig-story-1080x1920` | **1080×1920** | 9:16 | סטורי אינסטגרם |

**חוק קריטי על אינסטגרם:** פוסט פיד אינסטגרם הוא `1080×1350` (4:5) — **לא**
1080×1080. הריבוע הוא פורמט ישן שאינסטגרם כבר לא מעדיף. וואטסאפ נשאר ריבוע.

**רק 3 פורמטים.** אין hero לאתר, אין facebook, אין X. אם דור יבקש פורמט אחר —
לשאול, לא להמציא.

---

## פונטים — הגדרה מלאה

| שכבה | פונט | משקלים | שימוש |
|------|------|---------|--------|
| **תצוגה** | NextExit | Bold / Regular / Light | title, label "כנסת"/"תחקיר"/"דעה" |
| **גוף** | Narkiss Tam | Regular / Semibold | טקסט עברי (כשנדרש), credit לתמונה |
| **UI** | Inter | Bold / Regular / Light | label, lede, byline, URL בפס תחתון |

**הקבצים** ב-`assets/fonts/`:
- `NextExitBold.otf`
- `NextExitRegular.otf`
- `NextExitLight.otf`
- (Narkiss Tam מותקן במחשב של דור דרך Font Book — לא בתיקייה)

**התקנה חד-פעמית במחשב לפני הפעלה:**
```bash
cp <skill-dir>/assets/fonts/*.otf ~/Library/Fonts/
```

**אם Figma plugin עדיין מציג Inter** אחרי ההתקנה — צריך **restart מלא ל-Figma desktop**
(סגירה + פתיחה). plugin context שומר cache של רשימת הפונטים בפתיחה.

**Fallback בזמן ריצה:** הסקיל בודק `figma.listAvailableFontsAsync()` ואם
NextExit/Narkiss Tam לא מותקנים — נופל אוטומטית ל-Inter ומחזיר flag
`font_fallback_used: true` בפלט, כדי שדור ידע לעשות restart ולהפעיל שוב.

---

## פלטה — קנונית אלא אם הסיפור דורש אחרת

ברירת מחדל לתחקירים: `#141413` שחור + `#f4f1ec` קרם + `#f70d28` אדום + `#9e8e7c` אפור.
במקרה ספק — קנונית. סטייה מותרת **רק** כשהסיפור באמת דורש זאת — לרוב לא.

**טבלת השוואה — לא קטלוג שאסור לחרוג ממנו:**

| נושא | bg | fg | accent | תחושה |
|------|----|----|--------|--------|
| תחקיר/חקיקה (ברירת מחדל) | `#141413` שחור עמוק | `#f4f1ec` קרם | `#f70d28` אדום | אזעקה, חד |
| הומניטריות בעזה | `#1a1a2e` נייבי כהה | `#e8e4d6` קרם לח | `#c97064` חימר אדום | אבל, גרון תקוע |
| כסף ציבורי/שחיתות | `#2d2620` חום שרוף | `#f2c14e` ענבר זהב | `#d62828` אדום פצע | כעס, גניבה |
| משבר אקלים | `#0d1f1a` ירוק יער | `#e8f1ee` מנטה | `#ff7849` שמש קלויה | דחיפות |
| דעה — פוליטיקה | `#0f1620` כחול שינה | `#f7f3e8` ניר ישן | `#e76f51` אש קטנה | פרשנות שקטה |

**אסור תמיד:** פסטל-סוכר, corporate-tech (turquoise-OpenAI), צבעי-מותג מזוהים (ירוק WhatsApp), pastel.

**בדיקת contrast:** `fg` על `bg` חייב לעבור WCAG AA (4.5:1 ל-body).

צבעים מדויקים ב-`design-spec/tokens.md`.

---

## Layout pattern (זהה לכל 3 הפורמטים)

```
y=0       פס אדום 4px
y=4..H-4  תמונה (full-bleed, scaleMode FILL) + gradient overlay
y=textStart*H  אזור טקסט מתחיל (textStart ~0.45-0.55 לפי פורמט)
          label (Inter Bold, אדום, letter-spacing 4px)
          title (NextExit Bold, גדול, letter-spacing -2%, line-height 112%) — h1 verbatim
          lede  (Inter Regular, רוחב ~65% מהמסגרת, RTL right-aligned)
          byline (Inter Regular, אפור-credit)
          logo  (SVG ריבועי, ממורכז במרכז התחתון, לבן)
y=H-stripeH  פס URL אדום + "H A - M A K O M . C O . I L" (Inter Bold)
```

**שני מאפיינים קריטיים של הפורמט הזה:**
1. **לוגו במרכז התחתון** — לא בפינה ימין-עליון. הוא חלק מה-chrome התחתון, יחד עם פס ה-URL.
2. **Lede חובה** — משפט אחד שמסכם את הכתבה. רוחב צר מימין (~65%) שמשאיר נשימה משמאל.

---

## Gradient — קריטי שיהיה שקוף למעלה

```javascript
function gradientFor(textStart) {
  return {
    type: "GRADIENT_LINEAR",
    gradientTransform: [[0, 1, 0], [-1, 0, 1]],
    gradientStops: [
      { position: 0.00, color: { ...PALETTE.bg, a: 0.0 } },                    // שקוף
      { position: Math.max(0.01, textStart - 0.15), color: { ...PALETTE.bg, a: 0.0 } },  // שקוף
      { position: textStart, color: { ...PALETTE.bg, a: 0.78 } },              // מתחיל להחשיך
      { position: 1.00, color: { ...PALETTE.bg, a: 1.0 } },                    // שחור מלא
    ],
  };
}
```

הסיבה: התמונה צריכה להיראות בחצי העליון. אם הגרדיאנט מתחיל מ-0.2-0.5
alpha למעלה — התמונה נעלמת (במיוחד תמונות שכבר כהות מטבען).

---

## ⚠️ Gotcha: upload_assets לא עובד אוטומטית בעמוד שאינו currentPage

**הבעיה:** `upload_assets` עם `nodeId` בעמוד שאינו currentPage **לא תמיד
מחיל את התמונה כ-fill על ה-node**. ההעלאה מצליחה (`success: true` עם
`imageHash`), אבל ה-node נשאר עם fill מקורי (solid).

**הפתרון:** השתמש ב-`imageHash` ישירות ב-`use_figma` API:

```javascript
const HASH = "c4988773...";  // מ-upload_assets המוצלח
for (const id of photoNodeIds) {
  const node = await figma.getNodeByIdAsync(id);
  node.fills = [{ type: "IMAGE", scaleMode: "FILL", imageHash: HASH }];
}
```

---

## Per-format config (נסיון מוצלח — תואם הפרופורציות שדור אישר)

הערכים למטה הם לכותרת קצרה-בינונית, והם הפרופורציה הנכונה בין הפונט לגודל
הפריים (כפי שדור אישר על דוגמת דרעי/ביקורי משפחות). **לכותרת h1 ארוכה —
הקטן titleSize בלבד, לא את שאר היחסים.**

| frame | מידות | textStart | padX | labelSize | titleSize | ledeSize | bylineSize | stripeH | logoH |
|-------|-------|-----------|------|-----------|-----------|----------|-----------|---------|-------|
| whatsapp-1080x1080  | 1080×1080 | 0.45 | 60 | 24 | 60 | 22 | 22 | 50 | 64 |
| instagram-1080x1350 | 1080×1350 | 0.50 | 60 | 24 | 52 | 24 | 22 | 52 | 72 |
| ig-story-1080x1920  | 1080×1920 | 0.55 | 72 | 26 | 95 | 35 | 30 | 56 | 92 |

ראה `scripts/build_graphics_page.md` לתבנית JS מלאה.

---

## איסוף תמונות — סדר עדיפויות

**תמונה אחת לכל 3 הפורמטים** — אותה תמונת hero/og:image של הכתבה.

1. **ידני** — אם דור צירף תמונה לבקשה או שם תמונה בקנבס של הקובץ Figma → להשתמש בה.
2. **og:image של הכתבה** — ברירת המחדל.
3. **חילוץ candidate images מהגוף** — אם אין og:image טוב (לרוב תמונות flash90 לפי שמות הקבצים).
4. **WebSearch** — אם הכתבה דורשת תמונה ספציפית (דובר, מקום) שאין בכתבה (מקור מועדף: Wikipedia, פלאש 90, צילומי מסך מאתרי חדשות).
5. **Adobe Firefly** — fallback להמחשה (אם אין תמונה אמיתית). פרומפט קבוע:
   `dark cinematic Hebrew journalism aesthetic, no text, no faces, atmospheric`.

**credit חובה לכל תמונה** — text node קטן Narkiss Tam Light 22pt, opacity 0.85.

---

## נכסים קבועים (קריטי — לא לייצר מטקסט)

| נכס | נתיב | שימוש |
|-----|------|--------|
| לוגו ריבועי שחור (SVG) | `assets/logo-square-black.svg` | לוגו במרכז התחתון (לבן), כחלק מ-chrome התחתון |
| לוגו wordmark לבן (PNG) | `assets/logo-wordmark-white.png` | אופציונלי — אם פורמט דורש wordmark במקום ריבוע |

**חוק ברזל:** לעולם **לא** ליצור `figma.createText("המקום\nהכי חם\nבגיהנום")`
לבניית לוגו. תמיד `figma.createNodeFromSvg()` ל-SVG או `upload_assets()` ל-PNG.

**טיפ ל-SVG:** אחרי `createNodeFromSvg()` יש לאפס את ה-fill של ה-frame
העטיפה (לפעמים נטענת כ-solid white) ולעדכן fills רק על vector children:
```javascript
node.fills = [];
const recurse = (n) => {
  if (["VECTOR", "BOOLEAN_OPERATION", "POLYGON", "RECTANGLE"].includes(n.type)) {
    n.fills = [{ type: "SOLID", color: fillColor }];
  }
  if ("children" in n) n.children.forEach(recurse);
};
recurse(node);
```

---

## תהליך הפעלה (Claude reads this and follows)

1. קורא SKILL.md הזה.
2. (אופציונלי) קורא `design-spec/tokens.md` לפרטי צבע מדויקים.
3. שולף את הכתבה (WebFetch / defuddle) ומחלץ:
   - **h1 verbatim** (הכותרת — לא og:title!)
   - og:image (התמונה)
   - byline
   - קטגוריה (label)
   - משפט lede אחד שמסכם את הכתבה
4. בוחר/מאתר את התמונה (ראה "איסוף תמונות").
5. בוחר פלטה — קנונית אלא אם הנושא דורש סטייה (ראה טבלת הפלטה).
6. קורא ל-MCP figma `create_new_file` editorType=design + planKey.
7. **קורא ל-`use_figma` עם הקוד מ-`scripts/build_graphics_page.md`** כדי לבנות
   את 3 הפריימים: whatsapp-1080x1080, instagram-1080x1350, ig-story-1080x1920.
   לכל פריים: rect placeholder לתמונה עם node.id שמור.
8. מעלה את התמונה (`upload_assets`) ושומר את ה-`imageHash`.
9. **מחיל את אותה תמונה על כל 3 הפלייסהולדרים — ישירות עם `imageHash`**
   (ראה "Gotcha" לעיל), לא דרך `upload_assets` per-node.
10. screenshot של 3 הפריימים ל-QA חזותי.
11. מחזיר לדור: URL לקובץ Figma, רשימת 3 הפריימים, התמונה+credit,
    flag `font_fallback_used` אם נפל ל-Inter.

---

## QA חזותי לפני מסירה

לפני שמחזירים URL לדור — screenshot של כל 3 הפריימים, ולוודא:

- ☐ **הכותרת בכל 3 הגרפיקות = h1 verbatim** (לא ה-`og:title`, לא קיצור, לא המצאה)
- ☐ כל 3 הפריימים קיימים: whatsapp-1080x1080, instagram-1080x1350, ig-story-1080x1920
- ☐ **התמונה מופיעה בכל 3 הפריימים** (לא שחור — בדוק אם `upload_assets` לא הפעיל; אם כן, החל ידנית עם imageHash)
- ☐ **גרדיאנט שקוף למעלה** בכל הפריימים (התמונה נראית, לא מוסתרת)
- ☐ **לוגו במרכז התחתון** של כל פריים (לא בפינה ימין-עליון)
- ☐ אינסטגרם הוא 4:5 (1080×1350), לא ריבוע
- ☐ label + lede + byline במקום
- ☐ פס URL אדום בתחתית

---

## כללים כלליים

1. **אין אימוג'ים** באף גרפיקה.
2. **כל תמונה — credit** (אפילו אם זה רק "Firefly").
3. **לא מייצרים PNG ב-Pillow.** הפלט הוא Figma file. דור עורך, ואז מייצא PNG/JPG דרך Figma.
4. **זה לא קרוסלה.** אם דור רוצה רב-שקפי — hamakom-carousel.

---

## CLI / שימוש מתוך Claude

קלט אופייני מדור:
```
תעשה לי את הגרפיקות לכתבה הזו: https://www.ha-makom.co.il/<slug>/
```

או:
```
גרפיקה לאינסטגרם + סטורי לכתבה הזו: <PASTE / URL>
תמונה: /path/to/photo.jpg
```

---

## פלט אופייני

```
קובץ Figma: https://www.figma.com/design/<KEY>
פונט בשימוש: NextExit + Narkiss Tam (font_fallback_used: false)

Graphics — פורמטים (3 פריימים)
  whatsapp-1080x1080     (ריבוע 1:1)
  instagram-1080x1350    (4:5 — לא ריבוע)
  ig-story-1080x1920     (9:16)

תמונה: og:image / פלאש 90 בכל 3 הגרפיקות + credit
```
