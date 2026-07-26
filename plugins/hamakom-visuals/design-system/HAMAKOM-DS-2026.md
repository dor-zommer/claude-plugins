# HaMakom Design System 2026 — מקור אמת ויזואלי

> **מסמך זה הוא מקור-האמת היחיד** לעיצוב הוויזואלי של "המקום הכי חם בגיהנום"
> בכל הסקילים תחת `hamakom-visuals` (carousel, graphic, reel).
> מקור: חבילת ה-DS שדור מסר מ-Claude Design — `~/Dor's Cowork /HaMakom Design System/`.
>
> **בסתירה בין קובץ זה לבין כל מסמך אחר בסקיל — קובץ זה גובר.**
> בעבר הסקילים השתמשו בפלטה ישנה (שחור/אדום `#f70d28` + NextExit/Narkiss Tam).
> זה **בוטל**. ה-DS האקטואלי הוא שנהב/דיו/טרקוטה + HaMakom (תצוגה) + Publico Headline + Graphik HLAR.
>
> **הנכסים עצמם — `assets/` שליד הקובץ הזה (נוסף 19.07.2026):** לוגו (SVG+PNG),
> הפונטים (HaMakom של המותג + Publico Headline + Graphik HLAR מ-Fontef), והסגיר הקנוני
> (`closer_v3.mp4`). שלושת הסקילים מושכים משם — **אין יותר עותקים פר-סקיל.**
> פירוט, התקנת פונטים ורישיונות: `assets/README.md`.

---

## 0. העיקרון

זהות "המקום" היא **ניטרלית-טיפוגרפית עם טריו צבע לפי תפקיד**. ~90% מכל שקף
נשאר ניטרלי (שנהב + דיו); הצבע נדיר — ולכן הוא קורא. הטריו (טרקוטה / מרווה /
אברש) אף פעם לא דקורציה — תמיד **תפקיד**.

---

## 1. פלטה (קבועה — לא דינמית)

| Token | Hex | Figma RGB (0–1) | תפקיד |
|-------|-----|------------------|--------|
| `--bg` (שנהב) | `#faf9f5` | `0.9804, 0.9765, 0.9608` | רקע / קנבס |
| `--paper` | `#f3f1ea` | `0.9529, 0.9451, 0.9176` | משטח מורם, pill |
| `--ink` (דיו) | `#141413` | `0.0784, 0.0784, 0.0745` | טקסט ראשי + רקע כהה (CTA) |
| `--ink-2` | `#3b3a36` | `0.2314, 0.2275, 0.2118` | טקסט משני |
| `--ink-soft` | `#6b6a63` | `0.4196, 0.4157, 0.3882` | טקסט שלישוני, credit, url |
| `--line` | `#e3e1d8` | `0.8902, 0.8824, 0.8471` | קו-שיער |
| **`--terra`** (טרקוטה) | `#D97757` | `0.851, 0.4667, 0.3412` | **אינטראקציה + תגיות קטגוריה + מספרי-נתון** |
| `--terra-deep` | `#9C4527` | `0.6118, 0.2706, 0.1529` | קיקר/טקסט-טרקוטה על רקע בהיר |
| `--terra-cta` | `#C2562F` | `0.7608, 0.3373, 0.1843` | focus ring, תגית breaking |
| **`--sage`** (מרווה) | `#788C5D` | `0.4706, 0.549, 0.3647` | **CTA תמיכה + עולם הנתונים** |
| `--sage-deep` | `#4F5E38` | `0.3098, 0.3686, 0.2196` | טקסט-מרווה על בהיר |
| **`--heather`** (אברש) | `#8E6FA8` | `0.5569, 0.4353, 0.6588` | **קול הדעה + סדרת-נתונים שנייה** |
| `--heather-deep` | `#5E4476` | `0.3686, 0.2667, 0.4627` | טקסט-אברש על בהיר |
| `--sc-terra` (על כהה) | `#E8906F` | `0.9098, 0.5647, 0.4353` | טרקוטה בהיר על רקע דיו |
| `--on-dark-soft` | `#b7b5ac` | `0.7176, 0.7098, 0.6745` | טקסט עזר על רקע כהה |
| לבן | `#ffffff` | `1, 1, 1` | טקסט על תמונה/דיו |

