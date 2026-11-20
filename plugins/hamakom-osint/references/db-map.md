# מפת osint-db

**נבנה מהמאגר ב-20.11.2026** בסקריפט tools/build_db_map.py. הטבלה למטה נמדדת בכל בנייה; אין לערוך אותה ביד. המלכודות, בסוף, הן הידע שנכתב ביד.

## איך השרת מריץ שאילתה

- המאגר הוא Postgres. ה-MCP קורא ישירות ממנו, בתפקיד קריאה בלבד. אין SQLite ואין סנכרון לילי.
- `query_db`: SELECT או WITH אחד בלבד, עד 50 אלף תווים בפלט, ועד 10 שניות. שאילתה ארוכה יותר נקטעת בשגיאת timeout.
- `query_db` מחזיר 100 שורות כברירת מחדל. `LIMIT` בתוך ה-SQL לא מעלה את התקרה; כדי לקבל יותר מעבירים `limit` לכלי, עד 500.
- כלי קודם: `search_entity`, `entity_profile`, `legislation_history`, `search_exemption_documents`, `read_exemption_documents`, `new_since`. `query_db` רק למה שהם לא מחזירים. `describe_table()` מחזיר את רשימת הטבלאות, ו-`describe_table(name)` את העמודות של טבלה.
- לפני מסקנה של "אין במאגר": לבדוק ב-`scrape_runs` שהמקור רץ (`status IN ('ok','warn')`).

## הטבלאות

| טבלה | שורות | עמודות מאונדקסות | עמודת תאריך | השורה האחרונה | מצב |
|---|---|---|---|---|---|
| `exemptions` | 212,875 | `id`, `publisher`, `exemption_type`, `pub_date`, `amount_ils`, `enriched_at` | `pub_date_iso` | 2026-11-20 | פעיל |
| `budget_contracts` | 1,020,934 | `id`, `entity_id`, `publisher_name`, `order_id` | `order_date` | 2026-05-25 | פעיל |
| `budget_supports` | 329,580 | `id`, `recipient_entity_id`, `year`, `supporting_ministry` | `year` | 2025 | פעיל |
| `amutot` | 76,188 | `amuta_id`, `status`, `classification` | - | - | פעיל |
| `mavat_plans` | 37,576 | `pl_number`, `district_name`, `plan_county_name`, `station_desc`, `depositing_date` | `depositing_date` | 2026-10-19 | פעיל |
| `mavat_status_history` | 743 | `changed_at` | - | - | פעיל |
| `yosh_plans` | 2,632 | `pl_number`, `sector` | `depositing_date` | 2026-11-17 | פעיל |
| `yosh_status_history` | 114 | `changed_at` | - | - | פעיל |
| `mod_tenders` | 3,693 | `id`, `status` | `publish_date` | 2026-11-19 | פעיל |
| `gov_tenders` | 22,330 | `publication_id`, `publisher`, `status` | - | - | פעיל |
| `gov_tender_awards` | 10,652 | `publication_id`, `supplier_reg` | - | - | פעיל |
| `rmi_allocations` | 51,974 | `exemption_id` | - | - | פעיל |
| `knesset_bills` | 60,298 | `id`, `last_updated`, `knesset_num` | - | - | פעיל |
| `knesset_votes` | 37,055 | `vote_id`, `knesset_num`, `vote_date`, `is_accepted`, `sess_item_id` | `vote_date` | 2026-11-18 | פעיל |
| `knesset_vote_options` | ~2,270,687 | `vote_id`, `kmmbr_id`, `knesset_num`, `faction_id`, `vote_result` | - | - | פעיל |
| `knesset_mk_individuals` | 1,305 | `mk_individual_id` | - | - | פעיל |
| `knesset_mk_positions` | 17,430 | `id`, `person_id`, `knesset_num`, `is_current`, `committee_id` | - | - | פעיל |
| `knesset_queries` | 42,890 | `id`, `submit_date`, `person_id`, `gov_ministry_id` | - | - | פעיל |
| `knesset_protocol_attendees` | 547,650 | `doc_set`, `session_id`, `name` | - | - | פעיל |
| `legislation` | 7,499 | `id`, `ministry`, `is_open`, `pub_date`, `pub_date_iso` | `pub_date_iso` | 2026-11-19 | פעיל |
| `legislation_comments` | 159,465 | `comment_id`, `legislation_id`, `comment_date` | - | - | פעיל |
| `decisions` | 26,488 | `id`, `pub_date`, `decision_number` | `pub_date` | 2026-11-17 | פעיל |
| `gov_agendas` | 1,053 | `id`, `meeting_date` | `meeting_date` | 2026-11-11 | פעיל |
| `mevaker_reports` | 140 | - | `pub_date` | 2026-11-16 | פעיל |
| `mevaker_news` | 45 | `id`, `pub_date`, `topic` | `pub_date` | 2026-11-16 | פעיל |
| `mevaker_donations` | 112,396 | `id`, `election_type`, `donor_name`, `recipient`, `party`, `publication_date` | `publication_date` | 2026-10-29 | פעיל |
| `police_announcements` | 4,715 | `id`, `pub_date`, `channel` | `pub_date` | 2026-11-20T11:38:21 | פעיל |
| `idf_spokesman` | 20,507 | `id`, `url` | `pub_date` | 2026-11-20T12:02:29 | פעיל |
| `news_headlines` | 300,770 | `id`, `outlet`, `category`, `sector`, `url` | `pub_iso` | 2026-11-20T17:40:44 | פעיל |
| `wp_articles` | 6,008 | `post_id`, `author_id` | `pub_date` | 2026-11-08T08:00:00 | קפוא: האתר הוחלף; איסוף הכתבות מ-WP REST (local_news_wp_api.py) הוצא מהקרון ב-9.11.2026 |
| `ica_companies` | 733,995 | `company_id`, `name_he`, `status`, `registration_date`, `city` | `registration_date` | 2026-11-19 | פעיל |
| `ica_changes` | 688,775 | `company_id`, `company_name`, `request_type`, `status_date` | `status_date` | 2026-11-20 | פעיל |
| `maya_officers` | 21,530 | `id`, `name`, `company_name`, `position`, `person_id` | - | - | פעיל |
| `exemption_attachments` | 137,654 | `att_key`, `exemption_id`, `status`, `sha256` | - | - | פעיל |
| `scrape_runs` | 64,529 | `id`, `source` | `started_at` | 2026-11-20T17:40:01 | פעיל |

