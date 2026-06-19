# Build Figma — תבניות JS לבניית הקרוסלה

> **מסמך זה מחליף את הגרסה הישנה (11 slide-block templates).** הסטנדרט
> הנוכחי: שלושה sub-types בלבד — `cover` / `paragraph` / `cta`.
> 
> מבני הפלטה, הטיפוגרפיה ו-chrome מוגדרים ב-`design-spec/tokens.md`.
> חוקי הברזל וכללי תכנון הרצף ב-`SKILL.md`.

---

## Flow כללי

```
1. create_new_file editorType=design                    → file_key
2. use_figma (setup-globals + buildCover)               → cover frame + image placeholder ids
3. use_figma (buildParagraph × N)                       → paragraph frames + portrait/context placeholders
4. use_figma (buildCta + finalize)                      → cta frame
5. upload_assets(file_key, nodeId) × M                  → fill image placeholders
6. get_screenshot של 3-4 frames מרכזיים                 → QA חזותי
7. החזרה לדור: URL + summary + flag font_fallback_used
```

---

## אסטים קבועים

```javascript
// SVG logo (square black) — embedded as string
const LOGO_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 826.779 981.533"><polygon points="259.22,632.333 291.842,632.333 291.842,348.766 167.942,348.766 167.942,632.347 199.708,632.347 199.708,380.852 259.22,380.852"/><rect x="167.889" y="697.541" width="31.14" height="283.46"/><polygon points="362.386,727.164 458.536,727.164 458.536,979.336 491.345,979.336 491.345,696.08 362.386,696.08"/><rect x="372.239" y="790.695" width="30.964" height="188.631"/><rect x="320.724" y="94.762" width="32.486" height="251.961"/><path d="M269.214,726.952c9.006,0.4,17.714,0.788,27.355,1.217V946.7h-65.545v32.562h97.496V696.001h-59.306V726.952z"/><polygon points="393.655,283.529 426.327,283.529 426.327,0.048 299.131,0.048 299.131,31.293 393.655,31.293"/><path d="M0.059,979.3h135.806V697.668H0.059V979.3z M32.196,733.401h71.725v216.28H32.196V733.401z"/><path d="M0.116,632.244H135.9V348.826H0.116V632.244z M32.089,386.207h71.725v216.28H32.089V386.207z"/><path d="M0,283.353h135.903V0.086H0V283.353z M32.089,33.579h71.725v216.28H32.089V33.579z"/><rect x="207.886" width="32.114" height="284.877"/><rect x="490.249" y="348.749" width="30.762" height="145.599"/><polygon points="697.679,0.011 697.679,31.734 795.369,31.734 795.369,283.434 826.778,283.434 826.778,0.011"/><rect x="709.401" y="443.479" width="30.754" height="188.956"/><polygon points="697.705,380.242 795.721,380.242 795.721,632.242 826.742,632.242 826.742,348.792 697.705,348.792"/><rect x="709.462" y="94.67" width="30.805" height="188.767"/><polygon points="812.08,696.012 706.114,696.012 706.114,727.33 778.563,727.33 778.563,949.764 706.281,949.764 706.281,981.078 825.031,981.078 825.031,949.6 812.08,949.6"/><polygon points="544.922,380.259 642.14,380.259 642.14,600.708 544.883,600.708 544.883,632.243 673.894,632.243 673.894,348.828 544.922,348.828"/><rect x="531.811" y="697.488" width="30.72" height="144.053"/><path d="M597.297,278.46c0.726,1.763,2.641,4.239,4.093,4.302c9.048,0.397,18.122,0.2,27.537,0.2V0.079H597.2V185.01c-0.416,0.038-0.832,0.076-1.248,0.114c-0.717-1.612-1.471-3.208-2.144-4.837c-12.579-30.405-25.204-60.791-37.703-91.229c-11.514-28.039-22.859-56.147-34.398-84.175c-0.697-1.693-2.396-4.167-3.711-4.22c-9.188-0.369-18.397-0.195-27.878-0.195V283.54h31.687V97.332c0.44-0.041,0.881-0.081,1.322-0.122c0.633,1.448,1.297,2.882,1.894,4.344c10.053,24.609,20.1,49.219,30.141,73.833C569.181,209.754,583.165,244.137,597.297,278.46"/><path d="M603.073,727.68h38.748c0,14.283,0.099,27.563-0.079,40.842c-0.038,2.816-0.646,5.805-1.739,8.4c-27.725,65.875-55.554,131.707-83.343,197.555c-0.722,1.709-1.212,3.516-2.029,5.926c3.444,0.361,6.143,0.836,8.849,0.892c6.652,0.136,13.331-0.226,19.96,0.208c4.285,0.278,6.132-1.257,7.759-5.154c15.421-36.94,31.072-73.784,46.688-110.643c0.863-2.037,2.007-3.957,3.02-5.932c0.522,0.135,1.047,0.271,1.57,0.405v119.249h31.398v-283.45h-70.801V727.68z"/></svg>`;
```

---

## setup-globals.js (קוד טעינת פונטים + helpers)

```javascript
// Palette — passed in from caller, NOT hardcoded
// caller provides: { bg, fg, accent, muted }
const PALETTE = INPUT_PALETTE;  // injected at runtime

