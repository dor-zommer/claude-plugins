# Build Figma Simple — בילדר קרוסלה (HaMakom DS 2026)

> **תקן 2026** — הקוד הזה אומת חזותית מול דור (קרוסלת "בנט / הסכסוך הוא לא רסיס", יוני 2026).
> **קרא קודם** את `design-system/HAMAKOM-DS-2026.md` (מקור-האמת) ואת SKILL.md.
> פלטה: שנהב/דיו/טרקוטה. פונטים: Suez One + IBM Plex Sans Hebrew.
> פס-חתימה טריקולור **תחתון יחיד, 4px** בכל שקף (דרך `FOOT`) — אין פס עליון.
> **הפלטה הישנה (שחור/אדום `#f70d28` + NextExit/Narkiss Tam) בוטלה.**

---

## תהליך עבודה — צ׳ק-ליסט

```
[ ] שלוף את הכתבה (WP REST: /wp-json/wp/v2/posts?slug=<slug>&_embed)
[ ] חלץ: h1 verbatim, byline, פסקאות גוף, og/featured image, נתון-מחץ, ציטוט סיום
[ ] תמצת ל-8-10 שקפים: בחר את קו הסיפור, השמט פרוצדורה/תגובות מלאות/רקע משני
      ~300-450 תווים לשקף · השמטת משפטים מותרת · שכתוב משפט שנשאר — אסור
[ ] *** חוסם *** בדוק תמונות מקומיות לפני כל הורדה מהרשת:
      ls -t ~/Downloads | head -25          ← קבצי F<YYMMDD><XX><NNN>.jpg = פלאש 90 של דור
      ls -d ~/Downloads/*<שם-הכתבה>*        ← תיקייה על שם הכתבה = ייצוא קודם, לא מקור
      ls ~/Documents/המקום/
[ ] הקטן מקורות גדולים: sips -Z 2560 <file>  (מגבלת upload 10MB)
[ ] התקן Suez One + IBM Plex Sans Hebrew אם חסרים (ראה DS §2)
[ ] צור Figma file: create_new_file editorType=design
[ ] use_figma → בנה Carousel: cover + PS/PSData + IMG (עם quote בסיום) + CTA
[ ] upload_assets: hero → cover-hero-image (הלוגו ב-CTA הוא הריבועי מ-SVG — לא צריך upload)
[ ] get_screenshot ל-QA (cover + פסקה + דאטה + CTA)
[ ] הצע קאפשיין לפוסט
```

**קרדיטים לפי ראשי התיבות בשם קובץ פלאש 90** (`F<YYMMDD><XX><NNN>.jpg`):

| קוד | צלם | קרדיט מלא |
|-----|-----|-----------|
| `CG` | חיים גולדברג | צילום: חיים גולדברג/פלאש 90 |
| `YS` | יונתן סינדל | צילום: יונתן סינדל/פלאש 90 |
| `TN` | תומר נויברג | צילום: תומר נויברג/פלאש 90 |

---

## פלטה + פונטים — prelude (תמיד אותו)

```javascript
const C = {
  bg:{r:0.9804,g:0.9765,b:0.9608}, paper:{r:0.9529,g:0.9451,b:0.9176},
  ink:{r:0.0784,g:0.0784,b:0.0745}, ink2:{r:0.2314,g:0.2275,b:0.2118}, inkSoft:{r:0.4196,g:0.4157,b:0.3882},
  terra:{r:0.851,g:0.4667,b:0.3412}, terraDeep:{r:0.6118,g:0.2706,b:0.1529}, terraCta:{r:0.7608,g:0.3373,b:0.1843},
  sage:{r:0.4706,g:0.549,b:0.3647}, heather:{r:0.5569,g:0.4353,b:0.6588},
  scTerra:{r:0.9098,g:0.5647,b:0.4353}, onDarkSoft:{r:0.7176,g:0.7098,b:0.6745}, white:{r:1,g:1,b:1},
};

let HEAD="Inter", BODY="Inter";
const fonts = await figma.listAvailableFontsAsync();
if (fonts.some(f => f.fontName.family === "Suez One")) HEAD = "Suez One";
if (fonts.some(f => f.fontName.family === "IBM Plex Sans Hebrew")) BODY = "IBM Plex Sans Hebrew";
for (const fn of [{family:HEAD,style:"Regular"},{family:BODY,style:"Regular"},
  {family:BODY,style:"Medium"},{family:BODY,style:"SemiBold"},{family:BODY,style:"Bold"}])
  { try{ await figma.loadFontAsync(fn);}catch(e){} }
const fontFallback = (HEAD==="Inter" || BODY==="Inter");
```

