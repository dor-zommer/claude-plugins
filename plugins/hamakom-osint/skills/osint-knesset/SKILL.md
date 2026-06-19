---
allowed-tools: Read Grep Glob Bash WebSearch WebFetch TaskCreate TaskUpdate mcp__osint-db__list_tables mcp__osint-db__describe_table mcp__osint-db__query_db mcp__osint-db__search_entity mcp__osint-db__new_since
name: osint-knesset
description: פרופיילר כנסת מעל ה-osint-db עבור דסק "המקום הכי חם בגיהנום", בשלושה מצבים — (א) פרופיל ח"כ — שם ← פרטי הח"כ, תפקידים (סיעה/ועדה/תפקיד דרך knesset_mk_positions), חוקים שיזם (knesset_bill_initiators), והצבעות בולטות; (ב) מסלול הצעת חוק — knesset_bills לפי שם/מספר וסטטוס; (ג) פירוק הצבעה — knesset_votes לפי תיאור הסעיף + ספירת בעד/נגד/נמנע, ופילוח לכל ח"כ דרך knesset_vote_options (תמיד עם vote_id ספציפי כדי לא לסרוק 620 אלף שורות). מציף הצבעות חוצות-סיעה ומפתיעות. הפעל כשדור כותב "פרופיל ח\"כ", "מה X הצביע", "איזה חוקים X יזם", "תפרק לי את ההצבעה", "מי בעד ומי נגד", "מה הסטטוס של החוק", "מי יזם את ההצעה". כל פריט הוא ליד לבדיקה מול אתר הכנסת — לא ממצא מאומת. לתיק חוצה-תחומים על אותו אדם ראה osint-entity-dossier.
---

# osint-knesset — פרופיילר כנסת

סקיל לתחקיר נתוני הכנסת ב-osint-db בשלושה מצבים: פרופיל ח"כ, מסלול הצעת חוק, ופירוק הצבעה. התוצר הוא **לידים לבדיקה** — כל מספר ושם נבדק מול אתר הכנסת הרשמי לפני פרסום.

## עקרונות יסוד

