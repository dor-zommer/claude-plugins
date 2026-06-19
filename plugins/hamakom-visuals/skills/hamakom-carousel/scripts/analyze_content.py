#!/usr/bin/env python3
"""
analyze_content.py — מנתח תוכן כתבה ומחזיר תכנון קרוסלה.

קלט:
  --url URL                         (כתבה ב-ha-makom.co.il)
  --text-file PATH                  (טקסט גולמי, אם אין URL)
  --title TITLE                     (כותרת — חובה אם אין URL)
  --byline NAME                     (שם הכותב/ת — אופציונלי)
  --category CAT                    (קטגוריה — אופציונלי)
  --archetype ARCH                  (override ידני: A/B/C/D/E/F)
  --slides N                        (override אורך: 6/8/10/12)

פלט (JSON ל-stdout):
  {
    "archetype": "A",
    "archetype_reason": "...",
    "slides": [
      {"block": "cover-overlay", "title": "...", "lede": "...", "image_role": "hero", "image_hint": "..."},
      ...
    ],
    "metadata": {"title": "...", "byline": "...", "category": "...", "url": "..."}
  }
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple

# --- Constants ----------------------------------------------------------------

ARCHETYPES = {
    "A": "Investigation-System",
    "B": "Op-Ed",
    "C": "Profile",
    "D": "Breaking-Explainer",
    "E": "Document-Driven",
    "F": "Mosaic",
}

DEFAULT_SEQUENCES = {
    "A": [
        "cover-overlay", "hero-bleed-fade", "text-only-argument",
        "text-only-highlight", "split-text-photo", "split-text-cutouts",
        "split-text-concept", "split-text-document", "closing-symbol", "cta-red",
    ],
    "B": [
        "cover-overlay", "hero-bleed-fade", "text-only-argument",
        "text-only-highlight", "split-text-photo", "quote-pull",
        "text-only-argument", "cta-red",
    ],
    "C": [
        "cover-overlay", "hero-bleed-fade", "split-text-cutouts",
        "quote-pull", "split-text-photo", "text-only-highlight",
        "closing-symbol", "cta-red",
    ],
    "D": [
        "cover-overlay", "hero-bleed-fade", "text-only-highlight",
        "split-text-photo", "text-only-argument", "split-text-document",
        "closing-symbol", "cta-red",
    ],
    "E": [
        "cover-overlay", "hero-bleed-fade", "split-text-document",
        "split-text-document", "text-only-highlight", "text-only-argument",
        "split-text-photo", "cta-red",
    ],
    "F": [
        "cover-overlay", "hero-bleed-fade", "split-text-cutouts",
        "quote-pull", "split-text-photo", "quote-pull",
        "split-text-cutouts", "cta-red",
    ],
}

OPINION_CATEGORIES = {"דעות", "opinion", "op-ed", "opinions"}
INVESTIGATION_CATEGORIES = {"תחקירים", "investigation", "investigations"}
BREAKING_CATEGORIES = {"חם", "מדיני-בטחוני", "breaking", "hot"}

DOCUMENT_KEYWORDS = ["מסמך", "תזכיר", "דו\"ח", "פטור", "החלטה", "עתירה",
                     "תצהיר", "פרוטוקול", "תיק", "כתב אישום"]

COURT_PHRASES = ["בית משפט", "בג\"ץ", "פרקליטות", "פסק דין", "עתירה",
                 "הנשיא", "השופט", "השופטת", "הצדק", "המחוזי", "השלום"]

USER_AGENT = "Mozilla/5.0 (compatible; hamakom-carousel/1.0)"

# Common Hebrew first names — used as a strong signal that a two-word token is actually a person
HEBREW_FIRST_NAMES = {
    # masculine
    "דוד", "יוסף", "משה", "אברהם", "יצחק", "יעקב", "אהרן", "שמואל", "דניאל",
    "אורי", "אריאל", "אסף", "אסא", "איתי", "אילן", "אילון", "אלון", "אלי",
    "אליעזר", "אליה", "אהוד", "אביב", "אבי", "אמיר", "אסף", "בני", "בנימין",
    "ברק", "גיא", "גיל", "גלעד", "גידי", "דורון", "דוד", "דין", "דניאל",
    "הראל", "זאב", "זוהר", "חיים", "טל", "ידידיה", "יאיר", "ינון", "יואב",
    "יואל", "יונתן", "יוסי", "יותם", "ירון", "ישי", "כפיר", "לב", "ליאור",
    "מאור", "מאיר", "מיכאל", "מתן", "נדב", "ניר", "ניצן", "נמרוד", "סער",
    "עומר", "עידן", "עידו", "עוז", "ערן", "פלג", "צבי", "ראובן", "רוני",
    "רונן", "רועי", "רן", "רביב", "שגיא", "שחר", "שי", "שמעון", "שלמה",
    "שלום", "שאול", "תום", "תומר", "ינאי", "אביב", "בן", "בצלאל",
    # feminine
    "שרה", "רחל", "לאה", "רבקה", "מרים", "ענת", "אורית", "אורנה", "אריאלה",
    "אילנה", "אסתר", "אביגיל", "אמירה", "אמליה", "בת", "גלית", "גילה",
    "דנה", "דורית", "דליה", "הילה", "חני", "חנה", "טליה", "יעל", "יפה",
    "יפעת", "ירדן", "כרמית", "ליאת", "לילי", "לימור", "מיכל", "מיה", "מורן",
    "ניצן", "נטע", "נעמה", "נעמי", "נורית", "נילי", "סיגל", "ענבל", "ערות",
    "רוני", "רונית", "רינת", "רעות", "שירה", "שני", "שרון", "שלי", "שלומית",
    "טל", "תמר", "תהילה", "לילך", "אביגיל", "ששי-לי",
    # surnames sometimes used as first
    "נתניהו", "גלנט", "אייזנקוט", "כץ",
}

# --- HTML parsing -------------------------------------------------------------

class ArticleHTMLParser(HTMLParser):
    """Extract title, byline, body paragraphs, images, category from ha-makom HTML.

    Tracks `in_article_zone` carefully — between the first h1 and the first
    "related stories" marker. Outside the zone, we still capture meta tags but
    NOT body paragraphs or category links (which would otherwise pick up nav
    and footer content).
    """

    # H3 headings that mark the END of the article body (related links, comments, footer)
    ARTICLE_END_MARKERS = (
        "אולי יעניין", "הסיפורים החמים", "השאר תגובה", "אהבתם", "שתפו",
        "הכי חם בטוויטר", "הציוצים שלי", "אנחנו מחויבים", "כאן עושים עיתונות",
        "רוצה לקבל יותר", "הסיפור הקודם",
    )

    def __init__(self):
        super().__init__()
        self.in_h1 = False
        self.in_h2 = False
        self.in_h3 = False
        self.in_p = False
        self.in_blockquote = False
        self.in_strong = False
        self.in_a_author = False
        self.in_a_category = False
        # Zone tracking: True from first h1 close until first end-marker h3
        self.in_article_zone = False
        self._article_zone_armed = False  # set to True after first h1 close
        self.current_paragraph: List[str] = []
        self.title = ""
        self.subtitle = ""
        self.byline = ""
        self.categories: List[str] = []
        self.paragraphs: List[Dict] = []
        self.images: List[Dict] = []
        self.og_image = ""
        self.og_description = ""
        self.published_date = ""
        self._depth_blockquote = 0
        self._a_text: List[str] = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "meta":
            prop = attrs_dict.get("property", "") or attrs_dict.get("name", "")
            content = attrs_dict.get("content", "")
            if prop == "og:image" and not self.og_image:
                self.og_image = content
            elif prop == "og:description" and not self.og_description:
                # treat og:description as subtitle/lede if h2 wasn't found
                self.og_description = content
            elif prop in ("article:published_time", "datePublished"):
                self.published_date = content
            elif prop == "article:section" and not self.categories:
                self.categories.append(content)
        elif tag == "h1":
            self.in_h1 = True
            self.current_paragraph = []
        elif tag == "h2":
            self.in_h2 = True
            self.current_paragraph = []
        elif tag == "h3":
            # h3 inside the article zone may mark END of article
            self.in_h3 = True
            self.current_paragraph = []
        elif tag == "p":
            self.in_p = True
            self.current_paragraph = []
        elif tag == "blockquote":
            self.in_blockquote = True
            self._depth_blockquote += 1
        elif tag == "strong" or tag == "b":
            self.in_strong = True
        elif tag == "img":
            # WordPress lazy loading: real URL is in data-src, not src
            src = attrs_dict.get("data-src", "") or attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "") or attrs_dict.get("data-image-title", "")
            classes = attrs_dict.get("class", "")
            caption = attrs_dict.get("data-image-caption", "")
            if not src or src.startswith("data:"):
                return
            # filter known noise patterns by URL
            lower = src.lower()
            if any(skip in lower for skip in ("avatar", "banner", "cropped-",
                                              "icon", "loader", "spinner",
                                              "spacer", "1x1", "blank")):
                return
            # filter logo URLs (multiple naming patterns)
            if any(skip in lower for skip in ("/logo", "logo-", "-logo", "/new-logo",
                                              "logo.png", "logo.svg")):
                return
            # filter by CSS class (WP avatar/logo classes)
            if any(c in classes for c in ("avatar", "jeg_logo_img", "site-logo")):
                return
            # Only collect images from inside the article zone
            if self.in_article_zone:
                self.images.append({
                    "src": src,
                    "alt": alt or "",
                    "caption": caption or "",
                    "classes": classes,
                })
        elif tag == "a":
            href = attrs_dict.get("href", "")
            self._a_text = []
            if "/author/" in href:
                self.in_a_author = True
            elif "/category/" in href:
                self.in_a_category = True
        elif tag in ("footer", "aside"):
            # entering footer/aside — definitely outside article zone
            self.in_article_zone = False

    def handle_endtag(self, tag):
        text = "".join(self.current_paragraph).strip()
        a_text = "".join(self._a_text).strip()
        if tag == "h1" and self.in_h1:
            if not self.title and text:
                self.title = text
                # ARM the zone: next sibling content is article body
                self._article_zone_armed = True
                self.in_article_zone = True
            self.in_h1 = False
        elif tag == "h2" and self.in_h2:
            if not self.subtitle and text and 30 < len(text) < 600:
                self.subtitle = text
            self.in_h2 = False
        elif tag == "h3" and self.in_h3:
            # check if this h3 ends the article zone
            if self.in_article_zone:
                for marker in self.ARTICLE_END_MARKERS:
                    if marker in text:
                        self.in_article_zone = False
                        break
            self.in_h3 = False
        elif tag == "p" and self.in_p:
            if text and len(text) > 30 and self.in_article_zone:
                # also reject paragraphs that are clearly footer/related-story junk
                if not self._looks_like_junk(text):
                    self.paragraphs.append({
                        "text": text,
                        "is_quote": self.in_blockquote,
                        "is_strong_lead": self.in_strong,
                    })
            self.in_p = False
        elif tag == "blockquote" and self.in_blockquote:
            self._depth_blockquote -= 1
            if self._depth_blockquote <= 0:
                self.in_blockquote = False
                self._depth_blockquote = 0
        elif tag in ("strong", "b"):
            self.in_strong = False
        elif tag == "a":
            if self.in_a_author and a_text and not self.byline:
                self.byline = a_text
            elif self.in_a_category and a_text and a_text not in self.categories:
                # only collect categories inside the article zone (or before h1)
                # nav categories appear before h1; article categories appear right after
                if self.in_article_zone or not self._article_zone_armed:
                    # before zone armed = before h1 close, treat as nav — skip
                    # after zone armed AND in zone = real article categories
                    if self.in_article_zone:
                        self.categories.append(a_text)
            self.in_a_author = False
            self.in_a_category = False
            self._a_text = []
        elif tag in ("footer", "aside"):
            self.in_article_zone = False

    def handle_data(self, data):
        if self.in_h1 or self.in_h2 or self.in_h3 or self.in_p:
            self.current_paragraph.append(data)
        if self.in_a_author or self.in_a_category:
            self._a_text.append(data)

    @staticmethod
    def _looks_like_junk(text: str) -> bool:
        """Identify paragraphs that are nav/footer/related-story leftovers."""
        junk_markers = (
            "© 20", "כל הזכויות שמורות", "פיתוח Fatfish", "המקום הכי חם בגיהנום",
            "[email protected]", "אנחנו מחויבים לעיתונות", "כאן עושים עיתונות",
            "בקליק לניוזלטר", "Powered by", "data:image/svg",
        )
        return any(m in text for m in junk_markers)


# --- Fetching -----------------------------------------------------------------

def fetch_url(url: str) -> str:
    """Fetch raw HTML from URL."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace")


