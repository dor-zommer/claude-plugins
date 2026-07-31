# Build Graphics Page — תבנית Figma לעמוד הגרפיקות (HaMakom DS 2026)

> עמוד Figma אחד עם 3 פריימים ממותגים לכתבה: whatsapp-1080x1080,
> instagram-1080x1350, ig-story-1080x1920. ראה גם SKILL.md + מקור-האמת
> `../../../design-system/HAMAKOM-DS-2026.md`.
> פלטה: שנהב/דיו/טרקוטה. פונטים: Publico Headline Hebrew **Extrabold** (כותרת)
> + Graphik HLAR (גוף). הגרפיקה היא **cover-style**: תמונה full-bleed +
> gradient דיו + טקסט לבן.

---

## Flow

```
1. whoami → planKey
2. create_new_file (editorType=design)
3. upload_assets לתמונה — בלי nodeId → שמור imageHash
4. use_figma (עם פרמטר description!) → בונה 3 פריימים עם ה-imageHash
5. פריים בדיקה לכיול titleSize (מקף!) → get_screenshot → קובע גודל → מוחק אותו
6. get_screenshot על 3 הפריימים ל-QA
```

**`use_figma` דורש `description`.** בלי הפרמטר הזה הקריאה נופלת ב-validation
error לפני שהיא רצה. אין קשר לתוכן הסקריפט — פשוט לזכור לשלוח אותו.

---

## עקרונות עיצוב

1. **3 פורמטים תמיד** — whatsapp 1:1, instagram 4:5, ig-story 9:16.
2. **אינסטגרם = 1080×1350** (4:5 פיד — לא ריבוע. וואטסאפ נשאר ריבוע.)
3. **תמונה אחת לכולם** — אותה תמונת og/featured של הכתבה, full-bleed.
4. **לוגו לבן במרכז התחתון** (חלק מ-chrome התחתון, מעל פס-החתימה).
5. **כותרת + byline בלבד** — אין קיקר, אין lede, אין משנה, אין תגית קטגוריה.
6. **הכותרת צמודה ל-byline** — `titleGap = 0`. ממקמים מלמטה למעלה:
   byline → כותרת ישירות מעליו. הכותרת היא האלמנט העליון.
7. **byline = `שם | סוג הכתבה`** (בלי "מאת:"), Graphik Semibold.
   טור דעה → **אברש `#8E6FA8`**; תחקיר/כתבה → ink-soft `#6b6a63`.
8. **Gradient מעוגן בכותרת** — `p3 = titleFrac + 0.036`, `p2 = p3 − 0.327`.
   ~65-70% העליונים של התמונה גלויים לחלוטין.
9. **כותרת = h1 verbatim**, Publico Headline **Extrabold** — לא `og:title`, לא קיצור.
10. **פס-חתימה טריקולור תחתון יחיד** — 4px בקצה התחתון (טרקוטה·מרווה·אברש). אין פס עליון.
11. **שורת תחתית צמודה לפס**: credit צילום שמאל (x≈18, לבן opacity 0.53) +
    `HA-MAKOM.CO.IL` ממורכז (on-dark-soft). **תמונת AI — בלי שורת credit.**

---

## כותרת — שני חוקים

**א. h1 verbatim.** הכותרת היא ה-h1 של הכתבה, מילה במילה. אסור `og:title`
(SEO), אסור לקצר/לשפץ.

**ב. `titleSize` נקבע במדידה, לא בהעתקה מהקונפיג.** אם הכותרת מכילה מקף
מפריד ו-Figma שובר את השורה שם, המקף קופץ לקצה הלא נכון ונראה כמו טעות.
בנה פריים בדיקה עם 4–5 גדלים, צלם, בחר את הגדול ביותר שבו המקף תקין ואין
מילה יתומה — ואז מחק את פריים הבדיקה. הנימוק המלא ב-SKILL.md.

---

## תבנית JS (להזריק ל-use_figma)

