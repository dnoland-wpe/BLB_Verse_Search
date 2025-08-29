import re, sys, urllib.parse, subprocess

# Default translation (override with: -t ESV  or  (ESV)  or  [ESV])
DEFAULT_TRANS = "ESV"

# BLB 3-letter book codes (OT + NT)
BLB_CODES = {
    # OT
    "gen": "gen", "exod": "exo", "exo": "exo", "lev": "lev", "num": "num", "deut": "deu", "deu": "deu",
    "josh": "jos", "jos": "jos", "judg": "jdg", "jdg": "jdg", "ruth": "rut", "rut": "rut",
    "1sam": "1sa", "1 sa": "1sa", "1 sam": "1sa", "1sm": "1sa", "1sa": "1sa",
    "2sam": "2sa", "2 sa": "2sa", "2 sam": "2sa", "2sm": "2sa", "2sa": "2sa",
    "1kgs": "1ki", "1kg": "1ki", "1ki": "1ki", "1 kings": "1ki",
    "2kgs": "2ki", "2kg": "2ki", "2ki": "2ki", "2 kings": "2ki",
    "1chr": "1ch", "1 ch": "1ch", "1 chron": "1ch", "1chron": "1ch",
    "2chr": "2ch", "2 ch": "2ch", "2 chron": "2ch", "2chron": "2ch",
    "ezra": "ezr", "ezr": "ezr", "neh": "neh", "esth": "est", "est": "est", "job": "job",
    "ps": "psa", "pss": "psa", "psa": "psa", "psalm": "psa", "psalms": "psa",
    "prov": "pro", "pro": "pro", "prv": "pro",
    "eccl": "ecc", "ecc": "ecc", "qoh": "ecc",
    "song": "sng", "song of songs": "sng", "song of solomon": "sng", "sos": "sng", "sng": "sng",
    "isa": "isa", "jer": "jer", "lam": "lam", "ezek": "eze", "eze": "eze",
    "dan": "dan", "hos": "hos", "joel": "joe", "joe": "joe", "amos": "amo", "amo": "amo",
    "obad": "oba", "oba": "oba", "jonah": "jon", "jon": "jon", "mic": "mic",
    "nah": "nah", "hab": "hab", "zeph": "zep", "zep": "zep",
    "hag": "hag", "zech": "zec", "zec": "zec", "mal": "mal",
    # NT
    "mat": "mat", "matt": "mat", "mt": "mat", "matthew": "mat",
    "mark": "mar", "mrk": "mar", "mar": "mar", "mk": "mar",
    "luke": "luk", "luk": "luk", "lk": "luk",
    "john": "jhn", "jhn": "jhn", "jn": "jhn",
    "acts": "act", "act": "act", "ac": "act",
    "rom": "rom", "rm": "rom", "romans": "rom",
    "1 cor": "1co", "1cor": "1co", "1co": "1co", "1st cor": "1co", "first corinthians": "1co",
    "2 cor": "2co", "2cor": "2co", "2co": "2co", "2nd cor": "2co", "second corinthians": "2co",
    "gal": "gal", "eph": "eph", "phil": "phl", "php": "phl", "phl": "phl",
    "col": "col",
    "1 thess": "1th", "1th": "1th", "1 thes": "1th", "1thessalonians": "1th",
    "2 thess": "2th", "2th": "2th", "2 thes": "2th", "2thessalonians": "2th",
    "1 tim": "1ti", "1tim": "1ti", "1ti": "1ti",
    "2 tim": "2ti", "2tim": "2ti", "2ti": "2ti",
    "titus": "tit", "tit": "tit",
    "philem": "phm", "philemon": "phm", "phm": "phm",
    "heb": "heb", "hebrews": "heb",
    "james": "jam", "jas": "jam", "jam": "jam",
    "1 pet": "1pe", "1pet": "1pe", "1pe": "1pe",
    "2 pet": "2pe", "2pet": "2pe", "2pe": "2pe",
    "1 john": "1jo", "1jn": "1jo", "1 jn": "1jo", "1jo": "1jo",
    "2 john": "2jo", "2jn": "2jo", "2 jn": "2jo", "2jo": "2jo",
    "3 john": "3jo", "3jn": "3jo", "3 jn": "3jo", "3jo": "3jo",
    "jude": "jud", "jud": "jud",
    "rev": "rev", "revelation": "rev", "apocalypse": "rev"
}

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())

def pull_translation(s: str):
    # Accept: -t ESV  OR  trailing (ESV) / [ESV]
    m = re.search(r"(?:^|\s)-t\s+([A-Za-z0-9]+)\b", s, re.I)
    if m:
        trans = m.group(1).upper()
        s = (s[:m.start()] + s[m.end():]).strip()
        return s, trans
    m = re.search(r"[\(\[]\s*([A-Za-z0-9]+)\s*[\)\]]\s*$", s)
    if m:
        trans = m.group(1).upper()
        s = s[:m.start()].strip()
        return s, trans
    return s, DEFAULT_TRANS

