import shutil
import tempfile
import unittest
from pathlib import Path

from incubrix_engine.pipeline import Engine

ENGINE_ROOT = Path(__file__).resolve().parent.parent
INPUTS = [
    ("blog-style", ENGINE_ROOT / "tests" / "fixtures" / "blog_400_chars.txt"),
    ("transcript-style", ENGINE_ROOT / "tests" / "fixtures" / "transcript_1500_chars.txt"),
    ("bullet-list", ENGINE_ROOT / "tests" / "fixtures" / "bullet_list_6000_chars.txt"),
    ("long_input_launch_kit", ENGINE_ROOT / "content" / "long_input_launch_kit.txt"),
]
DEMO_TRANSCRIPT = ENGINE_ROOT / "content" / "demo_transcript.txt"
if DEMO_TRANSCRIPT.is_file():
    INPUTS.append(("demo_transcript", DEMO_TRANSCRIPT))


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg not on PATH")
class OfflineInputTests(unittest.TestCase):
    def test_week_profile_produces_at_least_ten_assets_for_each_input(self):
        for label, input_path in INPUTS:
            with self.subTest(input=label), tempfile.TemporaryDirectory(prefix="incubrix_input_test_") as temp_dir:
                engine = Engine(temp_dir)
                try:
                    summary = engine.run(input_path, "week")
                    self.assertGreaterEqual(summary["assets_produced"], 10)
                    self.assertEqual(summary["assets_rejected"], summary["rejected"])
                    self.assertEqual(summary["source_counts"]["offline"], summary["assets_produced"])
                finally:
                    engine.store.close()
                    for handler in engine.log.handlers[:]:
                        handler.close()
                        engine.log.removeHandler(handler)


if __name__ == "__main__":
    unittest.main()
