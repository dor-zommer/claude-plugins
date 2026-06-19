# Design Tokens — Carousel System

**מסמך זה מגדיר ערכים קבועים** (פונטים, מידות, chrome, אפקטים) שאינם
משתנים בין קרוסלות. **הפלטה — לא קבועה.** ראה סעיף "פלטה דינמית" למטה.

---

## פלטה דינמית (חוק ברזל 0b)

**אין פלטה קבועה למותג.** כל קרוסלה בוחרת פלטה חדשה שמתאימה לנושא,
הטון, והמצב הרגשי של הסיפור. ראה SKILL.md → "חוק 0b" לתהליך הבחירה.

**מבנה הפלטה** (4 צבעים שכל קרוסלה ממלאת):

| Token | תפקיד | דוגמה |
|-------|-------|--------|
| `--bg` | רקע דומיננטי | `#141413` שחור עמוק, `#1a1a2e` נייבי, `#2d2620` חום שרוף |
| `--fg` | טקסט ראשי (חייב contrast ≥ 4.5:1 עם bg) | `#f5f3ef` לבן שבור, `#e8e4d6` קרם, `#f2c14e` ענבר זהב |
| `--accent` | הדגשה (CTA bg, מספור, label, divider) | `#f70d28` אדום דם, `#c97064` חימר, `#ff7849` קלוי |
| `--muted` (אופציונלי) | טקסט עזר, ייחוסים, credit | `#a8a39b` אפור חם, `#8a7f72` חימר עמום |

**בדיקת contrast** — חובה לפני התחלת בנייה (WebAIM Contrast Checker או כלי מקביל). fg על bg = AA (4.5:1) ל-body, AAA (7:1) מועדף לכותרות.

**אסור:**
- Pastel / סוכר / corporate-tech
- מותגי-ספונסר (turquoise OpenAI, ירוק WhatsApp, סגול Twitch...)
- צבעים שלא הוחלטו בכוונה (אל "פשוט שנייצא, אדום")

**נשמר בפלט הסופי** — שורה ב-summary שמתעדת את הפלטה שנבחרה ולמה.

---

## Typography

**שלוש שכבות פונטים — שילוב חובה:**

| תפקיד | פונט | משקלים | דוגמת שימוש |
|-------|------|---------|--------------|
| **תצוגה / display** | `NextExit` (מילה אחת, בלי רווח!) | Bold / Regular / Light | שם בקאבר, label "כנסת"/"תחקיר", tagline (אם יש), ציטוטים בולטים, CTA, byline |
| **גוף / body** | `Narkiss Tam` | Regular / Semibold | פסקאות הכתבה (38-45pt). Semibold להדגשת ציטוט מרכזי בפסקה |
| **UI / numeric** | `Inter` | Bold / Light / Regular | מספור גדול "01"-"NN", טקסט בכפתור, URL strip בפס תחתון |

**הסיבה לחלוקה:**
- NextExit הוא ה-display font של המותג — מודרני, חד, גדול
- Narkiss Tam הוא ה-reading font — סריף יפה, נינוח לקריאה ארוכה
- Inter — נקי לעברית גם וגם ל-UI/numeric בלי תחושת "מותג"

### גדלים סטנדרטיים

