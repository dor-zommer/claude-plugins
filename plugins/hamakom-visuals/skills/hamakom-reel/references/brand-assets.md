# נכסי מותג — נתיבים ופתרון תקלות

## תיקיית החומרים הקבועה

**עודכן 19.07.2026 — הנכסים בריפו.** הלוגו, הפונטים והסגיר יושבים ב-
`design-system/assets/` של הפלאגין (ראה ה-README שם). אין יותר תלות בתיקייה
אישית בדסקטופ.

```bash
DS=$(ls -d ~/.claude/plugins/cache/hamakom-plugins/hamakom-visuals/*/design-system 2>/dev/null | sort -V | tail -1)
DS=${DS:-plugins/hamakom-visuals/design-system}
# $DS/assets/video/closer_v3.mp4 · $DS/assets/logo/ · $DS/assets/fonts/
```

**מה שנשאר מחוץ לריפו:** טראקי המוזיקה (WAV, 50MB) — אצל דור ב-
`~/Documents/המקום/שיווק/חומרים להכנת וידאו לרילז/`. התיקייה הזו מכילה:
- **closer_v3.mp4** — הסגיר הקנוני (1080×1920, 30fps, 6.00 שנ' = 180 פריימים,
  כולל פס סאונד). משתמשים בו כמות שהוא.
- **טראקים מוכנים** למוזיקת רקע (עדיפות ראשונה בשלב 7).

(העותק שהיה ב-`Desktop/סגיר וידאו המקום/` כבר לא שם — הנתיב הישן לא קיים.)

נכסי מותג נוספים תחת תיקיית Documents של דור (לבקש גישה עם
request_cowork_directory אם אין). בסיס: `Documents/המקום/שיווק/`

## לוגואים

| נכס | נתיב | שימוש |
|---|---|---|
| לוגו מרובע טיפוגרפי (SVG, שחור) | `שיווק/hamakom square black.svg` או `hamakom-carousel/assets/logo-square-black.svg` בפלאגין | **ווטרמרק עליון** (לבן ~72px, y≈48) + סגיר — לרסטר ולצבוע |
| לוגו רוחבי לבן (PNG 600x178) | `שיווק/New-Logo White .png` (שים לב לרווח לפני הסיומת) | לא בשימוש בריל (הווטרמרק הוא הריבועי) |

**רסטור מ-SVG עם cairosvg — לשמור על ערוץ האלפא ולצבוע רק RGB.**
המרה דרך לומיננס→אלפא שגויה: פיקסלים שקופים הם RGB=0 ולכן מתקבל ריבוע מלא.

המרת ה-SVG המרובע ללבן-שנהב:
```python
import cairosvg, numpy as np
from PIL import Image
cairosvg.svg2png(url='sq.svg', write_to='sq.png', output_width=700)
a = np.array(Image.open('sq.png').convert('RGBA'))
a[...,0]=240; a[...,1]=238; a[...,2]=230   # שנהב, אלפא נשמר
Image.fromarray(a).save('sq_ivory.png')
```
(`pip install cairosvg --break-system-packages` בסביבה נקייה.)

## פונטים

| פונט | נתיב | שימוש |
|---|---|---|
| **Suez One** (DS תצוגה) | Google Fonts — `ofl/suezone/SuezOne-Regular.ttf` | **ציטוטים — בלבן #ffffff בלבד**, כותרות |
| **IBM Plex Sans Hebrew** (DS גוף) | Google Fonts — `ofl/ibmplexsanshebrew/IBMPlexSansHebrew-*.ttf` | קיקר (Bold 30), "בתיעוד:" (Regular 34), URL (SemiBold — יש גליפים לטיניים) |
| ~~Narkiss Shimshon Extended~~ | `Desktop/NarkissShimshon-Extended.otf` | **ירד — לא בשימוש לציטוטים** (החלטת דור 3.7.2026) |
| DejaVu Sans (במערכת) | `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` | URL לטיני fallback |

ברירת-המחדל היא **DS 2026**: Suez One + IBM Plex Sans Hebrew (ראה
`../../design-system/HAMAKOM-DS-2026.md`). התקנה:
```bash
curl -sL "https://github.com/google/fonts/raw/main/ofl/suezone/SuezOne-Regular.ttf" -o /tmp/SuezOne-Regular.ttf
B="https://github.com/google/fonts/raw/main/ofl/ibmplexsanshebrew"
for w in Regular Medium SemiBold Bold; do curl -sL "$B/IBMPlexSansHebrew-$w.ttf" -o "/tmp/IBMPlexSansHebrew-$w.ttf"; done
cp /tmp/SuezOne-Regular.ttf /tmp/IBMPlexSansHebrew-*.ttf ~/Library/Fonts/
```
IBM Plex Sans Hebrew מכסה גם לטינית — "ha-makom.co.il" ייצא תקין.

## בעיית iCloud — קבצים ריקים / Resource deadlock

חלק מהקבצים בתיקיות הם placeholders של iCloud: גודל 0 בייט, או שהעתקה נכשלת עם
`Resource deadlock avoided`. **תמיד לוודא אחרי העתקה:** `[ -s file ]` ולנסות לטעון
ב-PIL (`ImageFont.truetype`). אם נכשל:
- פונטים: `Narkiss_Fontef/` היא התיקייה האמינה (הקבצים ב-`Classics/NarkisTam/`
  וב-`VC_classics/` לרוב ריקים). fallback נוסף: `VC_NarkisBlock-Bold.otf` תחת
  `Classics/NarkisBlock/`.
- לוגו: עותקים נוספים ב-`Documents/Media/logo.png`. אפשר גם לחלץ מריל קודם
  בתיקיית outputs.
- אם שום עותק לא נגיש — לומר לדור איזה קובץ חסר ולבקש שיעלה אותו לצ'אט.

## סביבת העבודה

- עבודה ב-`/tmp/vid/` (מהיר). תוצרים סופיים בלבד ל-outputs.
- **הסביבה מתאפסת בין סשנים ולפעמים באמצע** — `/tmp` נמחק כולל סקריפטים וקבצי
  ביניים. אם `/tmp/vid` נעלם: להתקין מחדש pip packages, להעתיק מחדש פונטים ולוגואים,
  ולהריץ שוב את הסקריפטים מהסקיל. תוצרי ביניים ששמרת ב-outputs שורדים.
- **רינדור RTL: אין libraqm במק של דור** (`from PIL import features;
  features.check('raqm')` = False). בכל סקריפטי הטקסט משתמשים ב-python-bidi
  (`bidi.algorithm.get_display`) ומסירים `direction='rtl'`/`'ltr'` —
  אחרת ValueError. עברית עם גרש — גרש עברי ׳ (U+05F3), לא אפוסטרוף לטיני.

## ElevenLabs (מוזיקה — עדיפות 2)

- מפתח API: `ELEVENLABS_API_KEY` ב-`~/Developer/video-use/.env` (hex גולמי,
  בלי `sk_`). אין קונקטור MCP — עובדים ב-curl.
- מפתחות שמופיעים בהיסטוריית settings.local.json — **פגי תוקף**; התקף רק
  ב-`video-use/.env`.
