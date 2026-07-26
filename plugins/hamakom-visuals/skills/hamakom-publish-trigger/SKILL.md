---
allowed-tools: Read Write Edit Bash Grep Glob WebFetch
name: hamakom-publish-trigger
description: >-
  הטריגר של "המקום הכי חם בגיהנום": כתבה פורסמה ב-ha-makom.co.il ← פותח תיקיית עבודה
  ומפעיל את סקילי הוויז'ואלס הקיימים בזה אחר זה — hamakom-graphic (3 גרפיקות),
  hamakom-carousel (קרוסלה), hamakom-reel (ריל). **הסקיל הזה לא מעצב כלום בעצמו** —
  הוא רק מזהה, מכין ומוסר. הפעל כשדור אומר "כתבה חדשה עלתה", "תפיץ את הכתבה",
  "תריץ את הטריגר", "תכין חומרים לרשתות", "תעשה הכל לכתבה הזו", או נותן URL של כתבה
  ומבקש את חומרי ההפצה. אם דור מבקש רק גרפיקה / רק קרוסלה / רק ריל — להפעיל את הסקיל
  הספציפי ישירות, לא את הטריגר.
---

# hamakom-publish-trigger — כתבה פורסמה, מפעיל את הכל

**חוק ראשון: הסקיל הזה לא מעצב, לא מרנדר ולא מגדיר פונטים.**
כל ההחלטות הוויזואליות חיות בסקילים הקיימים, והם מקור-האמת היחיד:

| סקיל | מה הוא בונה |
|---|---|
| `hamakom-graphic` | 3 גרפיקות בודדות — וואטסאפ 1:1 · פיד 4:5 · סטורי 9:16 |
| `hamakom-carousel` | קרוסלת אינסטגרם, 8-10 שקפים |
| `hamakom-reel` | ריל 9:16 (דורש חומרי גלם) |

אם נדרש שינוי עיצובי — **עורכים את הסקיל הרלוונטי או את
`design-system/HAMAKOM-DS-2026.md`, לעולם לא כאן.** שכפול לוגיקת עיצוב לתוך הטריגר
הוא באג, לא פיצ'ר: הוא נסחף מהמקור ומייצר שתי אמיתות.

## מה הטריגר כן עושה

1. **מזהה** כתבה חדשה ב-WordPress (עם `state.json` — לא מעבד פעמיים).
2. **פותח תיקיית עבודה**: `~/Desktop/הפצה/<תאריך>-<slug>/` עם `article.json`.
3. **מריץ את בדיקת ה-Downloads החוסמת** (חוק 5 ב-`hamakom-carousel`): מאתר קבצי
   פלאש 90 שדור הכין (`F<YYMMDD><XX><NNN>.jpg`), מזהה את הצלם לפי ראשי התיבות,
   וכותב `images.json`. **אלה המקור — לא להוריד תמונות מהאתר לפני הבדיקה הזו.**
4. **מוסר** — מדפיס את סדר הפעלת הסקילים.

## הרצה

```bash
S="$(ls -d ~/.claude/plugins/cache/hamakom-plugins/hamakom-visuals/*/skills/hamakom-publish-trigger/scripts 2>/dev/null | sort -V | tail -1)"
S="${S:-$HOME/Developer/hamakom-claude-plugins/plugins/hamakom-visuals/skills/hamakom-publish-trigger/scripts}"

python3 "$S/watch_published.py" --latest      # הכתבה האחרונה
python3 "$S/watch_published.py" --slug <slug> # כתבה ספציפית
python3 "$S/watch_published.py"               # כל מה שחדש מאז ההרצה הקודמת
```

אחרי שהתיקייה מוכנה — **הפעל את שלושת הסקילים לפי הסדר**, כל אחד על אותה תיקייה
ועם התמונות מ-`images.json`. כל סקיל מביא איתו את הכללים שלו; לקרוא אותו לפני הרצה.

## מה לא בסקיל הזה

- **קופי לרשתות** — פער נפרד. ה-DNA של הקאפשיינים יושב ב-`hamakom-distribute`.
- **תזמון ב-Hootsuite** — טיוטות בלבד, whitelist קשיח. ראה `hamakom-distribute`.
- **פרסום בפועל** — הסקיל לא שולח. דור מאשר ומפרסם.
