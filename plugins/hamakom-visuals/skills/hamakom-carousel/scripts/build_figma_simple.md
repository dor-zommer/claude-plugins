# Build Figma Simple — קוד מינימלי לקרוסלה

> **תקן 2026** — זה הקוד שהתכנס אליו אחרי עשרות איטרציות עם דור.
> תמיד קוראים את SKILL.md (סעיף "המודל הפשוט") לפני שמשתמשים בקובץ הזה.

---

## תהליך עבודה — צ׳ק-ליסט

```
[ ] WebFetch של הכתבה
[ ] חלץ: h1 verbatim, lede, byline, og:image, פסקאות
[ ] בדוק תיקיות מקומיות לתמונות (Downloads, ~/Documents/המקום/...)
[ ] צור Figma file: create_new_file editorType=design
[ ] upload_assets לתמונות
[ ] use_figma → build Carousel (קוד למטה)
[ ] use_figma → build Graphics page (ראה build_graphics_page.md)
[ ] upload_assets לוורדמרק (לחיוב על ה-CTA)
[ ] screenshot ל-QA חזותי
[ ] הצע קאפשיין לפוסט
```

---

## פלטה ופונטים — שיגרת ברירת מחדל

```javascript
const PALETTE = {
  bg:     { r: 0.0784, g: 0.0784, b: 0.0745 },  // #141413
  fg:     { r: 0.9569, g: 0.9451, b: 0.9255 },  // #f4f1ec
  accent: { r: 0.9686, g: 0.0510, b: 0.1569 },  // #f70d28
  muted:  { r: 0.6196, g: 0.5569, b: 0.4863 },  // #9e8e7c
};

let FD = "Inter", FB = "Inter";
try {
  const fs = await figma.listAvailableFontsAsync();
  if (fs.some(f => f.fontName.family === "NextExit")) FD = "NextExit";
  if (fs.some(f => f.fontName.family === "Narkiss Tam")) FB = "Narkiss Tam";
} catch(e) {}
for (const fam of [FD, FB, "Inter"]) {
  for (const st of ["Bold", "Regular", "Light", "Semi Bold", "Medium"]) {
    try { await figma.loadFontAsync({ family: fam, style: st }); } catch(e){}
  }
}

const BODY_SIZE = 42;
const BODY_LH = 152;
```

---

## Helpers — תמיד אותם

```javascript
const LOGO_SVG = `<svg xmlns="..." viewBox="0 0 826.779 981.533">...</svg>`;
// (קופי מ-build_figma.md המלא)

function NF(name, bg) {
  const f = figma.createFrame();
  f.name = name; f.resize(1080, 1350); f.y = 0;
  f.fills = [{ type: "SOLID", color: bg || PALETTE.bg }];
  f.clipsContent = true;
  return f;
}

function R({x,y,w,h,color,cornerRadius,opacity=1,fills}) {
  const r = figma.createRectangle();
  r.x = x; r.y = y; r.resize(w, h);
  if (fills) r.fills = fills;
  else r.fills = [{ type: "SOLID", color, opacity }];
  if (cornerRadius) r.cornerRadius = cornerRadius;
  return r;
}

async function T(o) {
  const t = figma.createText();
  try { t.fontName = { family: o.family, style: o.style }; }
  catch(e) {
    try { t.fontName = { family: "Inter", style: o.style }; }
    catch(e2) { t.fontName = { family: "Inter", style: "Regular" }; }
  }
  t.fontSize = o.size;
  if (o.lhPct) t.lineHeight = { unit: "PERCENT", value: o.lhPct };
  if (o.letterSpacing != null) t.letterSpacing = { unit: "PIXELS", value: o.letterSpacing };
  t.characters = o.chars;
  t.textAlignHorizontal = o.align;
  t.fills = [{ type: "SOLID", color: o.color }];
  t.x = o.x; t.y = o.y; t.resize(o.w, t.height);
  return t;
}

function L(frame, fill) {
  const n = figma.createNodeFromSvg(LOGO_SVG);
  if ("fills" in n) n.fills = [];
  const rec = (x) => {
    if (["VECTOR","BOOLEAN_OPERATION","POLYGON","RECTANGLE"].includes(x.type)) {
      if ("fills" in x) x.fills = [{ type: "SOLID", color: fill || PALETTE.fg }];
    }
    if ("children" in x) x.children.forEach(rec);
  };
  rec(n); n.resize(61, 72); n.x = 947; n.y = 56; n.name = "logo";
  frame.appendChild(n);
}

async function BB(frame, bg, fg) {
  frame.appendChild(R({ x:0, y:1294, w:1080, h:56, color: bg || PALETTE.accent }));
  frame.appendChild(await T({
    chars: "H A - M A K O M . C O . I L",
    family: "Inter", style: "Bold", size: 22,
    color: fg || PALETTE.fg,
    x: 0, y: 1310, w: 1080, align: "CENTER", letterSpacing: 4
  }));
}
```