def parse_article(html: str) -> Dict:
    """Run the HTML parser, return structured article data."""
    p = ArticleHTMLParser()
    p.feed(html)
    # If no subtitle was found in an h2 tag, fall back to og:description
    subtitle = p.subtitle or p.og_description
    return {
        "title": p.title,
        "subtitle": subtitle,
        "byline": p.byline,
        "categories": p.categories,
        "category": ", ".join(p.categories),  # back-compat string form
        "published_date": p.published_date,
        "og_image": p.og_image,
        "paragraphs": p.paragraphs,
        "images": p.images,
    }


# --- Analysis helpers ---------------------------------------------------------

def extract_quotes(paragraphs: List[Dict]) -> List[str]:
    """Pull out blockquotes and inline quoted passages.
    Skips quotes broken across words (regex pickups of abbreviations like "השב\"כ").
    """
    quotes = []
    seen = set()

    def add(q: str):
        q = q.strip()
        # reject quotes that start or end mid-word (after a letter that's part
        # of an abbreviation like השב"כ)
        if not q or len(q) < 25:
            return
        # reject if begins/ends with single Hebrew letter followed by comma/space
        if re.match(r"^[א-ת][,.\s]", q):
            return
        if q in seen:
            return
        seen.add(q)
        quotes.append(q)

    for para in paragraphs:
        if para["is_quote"]:
            add(para["text"])
            continue
        text = para["text"]
        # Hebrew geresh-style quotation marks "..."
        # but avoid matching across abbreviations (השב"כ, פצ"ר, מל"ם)
        # Strategy: only consider " that is NOT preceded by a single Hebrew letter
        # and not immediately followed by a single Hebrew letter (which suggests
        # it's part of an acronym).
        candidates = []
        # explicit Hebrew quote-of-speech marks ״...״
        for m in re.finditer(r'״([^״]{25,260})״', text):
            candidates.append(m.group(1))
        # plain " quotes — only if the opening is followed by a non-abbreviation
        # (i.e., next char is space, Hebrew letter that's NOT followed by another quote, etc.)
        # Most reliable: look for " preceded by space/start, ending with " followed by space/punct
        for m in re.finditer(r'(?:^|[\s\(])"([^"]{25,260}?)"(?=[\s,.;\)]|$)', text):
            inner = m.group(1)
            # filter: must look like a sentence — first char Hebrew letter (full word, not abbreviation fragment)
            if re.match(r"^[א-ת]", inner):
                # additional filter — first 4 chars shouldn't form a known abbreviation start
                candidates.append(inner)
        for c in candidates:
            add(c)
    return quotes


