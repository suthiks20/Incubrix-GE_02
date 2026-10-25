# IncuBrix content engine (Option 2)

Turns a source input into platform-native LinkedIn, Instagram and YouTube Shorts assets. The engine checks each asset, de-duplicates it, renders generated media and exports `calendar.csv` and `scheduler.csv`.

## Windows setup and run

Open Command Prompt in the `engine` folder:

```bat
py -m pip install pillow
python run.py run --input content\input_1.txt --out output
```

Install FFmpeg for Windows from [ffmpeg.org](https://ffmpeg.org/download.html), then add the folder containing `ffmpeg.exe` to `PATH`. For a temporary Command Prompt session, for example:

```bat
set PATH=C:\ffmpeg\bin;%PATH%
```

Run `ffmpeg -version`; it should print a version.

Gemini is optional. Set a key in Command Prompt before running if you want to try the live API:

```bat
set GEMINI_API_KEY=your_key
```

The key is read only from the environment variable named by `api_key_env` in `config.json`; it is not stored in the repository. `model` remains configurable there. If quota is exhausted, `gemini-2.5-flash-lite` is a lighter model alternative to try, subject to your account's model access and quota.

Without a key, or when Gemini fails, the engine uses an extractive offline generator that reuses sentences from the input and applies the same checks. It does not make live API calls or imply Gemini was tested.

## Outputs and troubleshooting

The output directory contains `calendar.csv`, scheduler-ready `scheduler.csv`, rendered assets and editable source JSON under `assets/`, logs under `logs/`, and `rejected.jsonl`. `logs/run_summary.jsonl` records counts, source, runtime, tokens, estimated cost and generation errors.

On HTTP 429, read the Google detail and wait if the quota is temporary; a daily quota error switches Gemini off for the rest of the run. You can also change `model` in `config.json` to a model available to your account. The offline fallback keeps the run going.

Run the 30-asset authored library through the same checks:

```bat
python run.py ingest --library content\library_30.json --out ..\main_output
```

Run the tests from the `engine` folder:

```bat
python -m unittest discover -s tests
```

## How it works

1. A profile in `config.json` plans formats and slots.
2. Gemini is attempted with bounded retries and backoff; errors are logged and generation falls back offline.
3. `incubrix_engine/checks.py` validates content, factual claims, links and format requirements. Rejected items are written to `rejected.jsonl`.
4. Four-word shingle similarity at or above `dedupe_similarity` in `config.json` rejects duplicates. Re-running the same input skips unchanged assets; edited inputs refresh matching slots.
5. SQLite stores assets and run history; exports are regenerated from rendered assets.

## Honest limits

- Gemini was run live on 25 Oct 2026 with gemini-3.8-flash: 8 assets, 9,610 tokens in, 3,624 out, with automatic recovery from one timeout and two 503s. The free tier allows 20 requests per day per model, so later runs hit HTTP 429 (PerDay quota); the engine now detects that on the first call, switches Gemini off for the run and falls back to offline generation. gemini-2.5-flash is retired for new keys (HTTP 404), so the default model is gemini-3.8-flash. A full 12-slot run needs about 12 requests, so one live run per day fits the free tier.
- Offline output is extractive and less varied than LLM output.
- Product facts allowed by the engine are limited to F1-F8 in `brand.json`.
- Scheduled slot times are a starting hypothesis, not a measured best time.
- Gemini outcome: worked once on 25 Oct 2026 (8 assets, tokens_in=9610, tokens_out=3624); free daily quota exhausted afterwards, offline fallback used.

Evidence: [Gemini live run](../evidence/run_logs/gemini_live_run_25Oct.txt) · [429 quota response](../evidence/run_logs/gemini_429_quota_25Oct.txt)

## AI and manual work disclosure

Claude (Anthropic) wrote the engine code, the copy in `content/library_30.json`, and drafted the launch kit. Product testing, screenshots, account audit and decisions are the candidate's manual work.