**הקצאת הטריו לפי תפקיד (חוק):**
- **טרקוטה** = אינטראקציה, קיקר קטגוריה, מספרי-נתון ענקיים.
- **מרווה** = כפתור התמיכה (CTA תרומה), עולם הנתונים (ברים/מפה).
- **אברש** = קול הדעה (קיקר/אקסנט בכתבות דעה), סדרת-נתונים שנייה.

**אסור:** pastel/סוכר, corporate-tech (turquoise OpenAI), צבעי-ספונסר (ירוק
WhatsApp), אדום `#f70d28` / ענבר `#d4a13a` (אלה הפלטה הישנה — לא בשימוש).

**ניגודיות:** `fg` על `bg` חייב WCAG AA (4.5:1) ל-body. דיו על שנהב = AAA.

---

## 2. טיפוגרפיה — שלוש פנים, שלושה תפקידים

**עדכון 20.07.2026 — שלושה פונטים, שלושה תפקידים.** HaMakom (פונט המותג) לתצוגה
חתימתית, Publico Headline לכותרות ארוכות, Graphik HLAR לגוף. Publico+Graphik מורשים
(Fontef #03515, חברה עד 10 עובדים); HaMakom הוא הפונט של המותג עצמו (נבנה מהלוגו).

| תפקיד | פונט | משקלים | שימוש |
|-------|------|---------|--------|
| **תצוגה-חתימה** | **HaMakom** | Regular (יחיד) | כותרת קאבר, מספר-מחץ, מחץ CTA "בלי בולשיט" — **כשהמחרוזת עברית** |
| **תצוגה-fallback** | **Publico Headline Hebrew** | Roman · Extrabold | אותם מקומות **כשיש לטינית/em-dash** (HaMakom לא מכסה) |
| **גוף / UI** | **Graphik HLAR** | Light · Regular · Medium | פסקאות, byline, credit, url, כפתור |

> **HaMakom = פונט התצוגה של המותג** — מודולרי, נגזר מהלוגו (עוצב מתן שליטא, קומפל דור).
> ב-brand-identity הוא ה-`--f-display` הראשי. **אילוץ קשה: 53 גליפים בלבד** — עברית,
> ספרות, ופיסוק (`! " ' ( ) , - . / : ; ? ׳ ״`), **אבל אין לטינית ואין em-dash `—`.** לכן
> משתמשים בו לתצוגה **רק אם המחרוזת נתמכת**; אחרת נופלים ל-Publico. הבחירה אוטומטית
> (`dispFont` בבילדרים בודק `/[A-Za-z—]/`). ה-url `HA-MAKOM.CO.IL` (לטיני) — תמיד Graphik.
>
> **גבול השימוש (החלטת דור 24.07.2026) — חוק:** HaMakom הוא פונט **תצוגה חתימתית קצרה
> בלבד** — כותרת קאבר, מספר-מחץ, קיקרים ותגיות, מחץ CTA. **אסור להשתמש בו לטקסט רץ:**
> ציטוטים, פסקאות, כיתובים ומשפטי מסך. **ציטוט = Publico Headline.** הפונט מודולרי
> וקריאותו יורדת ברצף; זו הסיבה שהוא לא נועד לשורות ארוכות.
> **Graphik מגיע רק עד Medium** — אין SemiBold/Bold; מה שהיה IBM Plex Bold/SemiBold → Graphik Medium.

### גדלים סטנדרטיים (@ 1080×1350)

| שימוש | פונט | Weight | Size | Line-height |
|-------|------|--------|------|-------------|
| כותרת קאבר | HaMakom → Publico Roman | Regular / Roman | 56–72 (דינמי) | 108% |
| byline קאבר (שם בלבד) | Graphik HLAR | Medium | 25 | — (ink-soft) |
| גוף פסקה | Graphik HLAR | Regular | 45–50 (auto-shrink בחריגה) | 160% |
| מספר-נתון ענק | HaMakom → Publico Extrabold | Regular / Extrabold | 110–200 | 100% |
| שורת פירוט נתון | Graphik HLAR | Medium | 32 | — (ink) |
| CTA שורה 1 | Graphik HLAR | Medium | 42 | — |
| CTA שורה 2 ("בלי בולשיט") | **HaMakom** (סלוגן המותג) | Regular | 76 | 110% |
| כפתור CTA ("לכתבה המלאה") | Graphik HLAR | Medium | 34 | — (היה Bold) |
| ציטוט עדות על תמונה | **Publico Headline** Roman | Roman | 45 | — (לבן) |
| url בפוטר / קאפשן | Graphik HLAR | Medium | 21–26 | — (letter-spacing 3) |

**מיפוי:** תצוגה עברית → HaMakom (נופל ל-Publico Roman/Extrabold על לטינית/em-dash) ·
גוף → Graphik Regular · Bold/SemiBold לשעבר → Graphik Medium (תקרה) · Light זמין, לא בשימוש.

### גודל דינמי לכותרת קאבר (verbatim — לא לקצר)

| אורך | fontSize |
|------|----------|
| עד 30 תווים | 72 |
| 30–50 | 64 |
| 50+ | 56 |

### קבצי פונט — התקנה

**הפונטים בריפו** (`assets/fonts/`, רישיון Fontef #03515). מותקנים ל-Figma כך:

```bash
DS=$(ls -d ~/.claude/plugins/cache/hamakom-plugins/hamakom-visuals/*/design-system 2>/dev/null | sort -V | tail -1)
DS=${DS:-plugins/hamakom-visuals/design-system}
cp "$DS"/assets/fonts/*.otf "$DS"/assets/fonts/*.ttf ~/Library/Fonts/
```
(ה-`.ttf` הוא HaMakom; ה-`.otf` הם Publico+Graphik.)

**Figma רואה אותם מיד אחרי `cp` — אין צורך ב-restart.** אם מותקנים גם קבצי TRIAL
(שם משפחה `... TRIAL`) — לא מזיק; ה-resolver מכוון לשמות הנקיים בלבד.

**resolver בזמן ריצה — חובה, לא לקודד שם קשיח.** הפונטים המסחריים נרשמים פר-משקל
(`Graphik HLAR Medium` / Regular) *וגם* בקיבוץ טיפוגרפי (`Graphik HLAR` / Medium), ולא
ידוע מראש איזו צורה Figma חושף. פותרים בזמן ריצה ובוחרים את הזוג הקיים:

```javascript
const fonts = await figma.listAvailableFontsAsync();
const AV = new Set(fonts.map(f => f.fontName.family + "||" + f.fontName.style));
const FB = {family:"Inter", style:"Regular"};
const pick = c => c.find(x => AV.has(x.family+"||"+x.style)) || c[c.length-1] || FB;
const HAMAKOM = pick([{family:"HaMakom",style:"Regular"},FB]);
const hamakomOK = s => HAMAKOM.family==="HaMakom" && !/[A-Za-z—]/.test(s);  // תצוגה עברית → HaMakom
const dispFont = (text,heavy) => hamakomOK(text) ? HAMAKOM : (heavy ? ROLE.dispXB : ROLE.disp);
const ROLE = {
  disp:   pick([{family:"Publico Headline Hebrew",style:"Roman"},{family:"Publico Headline Hebrew Roman",style:"Regular"},FB]),
  dispXB: pick([{family:"Publico Headline Hebrew",style:"Extrabold"},{family:"Publico Headline Hebrew Exbold",style:"Regular"},FB]),
  light:  pick([{family:"Graphik HLAR",style:"Light"},{family:"Graphik HLAR Light",style:"Regular"},FB]),
  reg:    pick([{family:"Graphik HLAR",style:"Regular"},FB]),
  med:    pick([{family:"Graphik HLAR",style:"Medium"},{family:"Graphik HLAR Medium",style:"Regular"},FB]),
};
for (const r of Object.values(ROLE)) { try{ await figma.loadFontAsync(r);}catch(e){} }
const fontFallback = Object.values(ROLE).some(r => r.family==="Inter");
```

הקוד המלא (כולל `roleFor` שממפה תפקיד לוגי → זוג, וקלמפ Bold/SemiBold→Medium) —
ב-`skills/hamakom-carousel/scripts/build_figma_simple.md` ו-`hamakom-graphic/scripts/build_graphics_page.md`.

---

## 3. פס-חתימה טריקולור (Tricolor signature)

החתימה של המותג — שלושת צבעי הטריו כ**פס אחד בלבד, תחתון**, בכל שקף.
מימין לשמאל: **טרקוטה · מרווה · אברש** (כל אחד שליש מהרוחב).

```javascript
function SIG(f, y, h){ // h=4 — נקרא פעם אחת בלבד לשקף (תחתון, חלק מהפוטר)
  f.appendChild(R({x:720, y, w:360, h, color:C.terra}));   // ימין
  f.appendChild(R({x:360, y, w:360, h, color:C.sage}));    // מרכז
  f.appendChild(R({x:0,   y, w:360, h, color:C.heather})); // שמאל
}
```

מיקום: **פס אחד בלבד — תחתון**, בקצה התחתון של השקף: `y = H − 4`
(`y=1346` בקנבס 1350). גובה **4px**. **אין פס עליון.**

---

## 4. פוטר ולוגו (Brandmark)

- **לוגו ריבועי מונוכרום** (`assets/logo/logo-square-black.svg`) פינה ימנית-תחתונה,
  ~50px גובה, צבוע לבן על רקע כהה / דיו על שנהב. **לעולם לא לבנות מטקסט.**
- לצדו (שמאלה ב-RTL): `HA-MAKOM.CO.IL` — Graphik HLAR Medium 21, ink-soft / on-dark-soft, letter-spacing 3.
- מתחת לכל זה: פס-חתימה טריקולור תחתון (4px, בקצה התחתון — הפס היחיד בשקף).

```javascript
async function FOOT(f, dark){
  const fg = dark ? C.onDarkSoft : C.inkSoft;
  LOGO(f, dark ? C.white : C.ink, 952, 1244, 50);
  f.appendChild(await T({chars:"HA-MAKOM.CO.IL", family:BODY, style:"SemiBold",
    size:21, color:fg, x:400, y:1262, w:520, align:"RIGHT", letterSpacing:3}));
  SIG(f, 1346, 4);
}
```

---

## 5. סוגי שקפים

### קאבר (image, full-bleed) — לפי ההירו שדור קיבע (3.7.2026, "00-cover" בקובץ הארגזים)
- תמונת hero **מקצה לקצה** (1080×1350, FILL) — **לא** קארד ממורכז, **לא** פינות מעוגלות.
- **הקיקר מעל הכותרת = ה-lede** (משפט תקציר הכתבה) בטרקוטה-בהיר `--sc-terra` —
  Graphik HLAR Medium 28, letter-spacing 2. **אין תגית קטגוריה בקאבר.**
- **הכותרת נמוכה ככל שניתן** — יושבת ~16px מעל ה-byline (לא באמצע הפריים);
  הקיקר צמוד ~14px מעל הכותרת. ממקמים מלמטה למעלה: byline → כותרת → קיקר.
- **byline = שם הכותב/ת בלבד** (בלי "כתבה ·" / "מאת:") — Graphik HLAR Medium 25,
  **ink-soft `#6b6a63`**.
- **gradient דיו מצומצם** — שקוף לחלוטין (alpha 0) עד ~7% מעל הקיקר, עולה
  לאלפא ~0.72 בגובה הקיקר, ומגיע לאלפא מלא (1.0) רק בתחתית. **~65-70%
  העליונים של התמונה חייבים להישאר גלויים לחלוטין.**
- כותרת Publico Headline Roman לבנה (verbatim).
- **לוגו לבן קטן ממורכז** (~42×50, y≈1244) — לא בפינה.
- **שורת תחתית אחת צמודה לפס** (y≈1313): credit צילום שמאל (x≈18, לבן opacity ~0.53,
  ‏18pt) + `HA-MAKOM.CO.IL` ממורכז (`--on-dark-soft`, Graphik Medium 21, ls 3).
- פס-חתימה תחתון 4px (הפס היחיד — אין פס עליון).

### שקף-פסקה (text)
- רקע שנהב. טקסט דיו, Graphik HLAR Regular, **מיושר-לעליון** (`y≈182`), x=80, w=920, RIGHT, lh 160%.
- פס-חתימה תחתון בלבד (דרך הפוטר). קיקר קטגוריה ("דעה" טרקוטה-עמוק) + קו טרקוטה קצר. אינדקס "02 / 09" (ink-soft, שמאל).
- auto-shrink הפונט (45–50) רק אם הטקסט חורג.
- פוטר.

### שקף-נתון (data)
- רקע שנהב. **מספר ענק בטרקוטה** (Publico Headline Extrabold, ממורכז, 110–200px).
- שורת פירוט מודגשת (Graphik HLAR Medium, ink),
  שורת פירוט (ink-2), שורת מקור (ink-soft). מספר verbatim מהכתבה + מקור.
- **טרקוטה לנתונים, לא מרווה** (מרווה = ברים/CTA תמיכה).

### CTA (dark) — לפי הפריים שדור קיבע (3.7.2026, "12-cta" בקובץ הארגזים)
- רקע **דיו** `#141413`. **פס-חתימה עליון** 4px (בשקף הזה בלבד; טרקוטה משמאל · מרווה במרכז · אברש מימין).
- **הלוגו הריבועי הטיפוגרפי בשנהב, גדול** — ~320×380, ממורכז (x≈380), y≈240. **לא וורדמרק.**
- שורה 1: "בלי בעלי הון.  בלי פרסומות." — **Graphik HLAR Medium 42** שנהב, ממורכז, y≈720.
- שורה 2: "בלי בולשיט" — **Publico Headline Extrabold 76** שנהב, ממורכז, y≈790.
- כפתור pill **טרקוטה** `#D97757` (400×108, radius 54, ממורכז, y≈970) עם "לכתבה המלאה" — Graphik HLAR Medium 34 **בשנהב**.
- פוטר: **רצועת שנהב ברוחב מלא** (56px, y=1294) עם `HA-MAKOM.CO.IL` בדיו — Graphik HLAR Medium 24, letter-spacing 4, ממורכז. בלי לוגו קטן, בלי פס תחתון.
- **לעולם לא** "כשציבור מממן, ציבור קובע".

---

## 6. צבעי JS — להעתקה

```javascript
const C = {
  bg:{r:0.9804,g:0.9765,b:0.9608}, paper:{r:0.9529,g:0.9451,b:0.9176},
  ink:{r:0.0784,g:0.0784,b:0.0745}, ink2:{r:0.2314,g:0.2275,b:0.2118},
  inkSoft:{r:0.4196,g:0.4157,b:0.3882}, line:{r:0.8902,g:0.8824,b:0.8471},
  terra:{r:0.851,g:0.4667,b:0.3412}, terraDeep:{r:0.6118,g:0.2706,b:0.1529}, terraCta:{r:0.7608,g:0.3373,b:0.1843},
  sage:{r:0.4706,g:0.549,b:0.3647}, sageDeep:{r:0.3098,g:0.3686,b:0.2196},
  heather:{r:0.5569,g:0.4353,b:0.6588}, heatherDeep:{r:0.3686,g:0.2667,b:0.4627},
  scTerra:{r:0.9098,g:0.5647,b:0.4353}, onDarkSoft:{r:0.7176,g:0.7098,b:0.6745}, white:{r:1,g:1,b:1},
};
```

---

## 7. אסור (כל שקף)

- אימוג'ים (בכלל — כולל ←, 👇, ✓).
- פלטה ישנה: שחור `#141413` כרקע ברירת-מחדל לכל שקף, אדום `#f70d28`, ענבר `#d4a13a`.
- פונטים ישנים: NextExit, Narkiss Tam, Noto Serif Hebrew (כפונט ראשי).
- shadows/outline על טקסט; קארד-תמונה ממורכז עם פינות מעוגלות; gradient צבעוני (רק שקיפות דיו).
- "כשציבור מממן, ציבור קובע" (סלוגן שדור פסל).
- `remove` לכל עמוד ה-Figma. עורכים פריים-פריים; דור עורך ידנית ו-autosave לא תמיד שומר.
