# -*- coding: utf-8 -*-
"""
build_weekly.py — בונה את הניוזלטר השבועי של "המקום הכי חם בגיהנום" כ-HTML
מתוך articles.json (פלט fetch_week.py) + issue.json (קונפיג העורך לשבוע).

עיצוב HaMakom DS 2026: רוחב 600, RTL. שנהב #faf9f5 / דיו #141413 / טרקוטה #D97757,
Suez One (כותרות) + IBM Plex Sans Hebrew (גוף), פס-חתימה טריקולור.

כלל בטיחות (הלקח מהמשבר של שני סשנים שדרסו זה לזה): כותב תמיד קובץ חדש
עם חותמת תאריך-שעה, ולעולם לא דורס קובץ קיים.

הרצה:
  python3 build_weekly.py
  ISSUE=issue.json ARTICLES=articles.json OUT_DIR=. python3 build_weekly.py

כל הפינות חוץ מ-[פתיח עורך / תחקיר השבוע / רשימת הכתבות / דעות / קרן ההגנה / פוטר]
הן אופציונליות: אם השדה ריק או מסומן ב-<<< >>> — הפינה נחתכת (חוץ מתמונת השבוע
שמופיעה תמיד, כ-placeholder אם אין תמונה).
"""
import json, html, re, os, urllib.parse, urllib.request, datetime

ISSUE_PATH    = os.environ.get("ISSUE", "issue.json")
ARTICLES_PATH = os.environ.get("ARTICLES", "articles.json")
OUT_DIR       = os.environ.get("OUT_DIR", ".")
UTM           = os.environ.get("UTM", "?utm_campaign=weekly&utm_medium=email&utm_source=newsletter")

FONT_HEAD = "'Suez One','Heebo',Georgia,serif"                       # כותרות/תצוגה (DS)
FONT_BODY = "'IBM Plex Sans Hebrew','Heebo',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"  # גוף/UI (DS)
FONT = FONT_BODY
# פלטת HaMakom DS 2026
INK='#141413'; IVORY='#faf9f5'; TERRA='#D97757'; SAGE='#788C5D'; HEATHER='#8E6FA8'
GOLD='#B4581F'   # טרקוטה כהה — אקסנט טקסט קטן על בהיר (קיקר/קרדיט/מאת)
AMBER='#E8906F'  # טרקוטה מובהרת — לייבלים/כפתורים/פסים על רקע דיו כהה
GREY='#6B6B6B'; LINE='#E6E6E6'
LOGO_WHITE=('https://uccprg.stripocdn.email/content/guids/'
            'CABINET_63cfa9cad8ed0171fb3fe41bc5aa8946a5ebd57995774e9a3e262bf666f3a22b/'
            'images/hamakomsquarewhiteh600_JLe.png')
BANNER_IMG=('https://uccprg.stripocdn.email/content/guids/'
            'CABINET_5253251cce9b3dc788ada2ba543bf444757c1feedcc6d2fa83b5d411bda0d7c8/'
            'images/bbanner_horizontal2_copy.png')
SLAPP_URL ='https://independent-press.co.il/ha-makom/slapp'
INVEST_URL='https://ha-makom.co.il/invest'+UTM
BANNER_URL='https://shakuf.co.il/join?utm_medium=newsletter&utm_source=ha-makom'
SOCIALS=[('פייסבוק','https://www.facebook.com/hottestplaceinhell/'),
         ('אינסטגרם','https://www.instagram.com/ha_makom/'),
         ('X','https://twitter.com/ha_makom'),
         ('טלגרם','https://t.me/ha_makom'),
         ('יוטיוב','https://www.youtube.com/Ha-makomCoIl')]

arts = json.load(open(ARTICLES_PATH, encoding='utf-8'))
cfg  = json.load(open(ISSUE_PATH,    encoding='utf-8'))
MISSING = []   # corners left as placeholders, reported at the end


def _is_ph(x):
    return (not x) or str(x).strip() == "" or str(x).strip().startswith("<<<")