---

## Helpers — תמיד אותם

```javascript
const LOGO_SVG = `<svg ...>`; // קופי מלא מ-assets/logo-square-black.svg (single-line) — ראה build_figma.md

function NF(name, bg){ const f=figma.createFrame(); f.name=name; f.resize(1080,1350); f.y=0;
  f.fills=[{type:"SOLID",color:bg||C.bg}]; f.clipsContent=true; return f; }

function R(o){ const r=figma.createRectangle(); r.x=o.x; r.y=o.y; r.resize(o.w,o.h);
  if(o.fills) r.fills=o.fills; else r.fills=[{type:"SOLID",color:o.color,opacity:o.opacity==null?1:o.opacity}];
  if(o.cornerRadius!=null) r.cornerRadius=o.cornerRadius; return r; }

async function T(o){ const t=figma.createText();
  try{t.fontName={family:o.family,style:o.style};}catch(e){t.fontName={family:BODY,style:"Regular"};}
  t.fontSize=o.size; if(o.lhPct) t.lineHeight={unit:"PERCENT",value:o.lhPct};
  if(o.letterSpacing!=null) t.letterSpacing={unit:"PIXELS",value:o.letterSpacing};
  t.characters=o.chars; t.textAlignHorizontal=o.align; t.fills=[{type:"SOLID",color:o.color}];
  t.x=o.x; t.y=o.y; t.resize(o.w,t.height); return t; }

// פס-חתימה טריקולור — ימין טרקוטה, מרכז מרווה, שמאל אברש.
// נקרא פעם אחת בלבד לשקף: תחתון, h=4, בקצה התחתון (y=1346). אין פס עליון.
function SIG(f,y,h){ f.appendChild(R({x:720,y,w:360,h,color:C.terra}));
  f.appendChild(R({x:360,y,w:360,h,color:C.sage})); f.appendChild(R({x:0,y,w:360,h,color:C.heather})); }

function LOGO(f,fill,x,y,size){ const n=figma.createNodeFromSvg(LOGO_SVG); if("fills" in n) n.fills=[];
  const rec=(z)=>{ if(["VECTOR","BOOLEAN_OPERATION","POLYGON","RECTANGLE"].includes(z.type)){ if("fills" in z) z.fills=[{type:"SOLID",color:fill}]; } if("children" in z) z.children.forEach(rec); };
  rec(n); const w=size*(826.779/981.533); n.resize(w,size); n.x=x; n.y=y; n.name="logo"; f.appendChild(n); }

async function FOOT(f,dark){ const fg=dark?C.onDarkSoft:C.inkSoft;
  LOGO(f, dark?C.white:C.ink, 952, 1244, 50);
  f.appendChild(await T({chars:"HA-MAKOM.CO.IL",family:BODY,style:"SemiBold",size:21,color:fg,x:400,y:1262,w:520,align:"RIGHT",letterSpacing:3}));
  SIG(f,1346,4); }
```

---

## קאבר (image, full-bleed)

הטקסט ממוקם **מלמטה למעלה** (byline → title) כך שהכותרת נמוכה ככל שניתן,
והגרדיאנט מחושב לפי מיקום הכותרת בפועל — כדי שלא יסתיר את התמונה
(~65-70% העליונים נשארים גלויים לחלוטין).

**בוטל 19.07.2026: הקיקר/lede בקאבר.** הקאבר נושא **שני אלמנטים בלבד** — כותרת
(h1 verbatim, גם כשהיא ציטוט) ו-**byline = שם הכותב/ת בלבד** ב-ink-soft. אין משנה,
אין lede, אין תגית קטגוריה.

