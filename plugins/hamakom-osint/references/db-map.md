# מפת osint-db - מקור אמת יחיד

מסמך העזר של כל סקילי `hamakom-osint` (וגם `hamakom-factcheck`, שקורא לאותו שרת). **אין לשכפל ספירות שורות, שמות עמודות או חוקי שאילתה לתוך SKILL.md** - כל סקיל מפנה לכאן. כך נמנעת הסחיפה שגילינו: סקילים שנכתבו בזמנים שונים החזיקו ספירות שונות ושמות עמודות שגויים.

נבדק מול ה-DB החי: **04.08.2026**. כל שורה כאן אומתה בהרצה, לא בהנחה.

---

## חוק הזהב: אין אגרגציה בלי WHERE

השרת קוטע כל שאילתה שחורגת מ-**מיליון צעדי VM של sqlite או 10 שניות** (`MAX_PROGRESS_CALLS × PROGRESS_EVERY` ב-`servers/osint-db/server.py`). המשמעות המעשית:

**נקטע (אומת בהרצה):**
```sql
SELECT supplier_names, COUNT(*), SUM(amount_ils) FROM exemptions
GROUP BY supplier_names HAVING COUNT(*) >= 5     -- 139K שורות, אין צמצום
```
```sql
SELECT publisher, COUNT(*), SUM(amount_ils) FROM exemptions GROUP BY publisher
```
```sql
SELECT supplier_name, SUM(volume) FROM budget_contracts GROUP BY supplier_name
```

**עובד מיד (אומת בהרצה):**
```sql
SELECT supplier_names, COUNT(*) deals, SUM(amount_ils) total FROM exemptions
WHERE publisher = 'משרד התחבורה והבטיחות בדרכים'   -- צמצום על עמודה מאונדקסת
GROUP BY supplier_names ORDER BY total DESC LIMIT 8
```

**הכלל:** כל `GROUP BY` חייב `WHERE` על עמודה מאונדקסת. אין "סקירה כללית של כל הטבלה" - יש סקירה של משרד, של שנה, של טווח סכומים. אם צריך תמונה רוחבית, הרץ כמה שאילתות מצומצמות וחבר את התוצאות בצד שלך.

`ORDER BY <עמודה מאונדקסת> ... LIMIT n` בלי `GROUP BY` עובד גם על הטבלאות הגדולות.

---

## עמודות מאונדקסות - נקודות הכניסה המותרות

זו הרשימה הקובעת. חיפוש על עמודה שאינה כאן, בטבלה גדולה, ייקטע.

| טבלה | שורות | נקודות כניסה מאונדקסות | מלכודת |
|---|---|---|---|
| `exemptions` | 139,233 | `publisher`, `exemption_type`, `pub_date`, `amount_ils` | **אין אינדקס על `supplier_names`.** `LIKE` עליה עובד (139K), אבל `GROUP BY` עליה נקטע |
| `budget_contracts` | 1,034,518 | `entity_id`, `publisher_name`, `volume` | **אין אינדקס על `supplier_name`. `LIKE '%ספק%'` עליה נקטע.** הכניסה היחידה היא `publisher_name=` או `entity_id=` |
| `budget_supports` | 329,578 | `recipient_entity_id`, `year`, `supporting_ministry`, `amount_approved` | **האינדקס הוא על ה-`recipient_entity_id`, לא על `recipient_entity_name`.** `LIKE` על השם בלי צמצום נקטע. צמצם קודם ב-`year=` או `supporting_ministry=` |
| `budget_items` | 9,005 | `year`, `code_level4` | קטנה, סובלנית |
| `budget_categories` | 45 | `year`+`depth`, `parent_code` | זעירה |
| `amutot` | 75,556 | `status`, `classification` | אין אינדקס על `name_he`, אבל `LIKE` עליה עובד (אומת). `GROUP BY` עליה - לא |
| `mavat_plans` | 36,796 | `district_name`, `plan_county_name`, `station_desc`, `depositing_date` | |
| `yosh_plans` | 2,569 | (קטנה, סובלנית) | |
| `mod_tenders` | 2,967 | `submission_date`, `publish_date`, `status` | |
| `knesset_vote_options` | **1,140,301** | `kmmbr_id`, `knesset_num`, `faction_id`, `vote_result` | חובה `WHERE vote_id=` ספציפי. ראה אזהרת העמודות למטה |
| `knesset_votes` | 32,281 | `knesset_num`, `vote_date`, `is_accepted` | |
| `news_headlines` | 21,527 | `pub_iso`, `outlet`, `category`, `sector` | |
| `mevaker_reports` | 145 | `pub_date` | `content_text LIKE` **עובד** (אומת) - 145 שורות בלבד |
| `legislation` | 287 | `ministry`, `is_open`, `pub_date` | |
| `decisions` | 429 | `pub_date`, `decision_number` | |
| `police_announcements` | 828 | `pub_date` | |
| `idf_spokesman` | 377 | `pub_date` | |
| `wp_articles` | 5,912 | (אין אינדקסים; קטנה) | **`category` ריק בכל 5,912 השורות** |