def hl(t):
    """מדגיש placeholder בצהוב כדי שיבלוט ב-preview (ונשאר HTML תקין)."""
    if _is_ph(t):
        return (f'<span style="background:#FFF3B0;color:#7a5b00;padding:1px 5px;'
                f'border-radius:3px">{t}</span>')
    return t

def enc(u):
    if not u: return u
    p = urllib.parse.urlsplit(u)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(p.path), p.query, p.fragment))


# ---------- article record access (with WP fallback for any referenced slug) ----------
def _fetch_slug(slug):
    try:
        u = (f"https://www.ha-makom.co.il/wp-json/wp/v2/posts?slug={slug}"
             f"&_fields=slug,link,title,excerpt,date,categories,jetpack_featured_media_url,yoast_head_json")
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 nl'})
        d = json.load(urllib.request.urlopen(req, timeout=20))
        if d:
            p = d[0]; y = p.get('yoast_head_json', {}) or {}
            arts[slug] = {
                'slug': slug, 'link': p.get('link', ''),
                'title': html.unescape(p.get('title', {}).get('rendered', '')).strip(),
                'excerpt': re.sub('<[^>]+>', '', html.unescape(p.get('excerpt', {}).get('rendered', ''))).strip(),
                'date': p.get('date', '')[:10], 'img': p.get('jetpack_featured_media_url') or '',
                'author': y.get('author', ''), 'is_opinion': 547 in (p.get('categories') or []),
            }
            return arts[slug]
    except Exception as e:
        print('  ! could not fetch slug', slug, '-', e)
    return None

def rec(s):
    r = arts.get(s) or _fetch_slug(s)
    if not r:
        raise KeyError("slug not found: " + s)
    return r

def link(s):    return rec(s)['link'] + UTM
def img(s):     return enc(rec(s)['img'])
def title(s):   return re.sub(r'\s*\|\s*(תחקיר|טור|דעה)\s*$', '', rec(s)['title']).strip()
def author(s):  return rec(s).get('author') or ''
def dt(s):
    d = rec(s)['date']
    if not d: return ''
    y, m, da = d.split('-'); return f'{da}/{m}'
def excerpt(s, n=200):
    e = rec(s)['excerpt']
    return (e[:n-1].rsplit(' ', 1)[0] + '…') if len(e) > n else e


# ---------- primitives (styling copied verbatim from the published v2) ----------
def P(t, c='#222222', sz=15, mb=12, extra=''):
    return (f'<p style="Margin:0 0 {mb}px;font-family:{FONT};font-size:{sz}px;line-height:24px;'
            f'color:{c};direction:rtl;text-align:right{extra}">{t}</p>')
def A(href, t, color=GOLD):
    return f'<a target="_blank" href="{href}" style="text-decoration:none;color:{color};font-weight:700">{t}</a>'
ROW = lambda inner, pad='0 28px': f'<tr><td dir="rtl" style="padding:{pad};Margin:0">{inner}</td></tr>'
def section_label(t):
    return ROW(f'<p style="Margin:0;font-family:{FONT};font-size:13px;font-weight:800;letter-spacing:3px;'
               f'color:{GOLD};direction:rtl;border-bottom:2px solid {INK};padding-bottom:8px;'
               f'display:inline-block">{t}</p>', pad='26px 28px 4px')
def strip(label, inner):
    return (f'<tr><td bgcolor="{INK}" dir="rtl" align="right" style="padding:30px 28px;Margin:0;'
            f'background-color:{INK}"><p style="Margin:0 0 14px;font-family:{FONT};font-size:13px;'
            f'font-weight:800;letter-spacing:3px;color:{AMBER};direction:rtl">{label}</p>{inner}</td></tr>')

def _with_utm(u):
    if not u: return ''
    return u if ('utm_' in u) else (u + UTM)


# ---------- sections ----------
def sig_bar(h=6):
    """פס-חתימה טריקולור: טרקוטה·מרווה·אברש (ימין→שמאל ב-RTL) — חתימת המותג."""
    cell = lambda c: (f'<td width="33.33%" height="{h}" style="height:{h}px;font-size:0;'
                      f'line-height:0;background-color:{c}">&nbsp;</td>')
    return ('<tr><td style="padding:0;Margin:0"><table width="100%" cellpadding="0" '
            'cellspacing="0" role="presentation" style="border-collapse:collapse"><tbody><tr>'
            f'{cell(TERRA)}{cell(SAGE)}{cell(HEATHER)}</tr></tbody></table></td></tr>')