---

## שקף טקסט — אחיד, 42pt, ממורכז אנכית

```javascript
async function PSlide(idx, text, xPos) {
  const num = String(idx).padStart(2, "0");
  const f = NF(`${num}-paragraph`);
  f.x = xPos;

  f.appendChild(R({ x:0, y:0, w:1080, h:3, color: PALETTE.accent }));
  L(f);
  f.appendChild(await T({
    chars: num, family: "Inter", style: "Bold", size: 110, color: PALETTE.accent,
    x: 820, y: 150, w: 200, align: "LEFT", lhPct: 100
  }));
  f.appendChild(R({ x:928, y:290, w:80, h:3, color: PALETTE.accent }));

  const body = await T({
    chars: text, family: FB, style: "Regular", size: BODY_SIZE, color: PALETTE.fg,
    x: 72, y: 340, w: 936, align: "RIGHT", lhPct: BODY_LH
  });
  body.textAutoResize = "HEIGHT";
  body.resize(936, body.height);

  // אם הטקסט גדול מדי — מקטינים, אבל לא מתחת ל-28pt
  const avail = 910;
  if (body.height > avail) {
    let s = BODY_SIZE;
    while (body.height > avail && s > 28) {
      s -= 2;
      body.fontSize = s;
      body.resize(936, body.height);
    }
  }

  // ממרכז אנכית בשטח הזמין
  body.y = 320 + Math.max(0, Math.floor((avail - body.height) / 2));
  f.appendChild(body);

  await BB(f);
  figma.currentPage.appendChild(f);
  return f.id;
}
```

---

## שקף ראיה (Evidence) — FIT, ללא קרופ

```javascript
async function ISlide(idx, imageHash, imgW, imgH, label, credit, xPos) {
  const num = String(idx).padStart(2, "0");
  const f = NF(`${num}-image`);
  f.x = xPos;

  f.appendChild(R({ x:0, y:0, w:1080, h:3, color: PALETTE.accent }));
  L(f);

  // Number top-right
  f.appendChild(await T({
    chars: num, family: "Inter", style: "Bold", size: 78, color: PALETTE.accent,
    x: 820, y: 120, w: 200, align: "LEFT", lhPct: 100
  }));

  // Label top-right
  if (label) {
    f.appendChild(await T({
      chars: label, family: "Inter", style: "Bold", size: 20, color: PALETTE.accent,
      x: 72, y: 60, w: 740, align: "RIGHT", letterSpacing: 4
    }));
  }

  // FIT image in middle area — ללא קרופ, התמונה במלואה
  const availTop = 200, availBottom = 1190;
  const availH = availBottom - availTop;
  const availW = 936;
  const aspect = imgW / imgH;
  let dispW, dispH;
  if (availW / availH > aspect) {
    dispH = availH;
    dispW = aspect * availH;
  } else {
    dispW = availW;
    dispH = availW / aspect;
  }
  const imgX = Math.floor((1080 - dispW) / 2);
  const imgY = availTop + Math.floor((availH - dispH) / 2);
  const img = R({ x: imgX, y: imgY, w: dispW, h: dispH, color: PALETTE.bg });
  // CRITICAL: scaleMode FILL בתוך rect שכבר חתוך לפי הפרופורציה הנכונה
  // (לא scaleMode FIT, כי FILL ב-rect בגודל הנכון = אין קרופ)
  img.fills = [{ type: "IMAGE", scaleMode: "FILL", imageHash: imageHash }];
  f.appendChild(img);

  // Credit bottom-center
  const credTxt = await T({
    chars: credit, family: FD, style: "Light", size: 16, color: PALETTE.fg,
    x: 72, y: 1230, w: 936, align: "CENTER"
  });
  credTxt.opacity = 0.85;
  f.appendChild(credTxt);

  await BB(f);
  figma.currentPage.appendChild(f);
  return f.id;
}
```

