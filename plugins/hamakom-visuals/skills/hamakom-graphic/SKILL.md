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
  כל פריים: תמונה full-bleed + gradient דיו + label/title/lede/byline + לוגו
  לבן במרכז התחתון + פס-חתימה טריקולור. הכותרת = h1 verbatim של הכתבה.

  פלטה: HaMakom DS 2026 — שנהב/דיו/טרקוטה (טריו +מרווה +אברש). פונטים
  Suez One + IBM Plex Sans Hebrew. עיצוב זהה לקאבר של hamakom-carousel.
  מקור-אמת: `../../design-system/HAMAKOM-DS-2026.md`.

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
| **תצוגה** | **Suez One** | Regular | title (h1 verbatim), ציטוטים |
| **גוף / UI** | **IBM Plex Sans Hebrew** | Regular / Medium / SemiBold / Bold | label, lede, byline, credit, url |

שני הפונטים ב-Google Fonts. התקנה חד-פעמית (אין צורך ב-restart):
```bash
mkdir -p /tmp/hmfonts && cd /tmp/hmfonts
curl -sL "https://github.com/google/fonts/raw/main/ofl/suezone/SuezOne-Regular.ttf" -o SuezOne-Regular.ttf
B="https://github.com/google/fonts/raw/main/ofl/ibmplexsanshebrew"
for w in Regular Medium SemiBold Bold; do curl -sL "$B/IBMPlexSansHebrew-$w.ttf" -o "IBMPlexSansHebrew-$w.ttf"; done
cp *.ttf ~/Library/Fonts/
```

**Fallback בזמן ריצה:** הסקיל בודק `figma.listAvailableFontsAsync()` ואם
Suez One / IBM Plex Sans Hebrew חסרים — נופל ל-Inter ומחזיר `font_fallback_used: true`.

---

## פלטה — HaMakom DS 2026 (קבועה)

הגרפיקה היא **cover-style**: תמונה full-bleed + gradient דיו + טקסט לבן.

| Token | Hex | תפקיד |
|-------|-----|--------|
| דיו `--ink` | `#141413` | gradient + רקע |
| לבן | `#ffffff` | כותרת (Suez One), לוגו |
| טרקוטה-בהיר | `#E8906F` | label קטגוריה (על כהה) |
| `--on-dark-soft` | `#b7b5ac` | lede + byline |
| חתימה | טרקוטה `#D97757` · מרווה `#788C5D` · אברש `#8E6FA8` | פס-חתימה למעלה+למטה |

**אסור:** אדום `#f70d28` / ענבר `#d4a13a` (פלטה ישנה — בוטלה), pastel,
corporate-tech (turquoise-OpenAI), צבעי-ספונסר (ירוק WhatsApp).

מספרים מדויקים (Figma RGB) ב-`../../design-system/HAMAKOM-DS-2026.md`.

---

## Layout pattern (זהה לכל 3 הפורמטים)

```
y=0       פס-חתימה טריקולור 8px (טרקוטה·מרווה·אברש)
y=0..H    תמונה (full-bleed, scaleMode FILL) + gradient דיו overlay
y=textStart*H  אזור טקסט מתחיל (textStart ~0.45-0.55 לפי פורמט)
          label (IBM Plex SemiBold, טרקוטה-בהיר #E8906F, letter-spacing 2)
          title (Suez One, גדול, line-height 108%) — h1 verbatim
          lede  (IBM Plex Regular, רוחב ~68% מהמסגרת, RTL right-aligned)
          byline (IBM Plex Medium, on-dark-soft)
          logo  (SVG ריבועי, ממורכז במרכז התחתון, לבן)
y=H-sigH  פס-חתימה טריקולור תחתון + "HA-MAKOM.CO.IL" (IBM Plex SemiBold) מתחתיו
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
      { position: 0.00, color: { ...C.ink, a: 0.0 } },                    // שקוף
      { position: Math.max(0.01, textStart - 0.15), color: { ...C.ink, a: 0.0 } },  // שקוף
      { position: textStart, color: { ...C.ink, a: 0.8 } },               // מתחיל להחשיך
      { position: 1.00, color: { ...C.ink, a: 1.0 } },                    // דיו מלא
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

| frame | מידות | textStart | padX | labelSize | titleSize (Suez One) | ledeSize | bylineSize | sigH | logoH |
|-------|-------|-----------|------|-----------|-----------|----------|-----------|------|-------|
| whatsapp-1080x1080  | 1080×1080 | 0.45 | 64 | 24 | 56 | 22 | 22 | 8 | 60 |
| instagram-1080x1350 | 1080×1350 | 0.50 | 64 | 25 | 56 | 24 | 23 | 8 | 64 |
| ig-story-1080x1920  | 1080×1920 | 0.55 | 72 | 28 | 80 | 32 | 28 | 8 | 84 |

(`sigH` = גובה פס-החתימה התחתון; ה-url יושב מתחתיו.)

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

**credit חובה לכל תמונה** — text node קטן IBM Plex Sans Hebrew Regular 18pt, לבן opacity 0.6.

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
2. **קורא `../../design-system/HAMAKOM-DS-2026.md`** (מקור-אמת — צבעים, פונטים, חתימה).
3. שולף את הכתבה (WebFetch / defuddle) ומחלץ:
   - **h1 verbatim** (הכותרת — לא og:title!)
   - og:image (התמונה)
   - byline
   - קטגוריה (label)
   - משפט lede אחד שמסכם את הכתבה
4. בוחר/מאתר את התמונה (ראה "איסוף תמונות").
5. פלטה קבועה — HaMakom DS 2026 (שנהב/דיו/טרקוטה). אין בחירת פלטה.
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
- ☐ **לוגו לבן במרכז התחתון** של כל פריים (לא בפינה)
- ☐ אינסטגרם הוא 4:5 (1080×1350), לא ריבוע
- ☐ label טרקוטה + lede + byline במקום; כותרת Suez One (לא NextExit)
- ☐ פס-חתימה טריקולור למעלה+למטה (לא פס אדום); url מתחת לפס התחתון

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
פלטה: שנהב/דיו/טרקוטה · פונטים: Suez One + IBM Plex Sans Hebrew (font_fallback_used: false)

Graphics — פורמטים (3 פריימים)
  whatsapp-1080x1080     (ריבוע 1:1)
  instagram-1080x1350    (4:5 — לא ריבוע)
  ig-story-1080x1920     (9:16)

תמונה: og:image / פלאש 90 בכל 3 הגרפיקות + credit
```