def pull_force_search(s: str):
    # Force keyword search if input begins with "? ", "search:", or contains " -s "
    s_stripped = s.lstrip()
    if s_stripped.startswith("?"):
        return s_stripped[1:].lstrip(), True
    if s_stripped.lower().startswith("search:"):
        return s_stripped[7:].lstrip(), True
    if re.search(r"(^|\s)-s(\s|$)", s_stripped):
        s_stripped = re.sub(r"(^|\s)-s(\s|$)", " ", s_stripped).strip()
        return s_stripped, True
    return s, False

def parse_reference(ref: str):
    """Return (code, chapter, verse) if it looks like a verse; otherwise None."""
    ref = ref.replace("—", "-").replace("–", "-").replace("：", ":")
    ref = re.sub(r"\s+", " ", ref).strip()
    if not ref:
        return None

    m = re.match(r"(?i)^\s*(.+?)\s*(\d.*)?$", ref)
    if not m:
        return None
    book_raw = norm(m.group(1))
    nums_raw = (m.group(2) or "").strip()

    book_key = book_raw
    book_key = re.sub(r"\bfirst\b", "1", book_key)
    book_key = re.sub(r"\bsecond\b", "2", book_key)
    book_key = re.sub(r"\bthird\b", "3", book_key)
    book_key = book_key.replace(" i ", " 1 ").replace(" ii ", " 2 ").replace(" iii ", " 3 ")
    book_key = book_key.replace("1st", "1").replace("2nd", "2").replace("3rd", "3")
    book_key = norm(book_key)

    candidates = {
        book_key,
        book_key.replace(".", ""),
        re.sub(r"\s+", "", book_key),
        re.sub(r"\s+", " ", book_key),
    }
    long_to_short = {
        "songs of solomon": "song of solomon",
        "song of songs": "song of songs",
        "song of sol": "song of solomon",
        "ecclesiastes": "eccl", "philippians": "phil", "colossians": "col",
        "thessalonians": "thess", "corinthians": "cor", "peter": "pet"
    }
    for k, v in long_to_short.items():
        if k in book_key:
            candidates.add(norm(book_key.replace(k, v)))

    code = None
    for c in candidates:
        if c in BLB_CODES:
            code = BLB_CODES[c]
            break
    if not code:
        first = book_key.split()[0]
        code = BLB_CODES.get(first)
    if not code:
        return None  # unknown book → treat as keyword search

    if not nums_raw:
        return None

    nums_norm = nums_raw.replace(" ", "")
    chap = verse = None
    m_colon = re.match(r"^(\d+):(\d+(?:-\d+)?)", nums_norm)
    if m_colon:
        chap, verse = m_colon.group(1), m_colon.group(2)
    else:
        digits = re.findall(r"\d+", nums_raw)
        if len(digits) >= 2:
            chap, verse = digits[0], digits[1]
        elif len(digits) == 1:
            chap = digits[0]
        else:
            return None

    return code, chap, verse

def build_url(trans: str, code: str, chap: str, verse: str):
    trans = trans.lower()
    if chap and verse and "-" not in verse:
        return f"https://www.blueletterbible.org/verse/{trans}/{code}/{chap}/{verse}/"
    elif chap and verse and "-" in verse:
        vstart = verse.split("-")[0]
        return f"https://www.blueletterbible.org/verse/{trans}/{code}/{chap}/{vstart}/"
    elif chap:
        return f"https://www.blueletterbible.org/{trans}/{code}/{chap}/1/"
    return None

def keyword_search_url(q: str, trans: str):
    return f"https://www.blueletterbible.org/search/search.cfm?Criteria={urllib.parse.quote_plus(q)}&t={trans.upper()}"

def open_in_chrome(url: str):
    # Open URL in Google Chrome via Launch Services (no AppleScript/Automation needed)
    try:
        subprocess.run(["open", "-a", "Google Chrome", url], check=False)
    except Exception:
        # Fallback to default browser
        subprocess.run(["open", url], check=False)

def main():
    if len(sys.argv) < 2:
        return
    raw = sys.argv[1]

    raw, force_search = pull_force_search(raw)
    raw, trans = pull_translation(raw)

    if force_search:
        url = keyword_search_url(raw, trans)
        open_in_chrome(url)
        return

    parsed = parse_reference(raw)
    if parsed:
        code, chap, verse = parsed
        url = build_url(trans, code, chap, verse)
        if url:
            open_in_chrome(url)
            return

    # Fallback: keyword search
    open_in_chrome(keyword_search_url(raw, trans))

if __name__ == "__main__":
    main()