def header():
    return (f'<tr><td align="center" bgcolor="{INK}" style="padding:24px 0 18px;Margin:0;background-color:{INK}">'
            f'<a href="https://ha-makom.co.il/{UTM}" target="_blank"><img src="{LOGO_WHITE}" height="80" '
            f'alt="המקום הכי חם בגיהנום" style="display:block;border:0;margin:0 auto;height:80px"></a>'
            f'<p style="Margin:12px 0 0;font-family:{FONT};font-size:12px;font-weight:700;letter-spacing:5px;'
            f'color:{AMBER};direction:rtl">הניוזלטר השבועי&nbsp;&nbsp;·&nbsp;&nbsp;{cfg.get("week_date","")}</p></td></tr>')

def note():
    en = cfg.get('editor_note', {}) or {}
    head = en.get('headline', ''); paras = en.get('paragraphs', []) or []
    if _is_ph(head) or any(_is_ph(p) for p in paras): MISSING.append('פתיח עורך')
    inner = (f'<p style="Margin:0 0 16px;font-family:{FONT_HEAD};font-size:27px;font-weight:900;line-height:34px;'
             f'color:#141413;direction:rtl;text-align:right">{hl(head)}</p>')
    for p in paras:
        inner += P(hl(p) if _is_ph(p) else p)
    inner += P('<strong>דור זומר</strong>, עורך ראשי', GREY, 14, 0)
    return ROW(inner, pad='26px 28px 24px')

def project():
    pr = cfg.get('project', {}) or {}
    if _is_ph(pr.get('title', '')): return ''
    u = _with_utm(pr.get('url', '') or 'https://ha-makom.co.il/')
    return (f'<tr><td bgcolor="{INK}" align="center" dir="rtl" style="padding:38px 30px;Margin:0;background-color:{INK}">'
            f'<p style="Margin:0 0 14px;font-family:{FONT};font-size:12px;font-weight:800;letter-spacing:4px;color:{AMBER};direction:rtl">{pr.get("label","חדש באתר")}</p>'
            f'<p style="Margin:0 0 14px;font-family:{FONT_HEAD};font-size:44px;font-weight:900;line-height:48px;color:#faf9f5;direction:rtl">'
            f'<a target="_blank" href="{u}" style="text-decoration:none;color:#faf9f5">{pr["title"]}</a></p>'
            + (f'<p style="Margin:0 0 22px;font-family:{FONT};font-size:16px;line-height:25px;color:#C7C7C7;direction:rtl">{pr.get("desc","")}</p>' if pr.get("desc") else '')
            + f'<table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto"><tbody><tr><td bgcolor="{AMBER}" style="border-radius:6px"><a target="_blank" href="{u}" style="display:inline-block;padding:13px 36px;font-family:{FONT};font-size:16px;font-weight:800;color:{INK};text-decoration:none">{pr.get("cta","לפרויקט המלא")}</a></td></tr></tbody></table></td></tr>')

def lead(slug, kicker='תחקיר השבוע'):
    return (f'<tr><td style="padding:18px 28px 8px;Margin:0">'
            f'<p style="Margin:0 0 12px;font-family:{FONT};font-size:13px;font-weight:800;letter-spacing:3px;color:{GOLD};direction:rtl">{kicker}</p>'
            f'<a target="_blank" href="{link(slug)}"><img src="{img(slug)}" alt="{title(slug)[:70]}" width="544" style="display:block;border:0;width:100%;border-radius:8px;margin:0 0 16px"></a>'
            f'<h1 style="Margin:0 0 10px;font-family:{FONT_HEAD};font-size:30px;font-weight:900;line-height:37px;color:#141413;direction:rtl;text-align:right">'
            f'<a target="_blank" href="{link(slug)}" style="text-decoration:none;color:#141413">{title(slug)}</a></h1>'
            + P(excerpt(slug, 240), '#333333', 16, 12)
            + f'<p style="Margin:0;font-family:{FONT};font-size:12px;font-weight:700;color:{GOLD};direction:rtl;text-align:right">מאת {author(slug)} · {dt(slug)}</p></td></tr>')