def extract_named_people(text: str) -> List[str]:
    """Extract real people names — requires either:
       (a) first token matches HEBREW_FIRST_NAMES, OR
       (b) the same two-word phrase appears 3+ times in the text.
    """
    pattern = re.compile(r"(?<![א-ת])([א-ת]{2,12})\s+([א-ת]{2,18})(?![א-ת])")
    raw = pattern.findall(text)
    counts: Dict[str, int] = {}
    for first, last in raw:
        full = f"{first} {last}"
        counts[full] = counts.get(full, 0) + 1

    # noise blacklist — first words that are never first names but match the pattern
    NOISE_FIRSTS = {
        "באמצע", "מקורבים", "כ", "בני", "טוענים", "בררנית", "אמצעי", "השב",
        "בית", "כל", "אחרי", "לפני", "כמו", "בלי", "עם", "אבל", "ויש",
        "מאז", "אז", "ועוד", "וגם", "וכן", "בעת", "אצל", "כדי", "תוך",
        "מתוך", "ללא", "אחר", "ולא", "וגם", "וכל", "גם", "רק", "לא",
        "אחת", "שני", "שלוש", "ארבע", "חמש", "שש", "שבע", "שמונה",
        "המקום", "האדם", "האזרח", "הילד", "האם", "האב", "האח", "מערכת",
        "פרשת", "פרשיית", "תיק", "מבצע", "אירוע", "פגיעה", "תקיפה",
        "הוצא", "הוגש", "הותר", "נחקר", "נעצר", "נמצא", "פוטר", "מונה",
        "השב\"כ", "בין", "כשהוא", "כשהיא", "כשהם", "באמצעות", "במעמד",
        "במהלך", "במשך", "עוד", "ועד", "כפי", "כמובן", "באוגדה", "בפיקודו",
        "סרן", "סא\"ל", "אל\"מ", "תא\"ל", "ק\"א", "ק\"ב", "פצ\"ר", "פצ\"רית",
        "אז", "בשלב", "אגב",
    }
    NOISE_LASTS = {
        "היום", "השבוע", "השנה", "המשפט", "הביטחון", "המודיעין", "החקירה",
        "השב\"כ", "כשהוא", "כשהיא", "כשהם", "כשהן", "באוגדה", "ביוני",
        "בפברואר", "בנובמבר", "במרץ", "באפריל", "במאי", "ביולי", "באוגוסט",
        "בספטמבר", "באוקטובר", "בדצמבר", "בינואר", "ברצועה", "באוטו",
    }

    people = []
    for full, count in counts.items():
        first, last = full.split(" ", 1)
        if first in NOISE_FIRSTS or last in NOISE_LASTS:
            continue
        is_known_first = first in HEBREW_FIRST_NAMES
        is_known_last = last in HEBREW_FIRST_NAMES  # sometimes order is reversed
        if is_known_first or is_known_last:
            people.append(full)
        elif count >= 3:
            # frequent enough — likely a real name even if not in our list
            people.append(full)
    return people


