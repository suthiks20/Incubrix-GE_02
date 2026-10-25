"""Brand and platform checks. An asset is exportable only if check_asset() returns no failures."""
import re

NUM_RE = re.compile(r"\d[\d:.,x%]*")

def words(text):
    return len(re.findall(r"\w[\w'’-]*", text))

def numbers_in(text):
    return [n.rstrip(".,:") for n in NUM_RE.findall(text)]

def check_asset(a, brand, source_text=""):
    """Return list of failure strings (empty = pass)."""
    fails = []
    plat = a.get("platform"); fmt = a.get("format")
    rules = brand["platform_rules"].get(plat)
    if not rules:
        return [f"unknown platform {plat}"]
    hook = (a.get("hook") or "").strip()
    caption = (a.get("caption") or "").strip()
    cta = (a.get("cta") or "").strip()
    tags = a.get("hashtags") or []
    body_all = " ".join([hook, caption, cta] + list(a.get("slides") or []) + list(a.get("beats") or []))

    if not hook: fails.append("missing hook")
    elif len(hook) > brand["hook_max_chars"]: fails.append(f"hook too long ({len(hook)} chars)")
    if not caption: fails.append("missing caption")
    if not cta: fails.append("missing call to action")
    lo, hi = rules["hashtags"]
    if not (lo <= len(tags) <= hi): fails.append(f"hashtags {len(tags)} not in {lo}-{hi}")
    if not all(t.startswith("#") and " " not in t for t in tags): fails.append("malformed hashtag")
    u = a.get("utm_link") or ""
    if not all(k in u for k in ("utm_source=", "utm_campaign=", "utm_content=", "utm_medium=")):
        fails.append("missing UTM link")

    if fmt == "Text post" and "max_words" in rules and words(caption) > rules["max_words"]:
        fails.append(f"post is {words(caption)} words (max {rules['max_words']})")
    if "max_caption_chars" in rules and len(caption) > rules["max_caption_chars"]:
        fails.append("caption too long")
    if "max_title_chars" in rules and len(hook) > rules["max_title_chars"]:
        fails.append("title too long")

    if fmt == "Short video":
        beats = a.get("beats") or []
        if not (4 <= len(beats) <= 10): fails.append("video needs 4-10 beats")
        if sum(a.get("beat_seconds") or [3] * len(beats)) > 60: fails.append("video over 60 s")
    if fmt == "Carousel":
        s = a.get("slides") or []
        lo2, hi2 = rules.get("carousel_slides", [5, 9])
        if not (lo2 <= len(s) <= hi2): fails.append(f"carousel needs {lo2}-{hi2} slides")
    if fmt in ("Carousel", "Graphic", "Short video"):
        for t in (a.get("slides") or []) + (a.get("beats") or []):
            if words(t) > brand["words_per_slide_max"]:
                fails.append("slide/beat text too long"); break

    for pat in brand["banned_regex"]:
        if re.search(pat, body_all, re.I): fails.append(f"banned phrase /{pat}/")
    allowed = set(brand["allowed_numbers"]) | set(numbers_in(source_text))
    bad = [n for n in numbers_in(body_all) if n not in allowed]
    if bad: fails.append("numbers with no source: " + ", ".join(sorted(set(bad))))

    facts_used = a.get("facts_used") or []
    unknown = [f for f in facts_used if f not in brand["facts"]]
    if unknown: fails.append("unknown fact ids " + ",".join(unknown))
    if re.search(r"incubrix|credits?\b|clips\b|template", body_all, re.I) and not facts_used:
        fails.append("product mention with no fact id")
    if a.get("rights") not in ("generated", "own"):
        fails.append("rights not cleared (generated or own media only)")
    return fails