---

## CTA — קנוני, לא משתנה

```javascript
const cta = NF("NN-cta", PALETTE.accent);
cta.x = xPos;

const wm = R({ x:300, y:200, w:480, h:142, color: PALETTE.accent });
wm.name = "wordmark-logo";
cta.appendChild(wm);
// אחרי הבנייה — upload_assets עם logo-wordmark-white.png ל-nodeId שלו

cta.appendChild(await T({
  chars: "בלי בעלי הון.  בלי פרסומות.",
  family: FD, style: "Bold", size: 56, color: PALETTE.fg,
  x: 72, y: 460, w: 936, align: "CENTER", lhPct: 120
}));
cta.appendChild(await T({
  chars: "בלי בולשיט",
  family: FD, style: "Bold", size: 130, color: PALETTE.fg,
  x: 72, y: 600, w: 936, align: "CENTER", lhPct: 105
}));
const btn = R({ x:320, y:900, w:440, h:110, color: PALETTE.fg, cornerRadius: 55 });
btn.name = "btn-pill";
cta.appendChild(btn);
cta.appendChild(await T({
  chars: "לתחקיר המלא",
  family: "Inter", style: "Bold", size: 38, color: PALETTE.accent,
  x: 320, y: 935, w: 440, align: "CENTER"
}));
cta.appendChild(R({ x:0, y:0, w:1080, h:3, color: PALETTE.fg }));
L(cta, PALETTE.fg);
await BB(cta, PALETTE.fg, PALETTE.accent);  // bottom strip white bg, red text
figma.currentPage.appendChild(cta);
```

---

## אחוד פסקאות — איך מחלקים את הכתבה

**עיקרון:** פסקה אחת = שקף אחד, אלא אם **הפסקה קצרה מ-200 תווים** — אז מאחדים עם הסמוכה.

```javascript
// דוגמה: פסקה 1 ופסקה 2 בכתבה
const SLIDE_1_TEXT = "אתחיל בגילוי נאות... [פסקה 1 קצרה]\n\nבילדותי הסכנה הייתה דבר מוחשי... [פסקה 2 ארוכה]";
// → שקף אחד
```

**אם פסקה ארוכה מ-500 תווים** — היא תופסת שקף לעצמה (לא מאחדים).

**מילוי שקף — שואפים ל-85-95%:**
- אחרי `body.resize(936, body.height)`, גובה הטקסט צריך להיות בין 770 ל-870 (מתוך 910 זמין).
- אם פחות → לאחד עם הפסקה הבאה.
- אם יותר → להוריד פונט עד 28pt (Auto-Fit Loop).

---

## ניקוי לפני rebuild

**רק** מוחקים frames של עצמנו:

```javascript
for (const c of [...page.children]) {
  const n = c.name || "";
  if (n === "00-cover" ||
      /^\d{2}-paragraph$/.test(n) ||
      /^\d{2}-paragraph-image$/.test(n) ||
      /^\d{2}-image$/.test(n) ||
      n.startsWith("evidence-") ||
      /^\d{2}-cta$/.test(n)) {
    c.remove();
  }
}
// כל מה ששמו "אינסטגרם", "Frame N", "unnamed N", או שם בעברית של דור —
// לא נוגעים!
```

---

## upload_assets — gotcha חוזר

```javascript
// השקף שלך:
const photoNode = ...;  // rect שתשמש פלייסהולדר לתמונה

// 1. בקש upload_assets (מחזיר submitUrl):
//    mcp.figma upload_assets fileKey count=1
// 2. POST קובץ ל-submitUrl
// 3. מקבל imageHash בתגובה

// אחר כך תמיד החל ידנית עם imageHash:
photoNode.fills = [{
  type: "IMAGE",
  scaleMode: "FILL",  // או "FIT" לראיה
  imageHash: HASH_FROM_UPLOAD
}];

// אל תסמוך על "placedOnNodeId" — לא תמיד עובד.
```