| Token | פונט | Weight | Size (px @ 1080×1350) | Line-height | שימוש |
|-------|------|--------|------------------------|-------------|--------|
| `--type-cover-title` | NextExit | Bold | 64-100 (דינמי) | 108% | כותרת בקאבר (טבלה למטה) |
| `--type-cover-label` | NextExit | Regular | 32 | 100% | label בקאבר ("כנסת", "תחקיר") + letter-spacing 6px |
| `--type-cover-byline` | NextExit | Regular | 28 | 130% | byline ("תחקיר: סיון תהל") |
| `--type-cover-imgcredit` | NextExit | Light | 22 | 130% | credit לתמונת hero בקאבר |
| `--type-slide-num` | Inter | Bold | 96 | 100% | מספור "01"/"02"/.../"NN" באדום |
| `--type-body` | Narkiss Tam | Regular | 38-45 (לפי תוכן) | 155% | פסקה body |
| `--type-body-emphasis` | Narkiss Tam | Semibold | 40-45 | 155% | פסקה body שכוללת ציטוט חזק |
| `--type-credit` | NextExit | Light | 28 | 130% | credit לתמונה (קאטאוט/הקשר/וכו') |
| `--type-cta-line1` | NextExit | Bold | 56 | 120% | "בלי בעלי הון. בלי פרסומות." |
| `--type-cta-line2` | NextExit | Bold | 96-110 | 105% | "בלי בולשיט" |
| `--type-cta-button` | Inter | Bold | 36 | 100% | "לתחקיר המלא" |
| `--type-url` | Inter | Light | 26 | 100% | URL strip בפס תחתון, letter-spacing 4px, ALL-CAPS |

### גודל דינמי לכותרת בקאבר (חוק 0a)

הכותרת בקאבר היא **מילה במילה מהכתבה** — לא לקצר. גודל לפי אורך:

| אורך הכותרת | fontSize | שורות אופייני |
|--------------|----------|----------------|
| עד 25 תווים | 100pt | 1-2 |
| 25-45 תווים | 84pt | 2-3 |
| 45-65 תווים | 72pt | 3 |
| 65+ תווים | 64pt | 4 |

מינ׳ אבסולוטי: 60pt. מתחת לזה — חוזרים לכותב ומבקשים כותרת קצרה יותר
לפרסום (נדיר).

### קבצי הפונט

| משקל | קובץ | נתיב |
|------|------|------|
| Light | NextExitLight.otf | `assets/fonts/NextExitLight.otf` |
| Regular | NextExitRegular.otf | `assets/fonts/NextExitRegular.otf` |
| Bold | NextExitBold.otf | `assets/fonts/NextExitBold.otf` |

**Narkiss Tam** — לא נמצא בתיקיית הסקיל. מותקן במחשב של דור (Font Book).

**Inter** — מותקן ב-Figma by default.

### התקנה חד-פעמית

```bash
cp ~/Documents/המקום/שיווק/hamakom-carousel/assets/fonts/*.otf ~/Library/Fonts/
```
או דרך Font Book → File → Add Fonts.

### אחרי ההתקנה: restart מלא ל-Figma desktop

**זה לא מספיק לעשות "Reload"**. צריך:
1. סגירה מלאה של אפליקציית Figma (Cmd+Q)
2. וידוא שאין תהליך figma שעדיין רץ (`ps aux | grep -i figma`)
3. פתיחה מחדש

**הסיבה:** Figma plugin context טוען רשימת פונטים פעם אחת ב-startup
ושומר cache. גם אם הפונט מותקן ב-macOS, ה-plugin לא יראה אותו עד restart.

### Fallback בזמן ריצה

הסקיל בודק:
```javascript
const fonts = await figma.listAvailableFontsAsync();
const hasNextExit = fonts.some(f => f.fontName.family === "NextExit");
const hasNarkissTam = fonts.some(f => f.fontName.family === "Narkiss Tam");
```

אם חסר — נופל ל-Inter ומחזיר flag `font_fallback_used: true` בפלט.

---

## כיוון ויישור

- **כיוון:** RTL בכל השקפים
- **יישור body:** ימין (`textAlignHorizontal = "RIGHT"`)
- **יישור CTA:** מרכז (`CENTER`)
- **יישור מספור שקף "01":** LEFT (האפקט בעין: ימין-עליון של ה-content area, אבל ב-Figma הקואורדינטה היא ב-left-margin)

---

## Dimensions

**גודל קנבס:** 1080×1350 (Instagram 4:5). יחס: 0.8.

| Token | Value | שימוש |
|-------|-------|--------|
| `--canvas-w` | 1080 | רוחב |
| `--canvas-h` | 1350 | גובה |
| `--margin-x` | 72 | שוליים אופקיים |
| `--margin-y-top` | 132 | מרווח אנכי עליון (אחרי chrome) |
| `--margin-y-bottom` | 1294 | תחילת ה-URL strip |
| `--content-w` | 936 | רוחב אזור הטקסט (1080 - 2×72) |
| `--gap-paragraph` | 36 | מרווח אנכי בין פסקאות באותו שקף |

---

## Chrome (קבוע בכל שקף שאינו CTA)

### 1. פס אדום עליון
- צבע: `--accent` של הפלטה
- גובה: **3px**
- ממוקם: y=0, רוחב מלא 1080

### 2. לוגו ריבועי (chrome פינתי)
- **קובץ:** `assets/logo-square-black.svg` (vector)
- **טעינה:** `figma.createNodeFromSvg(LOGO_SVG)`. אחרי הטעינה: `node.fills = []`
  (להסיר את ה-fill של ה-frame העטיפה), ועדכן fills רק על vector children
  ל-`--fg` או ל-`--accent` בהתאם לבחירה עיצובית.
- **גודל:** 72×61 (שמירת aspect ratio של ה-SVG, viewBox 826×981)
- **מיקום:** x=947, y=56 (פינה ימנית-עליונה ב-RTL = שמאל-עליון בקואורדינטות Figma)
- **לעולם** לא לבנות מטקסט.

### 3. לוגו wordmark (לבן, אופקי) — רק ב-CTA
- **קובץ:** `assets/logo-wordmark-white.png`
- **טעינה:** `upload_assets()` עם nodeId של rect placeholder
- **גודל:** ~480×142, ממורכז x=300, y=200 בשקף ה-CTA
- **לעולם** לא לבנות מטקסט.

### 4. מספור שקף "01"/"02"/.../"NN"
- **פונט:** Inter Bold 96pt
- **צבע:** `--accent`
- **מיקום:** x=72, y=152
- **יישור:** LEFT (בתוך bounding box רחב)
- **לא מופיע בקאבר** (במקום זה: REC dot)
- **לא מופיע ב-CTA**

### 5. REC dot (קאבר בלבד)
- עיגול `--accent`, קוטר 20px
- מיקום: x=56, y=64
- ליד הנקודה: "REC" Inter Bold 18pt לבן

### 6. פס אדום תחתון + URL
- צבע: `--accent`
- גובה: 56px (y=1294 → y=1350)
- טקסט במרכז: "H A - M A K O M . C O . I L"
- פונט: `--type-url`, צבע `--fg`, letter-spacing 4px
- **CTA exception:** ב-CTA הפס לבן עם טקסט אדום (אינוורסיה)

---

## Layout — Grid

```
y=0       ┌──────────────────────────────────┐
          │ פס אדום 3px                       │  ← top stripe
y=3       ├──────────────────────────────────┤
          │ logo 72×61   REC/space            │  ← chrome row (y=56-128)
y=132     ├──────────────────────────────────┤
          │                                  │
          │ content zone                     │  ← gut of slide
          │ x=72 .. x=1008 (width 936)       │     y=132 .. y=1294
          │ y=132 .. y=1294 (height 1162)    │
          │                                  │
y=1294    ├──────────────────────────────────┤
          │ פס אדום 56px + URL               │  ← bottom stripe
y=1350    └──────────────────────────────────┘
```

---

## Effects

### Gradient על תמונת hero בקאבר
```
linear top → bottom:
  alpha 0.10 @ 0%
  alpha 0.50 @ 55%
  alpha 1.00 @ 100%   (color = --bg)
```

### Gradient fade (לא בשימוש כיום אבל זמין)
```
linear top → bottom:
  alpha 0.00 @ 0%
  alpha 0.40 @ 50%
  alpha 1.00 @ 75%
```

### Image filter סטנדרטי (אם רצויה אווירה)
- saturate: 0.85
- contrast: 1.10
- brightness: 0.90

---

## Divider — קו אדום קצר

לשימוש מתחת ל-label בקאבר, מתחת למספור בשקף-פסקה, או כ-separator קל:

- **אורך:** 70-100px
- **עובי:** 3-4px
- **צבע:** `--accent`
- **מיקום:** x = `1080 - 72 - length` (ימין מיושר)

---

## אסור

- אימוג'יז (בכלל)
- shadows על טקסט
- decorative shapes (חצים, פלוסים, אסטריסקים, פרחים, וכו')
- frames מעוגלים (corner-radius > 8px) — חוץ מ-button pill ב-CTA (corner-radius 55px)
- gradient בצבעים שאינם `--bg` (כלומר, gradient תמיד שקיפות של ה-bg, לא אדום-לכתום וכו')
- text-stroke / outline על טקסט
- icon fonts (Font Awesome / Material Icons)
