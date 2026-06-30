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
5. **Lede חובה** — משפט סיכום אחד מהכתבה.
6. **Gradient דיו שקוף למעלה** — מתחיל להחשיך רק מ-textStart.
7. **כותרת = h1 verbatim** (Suez One) — לא `og:title`, לא קיצור.
8. **פס-חתימה טריקולור** למעלה ולמטה (טרקוטה·מרווה·אברש).

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
  lede:   "משפט הסיכום של הכתבה — מה זה ולמה זה חשוב",
  label:  "תחקיר · צבא",          // קטגוריות מהכתבה
  byline: "תחקיר · שם הכותב/ת",
};

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
// פס-חתימה טריקולור ברוחב מלא (כל הפורמטים W=1080)
function sig(frame, W, y, h){
  const t=Math.round(W/3);
  frame.appendChild(rect({x:2*t,y,w:W-2*t,h,color:C.terra}));
  frame.appendChild(rect({x:t,y,w:t,h,color:C.sage}));
  frame.appendChild(rect({x:0,y,w:t,h,color:C.heather}));
}
function gradientFor(textStart) {
  return { type:"GRADIENT_LINEAR", gradientTransform:[[0,1,0],[-1,0,1]], gradientStops:[
    { position:0.0, color:{...C.ink,a:0.0} },
    { position:Math.max(0.01,textStart-0.15), color:{...C.ink,a:0.0} },
    { position:textStart, color:{...C.ink,a:0.8} },
    { position:1.0, color:{...C.ink,a:1.0} },
  ]};
}

// ============================ BUILD FRAME ============================
async function buildGraphic(name, posX, posY, W, H, o) {
  const frame = figma.createFrame(); frame.name=name; frame.resize(W,H);
  frame.x=posX; frame.y=posY; frame.fills=[{type:"SOLID",color:C.ink}]; frame.clipsContent=true;

  // 1. תמונה full-bleed
  const photo = rect({ x:0, y:0, w:W, h:H, color:C.ink }); photo.name="photo";
  photo.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:HERO_IMAGE_HASH}]; frame.appendChild(photo);
  // 2. gradient דיו
  frame.appendChild(rect({ x:0, y:0, w:W, h:H, fills:[gradientFor(o.textStart)] }));
  // 3. פס-חתימה עליון
  sig(frame, W, 0, 8);

  const padX=o.padX, contentW=W-padX*2;
  // 4. label טרקוטה (IBM Plex SemiBold)
  const labelTxt = await txt({ chars:CONTENT.label, family:BODY, style:"SemiBold", size:o.labelSize,
    color:C.scTerra, x:padX, y:Math.floor(H*o.textStart)+o.labelOffsetTop, w:contentW, align:"RIGHT", letterSpacing:2 });
  frame.appendChild(labelTxt);
  // 5. כותרת Suez One verbatim
  const title = await txt({ chars:CONTENT.title, family:HEAD, style:"Regular", size:o.titleSize,
    color:C.white, x:padX, y:labelTxt.y+labelTxt.height+o.labelToTitleGap, w:contentW, align:"RIGHT", lhPct:108 });
  frame.appendChild(title);
  // 6. lede (IBM Plex)
  if (o.showLede) {
    const ledeW=Math.floor(contentW*o.ledeWidthPct), ledeX=W-padX-ledeW;
    frame.appendChild(await txt({ chars:CONTENT.lede, family:BODY, style:"Regular", size:o.ledeSize,
      color:C.onDarkSoft, x:ledeX, y:title.y+title.height+o.titleToLedeGap, w:ledeW, align:"RIGHT", lhPct:150 }));
  }
  // 7. chrome תחתון: byline → לוגו לבן מרכזי → פס-חתימה תחתון + url
  const sigH=o.stripeH, logoH=o.logoH, logoW=Math.round(logoH*(826.779/981.533));
  const sigY=H-sigH, logoY=sigY-logoH-o.logoBottomGap;
  frame.appendChild(await txt({ chars:CONTENT.byline, family:BODY, style:"Medium", size:o.bylineSize,
    color:C.onDarkSoft, x:padX, y:logoY-o.logoTopGap-o.bylineSize-6, w:contentW, align:"RIGHT" }));
  const logo=makeLogo(C.white, logoW, logoH); logo.x=Math.floor((W-logoW)/2); logo.y=logoY; frame.appendChild(logo);
  sig(frame, W, sigY, sigH);  // פס-חתימה תחתון (במקום פס אדום)
  frame.appendChild(await txt({ chars:"HA-MAKOM.CO.IL", family:BODY, style:"SemiBold", size:o.urlSize,
    color:C.white, x:0, y:sigY+sigH+6, w:W, align:"CENTER", letterSpacing:3 }));

  graphicsPage.appendChild(frame); return frame.id;
}

// ============================ 3 FORMATS (W=1080) ============================
await buildGraphic("whatsapp-1080x1080", 0, 0, 1080, 1080, {
  textStart:0.45, padX:64, labelSize:24, labelOffsetTop:30, labelToTitleGap:10,
  titleSize:56, titleToLedeGap:20, showLede:true, ledeSize:22, ledeWidthPct:0.68,
  stripeH:8, logoH:60, logoBottomGap:34, logoTopGap:14, bylineSize:22, urlSize:21 });

await buildGraphic("instagram-1080x1350", 1260, 0, 1080, 1350, {
  textStart:0.50, padX:64, labelSize:25, labelOffsetTop:8, labelToTitleGap:10,
  titleSize:56, titleToLedeGap:22, showLede:true, ledeSize:24, ledeWidthPct:0.70,
  stripeH:8, logoH:64, logoBottomGap:36, logoTopGap:16, bylineSize:23, urlSize:21 });

await buildGraphic("ig-story-1080x1920", 2520, 0, 1080, 1920, {
  textStart:0.55, padX:72, labelSize:28, labelOffsetTop:24, labelToTitleGap:12,
  titleSize:80, titleToLedeGap:24, showLede:true, ledeSize:32, ledeWidthPct:0.68,
  stripeH:8, logoH:84, logoBottomGap:40, logoTopGap:18, bylineSize:28, urlSize:23 });

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

✓ תמונה full-bleed, gradient דיו, label טרקוטה, כותרת Suez One לבנה, לוגו מרכזי-תחתון, פס-חתימה טריקולור.

✗ אסור: אדום `#f70d28` / פס אדום / NextExit; אינסטגרם ריבוע (פיד=4:5); gradient מ-alpha 0.2+ למעלה; פורמט רביעי.

---

## פלט QA

screenshot של 3 הפריימים — לוודא: תמונה נראית (לא דיו מלא), כותרת Suez One verbatim,
פס-חתימה טריקולור למעלה+למטה, לוגו לבן מרכזי, label טרקוטה.