// Font detection + load
let FONT_DISPLAY = "Inter";   // for NextExit fallback
let FONT_BODY    = "Inter";   // for Narkiss Tam fallback
let fontFallbackUsed = false;

try {
  const fonts = await figma.listAvailableFontsAsync();
  if (fonts.some(f => f.fontName.family === "NextExit")) {
    FONT_DISPLAY = "NextExit";
  } else {
    fontFallbackUsed = true;
  }
  if (fonts.some(f => f.fontName.family === "Narkiss Tam")) {
    FONT_BODY = "Narkiss Tam";
  } else {
    fontFallbackUsed = true;
  }
} catch (e) {
  fontFallbackUsed = true;
}

for (const family of [FONT_DISPLAY, FONT_BODY, "Inter"]) {
  for (const style of ["Bold", "Regular", "Light", "Semibold"]) {
    try { await figma.loadFontAsync({ family, style }); } catch (e) {}
  }
}
```

---

## Helpers (להזריק לתחילת כל buildXxx)

```javascript
function newFrame(name, idx, bg = PALETTE.bg) {
  const f = figma.createFrame();
  f.name = name;
  f.resize(1080, 1350);
  f.x = idx * (1080 + 120);  // 120px gap between frames
  f.y = 0;
  f.fills = [{ type: "SOLID", color: bg }];
  f.clipsContent = true;
  return f;
}

function rect({ x, y, w, h, color, cornerRadius, opacity = 1 }) {
  const r = figma.createRectangle();
  r.x = x; r.y = y; r.resize(w, h);
  r.fills = [{ type: "SOLID", color, opacity }];
  if (cornerRadius) r.cornerRadius = cornerRadius;
  return r;
}

async function txt({ chars, family, style, size, color, x, y, w, align, lhPct, letterSpacing }) {
  const t = figma.createText();
  try { t.fontName = { family, style }; }
  catch (e) {
    try { t.fontName = { family: "Inter", style }; }
    catch (e2) { t.fontName = { family: "Inter", style: "Regular" }; }
  }
  t.fontSize = size;
  if (lhPct) t.lineHeight = { unit: "PERCENT", value: lhPct };
  if (letterSpacing) t.letterSpacing = { unit: "PIXELS", value: letterSpacing };
  t.characters = chars;
  t.textAlignHorizontal = align;
  t.fills = [{ type: "SOLID", color }];
  t.x = x; t.y = y;
  t.resize(w, t.height);
  return t;
}