```javascript
const HERO = "<imageHash מה-upload>";
const cover=NF("00-cover",C.ink); cover.x=0;
const hImg=R({x:0,y:0,w:1080,h:1350,color:C.ink}); hImg.name="cover-hero-image";
hImg.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:HERO}]; cover.appendChild(hImg);
// טקסט — מלמטה למעלה: byline קבוע, כותרת ~16px מעליו, קיקר-lede ~14px מעל הכותרת
const byline=await T({chars:BYLINE, family:BODY, style:"Medium", size:25, color:C.inkSoft, x:80, y:1154, w:920, align:"RIGHT"});   // שם בלבד: "סיון תהל"
cover.appendChild(byline);
const title=await T({chars:TITLE, family:HEAD, style:"Regular", size:64, color:C.white, x:80, y:0, w:920, align:"RIGHT", lhPct:108}); // h1 verbatim (Suez One)
title.y = byline.y - 16 - title.height;                                     // הכותרת נמוכה ככל שניתן — ממש מעל ה-byline
cover.appendChild(title);
// אין קיקר/lede/משנה — הקאבר נושא כותרת + byline בלבד (19.07.2026)
// gradient דיו מצומצם — לפי מיקום הכותרת בפועל; מוזרק מעל התמונה, מתחת לטקסט
const lf = title.y / 1350;
const grad=R({x:0,y:0,w:1080,h:1350,color:C.ink});
grad.fills=[{type:"GRADIENT_LINEAR",gradientTransform:[[0,1,0],[-1,0,1]],gradientStops:[
  {position:0,color:{...C.ink,a:0}},{position:Math.max(0.01,lf-0.07),color:{...C.ink,a:0}},   // שקוף לחלוטין עד ~7% מעל הכותרת
  {position:lf,color:{...C.ink,a:0.72}},{position:1,color:{...C.ink,a:1}}]}];                 // אלפא מלא רק בתחתית
cover.insertChild(1,grad);
// שורת תחתית צמודה לפס: credit שמאל + url ממורכז; לוגו קטן ממורכז מעליהם
const cr=await T({chars:CREDIT, family:BODY, style:"Regular", size:18, color:C.white, x:18, y:1315, w:360, align:"LEFT"});
cr.fills=[{type:"SOLID",color:C.white,opacity:0.53}]; cover.appendChild(cr);
cover.appendChild(await T({chars:"HA-MAKOM.CO.IL",family:BODY,style:"SemiBold",size:21,color:C.onDarkSoft,x:295,y:1313,w:490,align:"CENTER",letterSpacing:3}));
LOGO(cover,C.white,519,1244,50);  // לוגו קטן ממורכז — לא בפינה
SIG(cover,1346,4);   // פס-חתימה תחתון יחיד — אין פס עליון
figma.currentPage.appendChild(cover);
// כותרת דינמית: ≤30 תווים→72 ; 30–50→64 ; 50+→56
```

---

## שקף-פסקה — שנהב, IBM Plex, מיושר-לעליון

**בלי קיקר קטגוריה ובלי אינדקס `NN / TOTAL`** (בוטלו 19.07.2026 — דור הסיר אותם מקרוסלת
מח"ש–מכת"ז). הסימן היחיד בראש השקף הוא **קו הטרקוטה הקצר**. אין `total` ואין `kicker`
בחתימת הפונקציה — הם לא מתקבלים ולא נוצרים.

```javascript
const BODY_PT = 48;   // 45-50 — טווח התקן שנקבע בקרוסלת מח"ש

async function PS(idx, text, xPos){
  const num=String(idx).padStart(2,"0");
  const f=NF(`${num}-paragraph`); f.x=xPos;   // פס-חתימה תחתון בלבד — מגיע מ-FOOT
  f.appendChild(R({x:936,y:148,w:64,h:4,color:C.terra}));   // קו טרקוטה קצר — הסימן היחיד בראש
  const body=await T({chars:text,family:BODY,style:"Regular",size:BODY_PT,color:C.ink,x:80,y:182,w:920,align:"RIGHT",lhPct:160});
  body.textAutoResize="HEIGHT"; body.resize(920,body.height);
  let s=BODY_PT; while(body.height>1020 && s>30){ s-=2; body.fontSize=s; body.resize(920,body.height); }
  f.appendChild(body);          // מיושר-לעליון (y=182), לא ממורכז אנכית
  await FOOT(f,false);
  figma.currentPage.appendChild(f);
  return f.id;
}
```

