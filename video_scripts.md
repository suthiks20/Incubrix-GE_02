# The two videos (you record them, unedited)

## (a) Product walkthrough, up to 5 minutes
Screen-record the real product. Speak in the first person. Show only what you saw working.
1. 0:00-0:30 Home page: idea box, the four templates, credits at the top (300).
2. 0:30-1:45 LinkedIn Content template: type the idea, choose single post, show the draft. Say the draft ran long and had unsourced numbers.
3. 1:45-2:30 Rewrite by chat (under 150 words, remove claims, end with a question). Show credits 283.
4. 2:30-4:00 Repurpose Video / Clips: upload a source of at least 2 minutes, show the 32-second 9:16 clip, then open the downloaded file and show black bars, no captions, quiet audio.
5. 4:00-4:40 New-user confusion: empty Content Hub, publishing page wording, reconnect banner, TikTok not available in your region.
6. 4:40-5:00 Summary. `engine/content/input_1.txt` is a ready script for the opening.

## (b) Technical demo, up to 8 minutes
Terminal in `engine/`. Commands in order:
1. `python run.py run --input content/input_1.txt --profile week --out demo` - show 20 assets, runtime and cost in the summary; open `demo/calendar.csv` and one video.
2. Same command again - show `new: 0, unchanged: 20`.
3. Edit one sentence in the input, run again - show `updated` count and that asset IDs did not change.
4. `python run.py run --input content/input_1.txt --profile week --out demo2 --simulate-failure render` - show the logged error, then run it again without the flag - show `recovered: 1`.
5. `python -m unittest discover -s tests` - show it passing.
6. If you have a Gemini key: `export GEMINI_API_KEY=...` and repeat step 1 with `--out demo3`; show tokens in `logs/run_summary.jsonl`.
Say one decision you would change (for example: the offline generator reuses input sentences; with more time you would add a second source input).
