# Build Figma Simple — בילדר קרוסלה (HaMakom DS 2026)

> **תקן 2026** — הקוד הזה אומת חזותית מול דור (קרוסלת "בנט / הסכסוך הוא לא רסיס", יוני 2026).
> **קרא קודם** את `design-system/HAMAKOM-DS-2026.md` (מקור-האמת) ואת SKILL.md.
> פלטה: שנהב/דיו/טרקוטה. פונטים: Suez One + IBM Plex Sans Hebrew. פסי-חתימה טריקולור.
> **הפלטה הישנה (שחור/אדום `#f70d28` + NextExit/Narkiss Tam) בוטלה.**

---

## תהליך עבודה — צ׳ק-ליסט

```
[ ] שלוף את הכתבה (WP REST: /wp-json/wp/v2/posts?slug=<slug>&_embed)
[ ] חלץ: h1 verbatim, byline, קטגוריה (label), פסקאות גוף, og/featured image
[ ] התקן Suez One + IBM Plex Sans Hebrew אם חסרים (ראה DS §2)
[ ] צור Figma file: create_new_file editorType=design
[ ] use_figma → בנה Carousel (קוד למטה): cover + פסקאות + CTA
[ ] upload_assets: hero → cover-hero-image ; wordmark → wordmark-logo (CTA)
[ ] get_screenshot ל-QA (cover + פסקה + CTA)
[ ] הצע קאפשיין לפוסט
```

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

// פס-חתימה טריקולור — ימין טרקוטה, מרכז מרווה, שמאל אברש
function SIG(f,y,h){ f.appendChild(R({x:720,y,w:360,h,color:C.terra}));
  f.appendChild(R({x:360,y,w:360,h,color:C.sage})); f.appendChild(R({x:0,y,w:360,h,color:C.heather})); }

function LOGO(f,fill,x,y,size){ const n=figma.createNodeFromSvg(LOGO_SVG); if("fills" in n) n.fills=[];
  const rec=(z)=>{ if(["VECTOR","BOOLEAN_OPERATION","POLYGON","RECTANGLE"].includes(z.type)){ if("fills" in z) z.fills=[{type:"SOLID",color:fill}]; } if("children" in z) z.children.forEach(rec); };
  rec(n); const w=size*(826.779/981.533); n.resize(w,size); n.x=x; n.y=y; n.name="logo"; f.appendChild(n); }

async function FOOT(f,dark){ const fg=dark?C.onDarkSoft:C.inkSoft;
  LOGO(f, dark?C.white:C.ink, 952, 1244, 50);
  f.appendChild(await T({chars:"HA-MAKOM.CO.IL",family:BODY,style:"SemiBold",size:21,color:fg,x:400,y:1262,w:520,align:"RIGHT",letterSpacing:3}));
  SIG(f,1342,8); }
```

---

## קאבר (image, full-bleed)

```javascript
const HERO = "<imageHash מה-upload>";
const cover=NF("00-cover",C.ink); cover.x=0;
const hImg=R({x:0,y:0,w:1080,h:1350,color:C.ink}); hImg.name="cover-hero-image";
hImg.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:HERO}]; cover.appendChild(hImg);
const grad=R({x:0,y:0,w:1080,h:1350,color:C.ink});
grad.fills=[{type:"GRADIENT_LINEAR",gradientTransform:[[0,1,0],[-1,0,1]],gradientStops:[
  {position:0,color:{...C.ink,a:0}},{position:0.4,color:{...C.ink,a:0.1}},
  {position:0.58,color:{...C.ink,a:0.5}},{position:0.78,color:{...C.ink,a:0.92}},{position:1,color:{...C.ink,a:1}}]}];
