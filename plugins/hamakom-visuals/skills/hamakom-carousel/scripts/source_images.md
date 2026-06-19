# Source Images — איסוף תמונות לקרוסלה

**זה לא קוד. זה הוראות לקלוד.** קלוד קורא את המסמך הזה אחרי
`analyze_content.py`, ומפעיל שיקול דעת על איזה תמונה מתאימה לכל שקף.

הקלט: JSON מ-analyze_content (עם `slides`, `metadata`, `candidate_images`).
הפלט: מילון `{slide_index: {"src": URL_OR_PATH, "source": "...", "credit": "...", "needs_cutout": bool, "prompt": "..."}}`.

---

## 4 שכבות (סדר עדיפויות)

### שכבה 1 — ידני (דור סיפק)

אם דור הוסיף בבקשה `--photos /path/1.jpg,/path/2.jpg,...` או הצמיד פיזית
תמונות לבקשה, **תמיד עדיפות גבוהה.** הקצה אותן ל-slide blocks לפי הסדר:

| slide block | תמונה ידנית מתאימה |
|---|---|
| `cover-overlay` | התמונה הדרמטית/חזקה ביותר (אם דור סימן "hero", לקחת אותה) |
| `hero-bleed-fade` | אותה תמונה של ה-cover (לא תמונה שניה) |
| `split-text-photo` | תמונת סצנה/מקום/אירוע — לא פנים |
| `split-text-cutouts` | תמונות פנים של דמויות מ-`slide.people` |
| `split-text-concept` | אם דור סיפק תמונה אבסטרקטית, מתאים. אחרת — דלג ל-Firefly |
| `split-text-document` | תמונת מסמך/חותמת/תיק. אחרת — Firefly |
| `closing-symbol` | אותה תמונה של cover (אם זה לוגו/סמל), או דחיית מתון |

**אם דור סיפק רק 2-3 תמונות:** הקצה אותן לשקפים החשובים ביותר (cover →
hero → split-text-photo), והשלם את השאר משכבות 2-4.

---

### שכבה 2 — חילוץ מ-URL של ha-makom

`analyze_content.py` כבר החזיר:
- `metadata.og_image` — התמונה הראשית של הכתבה ב-WordPress
- `candidate_images` — רשימת `<img>` שנמצאו בגוף הכתבה

**שימוש:**

1. **`metadata.og_image` → cover-overlay ו-hero-bleed-fade.**
   זו "תמונת הכתבה" שדור בחר ידנית ב-WordPress. תמיד עדיפות לקאבר.
   - credit: בדוק את ה-`caption` של ה-`<img>` שתואם ל-og_image (לרוב לא קיים);
     אם אין — סמן `"צילום: המקום הכי חם בגיהנום"` או `"אילוסטרציה"` לפי
     ה-alt/title.

2. **`candidate_images` → split-text-photo, split-text-document.**
   עבור על הרשימה ובחר לפי alt/caption:
   - אם ה-alt/caption מכיל "מסמך / חותמת / החלטה / תיק / קלסר" →
     `split-text-document`
   - אם ה-alt/caption מכיל "צילום / סצנה / אירוע / הפגנה / מקום / מבנה" →
     `split-text-photo`
   - אם ה-alt/caption מכיל "Yonatan Sindel / FLASH90 / GPO / קישור" — זה
     credit; השתמש בו כ-credit עצמו.

3. **תמיד שמור credit מ-`caption` של ה-`<img>`.** ב-WordPress של ha-makom,
   ה-caption כולל את הקרדיט בפורמט "Discussion of X: Photographer/Source".
   חתוך לקרדיט בלבד (אחרי ":" האחרון).

---

### שכבה 3 — חיפוש באינטרנט (WebSearch + WebFetch)

**מתי משתמשים:**
- אם נשארו שקפים בלי תמונה (לאחר שכבות 1-2)
- במיוחד `split-text-cutouts` (דורש פורטרטים של דמויות), שלא תמיד יש בכתבה
- ל-`split-text-photo` כשהתמונות מהכתבה לא מתאימות

**איך מחפשים:**

