# Build Graphics Page — תבנית Figma לעמוד הגרפיקות (HaMakom DS 2026)

> עמוד Figma אחד עם 3 פריימים ממותגים לכתבה: whatsapp-1080x1080,
> instagram-1080x1350, ig-story-1080x1920. ראה גם SKILL.md + מקור-האמת
> `../../../design-system/HAMAKOM-DS-2026.md`.
> פלטה: שנהב/דיו/טרקוטה. פונטים: Suez One + IBM Plex Sans Hebrew.
> הגרפיקה היא **cover-style**: תמונה full-bleed + gradient דיו + טקסט לבן.

---

## Flow

```
1. create_new_file (editorType=design)
2. use_figma → buildGraphicsPage(imageHash, content) — בונה 3 פריימים
3. upload_assets לתמונה → שמור imageHash
4. החל את ה-imageHash על 3 הפלייסהולדרים (ישירות, ראה Gotcha)
5. screenshot של 3 הפריימים ל-QA
```

---

## עקרונות עיצוב

1. **3 פורמטים תמיד** — whatsapp 1:1, instagram 4:5, ig-story 9:16.
2. **אינסטגרם = 1080×1350** (4:5 פיד — לא ריבוע. וואטסאפ נשאר ריבוע.)
3. **תמונה אחת לכולם** — אותה תמונת og/featured של הכתבה, full-bleed.
4. **לוגו לבן במרכז התחתון** (חלק מ-chrome התחתון, מעל פס-החתימה).
5. **בלי lede** — label + כותרת + byline בלבד.
6. **הכותרת נמוכה ככל שניתן** — ממוקמת מלמטה למעלה: byline → כותרת ~24-28px
   מעליו → label צמוד מעל הכותרת. לא באמצע הפריים.
7. **Gradient דיו מצומצם** — שקוף לחלוטין עד ~7% מעל ה-label, אלפא מלא רק
   בתחתית. ~65-70% העליונים של התמונה גלויים לחלוטין.
8. **כותרת = h1 verbatim** (Suez One) — לא `og:title`, לא קיצור.
9. **פס-חתימה טריקולור תחתון יחיד** — 4px בקצה התחתון (טרקוטה·מרווה·אברש). אין פס עליון.

---

## כותרת — חוק ברזל: h1 verbatim

הכותרת היא ה-h1 של הכתבה, מילה במילה. אסור `og:title` (SEO), אסור לקצר/לשפץ.
אם ה-h1 ארוך — הקטן `titleSize` בקונפיג של כל פורמט. Figma עושה wrap עם RIGHT.

---

## תבנית JS (להזריק ל-use_figma)