def count_people(text: str) -> int:
    return len(extract_named_people(text))


def count_dates(text: str) -> int:
    """Hebrew date patterns: 'ב-DD בMM YYYY' or 'DD/MM/YYYY' or 'YYYY'."""
    patterns = [
        r"\bב-?\d{1,2}\s+ב?[א-ת]+\s+\d{4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b(19|20)\d{2}\b",
    ]
    total = 0
    for pat in patterns:
        total += len(re.findall(pat, text))
    return total


def has_document_keywords(title: str, paragraphs: List[Dict]) -> int:
    """Returns count of document-related keywords in title + first 3 paragraphs."""
    head = title + " " + " ".join(p["text"] for p in paragraphs[:3])
    return sum(1 for kw in DOCUMENT_KEYWORDS if kw in head)


def has_court_phrases(paragraphs: List[Dict]) -> int:
    full = " ".join(p["text"] for p in paragraphs)
    return sum(1 for phrase in COURT_PHRASES if phrase in full)


def title_is_person(title: str) -> bool:
    """Heuristic: title contains a Hebrew first+last name and few other content words."""
    name_match = re.search(r"\b([א-ת]{2,12}\s+[א-ת]{2,15})\b", title)
    if not name_match:
        return False
    # filter common false positives
    name = name_match.group(1)
    if any(w in name for w in ["משפט", "ביטחון", "ממשלה"]):
        return False
    return True