cover.appendChild(grad);
SIG(cover,0,8);
cover.appendChild(await T({chars:LABEL, family:BODY, style:"SemiBold", size:27, color:C.scTerra, x:80, y:884, w:920, align:"RIGHT", letterSpacing:2}));   // קיקר טרקוטה "דעה · יהודה ושומרון"
cover.appendChild(await T({chars:TITLE, family:HEAD, style:"Regular", size:64, color:C.white, x:80, y:934, w:920, align:"RIGHT", lhPct:108}));            // h1 verbatim (Suez One)
cover.appendChild(await T({chars:BYLINE, family:BODY, style:"Medium", size:25, color:C.onDarkSoft, x:80, y:1186, w:920, align:"RIGHT"}));                  // "טור דעה · אריאל שוורץ"
const cr=await T({chars:CREDIT, family:BODY, style:"Regular", size:18, color:C.white, x:80, y:1266, w:400, align:"LEFT"}); cr.opacity=0.6; cover.appendChild(cr);
cover.appendChild(await T({chars:"HA-MAKOM.CO.IL",family:BODY,style:"SemiBold",size:21,color:C.onDarkSoft,x:430,y:1262,w:490,align:"RIGHT",letterSpacing:3}));
LOGO(cover,C.white,952,1244,50);
SIG(cover,1342,8);
figma.currentPage.appendChild(cover);
// כותרת דינמית: ≤30 תווים→72 ; 30–50→64 ; 50+→56
```

---

## שקף-פסקה — שנהב, IBM Plex, מיושר-לעליון

```javascript
async function PS(idx, total, text, xPos, kicker){
  const num=String(idx).padStart(2,"0");
  const f=NF(`${num}-paragraph`); f.x=xPos;
  SIG(f,0,8);
  f.appendChild(await T({chars:kicker||"דעה",family:BODY,style:"Bold",size:24,color:C.terraDeep,x:80,y:96,w:920,align:"RIGHT",letterSpacing:3}));
  f.appendChild(await T({chars:`${num} / ${String(total).padStart(2,"0")}`,family:BODY,style:"Medium",size:22,color:C.inkSoft,x:80,y:100,w:300,align:"LEFT",letterSpacing:1}));
  f.appendChild(R({x:936,y:148,w:64,h:4,color:C.terra}));
  const body=await T({chars:text,family:BODY,style:"Regular",size:40,color:C.ink,x:80,y:212,w:920,align:"RIGHT",lhPct:160});
  body.textAutoResize="HEIGHT"; body.resize(920,body.height);
  let s=40; while(body.height>990 && s>26){ s-=2; body.fontSize=s; body.resize(920,body.height); }
  f.appendChild(body);          // מיושר-לעליון (y=212), לא ממורכז אנכית
  await FOOT(f,false);
  figma.currentPage.appendChild(f);
  return f.id;
}
```

---

## שקף-נתון (data) — מספר ענק בטרקוטה

```javascript
async function DSlide(idx, total, number, kicker, headline, detail, source, xPos){
  const num=String(idx).padStart(2,"0");
  const f=NF(`${num}-data`); f.x=xPos;
  SIG(f,0,8);
  f.appendChild(await T({chars:`${num} / ${String(total).padStart(2,"0")}`,family:BODY,style:"Medium",size:22,color:C.inkSoft,x:80,y:100,w:300,align:"LEFT",letterSpacing:1}));
  f.appendChild(await T({chars:kicker,family:BODY,style:"Bold",size:26,color:C.terraDeep,x:80,y:330,w:920,align:"CENTER",letterSpacing:2}));
  f.appendChild(await T({chars:number,family:HEAD,style:"Regular",size:260,color:C.terra,x:40,y:380,w:1000,align:"CENTER",lhPct:100}));   // מספר ענק טרקוטה
  f.appendChild(await T({chars:headline,family:BODY,style:"Bold",size:42,color:C.ink,x:80,y:760,w:920,align:"CENTER",lhPct:130}));
  f.appendChild(await T({chars:detail,family:BODY,style:"Regular",size:28,color:C.ink2,x:80,y:880,w:920,align:"CENTER",lhPct:150}));
  f.appendChild(await T({chars:source,family:BODY,style:"Regular",size:20,color:C.inkSoft,x:80,y:1080,w:920,align:"CENTER"}));
  await FOOT(f,false);
  figma.currentPage.appendChild(f);
  return f.id;
}
```

---

## CTA — dark, pill שנהב

```javascript
const WM = "<imageHash וורדמרק לבן>";
const cta=NF("NN-cta",C.ink); cta.x=ctaX;
SIG(cta,0,8);
const wm=R({x:300,y:250,w:480,h:150,color:C.ink}); wm.name="wordmark-logo";
wm.fills=[{type:"IMAGE",scaleMode:"FIT",imageHash:WM}]; cta.appendChild(wm);
cta.appendChild(await T({chars:"בלי בעלי הון.  בלי פרסומות.",family:HEAD,style:"Regular",size:48,color:C.white,x:72,y:560,w:936,align:"CENTER",lhPct:120}));
cta.appendChild(await T({chars:"בלי בולשיט",family:HEAD,style:"Regular",size:112,color:C.white,x:72,y:650,w:936,align:"CENTER",lhPct:110}));
const btn=R({x:330,y:920,w:420,h:108,color:C.bg,cornerRadius:54}); btn.name="btn-pill"; cta.appendChild(btn);
cta.appendChild(await T({chars:"לכתבה המלאה",family:BODY,style:"Bold",size:36,color:C.ink,x:330,y:952,w:420,align:"CENTER"}));
await FOOT(cta,true);
figma.currentPage.appendChild(cta);
// לעולם לא "כשציבור מממן, ציבור קובע".
```

---

## פריסת frames

כל שקף ברוחב 1080 עם מרווח 100 → `x = i * 1180`. cover ב-0, CTA אחרון.
טקסט verbatim מהכתבה, בסדר הכתיבה; פסקה ארוכה מ-~520 תווים — אפשר לפצל בגבול משפט.

---

## ניקוי לפני rebuild (רק frames שלי)

```javascript
for (const c of [...figma.currentPage.children]) {
  const n=c.name||"";
  if (n==="00-cover" || /^\d{2}-paragraph$/.test(n) || /^\d{2}-data$/.test(n) || n==="NN-cta") c.remove();
}
// frames של דור (שם בעברית / "unnamed N") — לא נוגעים. אם דור ערך ידנית — עורכים פריים-פריים.
```

---

## upload_assets — gotcha

1. `upload_assets fileKey count=1 nodeId=<rect>` → מחזיר submitUrl.
2. POST הקובץ ל-submitUrl (multipart `file=@...`) → מחזיר `imageHash`.
3. אפשר להחיל ידנית: `node.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:HASH}]`
   (cover hero = FILL ; wordmark = FIT).

---

## פלט — דוגמה

```
קובץ Figma: https://www.figma.com/design/<KEY>
פלטה: שנהב #faf9f5 + דיו #141413 + טרקוטה #D97757 (טריו +מרווה +אברש)
פונטים: Suez One + IBM Plex Sans Hebrew (font_fallback_used: false)

עמוד Carousel: cover (full-bleed) + N פסקאות verbatim + CTA (dark)
```

ואחר כך **תמיד מציעים קאפשיין** לפוסט (בלי אימוג'ים).
