---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__plugin_hamakom-osint_osint-db__search_entity mcp__plugin_hamakom-osint_osint-db__entity_profile mcp__plugin_hamakom-osint_osint-db__search_exemption_documents mcp__plugin_hamakom-osint_osint-db__read_exemption_documents mcp__plugin_hamakom-osint_osint-db__query_db mcp__plugin_hamakom-osint_osint-db__describe_table mcp__plugin_hamakom-osint_osint-db__source_status mcp__plugin_hamakom-osint_osint-db__search_text
name: osint-land
version: '0.2.0'
description: >-
  הקצאות קרקע של רשות מקרקעי ישראל (רמ"י) עבור דסק "המקום הכי חם בגיהנום" מעל ה-osint-db - rmi_allocations (51,974 הקצאות ורכישות שפורקו מפרסומי הפטורים: סוג עסקה, ייעוד, יישוב, שטח), rmi_allocation_refs (גושים-חלקות ומספרי תוכניות), מול תוכניות הבנייה (mavat_plans) ויישובי הגדה (wb_places). מי קיבל קרקע מהמדינה, איפה, לאיזה ייעוד ובאיזו תמורה, ועל איזו תוכנית. הפעל כשדור כותב "הקצאות קרקע", "רמ"י הקצתה", "מי קיבל קרקע ב", "חכירה בלי מכרז", "הרשאה לשימוש", "קרקע לקיבוץ", "הקצאות ברהט", "קרקע בהתנחלויות", "על איזו תוכנית הוקצתה הקרקע". כל פריט הוא ליד לבדיקה מול פרסום הפטור ב-mr.gov.il, לא ממצא מאומת. לתוכניות עצמן ראה osint-planning ו-osint-yosh-planning; לפטורים בכלל ראה osint-exemptions.
---

# osint-land - הקצאות הקרקע של רמ"י

רמ"י מפרסמת כל הקצאה בלי מכרז כ"פטור ממכרז" ב-mr.gov.il, ולכן ההקצאות יושבות בתוך `exemptions`. `rmi_allocation_terms.py` מפרק את הטקסט החופשי לשדות, ל-`rmi_allocations` (שורה לפטור) ול-`rmi_allocation_refs` (גושים וחלקות, מספרי תוכניות).

- **לפני "אין במאגר" או "לא סוקר":** לקרוא ל-`source_status` (בלי שם, או עם שם הטבלה או העיתון). מקור קפוא, חסום, באיחור או בתקלה, ועיתון שהוסר, שותק או שאין לו כותרות, הם חוסר שלנו: לכתוב זאת במפורש, ולא להסיק שהדבר לא קרה.

## עקרונות יסוד

1. **הקצאה אינה הוצאה, והכסף זורם אל המדינה.** בהקצאת קרקע התמורה משולמת **לרשות** (החלטת דור, 8.11.2026). ב-`exemptions` זה מסומן ב-`amount_kind`:
   - `rmi_consideration_incl_vat` (10,028 שורות): "תמורה כולל מע"מ" מתוך הטקסט.
   - `rmi_allocation_published` (33,766 שורות): "היקף כספי" שפורסם בשורת הקצאה.
   - `NULL`: הוצאה (רכש של רמ"י עצמה, `direction = 'procurement'`).
   לעולם לא סוכמים את התמורה של הקצאות יחד עם הוצאות ממשלה, ולא מדרגים לפיה כ"כסף שהמדינה שילמה".
2. **"ערך הקרקע" (`exemptions.land_value_ils`) הוא ערך שמאי, לא תשלום.** ותמורה של 0.00 היא אפס מילולי בפרסום (הקצאה לצורכי ציבור, אזור עדיפות), לא חסר.
3. **הקצאה בלי מכרז היא הליך מוסדר.** הרחבת מושב, נחלה, שיוך דירות ובנייה עצמית הם רוב הטבלה. הסיפור הוא בחריגה: שטח עצום בתמורה זניחה, ייעוד שאינו מתיישב עם הנמען, אותו נמען שחוזר, או הקצאה על תוכנית שאושרה סמוך לפני כן.
4. **`direction`:** `allocation` 50,331 שורות, `procurement` 1,338 (רכש של רמ"י), `unknown` 305.
5. **המפרק אינו מושלם.** `land_use` ריק ב-16,880 שורות ו-`locality` ב-7,489. ריק אינו "אין". השדות נקראים מהטקסט, ולכן כל מספר נבדק בטקסט המקורי (`exemptions.title`, `contract_purpose`, `reasoning`).
6. **אדם פרטי.** רמ"י כותבת לפעמים שם של חוכר פרטי. מספר זהות לעולם אינו מפתח קישור. אל תבנה רשימות של אנשים פרטיים.

## כלי קודם

- לנמען בשמו (מועצה, קיבוץ, חברה): `search_entity("שם")` ואחריו `entity_profile(id)`. הפטורים של רמ"י מופיעים בפרופיל תחת הפטורים, בלי סכום (כי זו תמורה ולא הוצאה).
- לטקסט המלא של פרסום: `read_exemption_documents("<מספר הפטור>")`. לחיפוש במסמכים המצורפים: `search_exemption_documents("חכירה ...")`.
- `query_db` לסריקה לפי יישוב, ייעוד, סוג עסקה, שטח ותוכנית.

**טריות:**
```sql
SELECT max(e.pub_date_iso) last_pub, max(r.parsed_at) last_parsed
FROM rmi_allocations r JOIN exemptions e ON e.id = r.exemption_id
WHERE e.pub_date_iso <= to_char(CURRENT_DATE,'YYYY-MM-DD')
```

## מלכודות - קרא לפני שאתה כותב SQL

| מלכודת | מה עושים |
|---|---|
| `rmi_allocations` מאונדקסת רק במפתח (`exemption_id`) | כל סינון סורק 52 אלף שורות. עם JOIN ל-`exemptions` השאילתה לוקחת 2-3 שניות. אל תוסיף עוד JOIN גדול |
| `area_sqm` במ"ר, וכולל שמורות טבע ומחצבים (שמורת מצוק צינים: 647 מיליון מ"ר) | מסננים לפי `deal_type` ו-`land_use` לפני מיון לפי שטח |
| `deal_type` בכמה כתיבים ("הרשאה לתיכנון" ו"הרשאה לתכנון") | `SELECT DISTINCT` קודם (למטה) |
| `locality` הוא שם כפי שנכתב בפרסום, כולל "מ.א. ..." | השוואה מדויקת לשם מתוך הרשימה, לא `LIKE` חופשי |
| `pub_date_iso` ריק בחלק מהשורות | גבול עליון `<= to_char(CURRENT_DATE,'YYYY-MM-DD')` ועליון ותחתון מפורשים |

## מצב א - מה הוקצה לאחרונה

סוגי העסקאות:
```sql
SELECT direction, deal_type, count(*) n FROM rmi_allocations GROUP BY 1,2 ORDER BY 3 DESC
```

ההקצאות של החודש האחרון:
```sql
SELECT e.id, e.pub_date_iso, e.title, e.supplier_names, r.deal_type, r.land_use, r.locality, r.area_sqm,
       e.amount_ils AS consideration_ils, e.amount_kind, e.detail_url
FROM rmi_allocations r JOIN exemptions e ON e.id = r.exemption_id
WHERE r.direction = 'allocation'
  AND e.pub_date_iso BETWEEN to_char(CURRENT_DATE - 30,'YYYY-MM-DD') AND to_char(CURRENT_DATE,'YYYY-MM-DD')
ORDER BY r.area_sqm DESC NULLS LAST
LIMIT 60
```
`consideration_ils` הוא התמורה לרשות כשיש `amount_kind`, לא הוצאה.

## מצב ב - יישוב או נמען

הקצאות ביישוב אחד:
```sql
SELECT e.id, e.pub_date_iso, e.title, e.supplier_names, r.deal_type, r.land_use, r.area_sqm,
       e.amount_ils AS consideration_ils, e.detail_url
FROM rmi_allocations r JOIN exemptions e ON e.id = r.exemption_id
WHERE r.locality = '<יישוב>'
ORDER BY e.pub_date_iso DESC NULLS LAST
LIMIT 60
```
היישובים עם הכי הרבה הקצאות (בראש: רהט, ערערה בנגב, תל שבע, באר שבע, שגב שלום):
```sql
SELECT locality, count(*) n, sum(area_sqm) area_sqm FROM rmi_allocations
WHERE direction = 'allocation' AND locality IS NOT NULL
GROUP BY 1 ORDER BY 2 DESC LIMIT 50
```

נמען לפי מספר רשם (אחרי `search_entity`):
```sql
SELECT e.id, e.pub_date_iso, e.title, r.deal_type, r.land_use, r.locality, r.area_sqm,
       e.amount_ils AS consideration_ils, e.detail_url
FROM exemptions e JOIN rmi_allocations r ON r.exemption_id = e.id
WHERE e.supplier_ids = '<מספר רשם>'
ORDER BY e.pub_date_iso DESC NULLS LAST
LIMIT 60
```

## מצב ג - הקצאה על תוכנית

`rmi_allocation_refs` מחזיקה 8,756 הפניות לתוכניות ו-16,799 לגוש-חלקה. מתוך 1,896 מספרי תוכניות, 692 נמצאים ב-`mavat_plans` באותו כתיב בדיוק. זה קישור משדה תומך, ולא לפי שם:
```sql
SELECT f.ref_value AS plan, m.pl_name, m.station_desc, m.depositing_date, m.plan_county_name,
       e.id, e.pub_date_iso, e.title, r.deal_type, r.area_sqm, m.pl_url
FROM rmi_allocation_refs f
JOIN mavat_plans m ON m.pl_number = f.ref_value
JOIN rmi_allocations r ON r.exemption_id = f.exemption_id
JOIN exemptions e ON e.id = f.exemption_id
WHERE f.ref_kind = 'plan' AND r.direction = 'allocation'
ORDER BY e.pub_date_iso DESC NULLS LAST
LIMIT 60
```
**אף מספר תוכנית לא נמצא ב-`yosh_plans` באותו כתיב** (0 מתוך 1,896, נמדד 20.11.2026). זה הבדל בכתיב, לא היעדר: ב-`yosh_plans` המספר נכתב עם קידומת ורווחים (`יוש/ 17/ 3/ 1/ 1/ 426`), ובפרסומי רמ"י בלעדיהם (`426/1/3/19`). אין היום קישור אמין בין השניים. תוכנית ביו"ש נבדקת ביד, ב-osint-yosh-planning.

כל ההקצאות על תוכנית אחת:
```sql
SELECT e.id, e.pub_date_iso, e.title, e.supplier_names, r.deal_type, r.land_use, r.area_sqm, e.detail_url
FROM rmi_allocation_refs f
JOIN rmi_allocations r ON r.exemption_id = f.exemption_id
JOIN exemptions e ON e.id = f.exemption_id
WHERE f.ref_kind = 'plan' AND f.ref_value = '<מספר תוכנית>'
ORDER BY e.pub_date_iso
```

## מצב ד - יישובים מעבר לקו הירוק

2,079 הקצאות נושאות שם יישוב שקיים ב-`wb_places`. בראש הרשימה ביתר עילית (190), מעלה אדומים (173), אריאל (111) ואורנית (100). בדגימה של 20.11.2026 אלה חכירות למוסדות ציבור, לתעשייה ולשיוך דירות. **ההתאמה היא לפי שם בלבד, ויש בה שגיאות שנמדדו:**
- "אבשלום" (65 הקצאות) הוא ב-`wb_places` יישוב לשעבר ברצועת עזה (`area = 'gaza'`). ההקצאות של רמ"י על השם הזה הן כנראה ליישוב אחר באותו שם, ונבדקות בפרסום.
- "מי עמי" מסווג ב-`wb_places` כהתנחלות.

לכן מסננים לפי `area` ובודקים כל יישוב בפרסום עצמו:
```sql
SELECT w.name_he, w.kind, w.area, count(*) n, sum(r.area_sqm) area_sqm
FROM rmi_allocations r JOIN wb_places w ON w.name_he = r.locality
WHERE w.area = 'west_bank'
GROUP BY 1,2,3 ORDER BY 4 DESC
LIMIT 40
```
נושא רגיש עריכתית: מדווחים עובדתית מהפרסום, מייחסים לרמ"י, ובלי מסגור טעון.

## שלב האימות

- `detail_url` של הפטור: נוסח הפרסום, הנמען, השטח והתמורה.
- התוכנית: `pl_url` במבא"ת.
- גוש-חלקה: `ref_kind = 'parcel'` בפורמט `1/גוש/חלקה`, לבדיקה במפות של רמ"י.

## אתיקה

רוב ההקצאות הן לאנשים ולקהילות שזכאים להן לפי ההחלטות של מועצת מקרקעי ישראל. אל תציג הקצאה כמתנה. ייחס כל נתון לפרסום הרשמי, ופנה לרמ"י ולנמען לפני פרסום.

## דוח הדסק - מבנה קבוע

```markdown
# לידים - קרקע

## טווח הסריקה
[יישוב / נמען / תוכנית, תקופה, מתי הפרסום האחרון נקלט]

## לידים מדורגים
לכל ליד:
- **ההקצאה:** [נמען, יישוב, סוג עסקה, ייעוד, שטח, תאריך]
- **התמורה:** [תמורה לרשות וערך קרקע, ומה מהם 0.00 מילולי]
- **החריגה:** [מה לא מתיישב]
- **עדיפות:** [גבוהה / בינונית / נמוכה] + מה הראיה החסרה
- **המקור:** [detail_url + השאילתה]

**שורה תחתונה לדסק:** [הליד שהכי בשל, ולמה]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר.