```javascript
// ============================ INPUTS ============================
const HERO_IMAGE_HASH = "<from upload_assets of cover image>";
const C = {
  ink:{r:0.0784,g:0.0784,b:0.0745},     // דיו — gradient + רקע
  terra:{r:0.851,g:0.4667,b:0.3412}, sage:{r:0.4706,g:0.549,b:0.3647}, heather:{r:0.5569,g:0.4353,b:0.6588},
  inkSoft:{r:0.4196,g:0.4157,b:0.3882}, // byline של תחקיר/כתבה
  onDarkSoft:{r:0.7176,g:0.7098,b:0.6745}, white:{r:1,g:1,b:1},
};
const CONTENT = {
  title:  "הכותרת המלאה של הכתבה מילה במילה",   // h1 verbatim — האלמנט העליון
  byline: "שם הכותב/ת | טור דעה",                // שם + סוג, בלי "מאת:"
  credit: "צילום: ... (verbatim מה-figcaption)",  // null בתמונת AI/המחשה
};
const OPINION = true;   // טור דעה → byline באברש; אחרת ink-soft

// ============================ FONTS ============================
// חובה fallback ל-TRIAL לפני Inter: Figma לעיתים מגיש רשימת פונטים ישנה
// שבה הקבצים המורשים לא מופיעים, ורק ה-TRIAL של אותם typefaces זמין.
// נפילה ל-TRIAL כמעט בלתי מורגשת; נפילה ל-Inter שוברת את הזהות.
const fonts = await figma.listAvailableFontsAsync();
const AV = new Set(fonts.map(f => f.fontName.family + "||" + f.fontName.style));
const FB = {family:"Inter", style:"Regular"};
const pick = cands => cands.find(c => AV.has(c.family+"||"+c.style)) || cands[cands.length-1] || FB;
const ROLE = {
  disp:   pick([{family:"Publico Headline Hebrew",style:"Roman"},{family:"Publico Headline Hebrew Roman",style:"Regular"},{family:"Publico Headline Hebrew TRIAL",style:"Roman"},FB]),
  dispXB: pick([{family:"Publico Headline Hebrew",style:"Extrabold"},{family:"Publico Headline Hebrew Exbold",style:"Regular"},{family:"Publico Headline Hebrew TRIAL",style:"Extrabold"},FB]),
  light:  pick([{family:"Graphik HLAR",style:"Light"},{family:"Graphik HLAR Light",style:"Regular"},{family:"Graphik HLAR TRIAL",style:"Light"},FB]),
  reg:    pick([{family:"Graphik HLAR",style:"Regular"},{family:"Graphik HLAR TRIAL",style:"Regular"},FB]),
  med:    pick([{family:"Graphik HLAR",style:"Medium"},{family:"Graphik HLAR Medium",style:"Regular"},{family:"Graphik HLAR TRIAL",style:"Medium"},FB]),
  semi:   pick([{family:"Graphik HLAR",style:"Semibold"},{family:"Graphik HLAR TRIAL",style:"Semibold"},FB]),
};
// HaMakom — פונט תצוגת המותג (53 גליפים: עברית+ספרות+פיסוק, בלי לטינית/em-dash).
// לרוב לא זמין ב-Figma, וזה בסדר: h1 עם לטינית או מקף ממילא הולך ל-Publico.
const HAMAKOM = pick([{family:"HaMakom",style:"Regular"},FB]);
const HAMAKOM_GLYPHS = /^[ -"'-),-;?־א-ת׳-״]*$/;
const hamakomOK = s => HAMAKOM.family==="HaMakom" && HAMAKOM_GLYPHS.test(s);
function dispFont(text){ return hamakomOK(text) ? HAMAKOM : ROLE.dispXB; }  // כותרת = Extrabold
function roleFor(fam, style){
  if (fam==="HEAD") return style==="Extrabold" ? ROLE.dispXB : ROLE.disp;
  if (style==="Light") return ROLE.light;
  if (style==="Semibold") return ROLE.semi;
  if (style==="Medium"||style==="Bold") return ROLE.med;
  return ROLE.reg;
}
const HEAD="HEAD", BODY="BODY";
for (const r of [...Object.values(ROLE), HAMAKOM]) { try{ await figma.loadFontAsync(r);}catch(e){} }
const fontFallback = Object.values(ROLE).some(r => r.family==="Inter");      // כשל אמיתי
const trialCuts    = Object.values(ROLE).some(r => /TRIAL/.test(r.family));  // לציין בלבד

// ============================ PAGE ============================
const graphicsPage = figma.createPage();
graphicsPage.name = "Graphics — פורמטים";
await figma.setCurrentPageAsync(graphicsPage);

// קרא את הקובץ והדבק כאן את תוכנו כמו שהוא:
// design-system/assets/logo/logo-square-black.svg  (viewBox 0 0 826.779 981.533)
const LOGO_SVG = `<...paste the SVG file contents verbatim...>`;

// ============================ HELPERS ============================
function rect({ x, y, w, h, color, fills, opacity = 1 }) {
  const r = figma.createRectangle(); r.x=x; r.y=y; r.resize(w,h);
  if (fills) r.fills=fills; else r.fills=[{type:"SOLID",color,opacity}]; return r;
}
async function txt(o) {
  const t = figma.createText();
  const fn = o.font || roleFor(o.family, o.style);
  try { t.fontName=fn; } catch(e){ t.fontName={family:"Inter",style:"Regular"}; }
  t.fontSize=o.size; if(o.lhPct) t.lineHeight={unit:"PERCENT",value:o.lhPct};
  if(o.letterSpacing!=null) t.letterSpacing={unit:"PIXELS",value:o.letterSpacing};
  t.characters=o.chars; t.textAlignHorizontal=o.align; t.fills=[{type:"SOLID",color:o.color}];
  t.textAutoResize="HEIGHT";           // חובה לפני resize — אחרת הטקסט נחתך
  t.resize(o.w, t.height);
  t.x=o.x; t.y=o.y; return t;
}
function makeLogo(fillColor, w, h) {
  const node = figma.createNodeFromSvg(LOGO_SVG); if ("fills" in node) node.fills=[];
  const rec=(n)=>{ if(["VECTOR","BOOLEAN_OPERATION","POLYGON","RECTANGLE"].includes(n.type)){ if("fills" in n) n.fills=[{type:"SOLID",color:fillColor}]; } if("children" in n) n.children.forEach(rec); };
  rec(node); node.resize(w,h); node.name="logo"; return node;
}
// פס-חתימה טריקולור ברוחב מלא. פעם אחת לפריים — תחתון, h=4, y=H-4. אין פס עליון.
function sig(frame, W, y, h){
  const t=Math.round(W/3);
  frame.appendChild(rect({x:2*t,y,w:W-2*t,h,color:C.terra}));
  frame.appendChild(rect({x:t,y,w:t,h,color:C.sage}));
  frame.appendChild(rect({x:0,y,w:t,h,color:C.heather}));
}
// גרדיאנט מעוגן בכותרת — היחסים שדור כייל ידנית 31.07.2026
function gradientFor(titleFrac) {
  const p3 = titleFrac + 0.036;
  const p2 = Math.max(0.001, p3 - 0.327);
  return { type:"GRADIENT_LINEAR", gradientTransform:[[0,1,0],[-1,0,1]], gradientStops:[
    { position:0.0, color:{...C.ink,a:0.0} },
    { position:p2,  color:{...C.ink,a:0.0} },
    { position:p3,  color:{...C.ink,a:0.72} },
    { position:1.0, color:{...C.ink,a:1.0} },
  ]};
}

// ============================ BUILD FRAME ============================
// מלמטה למעלה: פס-חתימה → שורת credit+url → לוגו → byline → כותרת (צמודה, gap 0).
// הגרדיאנט מחושב לפי מיקום הכותרת בפועל ומוזרק מעל התמונה, מתחת לטקסט.
async function buildGraphic(name, posX, posY, W, H, o) {
  const frame = figma.createFrame(); frame.name=name; frame.resize(W,H);
  frame.x=posX; frame.y=posY; frame.fills=[{type:"SOLID",color:C.ink}]; frame.clipsContent=true;

  // 1. תמונה full-bleed
  const photo = rect({ x:0, y:0, w:W, h:H, color:C.ink }); photo.name="photo";
  photo.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:HERO_IMAGE_HASH}]; frame.appendChild(photo);

  // 2. chrome תחתון
  const sigH=4, sigY=H-sigH;
  sig(frame, W, sigY, sigH);
  const url = await txt({ chars:"HA-MAKOM.CO.IL", family:BODY, style:"Medium", size:o.urlSize,
    color:C.onDarkSoft, x:0, y:sigY-o.urlSize-12, w:W, align:"CENTER", letterSpacing:3 });
  frame.appendChild(url);
  if (CONTENT.credit) {                       // צילום בלבד — תמונת AI בלי credit
    const credit = await txt({ chars:CONTENT.credit, family:BODY, style:"Regular", size:18,
      color:C.white, x:18, y:0, w:o.creditW, align:"LEFT" });
    credit.fills=[{type:"SOLID",color:C.white,opacity:0.53}];
    credit.y = sigY - credit.height - 10; frame.appendChild(credit);
  }
  const logoH=o.logoH, logoW=Math.round(logoH*(826.779/981.533));
  const logo=makeLogo(C.white, logoW, logoH);
  logo.x=Math.floor((W-logoW)/2); logo.y=url.y-logoH-o.logoGap; frame.appendChild(logo);

  // 3. byline — שם | סוג, בצבע התפקיד
  const byline = await txt({ chars:CONTENT.byline, family:BODY, style:"Semibold", size:o.bylineSize,
    color: OPINION ? C.heather : C.inkSoft, x:52, y:0, w:952, align:"RIGHT" });
  byline.y = logo.y - o.bylineGap - byline.height; frame.appendChild(byline);

  // 4. כותרת Publico Extrabold verbatim — צמודה ל-byline (gap 0), האלמנט העליון
  const title = await txt({ chars:CONTENT.title, font:dispFont(CONTENT.title), size:o.titleSize,
    color:C.white, x:60, y:0, w:952, align:"RIGHT", lhPct:108 });
  title.y = byline.y - title.height; frame.appendChild(title);

  // 5. gradient — לפי מיקום הכותרת בפועל; מעל התמונה, מתחת לטקסט
  const grad = rect({ x:0, y:0, w:W, h:H, fills:[gradientFor(title.y / H)] });
  grad.name = "gradient";
  frame.insertChild(1, grad);

  graphicsPage.appendChild(frame);
  return { id:frame.id, photoId:photo.id, titleId:title.id,
    titleH:Math.round(title.height), titleFrac:+(title.y/H).toFixed(3), chars:title.characters };
}

// ============================ 3 FORMATS (W=1080) ============================
// titleSize = נקודת פתיחה. כייל לפי בדיקת המקף לפני שמוסרים.
const r1 = await buildGraphic("whatsapp-1080x1080", 0, 0, 1080, 1080, {
  titleSize:70, bylineSize:30, bylineGap:34, logoH:60, logoGap:16, urlSize:21, creditW:480 });

const r2 = await buildGraphic("instagram-1080x1350", 1260, 0, 1080, 1350, {
  titleSize:70, bylineSize:30, bylineGap:34, logoH:64, logoGap:18, urlSize:21, creditW:480 });

const r3 = await buildGraphic("ig-story-1080x1920", 2520, 0, 1080, 1920, {
  titleSize:80, bylineSize:38, bylineGap:43, logoH:84, logoGap:20, urlSize:23, creditW:520 });

// אימות שקט: הכותרת חייבת להיות זהה תו-בתו בשלושת הפריימים
const titlesIdentical = new Set([r1,r2,r3].map(r=>r.chars)).size === 1;

return { status:"ok", pageId:graphicsPage.id, fontFallback, trialCuts, titlesIdentical,
  resolved:ROLE, frames:[r1,r2,r3], createdNodeIds:[r1.id,r2.id,r3.id] };
```

