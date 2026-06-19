# נכסי מותג — נתיבים ופתרון תקלות

כל הנתיבים תחת תיקיית Documents של דור (לבקש גישה עם request_cowork_directory אם אין).
בסיס: `Documents/המקום/שיווק/`

## לוגואים

| נכס | נתיב | שימוש |
|---|---|---|
| לוגו רוחבי לבן (PNG 600x178) | `שיווק/New-Logo White .png` (שים לב לרווח לפני הסיומת) | ווטרמרק עליון |
| לוגו מרובע (SVG, שחור) | `שיווק/hamakom square black.svg` | סגיר — לרסטר ולצבוע |

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
| Narkiss Shimshon Extended | `Desktop/NarkissShimshon-Extended.otf` | ציטוטים, כותרות, קיקרים |
| Narkiss Tam Regular/Medium | `שיווק/Bezalel Fonts/Narkiss_Fontef/NarkissTam-*.otf` | שורות "בתיעוד:" |
| DejaVu Sans (במערכת) | `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` | URL לטיני בלבד |

חשוב: לפונטים העבריים אין גליפים לטיניים — "ha-makom.co.il" בנרקיס ייצא ריבועים.

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
- בדיקת PIL: `from PIL import features; features.check('raqm')` חייב True
  (רינדור RTL). אם False — להשתמש ב-python-bidi עם get_display במקום direction='rtl'.
