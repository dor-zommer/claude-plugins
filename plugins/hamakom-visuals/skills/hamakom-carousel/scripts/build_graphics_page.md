# Build Graphics Page — תבנית Figma לעמוד הנלווה

> זה ה-**עמוד השני** של קובץ ה-Figma של הקרוסלה. 6 פריימים ממותגים לשימוש
> ב-Hero של האתר, אינסטגרם, פייסבוק, X, וואטסאפ. ראה גם סעיף "עמוד נלווה"
> ב-SKILL.md.

---

## Flow

```
1. אחרי שעמוד 1 (Carousel) נבנה ו-cover-hero-image הועלה
2. שמור את ה-imageHash שחזר מ-upload_assets
3. use_figma → buildGraphicsPage(coverImageHash, palette, content)
4. screenshot של hero-1140x815 + IG square ל-QA
```

---

## עקרונות עיצוב

1. **6 פורמטים תמיד** — לא יותר, לא פחות
2. **Hero לאתר = 1140×815** (לא 1920×1080 — האתר חותך!)
   **אינסטגרם = 1080×1350** (4:5 פיד — לא 1080×1080 ריבוע. וואטסאפ נשאר ריבוע.)
3. **תמונה אחת לכולם** — אותה תמונת hero/og:image של הכתבה
4. **לוגו במרכז התחתון** — לא בפינה. חלק מ-chrome התחתון.
5. **Lede חובה** (חוץ מ-FB) — משפט סיכום אחד מהכתבה
6. **Gradient שקוף למעלה** — מתחיל להחשיך רק מ-textStart
7. **כותרת = h1 verbatim** — לא ה-`<title>` SEO, לא קיצור, לא להמציא. ראה
   "כותרת" למטה.

---

## כותרת — חוק ברזל: h1 verbatim

**הכותרת היא ה-h1 של הכתבה, מילה במילה.** אסור להשתמש ב-`meta-og:title`
(זה לרוב SEO title — כותרת מקוצרת ופחות מדויקת לסושיאל). אסור לקצר.
אסור לשפץ. אסור להפוך לשאלה רטורית.

**איך לחלץ:** מה-WebFetch של הכתבה, הכותרת הראשונה אחרי הקטגוריה (לפני
ה-byline והתאריך). היא לרוב בתוך `# כותרת...` במרקדאון של ה-fetch.

**דוגמה לא נכון/נכון:**

```
HTML:
  <h1>מה מחקר על 17 פארקים בערים מעורבות חושף על המרחב הציבורי בישראל</h1>
  <meta property="og:title" content="פארק רק ליהודים? מחקר חושף הדרה בערים מעורבות">

✓ CONTENT.title = "מה מחקר על 17 פארקים בערים מעורבות חושף על המרחב הציבורי בישראל"
✗ CONTENT.title = "פארק רק ליהודים? מחקר חושף הדרה בערים מעורבות"
```

**אם ה-h1 ארוך:** הקטן `titleSize` בקונפיג של כל פורמט. אל תקטין את הטקסט.
Figma עושה wrap אוטומטי עם RIGHT align בעברית.

---

## תבנית JS (להזריק ל-use_figma)