"~" הוא אומדן של Postgres לטבלה של יותר משני מיליון שורות.

---

## מלכודות (נכתב ביד, נבדק מול המאגר ב-20.11.2026)

### תאריכים
- `exemptions.pub_date` הוא DD/MM/YYYY, ובחלק גדול מהשורות ריק. למיון ולסינון: `pub_date_iso`.
- `legislation.pub_date` הוא DD/MM/YYYY; `legislation.pub_date_iso` מחושב במאגר.
- `yosh_plans.depositing_date` הוא DD/MM/YYYY, `mavat_plans.depositing_date` הוא ISO. השוואה של עמודת DD/MM לתאריך מחזירה זבל או שגיאה.
- `decisions.decision_date` הוא ISO.
- על כל עמודת תאריך טקסטואלית: `osint_date(col)` מחזיר ISO מכל הפורמטים, וזו הדרך הבטוחה. `date('now','-N days')` עובד ב-`query_db`, כי השרת מתרגם אותו לטקסט ISO לפי שעון ירושלים. ב-Postgres ישיר, מחוץ לשרת, הוא לא קיים.

### תאימות SQL
- השרת מתרגם רק את `date('now', ...)`, `datetime('now', ...)`, `strftime` ו-`group_concat`. כל השאר הוא Postgres: אין `instr` (`strpos`), אין `MAX(a,b)` סקלרי (`GREATEST`), אין `rowid`. ב-`string_agg(x, ' | ')` אפשר להשתמש ישירות.
- `ORDER BY x DESC` שם NULL ראשון. על עמודות סכום: `NULLS LAST`.
- שגיאות בנוסח Postgres: `column "x" does not exist`.