def is_recent(published_date: str, hours: int = 24) -> bool:
    """Was article published within last N hours?"""
    if not published_date:
        return False
    try:
        dt = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - dt).total_seconds() < hours * 3600
    except ValueError:
        return False


# --- Archetype selection ------------------------------------------------------

def choose_archetype(article: Dict, override: Optional[str] = None) -> Tuple[str, str]:
    """Returns (archetype_letter, reason_text).

    Selection logic (in priority order):
    1. Manual override
    2. Opinion category → B
    3. Strong investigation signals (court + docs + dates) → A
       (even without explicit "תחקירים" category, since articles are often
       tagged by topic like "דמוקרטיה במשבר" or "משפט ופלילים")
    4. Mosaic — 4+ protagonists AND no strong investigation signals
    5. Document-driven — explicit mention of document/petition in title
    6. Breaking — recent + hot category
    7. Profile — title is a person name
    8. Default → A
    """
    if override:
        return override.upper(), f"override ידני: {override}"

    title = article.get("title", "")
    subtitle = article.get("subtitle", "")
    category = (article.get("category") or "").strip()
    paragraphs = article.get("paragraphs", [])
    full_text = " ".join(p["text"] for p in paragraphs)

    cat_lower = category.lower()

    # Rule 2: Opinion
    if any(c in cat_lower for c in OPINION_CATEGORIES):
        return "B", f"קטגוריה '{category}' = דעות → Op-Ed"

    # Compute investigation-strength score
    is_invest_cat = any(c in cat_lower for c in INVESTIGATION_CATEGORIES)
    doc_count = has_document_keywords(title + " " + subtitle, paragraphs)
    court_count = has_court_phrases(paragraphs)
    date_count = count_dates(full_text)
    invest_score = doc_count + court_count + (date_count // 3)

    # Rule 3a: Explicit investigation category — lower threshold
    if is_invest_cat and invest_score >= 2:
        return "A", (f"קטגוריה 'תחקירים' + {doc_count} מסמכים, "
                     f"{court_count} ביטויי בית-משפט, {date_count} תאריכים")

    # Rule 3b: Strong investigation signals even without explicit category
    # (articles often tagged by topic like "דמוקרטיה במשבר" but still are תחקירים)
    if invest_score >= 5:
        return "A", (f"סיגנלי תחקיר חזקים: {doc_count} מסמכים, "
                     f"{court_count} ביטויי בית-משפט, {date_count} תאריכים")

    # Rule 4: Mosaic — only if NOT a strong investigation
    people = count_people(full_text)
    if people >= 4 and invest_score < 3:
        return "F", f"{people} דמויות שונות בכתבה (sub-investigation) → Mosaic"

    # Rule 5: Document-driven
    if has_document_keywords(title + " " + subtitle, paragraphs) >= 1:
        return "E", f"כותרת/לי\"ד מזכיר מסמך/תזכיר/דו\"ח/החלטה"

    # Rule 6: Breaking
    if is_recent(article.get("published_date", "")) and \
       any(c in cat_lower for c in BREAKING_CATEGORIES):
        return "D", f"פורסם ב-24h אחרונות + קטגוריה '{category}'"

    # Rule 7: Profile
    if title_is_person(title):
        return "C", f"הכותרת מכילה שם דמות → Profile"

    # Rule 8: Default
    return "A", "ברירת מחדל — Investigation-System"


# --- Sequence assembly --------------------------------------------------------

def adjust_sequence_length(sequence: List[str], target: int) -> List[str]:
    """Trim or extend a sequence to the target length, keeping cover/hero/cta."""
    if target == len(sequence):
        return sequence
    cover = sequence[0]    # cover-overlay
    hero = sequence[1]     # hero-bleed-fade
    cta = sequence[-1]     # cta-red
    middle = sequence[2:-1]

    target_middle = target - 3
    if target_middle < 1:
        target_middle = 1

    if target_middle < len(middle):
        # Trim — remove from the middle (keep first and last middle blocks)
        keep_indices = sorted([0, len(middle) - 1] +
                              list(range(1, len(middle) - 1))[:target_middle - 2])
        middle = [middle[i] for i in keep_indices][:target_middle]
    elif target_middle > len(middle):
        # Extend — duplicate variation-friendly blocks
        fillers = ["text-only-argument", "quote-pull", "split-text-photo"]
        idx = 0
        while len(middle) < target_middle:
            candidate = fillers[idx % len(fillers)]
            # don't allow duplicate adjacency
            if not middle or middle[-1] != candidate:
                middle.append(candidate)
            idx += 1

    return [cover, hero] + middle + [cta]


def enforce_no_adjacent_duplicates(sequence: List[str]) -> List[str]:
    """Reorder if any block appears twice in a row."""
    out = [sequence[0]]
    for block in sequence[1:]:
        if out[-1] == block:
            # find a swap target later
            swapped = False
            for j in range(len(out) - 2, 0, -1):
                if out[j] != block and (j == 0 or out[j - 1] != block):
                    # swap doesn't help here in simple case; just insert filler
                    out.append("text-only-argument")
                    swapped = True
                    break
            if not swapped:
                out.append(block)  # accept duplicate as last resort
                continue
        out.append(block)
    return out


# --- Content slicing per slide ------------------------------------------------

def assign_content_to_slides(article: Dict, sequence: List[str]) -> List[Dict]:
    """For each slide block in the sequence, pick the right text and image hint."""
    paragraphs = article.get("paragraphs", [])
    quotes = extract_quotes(paragraphs)
    title = article.get("title", "")
    subtitle = article.get("subtitle", "")
    byline = article.get("byline", "")
    body_paras = [p["text"] for p in paragraphs if not p["is_quote"]]

    slides = []
    para_cursor = 0
    quote_cursor = 0

    for idx, block in enumerate(sequence):
        slide: Dict = {"index": idx, "block": block}

        if block == "cover-overlay":
            slide["title"] = title
            slide["byline"] = byline
            slide["image_role"] = "hero"
            slide["image_hint"] = title  # for sourcing

        elif block == "hero-bleed-fade":
            slide["lede"] = subtitle or (body_paras[0] if body_paras else "")
            slide["body"] = body_paras[1] if len(body_paras) > 1 else ""
            para_cursor = 2
            slide["image_role"] = "hero-reuse"

        elif block == "text-only-argument":
            slide["paragraphs"] = body_paras[para_cursor:para_cursor + 2]
            para_cursor += 2

        elif block == "text-only-highlight":
            # find the most "highlight-worthy" paragraph (with dates or short bold-fact)
            highlight_idx = find_highlight_paragraph(body_paras, para_cursor)
            if highlight_idx is not None:
                slide["before"] = body_paras[max(0, highlight_idx - 1)] if highlight_idx > 0 else ""
                slide["highlight"] = body_paras[highlight_idx]
                slide["after"] = body_paras[highlight_idx + 1] if highlight_idx + 1 < len(body_paras) else ""
                para_cursor = max(para_cursor, highlight_idx + 2)
            else:
                slide["before"] = body_paras[para_cursor] if para_cursor < len(body_paras) else ""
                slide["highlight"] = body_paras[para_cursor + 1] if para_cursor + 1 < len(body_paras) else ""
                slide["after"] = body_paras[para_cursor + 2] if para_cursor + 2 < len(body_paras) else ""
                para_cursor += 3

        elif block == "split-text-photo":
            slide["paragraphs"] = body_paras[para_cursor:para_cursor + 1]
            para_cursor += 1
            slide["image_role"] = "scene"
            slide["image_hint"] = slide["paragraphs"][0][:120] if slide["paragraphs"] else ""

        elif block == "split-text-cutouts":
            slide["paragraphs"] = body_paras[para_cursor:para_cursor + 1]
            para_cursor += 1
            slide["image_role"] = "cutouts"
            # extract people names from the ENTIRE article (not just this paragraph)
            # — cutouts represent the protagonists across the whole story
            full_text = " ".join(p["text"] for p in paragraphs)
            ppl = extract_named_people(full_text)
            # rank by frequency in the article
            counts: Dict[str, int] = {}
            for name in ppl:
                counts[name] = full_text.count(name.split()[0])  # count by first name
            sorted_people = sorted(ppl, key=lambda n: counts.get(n, 0), reverse=True)
            slide["people"] = sorted_people[:3]

        elif block == "split-text-concept":
            slide["paragraphs"] = body_paras[para_cursor:para_cursor + 1]
            para_cursor += 1
            slide["image_role"] = "concept"
            slide["concept_prompt_seed"] = slide["paragraphs"][0][:200] if slide["paragraphs"] else title

        elif block == "split-text-document":
            slide["paragraphs"] = body_paras[para_cursor:para_cursor + 1]
            para_cursor += 1
            slide["image_role"] = "document"
            slide["image_hint"] = "מסמך / חותמת / החלטה משפטית"

        elif block == "quote-pull":
            if quote_cursor < len(quotes):
                slide["quote"] = quotes[quote_cursor]
                slide["attribution"] = guess_attribution(quotes[quote_cursor], paragraphs)
                quote_cursor += 1
            else:
                # fallback to short body paragraph
                slide["quote"] = body_paras[para_cursor] if para_cursor < len(body_paras) else ""
                slide["attribution"] = byline or "המקום"
                para_cursor += 1

        elif block == "closing-symbol":
            # take last meaningful paragraph for summary
            slide["summary"] = body_paras[-1] if body_paras else subtitle
            slide["image_role"] = "hero-reuse"

        elif block == "cta-red":
            slide["primary"] = "כשציבור מממן, ציבור קובע."
            slide["secondary"] = "ללא פרסומות. ללא בעלי הון."
            slide["button"] = "תמיכה קבועה"

        slides.append(slide)

    return slides


def find_highlight_paragraph(paras: List[str], start_from: int) -> Optional[int]:
    """Find a paragraph with a striking date/number/short factual punch."""
    for i in range(start_from, min(start_from + 8, len(paras))):
        p = paras[i]
        # paragraphs with explicit dates are good candidates
        if re.search(r"\bב-?\d{1,2}\s+ב?[א-ת]+\s+\d{4}\b", p):
            return i
        if len(p) < 180 and ("." in p[:140] or "," in p[:80]):
            return i
    return None


def extract_people_names(text: str) -> List[str]:
    """Use the stricter extract_named_people from above."""
    return extract_named_people(text)


def guess_attribution(quote: str, paragraphs: List[Dict]) -> str:
    """Find the paragraph containing this quote and grab nearby attribution."""
    for p in paragraphs:
        if quote[:40] in p["text"]:
            # look for "אמר/כתב/אמרה X" pattern
            m = re.search(r"(?:אמר|כתב|טען|הצהיר|הסביר|העיד)(?:ה|ו)?\s+([א-ת]{2,12}(?:\s+[א-ת]{2,15})?)", p["text"])
            if m:
                return m.group(1)
    return ""


# --- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Analyze article for carousel planning")
    parser.add_argument("--url", help="Article URL on ha-makom.co.il")
    parser.add_argument("--text-file", help="Plain-text article file")
    parser.add_argument("--title", help="Article title (if no URL)")
    parser.add_argument("--byline", default="", help="Author name")
    parser.add_argument("--category", default="", help="Article category")
    parser.add_argument("--archetype", help="Override archetype (A/B/C/D/E/F)")
    parser.add_argument("--slides", type=int, help="Override slide count (6/8/10/12)")
    args = parser.parse_args()

    if args.url:
        html = fetch_url(args.url)
        article = parse_article(html)
    elif args.text_file:
        with open(args.text_file, encoding="utf-8") as f:
            text = f.read()
        article = {
            "title": args.title or "",
            "subtitle": "",
            "byline": args.byline,
            "category": args.category,
            "published_date": "",
            "og_image": "",
            "paragraphs": [{"text": p.strip(), "is_quote": False}
                           for p in text.split("\n\n") if p.strip() and len(p.strip()) > 30],
            "images": [],
        }
    else:
        print("Error: must provide --url or --text-file", file=sys.stderr)
        sys.exit(2)

    # CLI metadata fallbacks
    if args.title:
        article["title"] = args.title
    if args.byline:
        article["byline"] = args.byline
    if args.category:
        article["category"] = args.category

    archetype, reason = choose_archetype(article, args.archetype)
    sequence = DEFAULT_SEQUENCES[archetype][:]

    target_slides = args.slides or len(sequence)
    sequence = adjust_sequence_length(sequence, target_slides)
    sequence = enforce_no_adjacent_duplicates(sequence)

    slides = assign_content_to_slides(article, sequence)

    output = {
        "archetype": archetype,
        "archetype_name": ARCHETYPES[archetype],
        "archetype_reason": reason,
        "slide_count": len(slides),
        "slides": slides,
        "metadata": {
            "title": article.get("title", ""),
            "subtitle": article.get("subtitle", ""),
            "byline": article.get("byline", ""),
            "category": article.get("category", ""),
            "published_date": article.get("published_date", ""),
            "og_image": article.get("og_image", ""),
            "url": args.url or "",
            "image_count_in_html": len(article.get("images", [])),
        },
        "candidate_images": article.get("images", [])[:20],
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