```javascript
// ============================ INPUTS ============================
const HERO_IMAGE_HASH = "<from upload_assets of cover image>";
const C = {
  bg:{r:0.9804,g:0.9765,b:0.9608},      // שנהב (לא בשימוש בגרפיקה — היא cover-style)
  ink:{r:0.0784,g:0.0784,b:0.0745},     // דיו — gradient + רקע
  terra:{r:0.851,g:0.4667,b:0.3412}, sage:{r:0.4706,g:0.549,b:0.3647}, heather:{r:0.5569,g:0.4353,b:0.6588},
  scTerra:{r:0.9098,g:0.5647,b:0.4353}, // טרקוטה-בהיר ל-label על כהה
  onDarkSoft:{r:0.7176,g:0.7098,b:0.6745}, white:{r:1,g:1,b:1},
};
const CONTENT = {
  title:  "הכותרת המלאה של הכתבה מילה במילה",
  label:  "תחקיר · צבא",          // קטגוריות מהכתבה
  byline: "תחקיר · שם הכותב/ת",
};
// אין lede — label + title + byline בלבד.

// ============================ FONTS ============================
let HEAD="Inter", BODY="Inter";
const fonts = await figma.listAvailableFontsAsync();
if (fonts.some(f => f.fontName.family === "Suez One")) HEAD = "Suez One";
if (fonts.some(f => f.fontName.family === "IBM Plex Sans Hebrew")) BODY = "IBM Plex Sans Hebrew";
for (const fn of [{family:HEAD,style:"Regular"},{family:BODY,style:"Regular"},
  {family:BODY,style:"Medium"},{family:BODY,style:"SemiBold"},{family:BODY,style:"Bold"}])
  { try{ await figma.loadFontAsync(fn);}catch(e){} }

// ============================ PAGE ============================
const graphicsPage = figma.createPage();
graphicsPage.name = "Graphics — פורמטים";
await figma.setCurrentPageAsync(graphicsPage);

const LOGO_SVG = `<...inline the same SVG from build_figma.md...>`;

// ============================ HELPERS ============================
function rect({ x, y, w, h, color, fills, opacity = 1 }) {
  const r = figma.createRectangle(); r.x=x; r.y=y; r.resize(w,h);
  if (fills) r.fills=fills; else r.fills=[{type:"SOLID",color,opacity}]; return r;
}
async function txt(o) {
  const t = figma.createText();
  try { t.fontName={family:o.family,style:o.style}; } catch(e){ t.fontName={family:"Inter",style:"Regular"}; }
  t.fontSize=o.size; if(o.lhPct) t.lineHeight={unit:"PERCENT",value:o.lhPct};
  if(o.letterSpacing!=null) t.letterSpacing={unit:"PIXELS",value:o.letterSpacing};
  t.characters=o.chars; t.textAlignHorizontal=o.align; t.fills=[{type:"SOLID",color:o.color}];
  t.x=o.x; t.y=o.y; t.resize(o.w,t.height); return t;
}
function makeLogo(fillColor, w, h) {
  const node = figma.createNodeFromSvg(LOGO_SVG); if ("fills" in node) node.fills=[];
  const rec=(n)=>{ if(["VECTOR","BOOLEAN_OPERATION","POLYGON","RECTANGLE"].includes(n.type)){ if("fills" in n) n.fills=[{type:"SOLID",color:fillColor}]; } if("children" in n) n.children.forEach(rec); };
  rec(node); node.resize(w,h); node.name="logo"; return node;
}
// פס-חתימה טריקולור ברוחב מלא (כל הפורמטים W=1080).
// נקרא פעם אחת בלבד לפריים — תחתון, h=4, בקצה התחתון (y=H-4). אין פס עליון.
function sig(frame, W, y, h){
  const t=Math.round(W/3);
  frame.appendChild(rect({x:2*t,y,w:W-2*t,h,color:C.terra}));
  frame.appendChild(rect({x:t,y,w:t,h,color:C.sage}));
  frame.appendChild(rect({x:0,y,w:t,h,color:C.heather}));
}
// גרדיאנט מצומצם — מבוסס מיקום ה-label בפועל (labelFrac = labelTxt.y / H)
function gradientFor(labelFrac) {
  return { type:"GRADIENT_LINEAR", gradientTransform:[[0,1,0],[-1,0,1]], gradientStops:[
    { position:0.0, color:{...C.ink,a:0.0} },
    { position:Math.max(0.01,labelFrac-0.07), color:{...C.ink,a:0.0} },  // שקוף לחלוטין עד ~7% מעל ה-label
    { position:labelFrac, color:{...C.ink,a:0.72} },                     // מתחיל להחשיך רק סמוך לטקסט
    { position:1.0, color:{...C.ink,a:1.0} },                            // אלפא מלא רק בתחתית
  ]};
}

// ============================ BUILD FRAME ============================
// הטקסט ממוקם מלמטה למעלה: פס-חתימה (קצה תחתון) → url → לוגו → byline →
// כותרת (~24-28px מעל ה-byline) → label (צמוד מעל הכותרת).
// הגרדיאנט מחושב לפי מיקום ה-label בפועל ומוזרק מעל התמונה, מתחת לטקסט.
async function buildGraphic(name, posX, posY, W, H, o) {
  const frame = figma.createFrame(); frame.name=name; frame.resize(W,H);
  frame.x=posX; frame.y=posY; frame.fills=[{type:"SOLID",color:C.ink}]; frame.clipsContent=true;

  // 1. תמונה full-bleed
  const photo = rect({ x:0, y:0, w:W, h:H, color:C.ink }); photo.name="photo";
  photo.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:HERO_IMAGE_HASH}]; frame.appendChild(photo);

  const padX=o.padX, contentW=W-padX*2;

  // 2. chrome תחתון — מלמטה למעלה: פס-חתימה תחתון יחיד (4px) → url → לוגו
  const sigH=4, sigY=H-sigH;
  sig(frame, W, sigY, sigH);  // הפס היחיד בפריים — אין פס עליון
  const url = await txt({ chars:"HA-MAKOM.CO.IL", family:BODY, style:"SemiBold", size:o.urlSize,
    color:C.white, x:0, y:sigY-o.urlSize-12, w:W, align:"CENTER", letterSpacing:3 });
  frame.appendChild(url);
  const logoH=o.logoH, logoW=Math.round(logoH*(826.779/981.533));
  const logo=makeLogo(C.white, logoW, logoH);
  logo.x=Math.floor((W-logoW)/2); logo.y=url.y-logoH-o.logoGap; frame.appendChild(logo);

  // 3. byline מעל הלוגו
  const byline = await txt({ chars:CONTENT.byline, family:BODY, style:"Medium", size:o.bylineSize,
    color:C.onDarkSoft, x:padX, y:0, w:contentW, align:"RIGHT" });
  byline.y = logo.y - o.bylineGap - byline.height; frame.appendChild(byline);

  // 4. כותרת Suez One verbatim — נמוכה ככל שניתן, ~24-28px מעל ה-byline
  const title = await txt({ chars:CONTENT.title, family:HEAD, style:"Regular", size:o.titleSize,
    color:C.white, x:padX, y:0, w:contentW, align:"RIGHT", lhPct:108 });
  title.y = byline.y - o.titleGap - title.height; frame.appendChild(title);

  // 5. label טרקוטה — צמוד מעל הכותרת
  const labelTxt = await txt({ chars:CONTENT.label, family:BODY, style:"SemiBold", size:o.labelSize,
    color:C.scTerra, x:padX, y:0, w:contentW, align:"RIGHT", letterSpacing:2 });
  labelTxt.y = title.y - o.labelGap - labelTxt.height; frame.appendChild(labelTxt);

  // 6. gradient דיו מצומצם — לפי מיקום ה-label בפועל; מוזרק מעל התמונה, מתחת לטקסט
  const grad = rect({ x:0, y:0, w:W, h:H, fills:[gradientFor(labelTxt.y / H)] });
  frame.insertChild(1, grad);

  graphicsPage.appendChild(frame); return frame.id;
}

// ============================ 3 FORMATS (W=1080) ============================
await buildGraphic("whatsapp-1080x1080", 0, 0, 1080, 1080, {
  padX:64, labelSize:24, labelGap:12, titleSize:56, titleGap:26,
  bylineSize:22, bylineGap:22, logoH:60, logoGap:16, urlSize:21 });

await buildGraphic("instagram-1080x1350", 1260, 0, 1080, 1350, {
  padX:64, labelSize:25, labelGap:12, titleSize:56, titleGap:26,
  bylineSize:23, bylineGap:24, logoH:64, logoGap:18, urlSize:21 });

await buildGraphic("ig-story-1080x1920", 2520, 0, 1080, 1920, {
  padX:72, labelSize:28, labelGap:14, titleSize:80, titleGap:28,
  bylineSize:28, bylineGap:28, logoH:84, logoGap:20, urlSize:23 });

return { status:"ok", pageId:graphicsPage.id, head:HEAD, body:BODY };
```