def hero(slug, kicker='מתחת לרדאר'):
    return (f'<tr><td style="padding:22px 28px 8px;Margin:0;border-top:6px solid {INK}">'
            f'<p style="Margin:0 0 12px;font-family:{FONT};font-size:13px;font-weight:800;letter-spacing:3px;color:{GOLD};direction:rtl">{kicker}</p>'
            f'<a target="_blank" href="{link(slug)}"><img src="{img(slug)}" alt="{title(slug)[:70]}" width="544" style="display:block;border:0;width:100%;border-radius:8px;margin:0 0 16px"></a>'
            f'<h2 style="Margin:0 0 10px;font-family:{FONT_HEAD};font-size:27px;font-weight:900;line-height:34px;color:#141413;direction:rtl;text-align:right">'
            f'<a target="_blank" href="{link(slug)}" style="text-decoration:none;color:#141413">{title(slug)}</a></h2>'
            + P(excerpt(slug, 230), '#333333', 16, 12)
            + f'<p style="Margin:0;font-family:{FONT};font-size:12px;font-weight:700;color:{GOLD};direction:rtl;text-align:right">מאת {author(slug)} · {dt(slug)}</p></td></tr>')

def item(slug):
    return (f'<tr><td dir="rtl" style="padding:18px 28px;Margin:0;border-top:1px solid {LINE}">'
            f'<table width="100%" dir="rtl" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse"><tbody><tr>'
            f'<td class="imgcell" width="140" valign="top" style="padding:0 0 0 16px"><a target="_blank" href="{link(slug)}"><img class="thumb" src="{img(slug)}" alt="" width="140" style="display:block;border:0;width:140px;border-radius:5px"></a></td>'
            f'<td class="txtcell" valign="top" align="right" dir="rtl" style="padding:0">'
            f'<a target="_blank" href="{link(slug)}" style="text-decoration:none;color:#141413"><span style="font-family:{FONT};font-size:18px;font-weight:700;line-height:24px;color:#141413">{title(slug)}</span></a>'
            f'<p class="m-hide" style="Margin:6px 0 0;font-family:{FONT};font-size:13px;line-height:19px;color:#444;direction:rtl">{excerpt(slug,90)}</p>'
            f'<p style="Margin:6px 0 0;font-family:{FONT};font-size:12px;color:{GREY};direction:rtl">מאת {author(slug)} · {dt(slug)}</p>'
            f'</td></tr></tbody></table></td></tr>')

def data_strip():
    ds = cfg.get('data_stat', {}) or {}
    if _is_ph(ds.get('img', '')): return ''
    u = _with_utm(ds.get('url', '') or 'https://ha-makom.co.il/')
    return strip(ds.get('label', 'הנתון של השבוע'),
                 f'<a target="_blank" href="{u}"><img src="{enc(ds["img"])}" alt="{ds.get("alt","")}" width="440" '
                 f'style="display:block;border:0;width:100%;max-width:440px;margin:0 auto;border-radius:8px"></a>')