**מילוי השקף (חוק 19.07.2026 — גובר על הכלל הקודם):** **~300-450 תווים לשקף.**
השקף מחזיק **תמצית**, לא פסקה מלאה: משמיטים משפטי המשך, ציטוטים משניים ופירוט פרוצדורלי.
**מה שנשאר — בלשון הכותב מילה במילה; אסור לשכתב משפט שנשאר.** auto-shrink רק אם חורג.
(היעד הקודם, 600-900 תווים, נגזר מחוק ה-verbatim שבוטל.)

---

## שקף-פסקה עם נתון (`PSData`) — הנתון בתוך הטקסט, לא לבדו

**`DSlide` כשקף עצמאי בוטל (19.07.2026).** בקרוסלה שדור פרסם הנתון לא עמד לבדו — הוא ישב
**בתוך** שקף הטקסט שמדבר עליו. שקף נתון נפרד קטע את הקריאה והוסיף שקף שלא היה צריך.

המבנה: פסקה מתומצתת → **מספר ענק Suez One בטרקוטה** → **שורת פירוט IBM Plex Bold**.
זה המקום היחיד (יחד עם שורות נתון) שבו Bold מותר.

```javascript
// גודל המספר מותאם לאורכו: קצר ("6/45") ענק; מחרוזת ארוכה קטנה יותר.
function numSize(s){ const n=String(s).length; return n<=4?200 : n<=6?170 : n<=9?140 : 110; }

async function PSData(idx, text, number, detail, xPos){
  const num=String(idx).padStart(2,"0");
  const f=NF(`${num}-psdata`); f.x=xPos;
  f.appendChild(R({x:936,y:148,w:64,h:4,color:C.terra}));
  const body=await T({chars:text,family:BODY,style:"Regular",size:BODY_PT,color:C.ink,x:80,y:182,w:920,align:"RIGHT",lhPct:160});
  body.textAutoResize="HEIGHT"; body.resize(920,body.height);
  let s=BODY_PT; while(body.height>560 && s>30){ s-=2; body.fontSize=s; body.resize(920,body.height); }
  f.appendChild(body);
  // הנתון יושב מתחת לפסקה, לא בשקף משלו
  const big=await T({chars:number,family:HEAD,style:"Regular",size:numSize(number),color:C.terra,x:40,y:0,w:1000,align:"CENTER",lhPct:100});
  big.y = body.y + body.height + 60;
  f.appendChild(big);
  f.appendChild(await T({chars:detail,family:BODY,style:"Bold",size:32,color:C.ink,x:80,y:big.y+big.height+24,w:920,align:"CENTER",lhPct:140}));
  await FOOT(f,false);
  figma.currentPage.appendChild(f);
  return f.id;
}
```

---

## שקף-תמונה (photo) — full-bleed לתמונות רגילות

**נוסף 19.07.2026.** לתמונות עיתונאיות רגילות (פלאש 90, פורטרטים, תמונות הקשר) —
full-bleed FILL עם כיתוב. **זה לא שקף ראיה:** `ISlide` נשאר **לצילומי מסך בלבד**
(FIT ללא קרופ, "שימוש לפי סעיף 27א׳"). שקפי `IMG` **לא נספרים כראיה**.

שקפי התמונה **משתלבים בין הפסקאות במיקום ההגיוני בנרטיב** — ליד הפסקה שמדברת על
מה שרואים — ולא נערמים בסוף. **חוק אי-הכפילות חל:** אותה תמונה לא מופיעה בשני שקפים.

