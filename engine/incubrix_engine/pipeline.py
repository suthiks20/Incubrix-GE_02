"""Main pipeline: plan slots -> generate -> check -> dedupe -> store -> render -> export."""
import json, time
from datetime import date, timedelta
from pathlib import Path
from .util import load_json, sha, jaccard, get_logger, Timer, ROOT
from .checks import check_asset
from .llm import generate_with_recovery
from .render import render_asset, RenderError
from .store import Store
from .export import export_all

PILLARS = ["The reformatting problem and how to fix it", "The product in action", "Hooks and captions",
           "Idea-to-published workflow", "Honest tests"]
SRC = {"LinkedIn": "linkedin", "Instagram": "instagram", "YouTube Shorts": "youtube"}

def plan_slots(profile):
    slots, n = [], 0
    for fmt_key, fmt in (("short_video", "Short video"), ("carousel", "Carousel"), ("graphic", "Graphic"), ("text_post", "Text post")):
        for i in range(profile.get(fmt_key, 0)):
            plat = {"Short video": ["Instagram", "YouTube Shorts"][i % 2], "Carousel": "LinkedIn",
                    "Graphic": "Instagram", "Text post": "LinkedIn"}[fmt]
            slots.append({"slot_id": f"{fmt_key}-{i+1}", "format": fmt, "platform": plat, "pillar": PILLARS[n % 5], "idx": n}); n += 1
    return slots

def nth_slot(cfg, platform, n):
    rule = cfg["slots_utc"][platform]; d = date.fromisoformat(cfg["start_date"]); found = -1
    while True:
        if d.weekday() in rule["days"]:
            found += 1
            if found == n: return f"{d.isoformat()} {rule['time']} UTC"
        d += timedelta(days=1)

def final_caption(a):
    tags = " ".join(a["hashtags"]); body = a["caption"].strip()
    head = "" if body.lower().startswith(a["hook"].lower()[:30]) else a["hook"] + "\n\n"
    extra = {"Instagram": "Link in bio.", "YouTube Shorts": "Link: " + a["utm_link"], "LinkedIn": ""}[a["platform"]]
    parts = [head + body]
    if a["cta"] and a["cta"] not in body: parts.append(a["cta"])
    if extra: parts.append(extra)
    parts.append(tags)
    return "\n\n".join(parts)