#### למשל לתומר אייגס (cutout):
```
WebSearch: "תומר אייגס" סרן "פרשת אייגס" portrait
WebSearch: "Tomer Eiges" "8200" IDF officer
```
מקור מועדף (לפי סדר):
1. Wikipedia / ויקיפדיה — Creative Commons, חופשי
2. אתרי חדשות ראשיים (ynet, מקור ראשון, הארץ) — שמור credit "צילום: [אתר]"
3. פלאש 90 / GPO — קרדיט חובה: "צילום: [שם הצלם] / פלאש 90"
4. צילומי מסך מ-X/Twitter/Facebook של הדמות — קרדיט: "מתוך עמוד הX של [שם]"

#### לסצנה (split-text-photo):
```
WebSearch: "מתקני שב"כ" "חדר חקירות" צילום
WebSearch: "מבצע ארנון" נוסייראת חילוץ
```

#### למסמך (split-text-document):
```
WebSearch: "עתירת האגודה לזכויות האזרח" שב"כ "התחום האפור" 2023 צילום מסמך
WebSearch: "פסק דין בג"ץ" נוהל שב"כ הנשיא עמית site:gov.il
```

**אחר WebSearch:**
- `WebFetch` של URL התמונה (לעיתים קרובות צריך להוריד את ה-image source)
- שמור ל-`~/Documents/המקום/שיווק/hamakom-carousel/output/<slug>/sourced/`
- שמור גם metadata: URL מקורי, credit, חיפוש שהוביל אליו

**חשוב:** אל תשתמש בתמונות שכוללות:
- ילדים/קטינים שזוהו (אלא אם נחוץ לסיפור ולקח אישור)
- אזרחים פרטיים שלא רלוונטיים לכתבה
- תמונות מ-pixabay/unsplash גנריות שלא קשורות לסיפור (אלה זייפנים — לא נראה
  אמיתי)

---

### שכבה 4 — Adobe Firefly (תמונות AI)

**מתי משתמשים:**
- `split-text-concept` — תמיד דרך Firefly (זו המטרה של ה-block הזה)
- `split-text-document` — fallback אם לא נמצא מסמך אמיתי
- `cover-overlay` — fallback אם אין og_image וגם חיפוש לא הניב משהו

**איך קוראים ל-Firefly:**

הקריאה היא דרך MCP tool: `mcp__e545ab6b-f611-4bbb-a2e6-28aea05b4ff2__document_render_layout`
(שמייצר תמונה דרך Firefly). תיעוד ב-Adobe MCP.

**מבנה הפרומפט — תמיד הסגנון הקבוע של "המקום":**

```
[נושא ספציפי לפי השקף], dark cinematic editorial photography, deep navy and
charcoal blacks with selective accent red lighting, dramatic chiaroscuro,
high contrast, photojournalism aesthetic, no text, no faces visible,
9:5 aspect ratio, Israeli Hebrew journalism context
```

**דוגמאות מהשב"כ:**

| שקף | פרומפט |
|---|---|
| concept | `interior of high-tech intelligence command center, holographic shin bet logo floating above central console, operators in silhouette, surveillance screens, red accent lighting, dark cinematic editorial...` |
| document fallback | `worn green folder on dark desk with official Hebrew stamp visible, dramatic side lighting, top-down macro shot, dark cinematic editorial...` |
| cover fallback | `empty interrogation room with single bare lightbulb, weathered concrete walls, two empty chairs at metal table, dark cinematic editorial...` |

**אסור בפרומפט:**
- "Hebrew text" — Firefly לא יודע לכתוב עברית, ייצא ג'יבריש
- "people / faces / portrait" — נשמור פנים אמיתיים לדמויות אמיתיות
- צבעים אחרים (cream/amber/blue saturated) — שובר את הפלטה
- "logo X" של ארגון מסוים שיש לו זכויות יוצרים — להחליף ל-"abstract emblem inspired by X"

**credit ב-Firefly:** "אילוסטרציה: Adobe Firefly".

---

## קאטאוטים (background removal) — Adobe MCP

תמונות שמיועדות ל-`split-text-cutouts` חייבות לעבור הסרת רקע.