function addLogo(frame, fillColor) {
  const node = figma.createNodeFromSvg(LOGO_SVG);
  node.name = "logo-square";
  // CRITICAL: remove wrapper-frame fill — without this the SVG renders as solid block
  if ("fills" in node) node.fills = [];
  // Only set fills on actual vector children
  const recurse = (n) => {
    if (["VECTOR", "BOOLEAN_OPERATION", "POLYGON"].includes(n.type)) {
      if ("fills" in n) n.fills = [{ type: "SOLID", color: fillColor }];
    }
    if ("children" in n) n.children.forEach(recurse);
  };
  recurse(node);
  // Aspect ratio of viewBox 826.779 × 981.533 ≈ 0.842
  node.resize(61, 72);
  node.x = 947;
  node.y = 56;
  frame.appendChild(node);
}

async function addBottomBar(frame, bgColor, txtColor) {
  frame.appendChild(rect({ x: 0, y: 1294, w: 1080, h: 56, color: bgColor }));
  const urlTxt = await txt({
    chars: "H A - M A K O M . C O . I L",
    family: "Inter", style: "Light", size: 26,
    color: txtColor,
    x: 0, y: 1311, w: 1080, align: "CENTER",
    letterSpacing: 4,
  });
  frame.appendChild(urlTxt);
}

async function addChrome(frame) {
  frame.appendChild(rect({ x: 0, y: 0, w: 1080, h: 3, color: PALETTE.accent }));
  addLogo(frame, PALETTE.fg);
  await addBottomBar(frame, PALETTE.accent, PALETTE.fg);
}

function coverGradient() {
  return {
    type: "GRADIENT_LINEAR",
    gradientTransform: [[0, 1, 0], [-1, 0, 1]],
    gradientStops: [
      { position: 0.00, color: { ...PALETTE.bg, a: 0.10 } },
      { position: 0.55, color: { ...PALETTE.bg, a: 0.50 } },
      { position: 1.00, color: { ...PALETTE.bg, a: 1.00 } },
    ],
  };
}