def followup():
    fu = cfg.get('followup', {}) or {}
    s = fu.get('slug', '')
    if _is_ph(s): return ''
    return (f'<tr><td bgcolor="{AMBER}" align="center" dir="rtl" style="padding:16px 28px;Margin:0;background-color:{AMBER}">'
            f'<p style="Margin:0;font-family:{FONT};font-size:20px;font-weight:900;letter-spacing:1px;color:{INK};direction:rtl">{fu.get("banner_title","בעקבות הפרסום")}</p>'
            + (f'<p style="Margin:4px 0 0;font-family:{FONT};font-size:13px;font-weight:700;color:{INK};direction:rtl">{fu["banner_sub"]}</p>' if fu.get("banner_sub") else '')
            + f'</td></tr><tr><td dir="rtl" align="right" style="padding:18px 28px 8px">'
            f'<a target="_blank" href="{link(s)}"><img src="{img(s)}" alt="{title(s)[:70]}" width="544" style="display:block;border:0;width:100%;border-radius:8px;margin:0 0 14px"></a>'
            f'<a target="_blank" href="{link(s)}" style="text-decoration:none"><span style="font-family:{FONT_HEAD};font-size:23px;font-weight:900;line-height:30px;color:#141413;direction:rtl">{title(s)}</span></a>'
            + P(excerpt(s, 200), '#333', 15, 8, ';margin-top:10px')
            + f'<p style="Margin:0;font-family:{FONT};font-size:12px;font-weight:700;color:{GOLD};direction:rtl">מאת {author(s)} · {dt(s)}</p></td></tr>')

def photo_strip():
    pw = cfg.get('photo_of_week', {}) or {}
    cap = pw.get('caption', ''); cred = pw.get('credit', 'צילום: ___ / פלאש 90')
    if _is_ph(pw.get('img', '')):
        MISSING.append('תמונת השבוע (פלאש90)')
        inner = (f'<div style="border:2px dashed {AMBER};border-radius:8px;padding:32px 16px;text-align:center;margin:0 0 12px">'
                 f'<p style="Margin:0;font-family:{FONT};font-size:15px;font-weight:700;color:{AMBER};direction:rtl">תמונת השבוע — להפיל כאן תמונה מפלאש90</p>'
                 f'<p style="Margin:8px 0 0;font-family:{FONT};font-size:12px;color:#9a9a9a;direction:rtl">{hl(cap)}</p></div>'
                 + f'<p style="Margin:0;font-family:{FONT};font-size:12px;color:#8a8a8a;direction:rtl;text-align:right">{cred}</p>')
    else:
        inner = (f'<img src="{enc(pw["img"])}" alt="{cap[:60]}" width="544" style="display:block;border:0;width:100%;border-radius:8px;margin:0 0 12px">'
                 + P(cap, '#D8D8D8', 14, 6)
                 + f'<p style="Margin:0;font-family:{FONT};font-size:12px;color:#8a8a8a;direction:rtl;text-align:right">{cred}</p>')
    return strip('תמונת השבוע', inner)

def reel_strip():
    r = cfg.get('reel', {}) or {}
    if _is_ph(r.get('url', '')) or _is_ph(r.get('poster', '')): return ''
    cap = r.get('caption', '')
    return strip('ברשתות שלנו',
        f'<a target="_blank" href="{r["url"]}"><img src="{enc(r["poster"])}" alt="" width="280" style="display:block;border:0;width:280px;max-width:100%;margin:0 auto 14px;border-radius:8px"></a>'
        + f'<table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 12px"><tbody><tr><td bgcolor="{AMBER}" style="border-radius:6px"><a target="_blank" href="{r["url"]}" style="display:inline-block;padding:11px 28px;font-family:{FONT};font-size:15px;font-weight:700;color:{INK};text-decoration:none">{r.get("cta","לריל")}</a></td></tr></tbody></table>'
        + (P(cap + ' ' + A('https://www.instagram.com/ha_makom/', '@ha_makom', AMBER), '#D8D8D8', 14, 0, ';text-align:center') if cap else ''))

def quote_strip():
    q = cfg.get('quote', {}) or {}
    s = q.get('slug', ''); txt = q.get('text', ''); attrib = q.get('attrib', '')
    if _is_ph(s) and _is_ph(txt): return ''
    if _is_ph(txt) or _is_ph(attrib): MISSING.append('ציטוט השבוע')
    body = ''
    if not _is_ph(s):
        body += f'<a target="_blank" href="{link(s)}"><img src="{img(s)}" alt="" width="544" style="display:block;border:0;width:100%;border-radius:8px;margin:0 0 16px"></a>'
    body += (f'<p style="Margin:0 0 12px;font-family:{FONT_HEAD};font-size:24px;font-weight:800;line-height:33px;'
             f'color:#faf9f5;direction:rtl;text-align:right">{hl(txt) if _is_ph(txt) else "״"+txt+"״"}</p>')
    more = A(link(s), 'לכתבה המלאה', AMBER) if not _is_ph(s) else ''
    body += P((hl(attrib) if _is_ph(attrib) else attrib) + ' ' + more, '#D8D8D8', 14, 0)
    return strip('ציטוט השבוע', body)

