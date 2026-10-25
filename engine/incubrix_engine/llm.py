"""Text generation: Gemini (free tier works) with retry, and a deterministic offline fallback."""
import json, os, re, time, urllib.request, urllib.error
from .util import norm

FACT_KEYWORDS = {
    "F1": r"template|typed an idea|full draft|wrote a draft",
    "F2": r"rewrite|rewrote",
    "F3": r"credit",
    "F4": r"clip",
    "F5": r"black bars|captions|quiet",
    "F6": r"2 minutes|minimum",
    "F7": r"175 words",
    "F8": r"sample data",
}

class LLMError(Exception):
    """transient=True: waiting and trying again may help (429/503/timeout).
    fatal=True: stop calling the API for the rest of this run (bad key, daily quota used up)."""
    def __init__(self, msg, transient=False, fatal=False):
        super().__init__(msg)
        self.transient: bool = transient
        self.fatal: bool = fatal

def build_prompt(slot, source, brand, base_url_line):
    facts = "\n".join(f"- {k}: {v['text']}" for k, v in brand["facts"].items())
    rules = "\n".join(f"- {r}" for r in brand["voice_rules"])
    fmt = slot["format"]
    shape = {
        "Short video": '"beats": ["5 to 8 short on-screen lines, max 9 words each, last one a question"]',
        "Carousel": '"slides": ["6 to 8 slides, max 25 words each, slide 1 is the hook, last is a question"]',
        "Graphic": '"slides": ["exactly 1 or 2 short lines for a single image"]',
        "Text post": '"slides": []',
    }[fmt]
    return f"""You write social posts for a creator-tool brand. Platform: {slot['platform']}. Format: {fmt}. Content pillar: {slot['pillar']}.
Voice rules:
{rules}
Product facts you may use (cite ids in facts_used). Do not claim anything else about the product:
{facts}
Use ONLY ideas and numbers that appear in the SOURCE below or in the facts. Idea number {slot['idx']}: choose a different part of the source than other numbers.
SOURCE:
\"\"\"{source[:6000]}\"\"\"
{('Fix these problems from your last attempt: ' + '; '.join(slot['feedback'])) if slot.get('feedback') else ''}
Return ONLY JSON with keys: "hook" (first line, max 100 chars), "caption" (the body; for a Text post max 140 words; no hashtags), "cta" (one question or action), "hashtags" (list, each starting with #), "facts_used" (list of fact ids, [] if none), {shape}."""

class GeminiClient:
    def __init__(self, cfg, simulate_failure=False):
        self.model = cfg["model"]; self.timeout = cfg["llm_timeout_s"]
        self.key = os.environ.get(cfg["api_key_env"], "")
        self.base = cfg.get("api_base", "https://generativelanguage.googleapis.com/v1beta")
        self.min_interval = cfg.get("llm_min_interval_s", 6)
        self.simulate_failure = simulate_failure
        self.tokens_in = 0; self.tokens_out = 0
        self.disabled = False; self._last_call = None

    @property
    def available(self):
        return bool(self.key) and not self.disabled

    def _pace(self):
        now = time.monotonic()
        if self._last_call is not None:
            wait = self.min_interval - (now - self._last_call)
            if wait > 0:
                time.sleep(wait)
        self._last_call = time.monotonic()

    def _redact(self, message):
        return message.replace(self.key, "[redacted]") if self.key else message

    def generate(self, prompt):
        if self.simulate_failure:
            raise LLMError("simulated failure")
        if not self.key:
            raise LLMError("no API key in environment", fatal=True)
        self._pace()
        url = f"{self.base}/models/{self.model}:generateContent"
        body = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                           "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7}}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "x-goog-api-key": self.key})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            try:
                error_body = json.loads(e.read().decode())
                detail = error_body.get("error", {}).get("message", "")
                if not isinstance(detail, str):
                    detail = ""
            except (json.JSONDecodeError, AttributeError, TypeError, UnicodeDecodeError, OSError):
                detail = ""
            finally:
                e.close()
            detail = self._redact(" ".join(detail.split())[:220])
            per_day = bool(re.search(r"per ?day|daily", detail, re.I))
            fatal = e.code in (400, 401, 403) or (e.code == 429 and per_day)
            raise LLMError(self._redact(f"HTTP {e.code} {e.reason}: {detail}"),
                           transient=e.code in (429, 500, 502, 503, 504) and not fatal, fatal=fatal)
        except (urllib.error.URLError, TimeoutError) as e:
            raise LLMError(self._redact(f"request failed: {e}"), transient=True)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise LLMError("bad response shape", transient=True)
        try:
            usage = data.get("usageMetadata", {})
            self.tokens_in += usage.get("promptTokenCount", 0); self.tokens_out += usage.get("candidatesTokenCount", 0)
            parts = data["candidates"][0]["content"]["parts"]
            text = "".join(p["text"] for p in parts if "text" in p and not p.get("thought"))
            text = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.I)
            return json.loads(text)
        except (KeyError, IndexError, TypeError, AttributeError, json.JSONDecodeError):
            raise LLMError("bad response shape", transient=True)