class Engine:
    def __init__(self, out_dir, client=None, simulate=None, root=ROOT):
        self.root = Path(root); self.cfg = load_json(self.root / "config.json"); self.brand = load_json(self.root / "brand.json")
        self.out = Path(out_dir); self.out.mkdir(parents=True, exist_ok=True)
        self.log = get_logger(self.out / "logs" / "engine.log"); self.store = Store(self.out / "engine.db")
        self.client = client; self.simulate = simulate or ""

    def _build(self, raw, slot, input_id, input_hash, asset_id, sched, source_label, tools):
        a = {"asset_id": asset_id, "platform": slot["platform"], "format": slot["format"], "pillar": slot["pillar"],
             "hook": raw.get("hook", "").strip(), "caption": raw.get("caption", "").strip(), "cta": raw.get("cta", "").strip(),
             "hashtags": raw.get("hashtags", []), "slides": raw.get("slides", []), "beats": raw.get("beats", []),
             "facts_used": raw.get("facts_used", []), "rights": "generated", "source_input": source_label,
             "tools_used": tools, "scheduled": sched, "input_hash": input_hash, "input_id": input_id}
        a["utm_link"] = (f"{self.cfg['base_url']}?utm_source={SRC[a['platform']]}&utm_medium=social"
                         f"&utm_campaign={self.cfg['campaign']}&utm_content={asset_id}")
        a["final_caption"] = final_caption(a)
        return a

    def _process(self, key, raw, slot, input_id, input_hash, source_text, source_label, tools, stats, asset_id=None):
        cur = self.store.get(key)
        aid = asset_id or (cur["asset_id"] if cur else f"A{self.store.next_id():02}")
        n_plat = sum(1 for x in self.store.all_assets() if x["data"]["platform"] == slot["platform"] and x["key"] != key)
        sched = cur["data"]["scheduled"] if cur else nth_slot(self.cfg, slot["platform"], n_plat)
        a = self._build(raw, slot, input_id, input_hash, aid, sched, source_label, tools)
        fails = check_asset(a, self.brand, source_text)
        if fails: return a, fails, None
        others = [x["data"] for x in self.store.all_assets() if x["key"] != key and x["status"] != "rejected"]
        for o in others + stats["accepted"]:
            sim = jaccard(a["hook"] + " " + a["caption"], o["hook"] + " " + o["caption"])
            if sim >= self.cfg["dedupe_similarity"]: return a, None, f"duplicate of {o['asset_id']} (similarity {sim:.2f})"
        return a, None, None

    def _finish(self, key, a, slot, content_hash, stats, run_id):
        folder = self.out / "assets" / a["asset_id"]; folder.mkdir(parents=True, exist_ok=True)
        self.store.upsert(key, a["asset_id"], a["input_id"], slot["slot_id"], content_hash, "checked", a)
        try:
            sim = self.simulate == "render" and not stats["sim_done"]
            if sim: stats["sim_done"] = True   # simulate exactly one failure per run
            files = render_asset(a, folder, simulate_failure=sim)
            a["files"] = [str(f.relative_to(self.out)) for f in files]
            (folder / f"{a['asset_id']}_source.json").write_text(json.dumps(a, indent=2, ensure_ascii=False), encoding="utf-8")
            a["source_file"] = str((folder / f"{a['asset_id']}_source.json").relative_to(self.out))
            self.store.set_status(key, "rendered", a); stats["accepted"].append(a)
        except RenderError as e:
            msg = f"render failed for {a['asset_id']}: {e}"; self.log.error(msg); self.store.add_error(run_id, msg)
            self.store.set_status(key, "render_failed", a); stats["render_failed"] += 1; stats["errors"].append(msg)

    def run(self, input_path, profile="standard"):
        input_path = Path(input_path); source = input_path.read_text(encoding="utf-8")
        input_id = input_path.stem; input_hash = sha(source)
        slots = plan_slots(self.cfg["profiles"][profile]); stats = {"accepted": [], "rejected": 0, "dupes": 0, "unchanged": 0,
              "updated": 0, "new": 0, "render_failed": 0, "recovered": 0, "errors": [], "sim_done": False}
        run_id = self.store.add_run(started=time.time(), input_id=input_id, input_chars=len(source), produced=0, rejected=0, duplicates=0, runtime_s=0, cost_usd=0)
        self.log.info(f"run start input={input_id} chars={len(source)} slots={len(slots)}")
        tokens_before = (getattr(self.client, "tokens_in", 0), getattr(self.client, "tokens_out", 0))
        with Timer() as t:
            for slot in slots:
                key = sha(f"{input_id}|{slot['slot_id']}"); cur = self.store.get(key)
                if cur and cur["data"].get("input_hash") == input_hash and cur["status"] == "rendered":
                    stats["unchanged"] += 1; stats["accepted"].append(cur["data"]); continue
                if cur and cur["data"].get("input_hash") == input_hash and cur["status"] == "render_failed":
                    self._finish(key, cur["data"], slot, cur["content_hash"], stats, run_id)
                    if self.store.get(key)["status"] == "rendered": stats["recovered"] += 1
                    continue
                errs = []
                raw, how = generate_with_recovery(self.client, slot, source, self.brand, self.cfg, self.log, errs)
                a, fails, dup = self._process(key, raw, slot, input_id, input_hash, source, input_path.name, f"{how}, ffmpeg, Pillow", stats)
                if fails and how == "gemini":
                    slot2 = dict(slot, feedback=fails); raw, how = generate_with_recovery(self.client, slot2, source, self.brand, self.cfg, self.log, errs)
                    a, fails, dup = self._process(key, raw, slot, input_id, input_hash, source, input_path.name, f"{how}, ffmpeg, Pillow", stats)
                for e in errs: self.store.add_error(run_id, e)
                stats["errors"] += errs
                if fails or dup:
                    reason = "; ".join(fails) if fails else dup
                    self.log.info(f"REJECT {slot['slot_id']}: {reason}")
                    (self.out / "rejected.jsonl").open("a", encoding="utf-8").write(json.dumps({"slot": slot["slot_id"], "reason": reason, "asset": a}, ensure_ascii=False) + "\n")
                    stats["rejected"] += 1; stats["dupes"] += 1 if dup else 0; continue
                ch = sha(json.dumps([a["hook"], a["caption"], a["slides"], a["beats"]]))
                if cur and cur["content_hash"] == ch and cur["status"] == "rendered":   # input changed, this asset did not
                    d = dict(cur["data"], input_hash=input_hash); self.store.set_status(key, "rendered", d)
                    stats["unchanged"] += 1; stats["accepted"].append(d); continue
                stats["updated" if cur else "new"] += 1
                self._finish(key, a, slot, ch, stats, run_id)
        tokens = (getattr(self.client, "tokens_in", 0) - tokens_before[0],
                  getattr(self.client, "tokens_out", 0) - tokens_before[1])
        c = self.cfg["cost_per_1k_tokens_usd"]; cost = tokens[0] / 1000 * c["input"] + tokens[1] / 1000 * c["output"]
        produced = len([x for x in stats["accepted"]])
        self.store.db.execute("UPDATE runs SET produced=?,rejected=?,duplicates=?,runtime_s=?,cost_usd=?,note=? WHERE id=?",
                              (produced, stats["rejected"], stats["dupes"], t.seconds, cost, json.dumps({k: stats[k] for k in ("new", "updated", "unchanged", "recovered", "render_failed")}), run_id))
        self.store.db.commit()
        export_all(self.store, self.out)
        source_counts = {"gemini": 0, "offline": 0, "other": 0}
        for item in stats["accepted"]:
            tools = item.get("tools_used", "")
            source_name = "gemini" if tools.startswith("gemini") else "offline" if tools.startswith("offline") else "other"
            source_counts[source_name] += 1
        summary = {"input": input_id, "input_chars": len(source), "slots": len(slots), "produced": produced, "new": stats["new"],
                   "updated": stats["updated"], "unchanged": stats["unchanged"], "rejected": stats["rejected"], "duplicates_removed": stats["dupes"],
                   "assets_produced": produced, "assets_rejected": stats["rejected"], "run_id": run_id,
                   "input_name": input_path.name, "render_failed": stats["render_failed"], "recovered": stats["recovered"],
                   "runtime_seconds": round(t.seconds, 2), "runtime_min": round(t.seconds / 60, 2),
                   "tokens_in": tokens[0], "tokens_out": tokens[1], "estimated_cost_usd": round(cost, 4),
                   "direct_cost_usd": round(cost, 4), "source_counts": source_counts,
                   "errors": stats["errors"], "error_lines": stats["errors"]}
        (self.out / "logs").mkdir(exist_ok=True)
        with (self.out / "logs" / "run_summary.jsonl").open("a", encoding="utf-8") as f: f.write(json.dumps(summary) + "\n")
        self.log.info("run done " + json.dumps(summary)); return summary

    def ingest(self, library_path):
        """Run an already-written asset library through the same checks, dedupe, render and export."""
        lib = load_json(library_path); source = ""
        # numbers are grounded only in real source material, never in the library being checked
        for src in (self.root.parent / "product_notes.txt", self.root / "content" / "input_1.txt"):
            if src.exists(): source += src.read_text(encoding="utf-8") + "\n"
        stats = {"accepted": [], "rejected": 0, "dupes": 0, "new": 0, "updated": 0, "unchanged": 0, "render_failed": 0, "recovered": 0, "errors": [], "sim_done": False}
        run_id = self.store.add_run(started=time.time(), input_id="library", input_chars=len(source), produced=0, rejected=0, duplicates=0, runtime_s=0, cost_usd=0)
        with Timer() as t:
            for item in lib["assets"]:
                slot = {"slot_id": item["id"], "format": item["format"], "platform": item["platform"], "pillar": item["pillar"], "idx": 0}
                key = sha("library|" + item["id"]); ih = sha(json.dumps(item, sort_keys=True))
                cur = self.store.get(key)
                if cur and cur["data"].get("input_hash") == ih and cur["status"] == "rendered":
                    stats["unchanged"] += 1; stats["accepted"].append(cur["data"]); continue
                a, fails, dup = self._process(key, item, slot, "library", ih, source, "authored library (product_notes.txt, input_1.txt)", "Claude (drafting), ffmpeg, Pillow", stats, asset_id=item["id"])
                if fails or dup:
                    reason = "; ".join(fails) if fails else dup; self.log.info(f"REJECT {item['id']}: {reason}")
                    (self.out / "rejected.jsonl").open("a", encoding="utf-8").write(json.dumps({"slot": item["id"], "reason": reason}, ensure_ascii=False) + "\n")
                    stats["rejected"] += 1; stats["dupes"] += 1 if dup else 0; continue
                stats["updated" if cur else "new"] += 1
                self._finish(key, a, slot, sha(json.dumps([a["hook"], a["caption"], a["slides"], a["beats"]])), stats, run_id)
        produced = len(stats["accepted"])
        self.store.db.execute("UPDATE runs SET produced=?,rejected=?,duplicates=?,runtime_s=?,cost_usd=? WHERE id=?",
                              (produced, stats["rejected"], stats["dupes"], t.seconds, 0, run_id)); self.store.db.commit()
        export_all(self.store, self.out)
        source_counts = {"gemini": 0, "offline": 0, "other": 0}
        for item in stats["accepted"]:
            tools = item.get("tools_used", "")
            source_name = "gemini" if tools.startswith("gemini") else "offline" if tools.startswith("offline") else "other"
            source_counts[source_name] += 1
        summary = {"run_id": run_id, "input": "library", "input_name": Path(library_path).name,
                   "produced": produced, "assets_produced": produced,
                   "rejected": stats["rejected"], "assets_rejected": stats["rejected"],
                   "runtime_seconds": round(t.seconds, 2), "runtime_min": round(t.seconds / 60, 2),
                   "tokens_in": 0, "tokens_out": 0, "estimated_cost_usd": 0.0, "direct_cost_usd": 0.0,
                   "source_counts": source_counts, "errors": stats["errors"], "error_lines": stats["errors"]}
        with (self.out / "logs" / "run_summary.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(summary) + "\n")
        return summary
