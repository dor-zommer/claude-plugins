# HaMakom Design System 2026 — מקור אמת ויזואלי

> **מסמך זה הוא מקור-האמת היחיד** לעיצוב הוויזואלי של "המקום הכי חם בגיהנום"
> בכל הסקילים תחת `hamakom-visuals` (carousel, graphic, reel).
> מקור: חבילת ה-DS שדור מסר מ-Claude Design — `~/Dor's Cowork /HaMakom Design System/`.
>
> **בסתירה בין קובץ זה לבין כל מסמך אחר בסקיל — קובץ זה גובר.**
> בעבר הסקילים השתמשו בפלטה ישנה (שחור/אדום `#f70d28` + NextExit/Narkiss Tam).
> זה **בוטל**. ה-DS האקטואלי הוא שנהב/דיו/טרקוטה + Suez One + IBM Plex Sans Hebrew.

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

## 2. טיפוגרפיה — שתי פנים, שני תפקידים

| תפקיד | פונט | משקלים | שימוש |
|-------|------|---------|--------|
| **תצוגה** | **Suez One** | Regular (הפונט כבד מטבעו) | כותרות, ציטוטים, מספרי-נתון, שורות CTA |
| **גוף / UI** | **IBM Plex Sans Hebrew** | Regular / Medium / SemiBold / Bold | פסקאות, קיקרים, byline, credit, url, כפתור |

> פונט הלוגו ("HaMakom") הוא artwork קנייני (PNG בלבד) — **לעולם לא live type**.
> Suez One הוא תחליף-הכותרות המאושר, בדיוק כמו באתר הפרודקשן.

### גדלים סטנדרטיים (@ 1080×1350)

| שימוש | פונט | Weight | Size | Line-height |
|-------|------|--------|------|-------------|
| כותרת קאבר | Suez One | Regular | 56–72 (דינמי לפי אורך) | 108% |
| קיקר קאבר | IBM Plex | SemiBold | 27 | — (letter-spacing 2) |
| byline קאבר | IBM Plex | Medium | 25 | — |
| גוף פסקה | IBM Plex | Regular | 40 (auto-shrink → 26) | 160% |
| קיקר פסקה ("דעה") | IBM Plex | Bold | 24 | — (letter-spacing 3) |
| אינדקס פסקה ("02 / 09") | IBM Plex | Medium | 22 | — |
| מספר-נתון ענק | Suez One | Regular | 200–300 | 100% |
| kicker נתון | IBM Plex | Bold | 26 | — (terra-deep) |
| CTA שורה 1 | Suez One | Regular | 48 | 120% |
| CTA שורה 2 ("בלי בולשיט") | Suez One | Regular | 112 | 110% |
| כפתור CTA | IBM Plex | Bold | 36 | — |
| url בפוטר | IBM Plex | SemiBold | 21 | — (letter-spacing 3) |

### גודל דינמי לכותרת קאבר (verbatim — לא לקצר)

| אורך | fontSize |
|------|----------|
| עד 30 תווים | 72 |
| 30–50 | 64 |
| 50+ | 56 |

### קבצי פונט — התקנה

שני הפונטים ב-Google Fonts (פתוחים). **לא מותקנים מקומית כברירת מחדל** —
Figma צריך אותם מותקנים. הורדה + התקנה:

```bash
mkdir -p /tmp/hmfonts && cd /tmp/hmfonts
curl -sL "https://github.com/google/fonts/raw/main/ofl/suezone/SuezOne-Regular.ttf" -o SuezOne-Regular.ttf
B="https://github.com/google/fonts/raw/main/ofl/ibmplexsanshebrew"
for w in Regular Medium SemiBold Bold; do curl -sL "$B/IBMPlexSansHebrew-$w.ttf" -o "IBMPlexSansHebrew-$w.ttf"; done
cp *.ttf ~/Library/Fonts/
```