**MCP tool:** `mcp__e545ab6b-f611-4bbb-a2e6-28aea05b4ff2__image_remove_background`

**Flow:**
1. אסוף את התמונה (משכבה 2/3) — כקובץ מקומי או URL
2. קרא ל-image_remove_background עם ה-path
3. שמור את הפלט (PNG עם רקע שקוף) ב-`output/<slug>/cutouts/<name>.png`
4. השתמש ב-PNG הזה כקלט להעלאה לפיגמה

**Fallback אם אין Adobe MCP זמין:** שמור את התמונה המקורית, וב-Figma
הוסף instruction comment שדור יוכל להסיר רקע ידנית דרך Figma Plugin (כמו
"Remove BG" שיש כפיצ'ר ב-Figma).

---

## פורמט הפלט (לקריאת build_figma)

```json
{
  "slide_assignments": {
    "0": {
      "src": "https://www.ha-makom.co.il/wp-content/uploads/2026/05/Untitled-1024x560.png",
      "source": "og_image",
      "credit": "אילוסטרציה: בינה מלאכותית | המקום הכי חם בגיהנום",
      "needs_cutout": false,
      "downloaded_path": "/path/to/local/copy.png",
      "role": "hero-cover"
    },
    "1": {
      "src": "<same as 0>",
      "source": "og_image",
      "credit": "...",
      "needs_cutout": false,
      "role": "hero-reuse"
    },
    "4": {
      "src": "https://i0.wp.com/.../F250701YS12.jpg",
      "source": "candidate_images",
      "credit": "צילום: Yonatan Sindel / פלאש 90",
      "needs_cutout": false,
      "role": "scene",
      "alt": "דיון בעתירות שעניינן אופן מינוי ראש השב\"כ"
    },
    "5": {
      "people": [
        {"name": "תומר אייגס", "src": "...", "cutout_path": "/path/cutouts/eiges.png", "credit": "..."},
        {"name": "דוד זיני", "src": "...", "cutout_path": "/path/cutouts/zini.png", "credit": "..."},
        {"name": "בצלאל זיני", "src": "...", "cutout_path": "/path/cutouts/btsalel.png", "credit": "..."}
      ],
      "role": "cutouts"
    },
    "6": {
      "src": "<Firefly output URL or local path>",
      "source": "firefly",
      "credit": "אילוסטרציה: Adobe Firefly",
      "needs_cutout": false,
      "role": "concept",
      "prompt": "interior of high-tech intelligence command center..."
    },
    "7": {
      "src": "<...>",
      "source": "websearch | firefly fallback",
      "credit": "...",
      "role": "document"
    },
    "8": {
      "src": "<same as 0 — closing symbol reuses cover image>",
      "source": "og_image",
      "credit": "...",
      "role": "hero-reuse"
    }
  },
  "summary": {
    "total_slides_needing_images": 7,
    "manual": 0,
    "from_url": 3,
    "from_search": 1,
    "from_firefly": 3,
    "cutouts_processed": 3
  }
}
```

---

## כללי ברזל

1. **כל תמונה חייבת credit.** אם לא יודעים — `"מקור: לא ידוע"`. זה לא בסדר
   אבל לפחות מסומן.
2. **לא להשתמש באותה תמונה ב-2 slide blocks (חוץ מ-cover↔hero↔closing-symbol).**
3. **אין תמונות של קטינים** אלא אם הסיפור עוסק בהם והם זוהו פומבית (כמו
   במקרה אורי אלמקייס שזוהה אחרי שהיה קטין).
4. **תמונות פלאש 90 — credit חובה ובדיקת רישיון.** אם הכתבה ב-ha-makom
   משתמשת בתמונה של פלאש 90, ה-licensing כבר שולם — אז זה בסדר.
5. **תמונות Firefly — תמיד "אילוסטרציה: Adobe Firefly".**
6. **עדיפויות בעת קצרה:** og_image → ידני → candidate → search → Firefly.
   אם חסר זמן — להשתמש ב-og_image לכל מה שאפשר ו-Firefly לשאר.