```javascript
// ============================
// INPUTS (החליפו לפי הכתבה)
// ============================
const HERO_IMAGE_HASH = "<from upload_assets of cover image>";
const PALETTE = {
  bg:     { r: 0.0784, g: 0.0784, b: 0.0745 },  // example: dark
  fg:     { r: 0.9569, g: 0.9451, b: 0.9255 },
  accent: { r: 0.9686, g: 0.0510, b: 0.1569 },  // ha-makom red — קבוע
  muted:  { r: 0.6196, g: 0.5569, b: 0.4863 },
};
const CONTENT = {
  title:  "הכותרת המלאה של הכתבה מילה במילה",
  lede:   "משפט הסיכום של הכתבה — מה זה ולמה זה חשוב",
  label:  "תחקיר  ·  צבא",  // קטגוריות מהכתבה
  byline: "תחקיר: שם הכותב/ת  ·  הקשר",
};

// ============================
// FONT LOADING
// ============================
let FONT_DISPLAY = "Inter";
try {
  const fonts = await figma.listAvailableFontsAsync();
  if (fonts.some(f => f.fontName.family === "NextExit")) FONT_DISPLAY = "NextExit";
} catch (e) {}

for (const fam of [FONT_DISPLAY, "Inter"]) {
  for (const style of ["Bold", "Regular", "Light", "Semi Bold"]) {
    try { await figma.loadFontAsync({ family: fam, style }); } catch (e) {}
  }
}

// ============================
// CREATE PAGE
// ============================
const graphicsPage = figma.createPage();
graphicsPage.name = "Graphics — פורמטים";
await figma.setCurrentPageAsync(graphicsPage);

// ============================
// LOGO SVG — same as carousel
// ============================
const LOGO_SVG = `<...inline the same SVG from build_figma.md...>`;

// ============================
// HELPERS
// ============================
function rect({ x, y, w, h, color, fills, opacity = 1 }) {
  const r = figma.createRectangle();
  r.x = x; r.y = y; r.resize(w, h);
  if (fills) r.fills = fills;
  else r.fills = [{ type: "SOLID", color, opacity }];
  return r;
}

async function txt(opts) {
  const t = figma.createText();
  try { t.fontName = { family: opts.family, style: opts.style }; }
  catch (e) {
    try { t.fontName = { family: "Inter", style: opts.style }; } catch (e2) {
      try { t.fontName = { family: "Inter", style: "Regular" }; } catch (e3) {}
    }
  }
  t.fontSize = opts.size;
  if (opts.lhPct) t.lineHeight = { unit: "PERCENT", value: opts.lhPct };
  if (opts.letterSpacing != null) {
    t.letterSpacing = opts.letterSpacingUnit === "PERCENT"
      ? { unit: "PERCENT", value: opts.letterSpacing }
      : { unit: "PIXELS", value: opts.letterSpacing };
  }
  t.characters = opts.chars;
  t.textAlignHorizontal = opts.align;
  t.fills = [{ type: "SOLID", color: opts.color }];
  t.x = opts.x; t.y = opts.y;
  t.resize(opts.w, t.height);
  return t;
}

function makeLogo(fillColor, w, h) {
  const node = figma.createNodeFromSvg(LOGO_SVG);
  if ("fills" in node) node.fills = [];
  const recurse = (n) => {
    if (["VECTOR", "BOOLEAN_OPERATION", "POLYGON", "RECTANGLE"].includes(n.type)) {
      if ("fills" in n) n.fills = [{ type: "SOLID", color: fillColor }];
    }
    if ("children" in n) n.children.forEach(recurse);
  };
  recurse(node);
  node.resize(w, h);
  node.name = "logo";
  return node;
}

function gradientFor(textStart) {
  return {
    type: "GRADIENT_LINEAR",
    gradientTransform: [[0, 1, 0], [-1, 0, 1]],
    gradientStops: [
      { position: 0.00, color: { ...PALETTE.bg, a: 0.0 } },
      { position: Math.max(0.01, textStart - 0.15), color: { ...PALETTE.bg, a: 0.0 } },
      { position: textStart, color: { ...PALETTE.bg, a: 0.78 } },
      { position: 1.00, color: { ...PALETTE.bg, a: 1.0 } },
    ],
  };
}

// ============================
// BUILD GRAPHIC FRAME
// ============================
async function buildGraphic(name, posX, posY, W, H, opts) {
  const frame = figma.createFrame();
  frame.name = name;
  frame.resize(W, H);
  frame.x = posX; frame.y = posY;
  frame.fills = [{ type: "SOLID", color: PALETTE.bg }];
  frame.clipsContent = true;

  // 1. Background image (full-bleed)
  const photo = rect({ x: 0, y: 4, w: W, h: H - 4, color: PALETTE.bg });
  photo.name = "photo";
  photo.fills = [{ type: "IMAGE", scaleMode: "FILL", imageHash: HERO_IMAGE_HASH }];
  frame.appendChild(photo);

  // 2. Gradient overlay
  const grad = rect({ x: 0, y: 4, w: W, h: H - 4, color: PALETTE.bg });
  grad.fills = [gradientFor(opts.textStart)];
  frame.appendChild(grad);

  // 3. Top red stripe
  frame.appendChild(rect({ x: 0, y: 0, w: W, h: 4, color: PALETTE.accent }));

  const padX = opts.padX;
  const contentW = W - padX * 2;

  // 4. Label
  const labelTxt = await txt({
    chars: CONTENT.label,
    family: "Inter", style: "Bold", size: opts.labelSize,
    color: PALETTE.accent,
    x: padX, y: Math.floor(H * opts.textStart) + opts.labelOffsetTop, w: contentW, align: "RIGHT",
    letterSpacing: 4, letterSpacingUnit: "PIXELS",
  });
  frame.appendChild(labelTxt);

  // 5. Title — NextExit Bold (or Inter fallback)
  const title = await txt({
    chars: CONTENT.title,
    family: FONT_DISPLAY, style: "Bold", size: opts.titleSize,
    color: PALETTE.fg,
    x: padX, y: labelTxt.y + labelTxt.height + opts.labelToTitleGap, w: contentW, align: "RIGHT",
    lhPct: 112,
    letterSpacing: -2, letterSpacingUnit: "PERCENT",
  });
  frame.appendChild(title);

  // 6. Lede (optional, narrower width)
  if (opts.showLede) {
    const ledeW = Math.floor(contentW * opts.ledeWidthPct);
    const ledeX = W - padX - ledeW;
    const lede = await txt({
      chars: CONTENT.lede,
      family: "Inter", style: "Regular", size: opts.ledeSize,
      color: PALETTE.fg,
      x: ledeX, y: title.y + title.height + opts.titleToLedeGap, w: ledeW, align: "RIGHT",
      lhPct: 140,
    });
    frame.appendChild(lede);
  }

  // 7. Bottom chrome: byline → logo (centered) → URL strip
  const stripeH = opts.stripeH;
  const logoH = opts.logoH;
  const logoW = Math.round(logoH * (826.779 / 981.533));
  const urlStripY = H - stripeH;
  const logoY = urlStripY - logoH - opts.logoBottomGap;

  const byline = await txt({
    chars: CONTENT.byline,
    family: "Inter", style: "Regular", size: opts.bylineSize,
    color: PALETTE.muted,
    x: padX, y: logoY - opts.logoTopGap - opts.bylineSize - 6, w: contentW, align: "RIGHT",
  });
  frame.appendChild(byline);

  const logo = makeLogo(PALETTE.fg, logoW, logoH);
  logo.x = Math.floor((W - logoW) / 2);
  logo.y = logoY;
  frame.appendChild(logo);

  frame.appendChild(rect({ x: 0, y: urlStripY, w: W, h: stripeH, color: PALETTE.accent }));
  const urlTxt = await txt({
    chars: "H A - M A K O M . C O . I L",
    family: "Inter", style: "Bold", size: opts.urlSize,
    color: PALETTE.fg,
    x: 0, y: urlStripY + Math.floor((stripeH - opts.urlSize) / 2) - 2, w: W, align: "CENTER",
    letterSpacing: 3, letterSpacingUnit: "PIXELS",
  });
  frame.appendChild(urlTxt);

  graphicsPage.appendChild(frame);
  return frame.id;
}

// ============================
// BUILD 6 FORMATS
// ============================

// 1. Hero לאתר — 1140×815 (קריטי, לא 1920×1080)
await buildGraphic("hero-1140x815-site", 0, 0, 1140, 815, {
  textStart: 0.52, padX: 52,
  labelSize: 18, labelOffsetTop: -8, labelToTitleGap: 8,
  titleSize: 46, titleToLedeGap: 16,
  showLede: true, ledeSize: 18, ledeWidthPct: 0.70,
  stripeH: 34, logoH: 42, logoBottomGap: 8, logoTopGap: 8,
  bylineSize: 16, urlSize: 16,
});

// 2. Instagram feed post — 1080×1350 (4:5). NOT square — square is the old format.
await buildGraphic("instagram-1080x1350", 1260, 0, 1080, 1350, {
  textStart: 0.50, padX: 60,
  labelSize: 24, labelOffsetTop: 8, labelToTitleGap: 8,
  titleSize: 52, titleToLedeGap: 20,
  showLede: true, ledeSize: 24, ledeWidthPct: 0.68,
  stripeH: 52, logoH: 72, logoBottomGap: 12, logoTopGap: 14,
  bylineSize: 22, urlSize: 22,
});

// 3. IG Story — 1080×1920
await buildGraphic("ig-story-1080x1920", 2460, 0, 1080, 1920, {
  textStart: 0.55, padX: 72,
  labelSize: 26, labelOffsetTop: 24, labelToTitleGap: 10,
  titleSize: 95, titleToLedeGap: 24,
  showLede: true, ledeSize: 35, ledeWidthPct: 0.65,
  stripeH: 56, logoH: 92, logoBottomGap: 12, logoTopGap: 18,
  bylineSize: 30, urlSize: 23,
});

// 4. Facebook — 1200×630 (compact, no lede)
await buildGraphic("facebook-1200x630", 0, 2050, 1200, 630, {
  textStart: 0.42, padX: 56,
  labelSize: 16, labelOffsetTop: 14, labelToTitleGap: 4,
  titleSize: 40, titleToLedeGap: 10,
  showLede: false,
  stripeH: 28, logoH: 38, logoBottomGap: 6, logoTopGap: 6,
  bylineSize: 16, urlSize: 16,
});

// 5. X — 1600×900
await buildGraphic("x-1600x900", 1320, 2050, 1600, 900, {
  textStart: 0.45, padX: 72,
  labelSize: 20, labelOffsetTop: 18, labelToTitleGap: 6,
  titleSize: 52, titleToLedeGap: 14,
  showLede: true, ledeSize: 20, ledeWidthPct: 0.68,
  stripeH: 36, logoH: 48, logoBottomGap: 8, logoTopGap: 8,
  bylineSize: 18, urlSize: 18,
});

// 6. WhatsApp — 1080×1080 (same config as IG Square)
await buildGraphic("whatsapp-1080x1080", 0, 3100, 1080, 1080, {
  textStart: 0.45, padX: 60,
  labelSize: 24, labelOffsetTop: 30, labelToTitleGap: 8,
  titleSize: 60, titleToLedeGap: 20,
  showLede: true, ledeSize: 22, ledeWidthPct: 0.65,
  stripeH: 50, logoH: 64, logoBottomGap: 10, logoTopGap: 14,
  bylineSize: 22, urlSize: 22,
});

return { status: "ok", pageId: graphicsPage.id, fontDisplay: FONT_DISPLAY };
```

