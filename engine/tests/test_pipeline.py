import csv, json, shutil, tempfile, unittest
from pathlib import Path
from incubrix_engine.pipeline import Engine
from incubrix_engine.llm import GeminiClient
from incubrix_engine.export import repo_relative_path
from check_workbook import COLS as WORKBOOK_COLUMNS, compare_rows
ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "content" / "input_1.txt"
TINY = {"short_video": 1, "carousel": 1, "graphic": 1, "text_post": 7}   # 10 assets, one video keeps tests fast
CALENDAR_COLUMNS = ["asset_id", "platform", "format", "content_pillar", "hook", "caption", "cta", "utm_link",
                    "final_file_url", "source_file_url", "source_input", "tools_used", "rights_checked", "ai_label_needed",
                    "scheduled_date", "test_published_url", "impressions_or_views", "engagement_rate", "clicks", "status", "notes"]

def make(tmp, **kw):
    e = Engine(tmp, **kw); e.cfg["profiles"]["tiny"] = TINY; return e

def rows(tmp):
    with open(Path(tmp) / "calendar.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))

class Pipeline(unittest.TestCase):
    def setUp(self): self.tmp = tempfile.mkdtemp()
    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def test_normal_run_makes_10_plus_with_utm_and_files(self):
        s = make(self.tmp).run(INPUT, "tiny"); self.assertGreaterEqual(s["produced"], 10)
        r = rows(self.tmp); self.assertGreaterEqual(len(r), 10)
        self.assertEqual(list(r[0]), CALENDAR_COLUMNS)
        self.assertTrue(all("utm_source=" in x["utm_link"] and x["final_file_url"] and x["scheduled_date"] for x in r))
        self.assertTrue(all(x["source_file_url"] for x in r))
        self.assertTrue(all("\\" not in x["final_file_url"] and "\\" not in x["source_file_url"] for x in r))
        source = json.loads((Path(self.tmp) / r[0]["source_file_url"]).read_text(encoding="utf-8"))
        self.assertTrue(source["hashtags"])
        with (Path(self.tmp) / "scheduler.csv").open(encoding="utf-8") as f:
            scheduler = list(csv.DictReader(f))
        scheduled = next(x for x in scheduler if x["asset_id"] == r[0]["asset_id"])
        self.assertTrue(all(tag in scheduled["text"] for tag in source["hashtags"]))
        self.assertTrue((Path(self.tmp) / "scheduler.csv").exists())

    def test_repeat_run_adds_nothing(self):
        make(self.tmp).run(INPUT, "tiny"); n = len(rows(self.tmp))
        s = make(self.tmp).run(INPUT, "tiny")
        self.assertEqual(s["new"], 0); self.assertEqual(s["unchanged"], n); self.assertEqual(len(rows(self.tmp)), n)

    def test_refresh_updates_in_place_without_duplicates(self):
        src = Path(self.tmp) / "in.txt"; src.write_text(INPUT.read_text(encoding="utf-8"), encoding="utf-8")
        make(self.tmp).run(src, "tiny"); before = rows(self.tmp); ids = {r["asset_id"] for r in before}
        src.write_text(src.read_text(encoding="utf-8").replace("the home page is simple",
                       "the home page feels simple to navigate"), encoding="utf-8")
        s = make(self.tmp).run(src, "tiny"); after = rows(self.tmp)
        self.assertEqual({r["asset_id"] for r in after}, ids); self.assertEqual(len(after), len(before))
        self.assertEqual(len({r["asset_id"] for r in after}), len(after))
        self.assertNotEqual([r["caption"] for r in before], [r["caption"] for r in after])

    def test_run_summary_has_required_metrics_and_source_counts(self):
        s = make(self.tmp).run(INPUT, "tiny")
        self.assertEqual(s["input_name"], INPUT.name)
        self.assertIsInstance(s["run_id"], int)
        self.assertEqual(s["assets_produced"], s["produced"])
        self.assertEqual(s["assets_rejected"], s["rejected"])
        self.assertGreaterEqual(s["runtime_seconds"], 0)
        self.assertEqual(s["source_counts"]["offline"], s["produced"])
        self.assertIn("tokens_in", s)
        self.assertIn("tokens_out", s)
        self.assertIn("estimated_cost_usd", s)
        self.assertIn("error_lines", s)

    def test_dedupe_blocks_copy_from_other_input(self):
        make(self.tmp).run(INPUT, "tiny"); n = len(rows(self.tmp)); copy = Path(self.tmp) / "copy.txt"
        copy.write_text(INPUT.read_text(encoding="utf-8"), encoding="utf-8")
        s = make(self.tmp).run(copy, "tiny"); self.assertGreater(s["duplicates_removed"], 0)
        self.assertEqual(len(rows(self.tmp)), n)

    def test_llm_failure_logged_and_recovered(self):
        c = GeminiClient(make(self.tmp).cfg, simulate_failure=True)
        s = make(self.tmp, client=c).run(INPUT, "tiny")
        self.assertGreaterEqual(s["produced"], 10); self.assertTrue(s["errors"])
        self.assertIn("simulated failure", (Path(self.tmp) / "logs" / "engine.log").read_text())

    def test_render_failure_then_recovery(self):
        s1 = make(self.tmp, simulate="render").run(INPUT, "tiny"); self.assertEqual(s1["render_failed"], 1)
        s2 = make(self.tmp).run(INPUT, "tiny"); self.assertEqual(s2["recovered"], 1); self.assertEqual(len(rows(self.tmp)), s2["produced"])

    def test_library_all_pass_and_counts(self):
        s = make(self.tmp).ingest(ROOT / "content" / "library_30.json"); self.assertEqual(s["produced"], 30); self.assertEqual(s["rejected"], 0)
        r = rows(self.tmp); self.assertGreaterEqual(sum(x["format"] == "Short video" for x in r), 10)
        self.assertGreaterEqual(sum(x["format"] in ("Carousel", "Graphic") for x in r), 5)
        self.assertTrue(all(x["tools_used"] == "Claude (copy), Python, Pillow, ffmpeg" for x in r))
        videos = [x for x in r if x["format"] == "Short video"]
        self.assertTrue(all(x["notes"].endswith("; silent video, add licensed audio in-app if wanted") for x in videos))
        source = json.loads((Path(self.tmp) / r[0]["source_file_url"]).read_text(encoding="utf-8"))
        self.assertTrue(source["hashtags"])

    def test_workbook_comparison_reports_each_cell_mismatch(self):
        workbook_rows = [["same"] * len(WORKBOOK_COLUMNS)]
        csv_rows = [{column: "same" for column in WORKBOOK_COLUMNS}]
        self.assertEqual(compare_rows(workbook_rows, csv_rows), [])
        csv_rows[0][WORKBOOK_COLUMNS[1]] = "different"
        self.assertEqual(compare_rows(workbook_rows, csv_rows), [
            "row 5, column platform: workbook='same', calendar='different'"
        ])
        self.assertEqual(compare_rows(workbook_rows, []), [
            "row count mismatch: workbook=1, calendar=0"
        ])

    def test_export_paths_are_repo_relative_and_forward_slash_separated(self):
        self.assertEqual(
            repo_relative_path(ROOT.parent / "main_output", "assets/C01/C01.pdf"),
            "main_output/assets/C01/C01.pdf",
        )

if __name__ == "__main__": unittest.main()