**Figma רואה אותם מיד אחרי `cp` — אין צורך ב-restart.** (בניגוד להערה הישנה.)
בזמן ריצה הסקיל בכל זאת בודק `figma.listAvailableFontsAsync()` ונופל ל-Inter
עם flag `font_fallback_used: true` אם חסר.

```javascript
let HEAD="Inter", BODY="Inter";
const fonts = await figma.listAvailableFontsAsync();
if (fonts.some(f => f.fontName.family === "Suez One")) HEAD = "Suez One";
if (fonts.some(f => f.fontName.family === "IBM Plex Sans Hebrew")) BODY = "IBM Plex Sans Hebrew";
for (const fn of [{family:HEAD,style:"Regular"},{family:BODY,style:"Regular"},
  {family:BODY,style:"Medium"},{family:BODY,style:"SemiBold"},{family:BODY,style:"Bold"}])
  { try{ await figma.loadFontAsync(fn);}catch(e){} }
```

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

- **לוגו ריבועי מונוכרום** (`assets/logo-square-black.svg`) פינה ימנית-תחתונה,
  ~50px גובה, צבוע לבן על רקע כהה / דיו על שנהב. **לעולם לא לבנות מטקסט.**
- לצדו (שמאלה ב-RTL): `HA-MAKOM.CO.IL` — IBM Plex SemiBold 21, ink-soft / on-dark-soft, letter-spacing 3.
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

### קאבר (image, full-bleed)
- תמונת hero **מקצה לקצה** (1080×1350, FILL) — **לא** קארד ממורכז, **לא** פינות מעוגלות.
- **בלי משנה (lede)** — label + כותרת + byline בלבד.
- **הכותרת נמוכה ככל שניתן** — יושבת ~24-28px מעל ה-byline (לא באמצע הפריים);
  הקיקר (label) צמוד מעל הכותרת. ממקמים מלמטה למעלה: byline → כותרת → label.
- **gradient דיו מצומצם** — שקוף לחלוטין (alpha 0) עד ~7% מעל ה-label, עולה
  לאלפא ~0.72 בגובה ה-label, ומגיע לאלפא מלא (1.0) רק בתחתית. **~65-70%
  העליונים של התמונה חייבים להישאר גלויים לחלוטין.**
- קיקר טרקוטה (`--sc-terra` על כהה). כותרת Suez One לבנה (verbatim).
- byline (`--on-dark-soft`). credit תמונה (לבן opacity .6) פינה שמאלית-תחתונה.
- פוטר: לוגו + url + פס-חתימה תחתון (הפס היחיד — אין פס עליון).

### שקף-פסקה (text)
- רקע שנהב. טקסט דיו, IBM Plex Regular, **מיושר-לעליון** (`y≈212`), x=80, w=920, RIGHT, lh 160%.
- פס-חתימה תחתון בלבד (דרך הפוטר). קיקר קטגוריה ("דעה" טרקוטה-עמוק) + קו טרקוטה קצר. אינדקס "02 / 09" (ink-soft, שמאל).
- auto-shrink הפונט מ-40 עד 26 אם הטקסט ארוך.
- פוטר.

### שקף-נתון (data)
- רקע שנהב. **מספר ענק בטרקוטה** (Suez One, ממורכז, 200–300px).
- kicker תיאורי בטרקוטה-עמוק (לא "הנתון" אלא תיאור), תיאור מודגש (Plex Bold, ink),
  שורת פירוט (ink-2), שורת מקור (ink-soft). מספר verbatim מהכתבה + מקור.
- **טרקוטה לנתונים, לא מרווה** (מרווה = ברים/CTA תמיכה).

### CTA (dark)
- רקע **דיו** `#141413`. וורדמרק לבן ממורכז. פס-חתימה תחתון בלבד (דרך הפוטר).
- "בלי בעלי הון.  בלי פרסומות." (Suez One לבן 48) / "בלי בולשיט" (Suez One לבן 112).
- כפתור pill **שנהב** (radius 54) עם "לכתבה המלאה" (IBM Plex Bold, ink).
- פוטר (גרסה כהה).
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