---

## אזהרות עמודות - שמות שנראים נכונים ואינם

אלה שגיאות שהיו בסקילים והופלו בהרצה:

- **`knesset_vote_options` - אין `mk_individual_id`.** העמודה היא `kmmbr_id`. `SELECT mk_individual_id FROM knesset_vote_options` מחזיר `no such column`. הטבלה כוללת גם `kmmbr_name` **ו-`faction_name`** - כלומר אין צורך ב-JOIN ל-`knesset_mk_individuals` או ל-`knesset_mk_positions` כדי לקבל שם וסיעה.
- **`mevaker_reports` - אין `ministry` ואין `type`.** העמודות: `id, title, url, pub_date, content_html, content_text, summary, first_seen_at, last_seen_at`. (זו גם באג פעיל ב-`search_entity` בשרת - ראה למטה.)
- **`wp_articles` - `category` קיים אבל ריק תמיד.** אל תסנן לפיו; הוא יתאים לאפס שורות בשקט.
- `knesset_mk_positions` מפתח לפי `person_id` (לא `mk_individual_id`).
- **`knesset_vote_options.faction_name` ריק בכנסת ה-25.** מאוכלס בהצבעות היסטוריות (נבדק: `vote_id` 20000-20100 מלא, 46000-46200 ריק בכל 8,508 השורות). אל תבנה פילוח סיעתי של הצבעה עכשווית עליו.

## מלכודת פורמט התאריך

**`yosh_plans.depositing_date` הוא `DD/MM/YYYY`** (למשל `10/05/2017`), בעוד **`mavat_plans.depositing_date` הוא ISO** (`2026-07-08`).

המשמעות: ב-`yosh_plans` כל `WHERE depositing_date >= '2026-05-01'` וכל `ORDER BY depositing_date DESC` **מחזירים זבל** - ההשוואה לקסיקוגרפית ולכן היום קודם לשנה. אומת: שאילתה על "90 הימים האחרונים" החזירה תוכניות מ-2014 ומ-2020.

הצורה הנכונה - המר בשאילתה:
```sql
substr(depositing_date,7,4)||'-'||substr(depositing_date,4,2)||'-'||substr(depositing_date,1,2) AS dep_iso
```
ואז `ORDER BY dep_iso DESC` או `WHERE dep_iso >= date('now','-90 days')`. עם ההמרה התוכניות האחרונות ביו"ש יוצאות אוגוסט 2026; בלעדיה 2014.

`decisions.decision_date` גם הוא בפורמט `DD.MM.YYYY` (למשל `09.04.2026`) - אותו זהירות. עמודות `pub_date` ו-`first_seen_at` ברוב הטבלאות הן ISO.

---

## עדכניות: איזו עמודה קובעת "חדש"

`pub_date` ריק בחלק גדול מהטבלאות. החתך לעדכניות הוא `first_seen_at`, וזה מה ש-`new_since` משתמש בו. אבל:

**אין `first_seen_at` בכלל (ולכן `new_since` מחזיר שגיאה):**
`news_headlines` (יש `scraped_at`), `election_polls` (יש `scraped_at`), `election_poll_seats`, `wp_articles` (יש `pub_date`).

**יש `first_seen_at` אבל הוא חסר משמעות:**
`budget_contracts`, `budget_supports`, `budget_items`, `budget_categories` - כולן נטענו ב-import חד-פעמי ב-24.07.2026, והחותמות הן שניות רצות של אותה טעינה. `new_since` עליהן יחזיר את **כל** הטבלה או **כלום**, לפי הצד של 24.07. אל תכלול אותן בלופ של דייג'סט יומי. `amutot` נטענה ב-24.07 ורועננה ב-02.08 - שני תאריכים בלבד.

---

## מצב הסקרייפרים - 04.08.2026

נשלף מ-`scrape_runs` (יש בה `source`; ראה חוק החלון למטה).

**חיים, הכניסו שורות חדשות היום:** `legislation`, `yosh`, `decisions`, `mavat`, `exemptions`, `police`.

**חיים ומעודכנים מאתמול:** כל זרוע הכנסת (`knesset`, `knesset_bills`, `knesset_committee_sessions`, `knesset_queries`, `knesset_session_items/documents/broadcasts`).

**תקועים - לא לבנות עליהם בלי אימות ידני:**

| מקור | ריצות | ריצה אחרונה | שורה חדשה אחרונה | כשלונות |
|---|---|---|---|---|
| `mevaker` (newsroom) | 1,985 | 04.08 | **09.05.2026** | 47 |
| `mevaker_reports` | 101 | **03.06.2026** | 26.05.2026 | 0 |
| `knesset_committees` | 325 | 04.08 | **07.07.2026** | 5 |
| `knesset_bill_initiators` | 331 | 04.08 | 29.07.2026 | 3 |
| `police` | 1,994 | 04.08 | 04.08 | 42 |
| `budget_*`, `amutot` | 3-4 | 02.08 | (dump, אין `new_count`) | 1 |

