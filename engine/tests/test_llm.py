import io
import json
import logging
import os
import urllib.error
import unittest
from pathlib import Path
from unittest.mock import patch

from incubrix_engine.llm import GeminiClient, LLMError, generate_with_recovery

ROOT = Path(__file__).resolve().parent.parent


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


def http_error(code, detail):
    body = json.dumps({"error": {"message": detail}}).encode()
    return urllib.error.HTTPError("http://localhost/generate", code, "Google error",
                                  {}, io.BytesIO(body))


def success_response(text='{"hook":"ok"}'):
    body = {
        "candidates": [{"content": {"parts": [
            {"text": "ignored thought", "thought": True},
            {"text": f"```json\n{text}\n```"},
        ]}}],
        "usageMetadata": {"promptTokenCount": 11, "candidatesTokenCount": 7},
    }
    return FakeResponse(json.dumps(body).encode())


class GeminiRecoveryTests(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            self.cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
            self.cfg.update(api_base="http://localhost", llm_min_interval_s=0,
                            llm_backoff_s=1, llm_retries=2)
            self.client = GeminiClient(self.cfg)
        self.slot = {"slot_id": "test-1", "platform": "LinkedIn", "format": "Text post",
                     "pillar": "Testing", "idx": 0}
        self.brand = json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
        self.log = logging.getLogger("test.gemini")

    def recover(self, client=None):
        errors = []
        with patch("incubrix_engine.llm.offline_asset", return_value={"hook": "offline"}) as fallback:
            asset, source = generate_with_recovery(client or self.client, self.slot, "source",
                                                   self.brand, self.cfg, self.log, errors)
        return asset, source, errors, fallback

    def test_503_then_200_succeeds_and_counts_tokens(self):
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   side_effect=[http_error(503, "temporary"), success_response()]) as urlopen:
            asset, source, errors, _ = self.recover()
        self.assertEqual(asset["hook"], "ok")
        self.assertEqual(source, "gemini")
        self.assertEqual((self.client.tokens_in, self.client.tokens_out), (11, 7))
        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(len(errors), 1)

    def test_daily_429_is_fatal_and_switches_off_client(self):
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   side_effect=http_error(429, "Quota exceeded per day")) as urlopen:
            asset, source, errors, fallback = self.recover()
        self.assertEqual((asset["hook"], source), ("offline", "offline"))
        self.assertTrue(self.client.disabled)
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(errors, ["slot test-1 attempt 1: HTTP 429 Google error: Quota exceeded per day"])
        fallback.assert_called_once()

    def test_per_minute_429_retries_with_backoff(self):
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   side_effect=[http_error(429, "Quota exceeded per minute"), success_response()]):
            with patch("incubrix_engine.llm.time.sleep") as sleep:
                asset, source, errors, _ = self.recover()
        self.assertEqual((asset["hook"], source), ("ok", "gemini"))
        self.assertFalse(self.client.disabled)
        sleep.assert_called_once_with(1)
        self.assertEqual(len(errors), 1)

    def test_401_and_403_are_fatal_without_retry(self):
        for status in (401, 403):
            with self.subTest(status=status):
                with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
                    self.client = GeminiClient(self.cfg)
                with patch("incubrix_engine.llm.urllib.request.urlopen",
                           side_effect=http_error(status, "invalid credentials")) as urlopen:
                    asset, source, errors, _ = self.recover()
                self.assertEqual((asset["hook"], source), ("offline", "offline"))
                self.assertTrue(self.client.disabled)
                self.assertEqual(urlopen.call_count, 1)
                self.assertEqual(len(errors), 1)

    def test_timeout_retries_then_uses_offline_fallback(self):
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   side_effect=TimeoutError("timed out")) as urlopen:
            with patch("incubrix_engine.llm.time.sleep") as sleep:
                asset, source, errors, _ = self.recover()
        self.assertEqual((asset["hook"], source), ("offline", "offline"))
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])
        self.assertEqual(len(errors), 3)
        self.assertTrue(all("timed out" in message for message in errors))

    def test_malformed_response_json_is_transient_bad_shape(self):
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   return_value=FakeResponse(b"{not-json")):
            with self.assertRaises(LLMError) as raised:
                self.client.generate("prompt")
        self.assertEqual(str(raised.exception), "bad response shape")
        self.assertTrue(raised.exception.transient)
        self.assertFalse(raised.exception.fatal)

    def test_invalid_generated_json_is_transient_bad_shape(self):
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   return_value=success_response("not-json")):
            with self.assertRaises(LLMError) as raised:
                self.client.generate("prompt")
        self.assertEqual(str(raised.exception), "bad response shape")
        self.assertTrue(raised.exception.transient)

    def test_missing_key_is_fatal_and_uses_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            client = GeminiClient(self.cfg)
        with patch("incubrix_engine.llm.urllib.request.urlopen") as urlopen:
            asset, source, errors, fallback = self.recover(client)
        self.assertEqual((asset["hook"], source), ("offline", "offline"))
        self.assertFalse(client.available)
        self.assertTrue(client.disabled)
        self.assertEqual(urlopen.call_count, 0)
        self.assertIn("no API key in environment", errors[0])
        fallback.assert_called_once()

    def test_http_error_includes_google_detail_without_key(self):
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   side_effect=http_error(503, "  Google says   try again later  ")):
            with self.assertRaises(LLMError) as raised:
                self.client.generate("prompt")
        self.assertIn("Google says try again later", str(raised.exception))
        self.assertNotIn("test-key", str(raised.exception))

    def test_http_error_detail_is_collapsed_and_truncated_to_220_chars(self):
        detail = "  Google   " + "detail " * 60
        with patch("incubrix_engine.llm.urllib.request.urlopen",
                   side_effect=http_error(503, detail)):
            with self.assertRaises(LLMError) as raised:
                self.client.generate("prompt")
        message_detail = str(raised.exception).rsplit(": ", 1)[1]
        self.assertEqual(len(message_detail), 220)
        self.assertNotIn("  ", message_detail)

    def test_client_paces_requests_to_minimum_interval(self):
        self.client.min_interval = 6
        with patch("incubrix_engine.llm.time.monotonic", side_effect=[1, 1, 3, 3]):
            with patch("incubrix_engine.llm.time.sleep") as sleep:
                self.client._pace()
                self.client._pace()
        sleep.assert_called_once_with(4)


if __name__ == "__main__":
    unittest.main()
