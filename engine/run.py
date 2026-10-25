#!/usr/bin/env python3
"""IncuBrix content engine CLI.
  python run.py run --input content/input_1.txt          # one long input -> 12+ checked assets
  python run.py ingest --library content/library_30.json # run the authored 30-asset library through the same checks
Set GEMINI_API_KEY to use Gemini; without it the engine uses its offline generator."""
import argparse, json, shutil, sys
from incubrix_engine.pipeline import Engine
from incubrix_engine.llm import GeminiClient
from incubrix_engine.util import load_json, ROOT

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "ingest"):
        p = sub.add_parser(name); p.add_argument("--out", default="output"); p.add_argument("--simulate-failure", choices=["llm", "render"])
        if name == "run":
            p.add_argument("--input", required=True); p.add_argument("--profile", default="standard", choices=["standard", "week"])
        else:
            p.add_argument("--library", required=True)
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found. Install it and add it to PATH (see engine/README.md, Windows setup).")
        return 1
    cfg = load_json(ROOT / "config.json")
    client = GeminiClient(cfg, simulate_failure=(a.simulate_failure == "llm"))
    eng = Engine(a.out, client=client, simulate=a.simulate_failure)
    res = eng.run(a.input, a.profile) if a.cmd == "run" else eng.ingest(a.library)
    print(json.dumps(res, indent=2))
    return 0 if res["produced"] else 1

if __name__ == "__main__":
    sys.exit(main())