function pickTitleSize(title) {
  const len = title.length;
  if (len <= 25) return 100;
  if (len <= 45) return 84;
  if (len <= 65) return 72;
  return 64;
}
```

---

## buildCover

**קלט:**
```typescript
{
  title: string;        // FULL article title — verbatim (חוק 0a)
  label: string;        // "כנסת" / "תחקיר" / "דעה" / etc.
  byline: string;       // "תחקיר: סיון תהל" / "דעה: אורן יפתחאל"
  imageCredit: string;  // "צילום: פלאש 90"
}
```

```javascript
async function buildCover(input) {
  const frame = newFrame("00-cover", 0);

  // 1. Hero image placeholder (filled via upload_assets)
  const heroImg = rect({ x: 0, y: 3, w: 1080, h: 817, color: PALETTE.bg });
  heroImg.name = "cover-hero-image";
  frame.appendChild(heroImg);

  // 2. Gradient overlay
  const grad = rect({ x: 0, y: 3, w: 1080, h: 817, color: PALETTE.bg });
  grad.fills = [coverGradient()];
  frame.appendChild(grad);

  // 3. Image credit at bottom of hero area
  const credit = await txt({
    chars: input.imageCredit,
    family: FONT_DISPLAY, style: "Light", size: 22,
    color: PALETTE.fg,
    x: 72, y: 770, w: 936, align: "RIGHT",
  });
  credit.opacity = 0.85;
  frame.appendChild(credit);

  // 4. Bg-color block below image
  const blackBlock = rect({ x: 0, y: 820, w: 1080, h: 474, color: PALETTE.bg });
  frame.appendChild(blackBlock);

  // 5. Label (red letter-spaced)
  const label = await txt({
    chars: input.label,
    family: FONT_DISPLAY, style: "Regular", size: 32,
    color: PALETTE.accent,
    x: 72, y: 850, w: 936, align: "RIGHT",
    letterSpacing: 6,
  });
  frame.appendChild(label);

  // 6. FULL title — verbatim (חוק 0a), dynamic size
  const titleSize = pickTitleSize(input.title);
  const title = await txt({
    chars: input.title,
    family: FONT_DISPLAY, style: "Bold", size: titleSize,
    color: PALETTE.fg,
    x: 72, y: 900, w: 936, align: "RIGHT",
    lhPct: 108,
  });
  frame.appendChild(title);

  // 7. Byline
  const byline = await txt({
    chars: input.byline,
    family: FONT_DISPLAY, style: "Regular", size: 28,
    color: PALETTE.muted || PALETTE.fg,
    x: 72, y: 1240, w: 936, align: "RIGHT",
  });
  byline.opacity = 0.75;
  frame.appendChild(byline);

  // 8. REC dot
  const dot = figma.createEllipse();
  dot.x = 56; dot.y = 64;
  dot.resize(20, 20);
  dot.fills = [{ type: "SOLID", color: PALETTE.accent }];
  frame.appendChild(dot);
  const recLabel = await txt({
    chars: "REC",
    family: "Inter", style: "Bold", size: 18,
    color: PALETTE.fg,
    x: 84, y: 64, w: 80, align: "LEFT",
  });
  frame.appendChild(recLabel);

  // 9. Top stripe
  frame.appendChild(rect({ x: 0, y: 0, w: 1080, h: 3, color: PALETTE.accent }));
  // 10. Logo SVG
  addLogo(frame, PALETTE.fg);
  // 11. Bottom URL strip
  await addBottomBar(frame, PALETTE.accent, PALETTE.fg);

  figma.currentPage.appendChild(frame);
  return {
    frameId: frame.id,
    heroImageNodeId: heroImg.id,  // for upload_assets
  };
}
```

---

## buildParagraph

**קלט:**
```typescript
{
  index: number;             // 1, 2, ..., N-1
  paragraph: string;         // verbatim from article
  bodyStyle?: "Regular" | "Semibold";  // Semibold for strong-quote paragraphs
  portrait?: { credit: string };       // optional — for quote slides
  contextImage?: { credit: string };   // optional — for context slides
}
```

```javascript
async function buildParagraph(input, slideIdx) {
  const num = String(input.index).padStart(2, "0");
  const frame = newFrame(`${num}-paragraph`, slideIdx);

  // 1. Top stripe + logo
  frame.appendChild(rect({ x: 0, y: 0, w: 1080, h: 3, color: PALETTE.accent }));
  addLogo(frame, PALETTE.fg);

  // 2. Big number "01"/"02"/.../"NN"
  const numTxt = await txt({
    chars: num,
    family: "Inter", style: "Bold", size: 96,
    color: PALETTE.accent,
    x: 72, y: 152, w: 300, align: "LEFT",
    lhPct: 100,
  });
  frame.appendChild(numTxt);

  // 3. Small red divider under number
  frame.appendChild(rect({ x: 72, y: 280, w: 80, h: 3, color: PALETTE.accent }));

  const bodyStyle = input.bodyStyle || "Regular";
  let portraitNodeId = null;
  let contextImageNodeId = null;

  if (input.portrait) {
    // Layout: portrait left (x=72, w=360, h=540), text right (x=452, w=556)
    const bodyTxt = await txt({
      chars: input.paragraph,
      family: FONT_BODY, style: bodyStyle, size: 42,
      color: PALETTE.fg,
      x: 452, y: 330, w: 556, align: "RIGHT",
      lhPct: 155,
    });
    frame.appendChild(bodyTxt);

    const portraitRect = rect({
      x: 72, y: 380, w: 360, h: 540,
      color: PALETTE.bg, cornerRadius: 8,
    });
    portraitRect.name = `portrait-${num}`;
    frame.appendChild(portraitRect);
    portraitNodeId = portraitRect.id;

    if (input.portrait.credit) {
      const pCredit = await txt({
        chars: input.portrait.credit,
        family: FONT_DISPLAY, style: "Light", size: 22,
        color: PALETTE.muted || PALETTE.fg,
        x: 72, y: 940, w: 360, align: "RIGHT",
      });
      pCredit.opacity = 0.7;
      frame.appendChild(pCredit);
    }
  } else if (input.contextImage) {
    // Layout: text top half (y=330..820), image bottom half (y=850..1290)
    const bodyTxt = await txt({
      chars: input.paragraph,
      family: FONT_BODY, style: bodyStyle, size: 42,
      color: PALETTE.fg,
      x: 72, y: 330, w: 936, align: "RIGHT",
      lhPct: 155,
    });
    frame.appendChild(bodyTxt);

    const ctxRect = rect({
      x: 0, y: 850, w: 1080, h: 440, color: PALETTE.bg,
    });
    ctxRect.name = `context-${num}`;
    frame.appendChild(ctxRect);
    contextImageNodeId = ctxRect.id;

    if (input.contextImage.credit) {
      const cCredit = await txt({
        chars: input.contextImage.credit,
        family: FONT_DISPLAY, style: "Light", size: 22,
        color: PALETTE.fg,
        x: 72, y: 1252, w: 936, align: "RIGHT",
      });
      cCredit.opacity = 0.85;
      frame.appendChild(cCredit);
    }
  } else {
    // Text-only paragraph: full width
    const bodyTxt = await txt({
      chars: input.paragraph,
      family: FONT_BODY, style: bodyStyle, size: 42,
      color: PALETTE.fg,
      x: 72, y: 330, w: 936, align: "RIGHT",
      lhPct: 155,
    });
    frame.appendChild(bodyTxt);
  }

  // 4. Bottom URL strip
  await addBottomBar(frame, PALETTE.accent, PALETTE.fg);

  figma.currentPage.appendChild(frame);
  return {
    frameId: frame.id,
    portraitNodeId,
    contextImageNodeId,
  };
}
```

---

## buildCta

**CTA קנוני — אין קלט.** הטקסט קבוע: "בלי בעלי הון. בלי פרסומות. / בלי בולשיט / לתחקיר המלא".

```javascript
async function buildCta(slideIdx) {
  // Background: PALETTE.accent (not bg!)
  const frame = newFrame(`${String(slideIdx).padStart(2, "0")}-cta`, slideIdx, PALETTE.accent);

  // 1. Wordmark logo placeholder
  const wordmark = rect({ x: 300, y: 200, w: 480, h: 142, color: PALETTE.accent });
  wordmark.name = "wordmark-logo";
  frame.appendChild(wordmark);

  // 2. "בלי בעלי הון. בלי פרסומות." — Bold 56pt
  const line1 = await txt({
    chars: "בלי בעלי הון. בלי פרסומות.",
    family: FONT_DISPLAY, style: "Bold", size: 56,
    color: PALETTE.fg,
    x: 72, y: 460, w: 936, align: "CENTER",
    lhPct: 120,
  });
  frame.appendChild(line1);

  // 3. "בלי בולשיט" — Bold 110pt (dominant)
  const line2 = await txt({
    chars: "בלי בולשיט",
    family: FONT_DISPLAY, style: "Bold", size: 110,
    color: PALETTE.fg,
    x: 72, y: 580, w: 936, align: "CENTER",
    lhPct: 105,
  });
  frame.appendChild(line2);

  // 4. Button pill
  const btn = rect({
    x: 320, y: 920, w: 440, h: 110,
    color: PALETTE.fg, cornerRadius: 55,
  });
  btn.name = "btn-pill";
  frame.appendChild(btn);

  const btnTxt = await txt({
    chars: "לתחקיר המלא",
    family: "Inter", style: "Bold", size: 36,
    color: PALETTE.accent,
    x: 320, y: 953, w: 440, align: "CENTER",
  });
  frame.appendChild(btnTxt);

  // 5. Chrome logo top-right
  addLogo(frame, PALETTE.fg);

  // 6. Bottom strip INVERTED (white bg, accent text)
  await addBottomBar(frame, PALETTE.fg, PALETTE.accent);

  figma.currentPage.appendChild(frame);
  return {
    frameId: frame.id,
    wordmarkNodeId: wordmark.id,  // for upload_assets
  };
}
```

---

## Orchestrator

```javascript
async function buildCarousel(plan) {
  // plan = {
  //   palette: { bg, fg, accent, muted? },          // chosen per article (חוק 0b)
  //   cover: { title, label, byline, imageCredit }, // title verbatim (חוק 0a)
  //   paragraphs: [{ index, paragraph, bodyStyle?, portrait?, contextImage? }, ...],
  //   images: {
  //     coverHero: pathOrUrl,
  //     portraits: { [paragraphIndex]: pathOrUrl, ... },
  //     contexts:  { [paragraphIndex]: pathOrUrl, ... }
  //   }
  // }

  const coverResult = await buildCover(plan.cover);
  const frames = [coverResult.frameId];
  const imageUploads = [{ nodeId: coverResult.heroImageNodeId, image: plan.images.coverHero }];

  for (let i = 0; i < plan.paragraphs.length; i++) {
    const slideIdx = i + 1;
    const para = plan.paragraphs[i];
    const r = await buildParagraph(para, slideIdx);
    frames.push(r.frameId);
    if (r.portraitNodeId && plan.images.portraits[para.index]) {
      imageUploads.push({ nodeId: r.portraitNodeId, image: plan.images.portraits[para.index] });
    }
    if (r.contextImageNodeId && plan.images.contexts[para.index]) {
      imageUploads.push({ nodeId: r.contextImageNodeId, image: plan.images.contexts[para.index] });
    }
  }

  const ctaIdx = plan.paragraphs.length + 1;
  const ctaResult = await buildCta(ctaIdx);
  frames.push(ctaResult.frameId);
  imageUploads.push({
    nodeId: ctaResult.wordmarkNodeId,
    image: "assets/logo-wordmark-white.png",
    scaleMode: "FIT",
  });

  figma.currentPage.name = plan.cover.title.substring(0, 60);
  figma.viewport.scrollAndZoomIntoView(frames.map(id => figma.getNodeById(id)));

  return {
    frames,
    imageUploads,
    fontFallbackUsed,
    palette: plan.palette,
  };
}

