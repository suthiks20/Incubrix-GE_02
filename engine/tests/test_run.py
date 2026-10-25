import contextlib
import io
import sys
import unittest
from unittest.mock import patch

import run


class FfmpegPreflightTests(unittest.TestCase):
    def test_missing_ffmpeg_prints_message_and_fails_before_run_or_ingest(self):
        expected = "ffmpeg not found. Install it and add it to PATH (see engine/README.md, Windows setup).\n"
        for args in (
            ["run.py", "run", "--input", "content/input_1.txt"],
            ["run.py", "ingest", "--library", "content/library_30.json"],
        ):
            with self.subTest(command=args[1]):
                output = io.StringIO()
                with patch.object(sys, "argv", args), patch.object(run.shutil, "which", return_value=None):
                    with patch.object(run, "load_json") as load_config:
                        with contextlib.redirect_stdout(output):
                            result = run.main()
                self.assertEqual(result, 1)
                self.assertEqual(output.getvalue(), expected)
                load_config.assert_not_called()


if __name__ == "__main__":
    unittest.main()