1. **המאגר מחזיר רשומות גולמיות.** טבלאות הכנסת הן שיקוף; ייתכנו עיכובי עדכון או רשומות חלקיות. אמת כל ממצא מול אתר הכנסת לפני שהוא הופך לסיפור.
2. **אל תסרוק את knesset_vote_options בלי vote_id.** הטבלה מכילה ~620,800 שורות (הצבעה פר-ח"כ). כל שאילתה עליה חייבת `WHERE vote_id = <מספר>` ספציפי, אחרת היא תיקטע.
3. **סטטוס ומספרים זזים.** סטטוס הצעת חוק, ספירת הצבעה והרכב ועדה משתנים. ציין את תאריך/כנסת ההקשר, והצלב מול האתר הרשמי.
4. **הצבעה חוצת-סיעה היא ליד, לא סקופ.** ח"כ שהצביע נגד הקו הוא נקודת פתיחה לבדיקה (אולי טעות רישום, אולי היעדרות, אולי הצבעה אמיתית) — לא כותרת מוכנה.
5. **כשאי-אפשר לקבוע — הערך כיוון והסתברות.** לכל ממצא תן רמת ביטחון + מה הראיה החסרה שתכריע.

## מצב א — פרופיל ח"כ

כל השאילתות במצב זה רצות עם `query_db`. ל-זיהוי ראשוני אפשר גם `search_entity("שם")`, אבל ההעמקה (תפקידים, יוזמות, הצבעות) היא תמיד `query_db`.

**זיהוי הח"כ:**
```sql
SELECT mk_individual_id, mk_individual_name, mk_individual_name_eng, mk_individual_first_name
FROM knesset_mk_individuals
WHERE mk_individual_name LIKE '%שם%'
```
(נוח גם: `search_entity("שם")` מחזיר את ה-ח"כ בין שאר ההתאמות.)

**תפקידים — סיעה, ועדה, תפקיד, נוכחי או היסטורי:**
```sql
SELECT knesset_num, faction_name, committee_name, duty_desc, start_date, finish_date, is_current
FROM knesset_mk_positions
WHERE person_id = <mk_individual_id>
ORDER BY is_current DESC, start_date DESC
```

**חוקים שיזם:**
```sql
SELECT b.id, b.name, b.type_desc, b.sub_type_desc, b.status_id, b.publication_date
FROM knesset_bill_initiators i
JOIN knesset_bills b ON b.id = i.bill_id
WHERE i.mk_individual_id = <mk_individual_id>
ORDER BY b.publication_date DESC
```

**הצבעות בולטות** — אתר הצבעות שבהן הח"כ נמצא בצד המיעוט/חוצה-סיעה. סנן תמיד לפי vote_id ספציפי:
```sql
SELECT vote_id, mk_individual_id, vote_result
FROM knesset_vote_options
WHERE vote_id = <vote_id> AND mk_individual_id = <mk_individual_id>
```

## מצב ב — מסלול הצעת חוק

```sql
SELECT id, knesset_num, name, type_desc, sub_type_desc, private_number,
       committee_id, status_id, publication_date, last_updated
FROM knesset_bills
WHERE name LIKE '%שם החוק%'      -- או: WHERE id = <מספר>
ORDER BY last_updated DESC
```
ואז את היוזמים:
```sql
SELECT i.mk_individual_id, m.mk_individual_name
FROM knesset_bill_initiators i
JOIN knesset_mk_individuals m ON m.mk_individual_id = i.mk_individual_id
WHERE i.bill_id = <id>
```
תרגם את `status_id` למשמעות מול אתר הכנסת (טרומית / ועדה / קריאה ראשונה וכו') — המאגר מחזיק קוד, האתר את הניסוח הקנוני.

## מצב ג — פירוק הצבעה

**איתור ההצבעה והספירה הכוללת:**
```sql
SELECT vote_id, knesset_num, session_id, sess_item_dscr, vote_item_dscr,
       vote_date, vote_type, is_accepted, total_for, total_against, total_abstain
FROM knesset_votes
WHERE vote_item_dscr LIKE '%נושא ההצבעה%'
ORDER BY vote_date DESC
```
**פילוח פר-ח"כ — תמיד עם vote_id מההצבעה שמצאת:**
```sql
SELECT vote_id, mk_individual_id, vote_result
FROM knesset_vote_options
WHERE vote_id = <vote_id>
```
לחיבור שמות הצבע מול `knesset_mk_individuals` לפי `mk_individual_id`. לזיהוי חוצי-סיעה — הצלב את הצבעת הח"כ מול הסיעה שלו ב-`knesset_mk_positions` (is_current) וחפש מי הצביע נגד רוב סיעתו.

## שלב משותף — העשרה ואימות

אתר הכנסת הוא מקור האמת לאימות: דף ההצעה, פרוטוקול ההצבעה, ודף הח"כ. כל סטטוס, ספירה ויוזם — אמת מולו לפני פרסום. ציין את הכנסת ומספר ההצבעה/ההצעה כדי שהעורך יוכל לאמת בעצמו.

## התמודדות עם תקלות

| תקלה | פתרון |
|---|---|
| שאילתה על knesset_vote_options נקטעת | חובה WHERE vote_id = <מספר>; אל תסרוק את כל הטבלה |
| שם ח"כ לא נמצא | נסה שם חלקי / כתיב אחר / mk_individual_name_eng; הצלב VIP_id |
| כמה ח"כים עם שם דומה | הבחן לפי mk_individual_id; ציין במפורש איזה זוהה |
| status_id לא ברור | תרגם מול אתר הכנסת; אל תמציא ניסוח שלב |
| total_for+against+abstain לא מסתדר | ייתכנו נעדרים/נמנעים שלא נספרו; אמת מול פרוטוקול ההצבעה |
| publication_date ריק | השתמש ב-last_updated או first_seen_at לעדכניות |

**אסור:** להציג הצבעה חוצת-סיעה או סטטוס חוק כעובדה בלי אימות מול אתר הכנסת. רשומת המאגר היא ליד.

## אתיקה

ח"כים ופעילותם הפרלמנטרית הם נתון ציבורי מובהק וניתן לתחקור. עם זאת, הצבעה בודדת אינה עמדה מלאה, והיעדרות אינה תמיד התנגדות. ייחס לרשומה הרשמית, אל תקבע מניע, ותן לח"כ הקשר (תפקיד, סיעה, מועד) במקום מספר ערום.

## ניהול העבודה

פתח רשימת משימות (TaskCreate) לפי המצב: זיהוי הח"כ/החוק/ההצבעה, שליפת הנתונים, הצלבה וזיהוי החריגים, אימות מול אתר הכנסת. ציין את הכנסת ומספרי הזיהוי לאורך הדרך.

## דוח הדסק — מבנה קבוע

```markdown
# כנסת — [פרופיל ח"כ / מסלול חוק / פירוק הצבעה]

## מה נבדק
[שם הח"כ / שם ומספר החוק / נושא ומספר ההצבעה + הכנסת]

## הממצאים
[מצב א: פרטי הח"כ, תפקידים נוכחיים/היסטוריים, חוקים שיזם, הצבעות בולטות.
מצב ב: שלב נוכחי, יוזמים, ציר זמן.
מצב ג: ספירת בעד/נגד/נמנע, מי בצד המיעוט, חוצי-סיעה]

## הלידים המעניינים
[הצבעה חוצת-סיעה / סטטוס מפתיע / ריכוז יוזמות — כל אחד עם
רמת ביטחון ומה שיכריע]

## מה לאמת מול אתר הכנסת
[רשימת בדיקות: דף ההצעה, פרוטוקול ההצבעה, דף הח"כ]

**שורה תחתונה לדסק:** [הליד הכי מעניין כאן ומה חוסם אותו מסיפור]

Sources: [שאילתות osint-db עם ה-vote_id/bill_id + קישורי אתר הכנסת]
```

כתוב בעברית, בלי אימוג'ים, חד וקצר. הדוח צריך לאפשר לעורך להבין תוך דקה את התמונה הפרלמנטרית — בלי להגיש אף מספר או הצבעה כעובדה לפני אימות מול הכנסת.