return await buildCarousel(PLAN_FROM_PYTHON);
```

---

## Image upload (after Figma JS done)

```bash
# Per imageUpload entry:
# 1. upload_assets() returns submitUrl
# 2. POST file to submitUrl
curl -X POST -F "file=@${IMAGE_PATH}" "${SUBMIT_URL}"
```

`scaleMode`:
- `FILL` — cover hero, portraits, context images
- `FIT` — wordmark logo

---

## הערות

### פונט NextExit
`figma.loadFontAsync()` ייכשל אם NextExit לא מותקן במחשב + Figma לא עשה
restart. במקרה כזה ה-flag `fontFallbackUsed=true` מוחזר. ל-helper `txt()`
יש try/catch שנופל ל-Inter.

### שינוי fontName של node קיים שהיה ב-NextExit
אם node נוצר עם NextExit ועכשיו NextExit לא נטען, אי אפשר לשנות `fontSize`
או `characters` ישירות — Figma זורק שגיאה "Cannot write to node with
unloaded font". הפתרון: לשנות `fontName` קודם לפונט שנטען:
```javascript
await figma.loadFontAsync({ family: "Inter", style: "Bold" });
node.fontName = { family: "Inter", style: "Bold" };
node.fontSize = X;       // עכשיו עובד
node.characters = Y;     // עכשיו עובד
```

### RTL
Figma מזהה עברית אוטומטית. אין צורך בהגדרה מיוחדת. `textAlignHorizontal: "RIGHT"`
מספיק לכל הטקסטים העבריים.

### תמונות
`figma.createImage()` ב-plugin context דורש Uint8Array (לא URL).
לכן השתמש ב-`upload_assets` MCP tool במקום — הוא מטפל בהורדה/העלאה אוטומטית.

### Atomicity
כל קריאה ל-`use_figma` היא transaction נפרדת. אם נכשלת באמצע — חצי
מה-frames יישארו בקובץ. עוטפים ב-try/catch ומחזירים לדור URL + רשימת
frames שכן נוצרו, כדי שיוכל לסיים ידנית.