### "חדש" מול "נקלט"
- `first_seen_at` אומר מתי שורה נקלטה, לא מתי קרה האירוע. אחרי השלמה לאחור, שורות ישנות מקבלות חותמת טרייה. כל פריט "חדש" נבדק גם לפי עמודת התאריך שלו בטבלה למעלה.
- ב-`budget_supports` יש שני ערכים בלבד של `first_seen_at` (טעינה מרוכזת), ולכן `new_since` עליה אינו אומר דבר.
- ב-`news_headlines` אין `first_seen_at`; עמודת הזמן היא `pub_iso` (ו-`scraped_at`).
- `scrape_runs.new_count` אינו "כמה נוספו" אלא כמה שורות עברו בריצה.

### scrape_runs
- כל המקורות מעורבבים, עם עמודת `source`. תמיד לסנן לפי מקור, עם `status IN ('ok','warn')`.
- שמות ה-`source` אינם שמות הטבלאות: `mavat`, `yosh`, `police`, `mevaker` (הודעות), `mevaker_library_collector` (הדוחות).

### מקורות קפואים
- `wp_articles` ו-`wp_article_locations` קפואות מ-9.11.2026, בהחלטה: האתר הוחלף. `category` שם מלאה (6,007 מתוך 6,008). אין כתבות אחרי התאריך הזה, וזה לא סימן שלא כתבנו.
- `election_polls` קפואה מ-9.11.2026: הבחירות לכנסת ה-26 הסתיימו.

### כנסת
- ב-`knesset_vote_options` אין `mk_individual_id`. העמודות: `kmmbr_id`, `kmmbr_name`, `faction_name`, `mk_person_id`. תמיד עם `WHERE vote_id =`.
- `faction_name` ריק בחלק מהקולות בכנסת ה-25 (581 מלאים מתוך 1,017 ב-30 ההצבעות האחרונות שנבדקו). פילוח סיעתי של הצבעה עכשווית: לבדוק כמה ריקים לפני שמסיקים.
- אותו ח"כ יכול להופיע ב-`knesset_mk_individuals` בשתי שורות עם שני מזהים. בזיהוי לפי שם, לבדוק את כל השורות.

### תרומות לבחירות (mevaker_donations)
- סדר השם אינו עקבי ("חיימוב יצחק" מול "יצחק חיימוב"). לחפש לפי שם משפחה, ולקבץ לפי `donor_last` ו-`donor_city`.
- `donor_city` מכיל ישויות HTML לצד שמות רגילים. לנרמל לפני קיבוץ.
- `donor_country` הוא מחרוזת ריקה ולא NULL (11,816 שורות). תרומות חוץ: `donor_country NOT IN ('', 'ישראל')`.
- `election_date` ריק בפריימריז. את מערכת הבחירות גוזרים מאשכולות של `publication_date`.
- כ-1,000 קבוצות של שורות זהות (תורם, מקבל, סכום, תאריך). לפני סכום מצטבר: להציג אותן ולא לסכום בשקט.
- אין לקבוע שתרומה חרגה מהתקרה בלי נוסח החוק והנחיות המבקר לאותה מערכת.

### רשם החברות ומאיה
- אין בעלי מניות של חברות פרטיות במאגר. `maya_officers` היא נושאי משרה בחברות ציבוריות בלבד. לבעלי מניות של חברה פרטית: הסקיל `checkid-holders`.
- `ica_companies.is_violating` הוא מחרוזת: `'מפרה'` (188,636), `'התראה'` (30) או ריק. "מפרה" הוא מצב נפוץ, בדרך כלל אי-הגשת דוח שנתי, ולא סיפור בפני עצמו.
- `company_id` הוא מספר ב-`ica_companies` וטקסט ב-`ica_changes` וב-`ica_liquidations`. ב-JOIN להשוות כמחרוזת.
- `maya_officers.company_name` הוא שם מקוצר. ההצלבה ל-`ica_companies` היא `LIKE`, לא שוויון.

### שם גג
- גוף רבים יושבים במאגר תחת הארגון שמעליהם. לפני "אין במאגר": לנסות את הארגון שמעל, שם רשום מלא עם ובלי "בע"מ", ראשי תיבות וכתיב מלא וחסר ("התיישבות" מול "התישבות").

### טבלאות שאינן מקורות
- טבלאות האזור האישי והצ'אט של קונטקסט חסומות לכלים ואינן מקור תחקיר.