---

## ⚠️ Gotcha — תמונה לא מופיעה אחרי upload_assets

`upload_assets({nodeId})` בעמוד שאינו currentPage מחזיר `success:true` אבל לא
מחיל את ה-fill. הפתרון: `upload_assets` ללא nodeId (פעם אחת) → imageHash, ואז:

```javascript
const HASH = "<from upload>";
for (const id of ["1:4","1:36","1:67"]) {          // 3 פלייסהולדרים
  const node = await figma.getNodeByIdAsync(id);
  node.fills = [{ type:"IMAGE", scaleMode:"FILL", imageHash:HASH }];
}
```

---

## עיצוב — כן/לא

✓ תמונה full-bleed, gradient דיו מצומצם (שקוף עד סמוך ל-label), label טרקוטה,
כותרת Suez One לבנה נמוכה (ממש מעל ה-byline), לוגו מרכזי-תחתון,
פס-חתימה טריקולור תחתון יחיד 4px בקצה התחתון.

✗ אסור: אדום `#f70d28` / פס אדום / NextExit; פס-חתימה עליון (הפס תחתון בלבד);
lede/משנה; כותרת באמצע הפריים; אינסטגרם ריבוע (פיד=4:5); gradient שמחשיך
מעל אזור הטקסט (~65-70% העליונים חייבים להישאר גלויים); פורמט רביעי.

---

## פלט QA

screenshot של 3 הפריימים — לוודא: תמונה נראית (לא דיו מלא — הגרדיאנט לא מסתיר
את ~65-70% העליונים), כותרת Suez One verbatim צמודה לתחתית (~24-28px מעל
ה-byline), אין lede, פס-חתימה טריקולור תחתון יחיד 4px (אין פס עליון),
לוגו לבן מרכזי, label טרקוטה צמוד מעל הכותרת.