def opinions_block():
    op = cfg.get('opinions', {}) or {}
    feat = op.get('feature', ''); items = op.get('items', []) or []
    out = section_label('דעות וטורים')
    if not _is_ph(feat):
        out += (f'<tr><td dir="rtl" align="right" style="padding:6px 28px 16px;Margin:0">'
                f'<a target="_blank" href="{link(feat)}"><img src="{img(feat)}" alt="{title(feat)[:70]}" width="544" style="display:block;border:0;width:100%;border-radius:8px;margin:0 0 14px"></a>'
                f'<p style="Margin:0 0 8px;font-family:{FONT};font-size:12px;font-weight:800;letter-spacing:2px;color:{GOLD};direction:rtl">הטור של {author(feat)}</p>'
                f'<a target="_blank" href="{link(feat)}" style="text-decoration:none"><span style="font-family:{FONT_HEAD};font-size:23px;font-weight:900;line-height:30px;color:#141413;direction:rtl">{title(feat)}</span></a>'
                + P(excerpt(feat, 180), '#333', 15, 0, ';margin-top:10px') + '</td></tr>')
    for s in items:
        if _is_ph(s): continue
        out += (f'<tr><td dir="rtl" align="right" style="padding:16px 28px;Margin:0;border-top:1px solid {LINE}">'
                f'<table width="100%" dir="rtl" cellpadding="0" cellspacing="0" role="presentation"><tbody><tr>'
                f'<td class="imgcell" width="96" valign="top" style="padding:0 0 0 14px"><a target="_blank" href="{link(s)}"><img class="thumb" src="{img(s)}" alt="" width="96" style="display:block;border:0;width:96px;border-radius:5px"></a></td>'
                f'<td class="txtcell" valign="top" align="right" dir="rtl">'
                f'<a target="_blank" href="{link(s)}" style="text-decoration:none"><span style="font-family:{FONT};font-size:16px;font-weight:700;color:#141413;line-height:22px">{title(s)}</span></a>'
                f'<p style="Margin:6px 0 0;font-family:{FONT};font-size:12px;color:{GREY};direction:rtl">מאת {author(s)}</p>'
                f'</td></tr></tbody></table></td></tr>')
    return out

def reads_block():
    reads = cfg.get('reads', []) or []
    reads = [r for r in reads if isinstance(r, dict) and not _is_ph(r.get('headline', ''))]
    if not reads: return ''
    body = P('מהשותפות שלנו ב״עיתונות העצמאית״:', '#D8D8D8', 14, 16)
    for i, r in enumerate(reads):
        if i: body += f'<div style="height:18px;border-bottom:1px solid #3a3a3a;margin:0 0 18px;font-size:0">&nbsp;</div>'
        body += (f'<p style="Margin:0 0 3px;font-family:{FONT};font-size:12px;font-weight:800;letter-spacing:2px;color:{AMBER};direction:rtl">{r.get("outlet","")}</p>'
                 f'<p style="Margin:0 0 6px;font-family:{FONT};font-size:18px;font-weight:800;line-height:25px;color:#faf9f5;direction:rtl;text-align:right"><a target="_blank" href="{r.get("url","#")}" style="text-decoration:none;color:#faf9f5">{r["headline"]}</a></p>'
                 + P(r.get('dek', '') + ' ' + A(r.get('url', '#'), 'לכתבה', AMBER), '#CFCFCF', 14, 0))
    return strip('המלצות קריאה', body)

