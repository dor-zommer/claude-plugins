# Build Graphics Page — תבנית Figma לעמוד הגרפיקות

> עמוד Figma אחד עם 3 פריימים ממותגים לכתבה: whatsapp-1080x1080,
> instagram-1080x1350, ig-story-1080x1920. ראה גם SKILL.md של hamakom-graphic.

---

## Flow

```
1. create_new_file (editorType=design)
2. use_figma → buildGraphicsPage(imageHash, palette, content) — בונה 3 פריימים
3. upload_assets לתמונה → שמור imageHash
4. החל את ה-imageHash על 3 הפלייסהולדרים (ישירות, ראה Gotcha)
5. screenshot של 3 הפריימים ל-QA
```

---

## עקרונות עיצוב

1. **3 פורמטים תמיד** — whatsapp 1:1, instagram 4:5, ig-story 9:16. לא יותר, לא פחות.
2. **אינסטגרם = 1080×1350** (4:5 פיד — לא 1080×1080 ריבוע. וואטסאפ נשאר ריבוע.)
3. **תמונה אחת לכולם** — אותה תמונת og:image של הכתבה
4. **לוגו במרכז התחתון** — לא בפינה. חלק מ-chrome התחתון.
5. **Lede חובה** — משפט סיכום אחד מהכתבה
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
// BUILD 3 FORMATS
// (whatsapp 1:1, instagram 4:5, ig-story 9:16 — אלה הפרופורציות שדור אישר)
// ============================

// 1. WhatsApp / Telegram — 1080×1080 (ריבוע 1:1)
await buildGraphic("whatsapp-1080x1080", 0, 0, 1080, 1080, {
  textStart: 0.45, padX: 60,
  labelSize: 24, labelOffsetTop: 30, labelToTitleGap: 8,
  titleSize: 60, titleToLedeGap: 20,
  showLede: true, ledeSize: 22, ledeWidthPct: 0.65,
  stripeH: 50, logoH: 64, logoBottomGap: 10, logoTopGap: 14,
  bylineSize: 22, urlSize: 22,
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

// 3. IG Story — 1080×1920 (9:16)
await buildGraphic("ig-story-1080x1920", 2520, 0, 1080, 1920, {
  textStart: 0.55, padX: 72,
  labelSize: 26, labelOffsetTop: 24, labelToTitleGap: 10,
  titleSize: 95, titleToLedeGap: 24,
  showLede: true, ledeSize: 35, ledeWidthPct: 0.65,
  stripeH: 56, logoH: 92, logoBottomGap: 12, logoTopGap: 18,
  bylineSize: 30, urlSize: 23,
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
const photoNodeIds = ["1:4", "1:36", "1:67"];  // 3 פלייסהולדרים: whatsapp, instagram, ig-story
for (const id of photoNodeIds) {
  const node = await figma.getNodeByIdAsync(id);
  node.fills = [{ type: "IMAGE", scaleMode: "FILL", imageHash: HASH }];
}
```

או — פשוט תכלול את הקריאה הזו כחלק מסוף `buildGraphicsPage`, אם ה-hash
זמין מההעלאה של ה-cover.

---

## עיצוב מנהג — כן/לא

✓ **כן:** Lede אחד שמסכם את הכתבה, אותה תמונה לכל 3 הפורמטים, לוגו תחתון-מרכזי

✗ **לא:**
- לא להפוך אינסטגרם לריבוע — פיד הוא 4:5 (1080×1350). ריבוע רק לוואטסאפ.
- לא להשתמש ב-`upload_assets` עם nodeId על עמוד שאינו currentPage — לא עובד עקבית
- לא לבנות גרדיאנט שמתחיל מ-alpha 0.20+ למעלה — מסתיר את התמונה
- לא להוסיף פורמט רביעי — 3 זה מה שדור צריך (hero/facebook/X לא בשימוש)

---

## פלט QA

לאחר בנייה, screenshot של 3 הפריימים:
1. `whatsapp-1080x1080` (ריבוע — טקסט בתוך המסגרת)
2. `instagram-1080x1350` (4:5 — תמונה נראית, לא שחור)
3. `ig-story-1080x1920` (9:16 — טקסט תחתון לא נחתך)

אם התמונה לא נראית באף אחד — לעבור על ה-Gotcha למעלה.
