# Build Update Card — תבנית Figma לכרטיס העדכון (HaMakom DS 2026)

> עמוד Figma אחד עם 3 פריימים: `update-whatsapp-1080x1080`,
> `update-instagram-1080x1350`, `update-story-1080x1920`.
> **קרא קודם** את SKILL.md ואת `../../design-system/HAMAKOM-DS-2026.md`.
> `use_figma` דורש פרמטר `description` — בלעדיו הקריאה נופלת ב-validation.

---

## Flow

```
1. whoami → planKey
2. create_new_file (editorType=design)
3. crop_for_formats.py base.png <YV>   → sq.png / feed.png / story.png
4. upload_assets count=4 (בלי nodeId) → POST כל קובץ → 4 imageHashes
5. use_figma → בונה את שלושת הפריימים
6. תיקון ה-pill לפי רוחב הטקסט (ראה "מלכודת ה-pill")
7. get_screenshot ×3 ל-QA → ניקוי Page 1
```

---

## תבנית JS

```javascript
// ============================ INPUTS ============================
const IMG = { sq:"<hash>", feed:"<hash>", story:"<hash>" };
const WORDMARK = "<hash>";
const WM_AR = 600/193;                       // יחס הוורדמרק המקורי

const C = {
  ink:{r:0.0784,g:0.0784,b:0.0745},
  terra:{r:0.851,g:0.4667,b:0.3412},
  sage:{r:0.4706,g:0.549,b:0.3647},
  heather:{r:0.5569,g:0.4353,b:0.6588},
  white:{r:1,g:1,b:1},
};
const CONTENT = {
  pill:  "עכשיו ב<מקום>",
  head:  "<שורת העדכון — שורה אחת>",
  sub:   "<סטטוס במשפט אחד>",
  byline:"<שם> | <סוג>",
};

// ============================ FONTS ============================
// resolver מלא עם fallback ל-TRIAL — ראה SKILL.md. נפילה ל-Inter היא כשל.

// ============================ PAGE ============================
const page = figma.createPage();
page.name = "Update card — 3 פורמטים";
await figma.setCurrentPageAsync(page);

// ============================ HELPERS ============================
function R(o){ const r=figma.createRectangle(); r.x=o.x; r.y=o.y; r.resize(o.w,o.h);
  if(o.fills) r.fills=o.fills;
  else r.fills=[{type:"SOLID",color:o.color,opacity:o.opacity==null?1:o.opacity}];
  if(o.cornerRadius!=null) r.cornerRadius=o.cornerRadius; return r; }

async function T(o){ const t=figma.createText();
  try{ t.fontName=o.font; }catch(e){ t.fontName={family:"Inter",style:"Regular"}; }
  t.fontSize=o.size; if(o.lhPct) t.lineHeight={unit:"PERCENT",value:o.lhPct};
  t.characters=o.chars; t.textAlignHorizontal=o.align;
  t.fills=[{type:"SOLID",color:o.color,opacity:o.opacity==null?1:o.opacity}];
  t.textAutoResize="HEIGHT"; t.resize(o.w,t.height); t.x=o.x; t.y=o.y; return t; }

// ============================ BUILD FRAME ============================
// מלמטה למעלה: פס → וורדמרק → byline → sub → head → pill → גרדיאנט.
async function buildCard(name, posX, W, H, imgHash, S) {
  const f = figma.createFrame(); f.name=name; f.resize(W,H); f.x=posX; f.y=0;
  f.fills=[{type:"SOLID",color:C.ink}]; f.clipsContent=true;

  const photo = R({x:0,y:0,w:W,h:H,color:C.ink}); photo.name="photo";
  photo.fills=[{type:"IMAGE",scaleMode:"FILL",imageHash:imgHash}];
  f.appendChild(photo);

  // פס-חתימה טריקולור תחתון יחיד
  const sigY = H - S.sigH, t3 = Math.round(W/3);
  f.appendChild(R({x:2*t3,y:sigY,w:W-2*t3,h:S.sigH,color:C.terra}));
  f.appendChild(R({x:t3,   y:sigY,w:t3,     h:S.sigH,color:C.sage}));
  f.appendChild(R({x:0,    y:sigY,w:t3,     h:S.sigH,color:C.heather}));

  // וורדמרק — העוגן של כל גוש הטקסט
  const wmH = Math.round(S.wmW / WM_AR);
  const wm = R({x:Math.round((W-S.wmW)/2), y:S.wmBottom-wmH, w:S.wmW, h:wmH, color:C.ink});
  wm.name="wordmark"; wm.fills=[{type:"IMAGE",scaleMode:"FIT",imageHash:WORDMARK}];
  f.appendChild(wm);

  const tx = S.padX, tw = W - 2*S.padX;
  const byline = await T({chars:CONTENT.byline, font:ROLE.med, size:S.bylineSize,
    color:C.terra, x:tx, y:0, w:tw, align:"RIGHT"});
  byline.y = wm.y - S.bylineGap - byline.height; f.appendChild(byline);

  const sub = await T({chars:CONTENT.sub, font:ROLE.reg, size:S.subSize,
    color:C.white, opacity:0.93, x:tx, y:0, w:tw, align:"RIGHT", lhPct:142});
  sub.y = byline.y - S.subGap - sub.height; f.appendChild(sub);

  const head = await T({chars:CONTENT.head, font:ROLE.dispXB, size:S.headSize,
    color:C.white, x:tx, y:0, w:tw, align:"RIGHT", lhPct:112});
  head.y = sub.y - S.headGap - head.height; f.appendChild(head);

  // --- pill: מודדים את הטקסט ברוחב טבעי, לא מניחים ---
  const pillTxt = await T({chars:CONTENT.pill, font:ROLE.med, size:S.pillSize,
    color:C.white, x:0, y:0, w:600, align:"RIGHT"});
  pillTxt.textAutoResize = "WIDTH_AND_HEIGHT";          // ← עכשיו width אמיתי
  const pillW = Math.ceil(pillTxt.width) + 2*S.pillPadH;
  const pillX = W - S.padX - pillW, pillY = head.y - S.pillGap - S.pillH;
  const pill = R({x:pillX, y:pillY, w:pillW, h:S.pillH, color:C.terra,
                  cornerRadius:Math.round(S.pillH/2)});
  pill.name="pill"; f.appendChild(pill);
  pillTxt.textAutoResize = "HEIGHT";
  pillTxt.resize(pillW, pillTxt.height);
  pillTxt.textAlignHorizontal = "CENTER";
  pillTxt.x = pillX;
  pillTxt.y = Math.round(pillY + (S.pillH - pillTxt.height)/2);
  f.appendChild(pillTxt);

  // גרדיאנט מעוגן ב-pill, מוזרק מעל התמונה ומתחת לטקסט
  const anchor = pillY / H;
  const p2 = Math.max(0.01, anchor - 0.22), p3 = Math.max(p2+0.01, anchor + 0.02);
  const grad = R({x:0,y:0,w:W,h:H,fills:[{type:"GRADIENT_LINEAR",
    gradientTransform:[[0,1,0],[-1,0,1]], gradientStops:[
      {position:0.0, color:{...C.ink,a:0.0}},
      {position:p2,  color:{...C.ink,a:0.0}},
      {position:p3,  color:{...C.ink,a:0.78}},
      {position:1.0, color:{...C.ink,a:1.0}},
    ]}]});
  grad.name="gradient"; f.insertChild(1, grad);

  page.appendChild(f);
  return { name, id:f.id, pillW, headH:Math.round(head.height), chars:CONTENT.head };
}

// ============================ 3 FORMATS ============================
const SQ    = { padX:56, sigH:6, wmW:330, wmBottom:1032, bylineGap:34, bylineSize:26,
                subGap:20, subSize:34, headGap:20, headSize:62,
                pillGap:22, pillH:52, pillSize:26, pillPadH:26 };
const FEED  = { ...SQ, wmBottom:1300 };
const STORY = { padX:60, sigH:6, wmW:370, wmBottom:1700, bylineGap:40, bylineSize:30,
                subGap:24, subSize:38, headGap:24, headSize:70,
                pillGap:26, pillH:60, pillSize:30, pillPadH:30 };

const r1 = await buildCard("update-whatsapp-1080x1080",  0,    1080, 1080, IMG.sq,    SQ);
const r2 = await buildCard("update-instagram-1080x1350", 1260, 1080, 1350, IMG.feed,  FEED);
const r3 = await buildCard("update-story-1080x1920",     2520, 1080, 1920, IMG.story, STORY);

const headsIdentical = new Set([r1,r2,r3].map(r=>r.chars)).size === 1;
const headOneLine = [r1,r2,r3].every(r => r.headH < 100);   // שורה אחת בלבד

return { status:"ok", pageId:page.id, fontFallback, trialCuts,
  headsIdentical, headOneLine, frames:[r1,r2,r3],
  createdNodeIds:[r1.id,r2.id,r3.id] };
```

---

## ניקוי Page 1 (חובה לפני מסירה)

```javascript
const first = figma.root.children[0];
await figma.setCurrentPageAsync(first);
const removed = [];
for (const c of [...first.children]) { removed.push(c.name); c.remove(); }
return { removed };
```

---

## עיצוב — כן/לא

✓ תמונה full-bleed עם הנושא בשליש העליון, גרדיאנט דיו מעוגן ב-pill, pill טרקוטה
צמוד לטקסט שלו, שורת עדכון אחת ב-Publico Extrabold, שורת משנה, byline טרקוטה,
וורדמרק ממורכז מהקובץ, פס-חתימה טריקולור תחתון יחיד 6px.

✗ אסור: h1 verbatim (זה `hamakom-graphic`); pill ברוחב קבוע; כותרת בשתי שורות;
לוגו מטקסט; פס-חתימה עליון; אדום `#f70d28`; נפילה ל-Inter; אימוג'ים;
גוש טקסט מתחת ל-y=1700 בסטורי.