def legal_block():
    lg = cfg.get('legal', 'default')
    lg = {} if (lg == 'default' or not isinstance(lg, dict)) else lg
    title_t = lg.get('title', 'שמים סוף לתביעות ההשתקה')
    body = (f'<tr><td dir="rtl" align="right" style="padding:26px 28px;Margin:0;border-top:3px solid {GOLD};background:#f4efe6">'
            f'<p style="Margin:0 0 6px;font-family:{FONT};font-size:13px;font-weight:800;letter-spacing:3px;color:{GOLD};direction:rtl">קרן ההגנה המשפטית</p>'
            f'<p style="Margin:0 0 16px;font-family:{FONT_HEAD};font-size:25px;font-weight:900;line-height:31px;color:#141413;direction:rtl">{title_t}</p>')
    if not _is_ph(lg.get('video_url', '')) and not _is_ph(lg.get('poster', '')):
        body += (f'<a target="_blank" href="{lg["video_url"]}"><img src="{enc(lg["poster"])}" alt="" width="300" style="display:block;border:0;width:300px;max-width:100%;margin:0 auto 12px;border-radius:8px"></a>')
        if lg.get('hook'):
            body += f'<p style="Margin:0 0 12px;font-family:{FONT};font-size:18px;font-weight:800;line-height:25px;color:#141413;direction:rtl;text-align:center">{lg["hook"]}</p>'
        body += (f'<table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 18px"><tbody><tr><td bgcolor="{GOLD}" style="border-radius:6px"><a target="_blank" href="{lg["video_url"]}" style="display:inline-block;padding:12px 30px;font-family:{FONT};font-size:15px;font-weight:700;color:#faf9f5;text-decoration:none">צפו בסרטון</a></td></tr></tbody></table>')
    default_body = ('על תחקירים שלנו הוגשו חמש תביעות השתקה — נגד המערכת, העיתונאיות והמרואיינות. '
                    'הקמנו קרן הגנה כדי שאף אחת לא תילחם לבד. אם אתם מאמינים בעיתונות עצמאית '
                    'שלא חייבת דבר לבעלי הון, למפרסמים או לפוליטיקאים — אנחנו צריכים אתכם איתנו. '
                    'ואם אין באפשרותכם, פשוט שתפו. זה שווה לא פחות.')
    body += P(lg.get('body', default_body), '#333', 15, 14)
    body += (f'<table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 12px"><tbody><tr><td bgcolor="{GOLD}" style="border-radius:6px"><a target="_blank" href="{SLAPP_URL}" style="display:inline-block;padding:13px 34px;font-family:{FONT};font-size:16px;font-weight:800;color:#faf9f5;text-decoration:none">לתמיכה בקרן ההגנה המשפטית</a></td></tr></tbody></table></td></tr>')
    return body

def banner_block():
    if cfg.get('support_banner') in (None, '', False): return ''
    return (f'<tr><td align="center" dir="rtl" style="padding:24px 28px 6px;Margin:0">'
            f'<a target="_blank" href="{BANNER_URL}"><img src="{BANNER_IMG}" alt="עיתונות עצמאית — הצטרפו אלינו" width="544" '
            f'style="display:block;border:0;width:100%;max-width:544px;margin:0 auto;border-radius:8px"></a></td></tr>')

def footer():
    links = '&nbsp;&nbsp;·&nbsp;&nbsp;'.join(
        f'<a href="{u}" target="_blank" style="color:#faf9f5;text-decoration:none;font-weight:700">{n}</a>' for n, u in SOCIALS)
    return (f'<tr><td align="center" bgcolor="{INK}" dir="rtl" style="padding:30px 28px;Margin:0;background-color:{INK}">'
            f'<img src="{LOGO_WHITE}" height="56" alt="המקום הכי חם בגיהנום" style="display:block;border:0;height:56px;margin:0 auto 14px">'
            f'<p style="Margin:0 0 12px;font-family:{FONT};font-size:13px;direction:rtl;color:#bbb">{links}</p>'
            f'<table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px"><tbody><tr><td bgcolor="{AMBER}" style="border-radius:6px"><a target="_blank" href="{INVEST_URL}" style="display:inline-block;padding:11px 30px;font-family:{FONT};font-size:15px;font-weight:800;color:{INK};text-decoration:none">תמכו בעיתונות עצמאית</a></td></tr></tbody></table>'
            f'<p style="Margin:0;font-family:{FONT};font-size:11px;line-height:18px;color:#888;direction:rtl">קיבלת מייל זה כי נרשמת לניוזלטר של המקום הכי חם בגיהנום.<br>'
            f'<a href="{{{{unsubscribe}}}}" style="color:#888;text-decoration:underline">להסרה מרשימת התפוצה</a></p></td></tr>')