---

## ⚠️ Gotcha חשוב — תמונה לא מופיעה אחרי upload_assets

**הבעיה:** `upload_assets({ nodeId, ... })` בעמוד שאינו currentPage **מחזיר
`success: true` אבל לא מחיל את התמונה כ-fill על ה-node**. הפלייסהולדר נשאר
עם SOLID color מקורי, התוצאה נראית שחור.

**אבחון:** קריאה ל-`get_metadata` או `use_figma` שמדפיסה את `child.fills`
מראה `SOLID` במקום `IMAGE`.

**הפתרון:** במקום `upload_assets` עם nodeId, השתמש ב-`upload_assets` ללא
nodeId (פעם אחת בלבד) כדי לקבל imageHash, ואז החל ידנית:

```javascript
// In a separate use_figma call
const HASH = "<from earlier upload>";
const photoNodeIds = ["8:4", "8:36", "8:67", "8:99", "8:130", "8:162"];
for (const id of photoNodeIds) {
  const node = await figma.getNodeByIdAsync(id);
  node.fills = [{ type: "IMAGE", scaleMode: "FILL", imageHash: HASH }];
}
```

או — פשוט תכלול את הקריאה הזו כחלק מסוף `buildGraphicsPage`, אם ה-hash
זמין מההעלאה של ה-cover.

---

## עיצוב מנהג — כן/לא

✓ **כן:** Lede אחד שמסכם את הכתבה, אותה תמונה לכל 6 הפורמטים, לוגו תחתון-מרכזי

✗ **לא:**
- לא לעשות Hero ב-1920×1080 (האתר חותך)
- לא להשתמש ב-`upload_assets` עם nodeId לעמוד 2 — לא עובד עקבית
- לא לבנות גרדיאנט שמתחיל מ-alpha 0.20+ למעלה — מסתיר את התמונה
- לא להוסיף פורמט שביעי — 6 זה מספיק

---

## פלט QA

לאחר בנייה, screenshot של:
1. `hero-1140x815-site` (לוודא טקסט בתוך המסגרת ולא נחתך)
2. `instagram-1080x1350` (לוודא תמונה נראית, לא שחור)

אם התמונה לא נראית באף אחד — לעבור על ה-Gotcha למעלה.