**פרמטר `quote` אופציונלי (19.07.2026):** ציטוט עדות חזק — בעיקר ציטוט הסיום של הקרוסלה —
נישא על התמונה ולא על שקף טקסט נפרד. כשיש ציטוט: הוא נכתב ב-**45pt לבן באזור
תחתון-אמצעי**, וה**כיתוב עולה לראש השקף** (y≈62) כדי לפנות לו את התחתית.

```javascript
async function IMG(idx, imageHash, caption, credit, xPos, quote){
  const num=String(idx).padStart(2,"0");
  const f=NF(`${num}-photo`,C.ink); f.x=xPos;
  const img=R({x:0,y:0,w:1080,h:1350,color:C.ink}); img.name=`photo-${num}`;
  img.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash}]; f.appendChild(img);
  let anchorY;   // הגובה שממנו הגרדיאנט מתחיל להתעבות
  if (quote){
    // ציטוט עדות: 45pt לבן, אזור תחתון-אמצעי; הכיתוב עולה לראש השקף
    const q=await T({chars:quote,family:BODY,style:"SemiBold",size:45,color:C.white,x:80,y:0,w:920,align:"RIGHT",lhPct:145});
    q.y = 1244 - 40 - q.height;
    f.appendChild(q);
    f.appendChild(await T({chars:caption,family:BODY,style:"SemiBold",size:26,color:C.white,x:80,y:62,w:920,align:"RIGHT",lhPct:140}));
    anchorY = q.y;
  } else {
    // בלי ציטוט: כיתוב מעל שורת התחתית
    const cap=await T({chars:caption,family:BODY,style:"SemiBold",size:26,color:C.white,x:80,y:0,w:920,align:"RIGHT",lhPct:140});
    cap.y = 1244 - 28 - cap.height;
    f.appendChild(cap);
    anchorY = cap.y;
  }
  // גרדיאנט דיו תחתון בלבד — שקוף לחלוטין עד ~7% מעל העוגן, 0.72 בגובהו, מלא בתחתית
  const lf = anchorY / 1350;
  const grad=R({x:0,y:0,w:1080,h:1350,color:C.ink});
  grad.fills=[{type:"GRADIENT_LINEAR",gradientTransform:[[0,1,0],[-1,0,1]],gradientStops:[
    {position:0,color:{...C.ink,a:0}},{position:Math.max(0.01,lf-0.07),color:{...C.ink,a:0}},
    {position:lf,color:{...C.ink,a:0.72}},{position:1,color:{...C.ink,a:1}}]}];
  f.insertChild(1,grad);
  const cr=await T({chars:credit,family:BODY,style:"Regular",size:18,color:C.white,x:18,y:1315,w:360,align:"LEFT"});
  cr.fills=[{type:"SOLID",color:C.white,opacity:0.53}]; f.appendChild(cr);   // credit שמאל
  f.appendChild(await T({chars:"HA-MAKOM.CO.IL",family:BODY,style:"SemiBold",size:21,color:C.onDarkSoft,x:295,y:1313,w:490,align:"CENTER",letterSpacing:3}));
  LOGO(f,C.white,519,1244,50);   // לוגו לבן ממורכז
  SIG(f,1346,4);                 // פס-חתימה תחתון
  figma.currentPage.appendChild(f);
  return f.id;
}
```

---

## CTA — dark, pill טרקוטה (הפריים הקנוני שדור קיבע, 3.7.2026 — "12-cta" בקובץ הארגזים)