def sentences(source):
    parts = re.split(r"(?<=[.!?])\s+|\n+", source)
    return [p.strip() for p in parts if len(p.split()) >= 5 and not p.lower().startswith(("hi,", "thanks for"))]

def usable(sents):
    """Drop sentences that make product claims we cannot tie to a verified fact id."""
    out = []
    for x in sents:
        product = re.search(r"incubrix|credits?\b|clips\b|template", x, re.I)
        if product and not any(re.search(p, x, re.I) for p in FACT_KEYWORDS.values()):
            continue
        out.append(x)
    return out

def offline_asset(slot, source):
    """Deterministic, extractive fallback. Plainer than the LLM output but passes the same checks."""
    S = usable(sentences(source)); L = len(S)
    if L < 2:
        raise LLMError("source has too few usable sentences")
    n = slot["idx"]
    s1 = S[n % L]; s2 = S[(n + 1 + n // L) % L]
    first = s1.rstrip(".!?")
    hook = (first if len(first) <= 100 else first[:97].rsplit(" ", 1)[0] + "...")
    facts = sorted({fid for fid, pat in FACT_KEYWORDS.items() if re.search(pat, s1 + " " + s2, re.I)})
    tags = {"LinkedIn": ["#ContentCreation", "#ShortFormVideo", "#CreatorTools"],
            "Instagram": ["#ContentCreation", "#CreatorTips", "#Reels", "#Repurposing"],
            "YouTube Shorts": ["#Shorts", "#ContentCreation", "#CreatorTips"]}[slot["platform"]]
    q = "What would you change in this?"
    a = {"hook": hook, "caption": f"{s1} {s2}", "cta": q, "hashtags": tags, "facts_used": facts, "slides": [], "beats": []}
    short = lambda x, k=9: " ".join(x.split()[:k])
    rest = [S[(n + 2 + j) % L] for j in range(4)]
    if slot["format"] == "Short video":
        a["beats"] = [short(hook), short(s2)] + [short(x) for x in rest[:3]] + [q]
    if slot["format"] == "Carousel":
        a["slides"] = [short(hook, 25), short(s2, 25)] + [short(x, 25) for x in rest[:3]] + [q]
    if slot["format"] == "Graphic":
        a["slides"] = [short(hook, 25)]
    return a

def generate_with_recovery(client, slot, source, brand, cfg, log, errors):
    """Try Gemini with retries and waiting; on repeated failure log the error and fall back to offline generation."""
    prompt = build_prompt(slot, source, brand, "")
    if client is not None and not client.disabled:
        attempts = cfg["llm_retries"] + 1
        for attempt in range(1, attempts + 1):
            try:
                out = client.generate(prompt)
                out.setdefault("slides", []); out.setdefault("beats", []); out.setdefault("facts_used", [])
                return out, "gemini"
            except LLMError as e:
                msg = f"slot {slot['slot_id']} attempt {attempt}: {e}"
                log.warning(msg); errors.append(msg)
                if e.fatal:
                    client.disabled = True
                    log.warning("Gemini switched off for the rest of this run")
                    break
                if e.transient and attempt < attempts:
                    wait = cfg.get("llm_backoff_s", 10) * attempt
                    log.warning(f"waiting {wait}s before trying again")
                    time.sleep(wait)
                elif not e.transient:
                    break
    log.warning(f"slot {slot['slot_id']}: using offline fallback generator")
    return offline_asset(slot, source), "offline"
