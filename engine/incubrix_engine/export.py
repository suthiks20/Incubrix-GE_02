"""Exports calendar.csv (same columns as the workbook 02_ASSETS tab) and scheduler.csv (bulk-upload shape)."""
import csv
from pathlib import Path

COLS = ["asset_id", "platform", "format", "content_pillar", "hook", "caption", "hashtags", "cta", "utm_link", "target_metric",
        "final_file_url", "source_file_url", "source_input", "tools_used", "rights_checked", "ai_label_needed",
        "scheduled_date", "test_published_url", "impressions_or_views", "engagement_rate", "clicks", "status", "notes"]

def export_all(store, out):
    out = Path(out); rows, sched = [], []
    for x in store.all_assets():
        if x["status"] != "rendered": continue
        a = x["data"]
        files = a.get("files", [])
        row = {"asset_id": a["asset_id"], "platform": a["platform"], "format": a["format"], "content_pillar": a["pillar"],
               "hook": a["hook"], "caption": a["final_caption"], "hashtags": " ".join(a.get("hashtags", [])),
               "cta": a["cta"], "utm_link": a["utm_link"], "target_metric": "UTM-attributed clicks",
               "final_file_url": ";".join(files), "source_file_url": a.get("source_file", ""), "source_input": a["source_input"],
               "tools_used": a["tools_used"], "rights_checked": "Yes", "ai_label_needed": "No", "scheduled_date": a["scheduled"],
               "test_published_url": "", "impressions_or_views": "", "engagement_rate": "", "clicks": "", "status": "Ready",
               "notes": "Facts: " + (",".join(a.get("facts_used", [])) or "none")}
        row["format"] = {"Text post": "Text post"}.get(row["format"], row["format"])
        rows.append(row)
        sched.append({"platform": a["platform"], "scheduled_utc": a["scheduled"], "text": a["final_caption"],
                      "media": ";".join(f for f in files if not f.endswith(".txt")), "first_comment_link": a["utm_link"] if a["platform"] == "LinkedIn" else "",
                      "asset_id": a["asset_id"]})
    rows.sort(key=lambda r: r["scheduled_date"]); sched.sort(key=lambda r: r["scheduled_utc"])
    with open(out / "calendar.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
    with open(out / "scheduler.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["platform", "scheduled_utc", "text", "media", "first_comment_link", "asset_id"]); w.writeheader(); w.writerows(sched)
    return len(rows)
