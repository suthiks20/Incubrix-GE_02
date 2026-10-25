import json, unittest
from pathlib import Path
from incubrix_engine.checks import check_asset, words
ROOT = Path(__file__).resolve().parent.parent
BRAND = json.load(open(ROOT / "brand.json"))

def good():
    return {"platform": "LinkedIn", "format": "Text post", "hook": "Black bars waste a vertical clip.",
            "caption": "Black bars waste a vertical clip. Reframe it first.", "cta": "Do you reframe?",
            "hashtags": ["#ContentCreation", "#ShortFormVideo"], "facts_used": [], "rights": "generated",
            "utm_link": "https://incubrix.com/?utm_source=linkedin&utm_medium=social&utm_campaign=c&utm_content=A01"}

class Checks(unittest.TestCase):
    def test_good_passes(self): self.assertEqual(check_asset(good(), BRAND), [])
    def test_unsourced_number_fails(self):
        a = good(); a["caption"] += " Creators lose 4-7 hours a week."
        self.assertTrue(any("numbers with no source" in f for f in check_asset(a, BRAND)))
    def test_number_in_source_passes(self):
        a = good(); a["caption"] += " It took 41 minutes."
        self.assertEqual(check_asset(a, BRAND, source_text="It took 41 minutes."), [])
    def test_banned_phrase_fails(self):
        a = good(); a["caption"] += " A total game-changer."
        self.assertTrue(any("banned" in f for f in check_asset(a, BRAND)))
    def test_product_claim_needs_fact(self):
        a = good(); a["caption"] += " IncuBrix adds captions for you."
        self.assertTrue(any("fact id" in f for f in check_asset(a, BRAND)))
    def test_missing_utm_and_hashtags(self):
        a = good(); a["utm_link"] = "https://incubrix.com/"; a["hashtags"] = []
        f = check_asset(a, BRAND); self.assertTrue(any("UTM" in x for x in f) and any("hashtags" in x for x in f))
    def test_long_post_fails(self):
        a = good(); a["caption"] = "word " * 160
        self.assertTrue(any("max 150" in f for f in check_asset(a, BRAND)))
    def test_rights(self):
        a = good(); a["rights"] = "stock"
        self.assertTrue(any("rights" in f for f in check_asset(a, BRAND)))
    def test_video_too_long(self):
        a = good(); a.update(format="Short video", platform="YouTube Shorts", hashtags=["#Shorts", "#ContentCreation"],
                             beats=["one two"] * 6, beat_seconds=[11] * 6, utm_link=a["utm_link"])
        self.assertTrue(any("over 60" in f for f in check_asset(a, BRAND)))
    def test_words(self): self.assertEqual(words("one two three"), 3)

if __name__ == "__main__": unittest.main()