`mevaker` רץ כל שעה שלושה חודשים ומחזיר את אותן 10 שורות. `mevaker_reports` פשוט הפסיק לרוץ בתחילת יוני; הדוחות שבטבלה מגיעים עד 07.07 ונכנסו בדרך אחרת.

**פער נוסף:** ל-`knesset_votes` יש רשומות עד 28.07.2026, אבל פילוח פר-ח"כ ב-`knesset_vote_options` קיים רק עד **17.07**, ו-`total_for`/`total_against` ריקים בהצבעות האחרונות. פירוק הצבעה טרייה לא יעבוד.

---

## חוק חלון הזמן ב-scrape_runs

`scrape_runs` מכילה 18,751 ריצות של **כל המקורות מעורבבים**, עם עמודת `source`. לכן `SELECT * FROM scrape_runs ORDER BY rowid DESC LIMIT 10` מחזיר תערובת ואי אפשר לגזור ממנה חלון פר-טבלה. הצורה הנכונה:

```sql
SELECT started_at FROM scrape_runs
WHERE source = 'exemptions' AND status = 'ok'
ORDER BY started_at DESC LIMIT 2
```

שמות ה-`source` אינם זהים לשמות הטבלאות: `mavat` (לא `mavat_plans`), `yosh` (לא `yosh_plans`), `mevaker` (ל-newsroom) מול `mevaker_reports` (לדוחות), `knesset` (לכמה טבלאות יחד).

**`new_count` אינו מספר החדשים.** בכל הריצות שנבדקו הוא שווה ל-`row_count` (למשל 2569=2569), כלומר הוא סופר את מה שנסרק. לקביעת "מה חדש" השתמש ב-`new_since` על `first_seen_at`, לא בעמודה הזאת.

---

## search_entity - מה הוא באמת מכסה

הכלי סורק **7 טבלאות בלבד**: `exemptions`, `knesset_mk_individuals`, `legislation`, `mevaker_reports`, `mavat_plans`, `yosh_plans`, `decisions`.

**הוא עיוור ל:** `budget_contracts` (מיליון שורות), `budget_supports` (330 אלף), `amutot` (75 אלף), `mod_tenders`, `knesset_bills`, `police_announcements`, `idf_spokesman`, `news_headlines`, `wp_articles`.

לכן תיק ישות שנבנה על `search_entity` לבד **מפספס את מפתח התקציב וגיידסטאר לגמרי**, בלי להודיע. חובה להשלים ידנית מול הטבלאות האלה (ראה `osint-money`).

**שתי תקלות פעילות בכלי:**

1. **`exemptions` נקטע בשקט על מונח בלי התאמות מוקדמות.** הפלט מכיל אז `{"table": "exemptions", "note": "scan too broad (aborted)"}` - שורה אחת קטנה שקל לפספס. אם היא שם, **אין מסקנה** על פטורים; זה לא "אין התאמות". אומת עם המונח "הזדקנות האוכלוסייה".
2. **`mevaker_reports` מחזיר שדות זבל:** `"\"ministry\"": "ministry"` ו-`"\"type\"": "type"`, כי המפה בשרת מפנה לעמודות שלא קיימות. ההתאמה עצמה תקינה; התעלם מהשדות האלה.

---

## הרחבת שם-גג (חוזר מ-osint-entity-dossier)

גופים רבים אינם במאגר בשמם המוכר אלא תחת ארגון-האם. לפני שמסיקים "אין במאגר": נסה את הארגון שמעליו, שם רשום מלא עם ובלי "בע"מ", ראשי תיבות מול שם מלא. דוגמה מאומתת: "החטיבה להתיישבות" כמעט ריקה, "ההסתדרות הציונית העולמית" מחזירה מאות מיליונים - אבל אז חובה להפריד בתוצאות מה שייך לישות המבוקשת ומה זרוע אחרת.

---

## תקרות השרת

| מגבלה | ערך |
|---|---|
| שורות לשאילתה | 500 (`MAX_LIMIT`) |
| תווים בפלט | 50,000 |
| צעדי VM | ~1,000,000 |
| timeout | 10 שניות |
| כלים | `list_tables`, `describe_table`, `query_db`, `search_entity`, `new_since` |
| מצב | קריאה בלבד (`mode=ro`), `SELECT`/`WITH` בלבד |

---

## טבלאות שאינן מקורות תחקיר

`saved_items`, `user_follows`, `user_digests`, `user_digest_sources`, `user_alert_prefs`, `home_brief_cache`, `news_topics_cache` - מצב האפליקציה של משתמשי קונטקסט (מזוהות ב-`user_email`), לא דאטה ממשלתי. `scrape_items` ו-`scrape_sources` ריקות (0 שורות).
