# נכסי המותג — מקור אחד לכל סקילי העיצוב

כל סקילי `hamakom-visuals` (**graphic**, **carousel**, **reel**) מושכים נכסים **מכאן בלבד**.
עד 19.07.2026 הלוגו היה משוכפל פעמיים והפונטים שלוש פעמים, ולכן שינוי מותג היה
צריך לקרות בשלושה מקומות. עכשיו — במקום אחד.

**הנתיב מתוך סקיל:** `../../design-system/assets/…`
(כלומר `plugins/hamakom-visuals/design-system/assets/…` מתוך שורש הריפו).

---

## מה יש כאן

| נתיב | מה זה | שימוש |
|------|-------|--------|
| `logo/logo-square-black.svg` | הלוגו הריבועי הטיפוגרפי, וקטורי | פוטר בכל שקף (~50px) · CTA גדול בשנהב (~320×380) · ווטרמרק בריל |
| `logo/logo-wordmark-white.png` | wordmark לבן | לא בשימוש ב-CTA מאז 3.7.2026 — שמור לצרכים אחרים |
| `fonts/publicoheadlinehebrew-{roman,extrabold}.otf` | פונט התצוגה | כותרות קאבר, ציטוטים, מספרי-נתון, מחץ CTA |
| `fonts/graphikhlar-{light,regular,medium}.otf` | פונט הגוף/UI | פסקאות, byline, credit, url, כפתורים |
| `fonts/fontef-license-03515.pdf` | רישיון הפונטים | חברה עד 10 עובדים, מונפק ל"המקום הכי חם בגיהנום" |
| `video/closer_v3.mp4` | **הסגיר הקנוני של הרילים** | 1080×1920 · 30fps · **6.000 שניות בדיוק** (180 פריימים) |

**משקלים — שים לב:** Publico Headline מגיע ב-**Roman** (רגיל) ו-**Extrabold** (מחץ).
Graphik HLAR מגיע ב-**Light / Regular / Medium בלבד — אין SemiBold ואין Bold.** לכן
כל מה שהיה IBM Plex SemiBold/Bold ממופה עכשיו ל-Graphik Medium (התקרה). ה-resolver
בבילדרים עושה את הקלמפ אוטומטית.

**חוק ברזל:** לעולם לא לבנות את הלוגו מטקסט (`figma.createText`). תמיד
`figma.createNodeFromSvg()` על ה-SVG, או `upload_assets()` על ה-PNG.

---

## התקנת הפונטים (חד-פעמית, לכל מי שמריץ סקיל עיצוב)

Figma צריך את הפונטים **מותקנים במערכת**. מהריפו:

```bash
cp plugins/hamakom-visuals/design-system/assets/fonts/*.otf ~/Library/Fonts/
```

Figma רואה אותם **מיד אחרי ה-cp** — אין צורך ב-restart. אם הם חסרים, הסקילים
נופלים ל-Inter ומחזירים `font_fallback_used: true`. ה-resolver בבילדרים בוחר בזמן
ריצה בין הקיבוץ הטיפוגרפי (`Graphik HLAR` / Medium) לצורה המפוצלת (`Graphik HLAR
Medium` / Regular), כי לא ידוע מראש איזו מהן Figma חושף.

---

## רישיונות — לקרוא לפני הפצה

- **Publico Headline Hebrew** ו-**Graphik HLAR**: פונטים **מסחריים** של Fontef,
  **רישיון End-Use #03515** (מצורף כ-`fonts/fontef-license-03515.pdf`). הרישיון הוא
  **"חברה עד 10 עובדים"** מונפק ל"המקום הכי חם בגיהנום", ומכסה בדיוק את 5 המשקלים
  כאן (Publico Roman/Extrabold, Graphik Light/Regular/Medium). הצוות (מתחת ל-10) בתוך
  התחום. **הפצה בריפו הפרטי לחברי הצוות = בגדר הרישיון.** אם הצוות גדל מעל 10 או
  משתמשים חיצוניים — לוודא מול Fontef.
- **קבצי TRIAL:** אם מותקנים אצל מישהו פונטי גרסת-ניסיון (שם משפחה `... TRIAL`) —
  אלה **לא** הקבצים המורשים; ה-resolver מכוון לשמות הנקיים. אין למסור אותם.
- **פונטי הפלטה הישנה** (NarkissTam, NarkissShimshon, NextExit — מסחריים, פלטה
  שבוטלה) עדיין יושבים תחת `skills/*/assets/fonts/` מהיסטוריה. **אינם בשימוש; מומלץ להסיר.**

---

## שינוי מותג

צבעים, פונטים, פסי-חתימה ומפרטי שקפים — **`../HAMAKOM-DS-2026.md`** הוא מקור-האמת.
שינוי מותג = עריכת הקובץ ההוא + החלפת הקובץ כאן. **לא** עריכה של סקיל בודד.