# ---------- assemble ----------
def build():
    rows = [sig_bar(), header(), note()]
    rows.append(project())
    if not _is_ph(cfg.get('lead', '')):
        rows.append(lead(cfg['lead'], cfg.get('lead_kicker', 'תחקיר השבוע')))
    rows.append(data_strip())
    rows.append(followup())
    rows.append(section_label(cfg.get('rundown_label', 'עוד שברים שקרו השבוע במקום הכי חם בגיהנום')))

    rundown = [s for s in (cfg.get('rundown', []) or []) if not _is_ph(s)]
    place_after = cfg.get('photo_of_week', {}).get('place_after', 1)
    photo_done = False
    for i, s in enumerate(rundown):
        rows.append(item(s))
        if i == place_after:
            rows.append(photo_strip()); photo_done = True
    if not photo_done:
        rows.append(photo_strip())

    he = cfg.get('hero', {}) or {}
    if not _is_ph(he.get('slug', '')):
        rows.append(hero(he['slug'], he.get('kicker', 'מתחת לרדאר')))
    rows.append(reel_strip())
    rows.append(quote_strip())
    rows.append(opinions_block())
    rows.append(reads_block())
    rows.append(legal_block())
    rows.append(banner_block())
    rows.append(footer())

    inner = ''.join(r for r in rows if r)
    pre = cfg.get('preheader', '')
    doc = f'''<!DOCTYPE html>
<html dir="rtl" lang="he" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>השבוע ב״המקום הכי חם בגיהנום״ · {cfg.get("week_date","")}</title>
<style type="text/css">
@import url('https://fonts.googleapis.com/css2?family=Suez+One&family=IBM+Plex+Sans+Hebrew:wght@400;500;600;700&family=Heebo:wght@400;500;700;800;900&display=swap');
body,table,td,p,a,span,div,strong{{font-family:'IBM Plex Sans Hebrew','Heebo',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;}}
h1,h2,h3{{font-family:'Suez One','Heebo',Georgia,serif;}}
body{{margin:0;padding:0;background:#e6e3da;}}
img{{-ms-interpolation-mode:bicubic;}}
@media only screen and (max-width:600px){{
 .ct{{width:100%!important;}}
 .imgcell{{width:104px!important;padding:0 0 0 12px!important;}}
 .thumb{{width:104px!important;height:auto!important;}}
 .m-hide{{display:none!important;max-height:0!important;overflow:hidden!important;}}
}}
</style>
</head>
<body style="margin:0;padding:0;background:#e6e3da">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{pre}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#e6e3da"><tbody><tr><td align="center" style="padding:18px 0">
<table role="presentation" class="ct" width="600" cellpadding="0" cellspacing="0" style="width:600px;max-width:600px;background:#faf9f5;border-radius:10px;overflow:hidden"><tbody>
{inner}
</tbody></table>
</td></tr></tbody></table>
</body></html>'''

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(OUT_DIR, f'weekly_{stamp}.html')
    # never overwrite
    while os.path.exists(out_path):
        stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_1'
        out_path = os.path.join(OUT_DIR, f'weekly_{stamp}.html')
    open(out_path, 'w', encoding='utf-8').write(doc)

    c = re.sub(r'<!--.*?-->', '', doc, flags=re.S)
    print('WROTE', out_path, '|', len(doc), 'bytes')
    print('tag balance  tr:', c.count('<tr') - c.count('</tr'),
          ' td:', c.count('<td') - c.count('</td'),
          ' table:', c.count('<table') - c.count('</table'))
    if MISSING:
        print('TO FILL  →  ' + '  |  '.join(dict.fromkeys(MISSING)))
    else:
        print('no placeholders left.')
    return out_path


if __name__ == '__main__':
    build()