```javascript
const cta=NF("NN-cta",C.ink); cta.x=ctaX;
// פס-חתימה עליון 4px (בשקף הזה בלבד): טרקוטה משמאל · מרווה במרכז · אברש מימין
cta.appendChild(R({x:0,y:0,w:360,h:4,color:C.terra}));
cta.appendChild(R({x:360,y:0,w:360,h:4,color:C.sage}));
cta.appendChild(R({x:720,y:0,w:360,h:4,color:C.heather}));
// הלוגו הריבועי הטיפוגרפי בשנהב — גדול, ממורכז (לא וורדמרק!)
const logoBig=LOGO_SQUARE(C.bg, 320, 380); logoBig.x=380; logoBig.y=240; cta.appendChild(logoBig);
cta.appendChild(await T({chars:"בלי בעלי הון.  בלי פרסומות.",family:BODY,style:"Medium",size:42,color:C.bg,x:72,y:720,w:936,align:"CENTER"}));
cta.appendChild(await T({chars:"בלי בולשיט",family:HEAD,style:"Regular",size:76,color:C.bg,x:72,y:790,w:936,align:"CENTER",lhPct:110}));
const btn=R({x:340,y:970,w:400,h:108,color:C.terra,cornerRadius:54}); btn.name="btn-pill"; cta.appendChild(btn);
cta.appendChild(await T({chars:"לכתבה המלאה",family:BODY,style:"Bold",size:34,color:C.bg,x:340,y:1004,w:400,align:"CENTER"}));
// פוטר: רצועת שנהב ברוחב מלא עם url בדיו — בלי FOOT הכהה ובלי פס תחתון
cta.appendChild(R({x:0,y:1294,w:1080,h:56,color:C.bg}));
cta.appendChild(await T({chars:"HA-MAKOM.CO.IL",family:BODY,style:"Bold",size:24,color:C.ink,x:0,y:1308,w:1080,align:"CENTER",letterSpacing:4}));
figma.currentPage.appendChild(cta);
// לעולם לא "כשציבור מממן, ציבור קובע".
```

`LOGO_SQUARE` = אותה פונקציית makeLogo של הלוגו הריבועי (SVG → vectors בצבע שנהב), בגודל 320×380.

---

## פריסת frames

כל שקף ברוחב 1080 עם מרווח 100 → `x = i * 1180`. cover ב-0, CTA אחרון.

**חלוקה לשקפים (19.07.2026 — לפי הקרוסלה שפורסמה):**
- **סה"כ 8-10 שקפים כולל קאבר ו-CTA.** הקרוסלה תמצית, לא הכתבה.
- **~300-450 תווים לשקף טקסט.**
- **תמצות מותר, שכתוב אסור:** משמיטים משפטי המשך, ציטוטים משניים, פירוט פרוצדורלי.
  משפט שנשאר — **בלשון הכותב מילה במילה**.
- **מה שנשאר בחוץ במכוון:** תאריכי הגשה והתכתבויות, תגובות רשמיות מלאות, רקע משני.
  הם בכתבה, וה-CTA מפנה אליה.
- הסדר הנרטיבי נשמר.

---

## ניקוי לפני rebuild (רק frames שלי)

```javascript
for (const c of [...figma.currentPage.children]) {
  const n=c.name||"";
  if (n==="00-cover" || /^\d{2}-paragraph$/.test(n) || /^\d{2}-psdata$/.test(n)
      || /^\d{2}-data$/.test(n)   // שקפי DSlide ישנים — מנוקים אם נשארו מריצה קודמת
      || /^\d{2}-photo$/.test(n) || /^evidence-/.test(n) || n==="NN-cta") c.remove();
}
// frames של דור (שם בעברית / "unnamed N") — לא נוגעים. אם דור ערך ידנית — עורכים פריים-פריים.
```

---

## upload_assets — gotcha

1. `upload_assets fileKey count=1 nodeId=<rect>` → מחזיר submitUrl.
2. POST הקובץ ל-submitUrl (multipart `file=@...`) → מחזיר `imageHash`.
3. אפשר להחיל ידנית: `node.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:HASH}]`
   (cover hero = FILL ; קאטאאוט PNG = FILL על rect ביחס הנכון).

---

## פלט — דוגמה

```
קובץ Figma: https://www.figma.com/design/<KEY>
פלטה: שנהב #faf9f5 + דיו #141413 + טרקוטה #D97757 (טריו +מרווה +אברש)
פונטים: Suez One + IBM Plex Sans Hebrew (font_fallback_used: false)

עמוד Carousel: 8-10 שקפים — cover (full-bleed) + פסקאות מתומצתות + PSData + IMG + CTA (dark)
```

ואחר כך **תמיד מציעים קאפשיין** לפוסט (בלי אימוג'ים).