---

## מבנה הקאבר — תבנית סטנדרטית

```javascript
const cover = NF("00-cover");
cover.x = 0;

// Hero image (placeholder + apply imageHash אחרי upload)
const hImg = R({ x:0, y:3, w:1080, h:817, color: PALETTE.bg });
hImg.name = "cover-hero-image";
hImg.fills = [{ type:"IMAGE", scaleMode:"FILL", imageHash: HERO_HASH }];
cover.appendChild(hImg);

// Gradient overlay (image → bg)
const grad = R({ x:0, y:3, w:1080, h:817, color: PALETTE.bg });
grad.fills = [{
  type: "GRADIENT_LINEAR",
  gradientTransform: [[0,1,0], [-1,0,1]],
  gradientStops: [
    { position: 0,    color: { ...PALETTE.bg, a: 0.10 } },
    { position: 0.55, color: { ...PALETTE.bg, a: 0.55 } },
    { position: 1,    color: { ...PALETTE.bg, a: 1.00 } },
  ],
}];
cover.appendChild(grad);

// Credit למקור התמונה
const cr = await T({ chars: IMG_CREDIT, family: FD, style:"Light", size:20, color: PALETTE.fg, x:72, y:770, w:936, align:"RIGHT" });
cr.opacity = 0.85;
cover.appendChild(cr);

// Bg block למטה
cover.appendChild(R({ x:0, y:820, w:1080, h:474, color: PALETTE.bg }));

// Label
cover.appendChild(await T({
  chars: LABEL,  // "תחקיר · המקומון" / "דעה · יהודה ושומרון"
  family: FD, style: "Regular", size: 30, color: PALETTE.accent,
  x: 72, y: 846, w: 936, align: "RIGHT", letterSpacing: 6
}));

// Title — H1 VERBATIM (חוק 0a)
cover.appendChild(await T({
  chars: TITLE,  // ה-h1 המלא של הכתבה
  family: FD, style: "Bold", size: 62,  // התאם 50-80 לפי אורך
  color: PALETTE.fg,
  x: 72, y: 898, w: 936, align: "RIGHT", lhPct: 110
}));

// Byline
cover.appendChild(await T({
  chars: BYLINE,  // "דעה: שם" / "תחקיר: שם"
  family: FD, style: "Regular", size: 26, color: PALETTE.muted,
  x: 72, y: 1240, w: 936, align: "RIGHT"
}));

// REC chrome
const dot = figma.createEllipse();
dot.x = 56; dot.y = 64; dot.resize(20, 20);
dot.fills = [{ type:"SOLID", color: PALETTE.accent }];
cover.appendChild(dot);
cover.appendChild(await T({
  chars: "REC", family: "Inter", style: "Bold", size: 18, color: PALETTE.fg,
  x: 84, y: 64, w: 80, align: "LEFT"
}));

cover.appendChild(R({ x:0, y:0, w:1080, h:3, color: PALETTE.accent }));
L(cover);
await BB(cover);
figma.currentPage.appendChild(cover);
```

---

## פלט אופייני — דוגמה

```
קובץ Figma: https://www.figma.com/design/<KEY>
פונט: Inter (fallback אם NextExit לא נטען)
פלטה: שחור #141413 + קרם #f4f1ec + אדום #f70d28

עמוד 1 — Carousel (12 שקפים):
  00 Cover (hero + h1 verbatim)
  01-10 פסקאות verbatim (מאוחדות לפי הצורך)
  11 CTA קנוני

עמוד 2 — Graphics — פורמטים (6 פריימים):
  hero-1140x815-site, instagram-1080x1350, ig-story-1080x1920,
  facebook-1200x630, x-1600x900, whatsapp-1080x1080

תמונות: og:image (cover) + N תמונות ראיה
```

ואחר כך **תמיד מציעים קאפשיין** לפוסט.