---

## ⚠️ Gotcha — תמונה לא מופיעה אחרי upload_assets

`upload_assets({nodeId})` בעמוד שאינו currentPage מחזיר `success:true` אבל לא
מחיל את ה-fill. הפתרון: `upload_assets` **ללא nodeId** (פעם אחת) → imageHash,
ואז להשתמש בו ישירות בסקריפט (כמו בתבנית למעלה), או:

```javascript
const HASH = "<from upload>";
for (const id of ["1:4","1:36","1:67"]) {
  const node = await figma.getNodeByIdAsync(id);
  node.fills = [{ type:"IMAGE", scaleMode:"FILL", imageHash:HASH }];
}
```

ה-URL שמוחזר מ-`upload_assets` הוא `submitUrl` — צריך POST של הקובץ עליו
(`curl -F "file=@..."`), והתשובה מחזירה את ה-`imageHash`.

---

## עיצוב — כן/לא

✓ תמונה full-bleed, gradient דיו מעוגן בכותרת, כותרת Publico **Extrabold** לבנה
צמודה ל-byline כאלמנט העליון, byline `שם | סוג` בצבע התפקיד, לוגו מרכזי-תחתון,
שורת credit+url צמודה לפס, פס-חתימה טריקולור תחתון יחיד 4px.

✗ אסור: אדום `#f70d28` / פס אדום / NextExit; פס-חתימה עליון; **כל שכבת טקסט
מעל הכותרת** — קיקר, lede, משנה או תגית קטגוריה; "מאת:" ב-byline; כותרת
באמצע הפריים; רווח בין הכותרת ל-byline; אינסטגרם ריבוע (פיד=4:5); gradient
שמחשיך מעל אזור הטקסט; פורמט רביעי; נפילה ל-Inter.

---

## פלט QA

`get_screenshot` על 3 הפריימים — לוודא: תמונה נראית (~65-70% העליונים גלויים),
**המקף בכותרת במקום הנכון**, אין מילה יתומה בשורה אחרונה, הכותרת זהה תו-בתו
בשלושת הפריימים, byline בצבע התפקיד, פונטים לא Inter, פס-חתימה תחתון יחיד,
לוגו לבן מרכזי, ופריימי בדיקה זמניים נמחקו.
