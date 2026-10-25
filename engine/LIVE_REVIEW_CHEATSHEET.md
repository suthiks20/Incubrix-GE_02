# Live review cheatsheet

## Trace an asset to its verified facts

1. Find the asset ID in the relevant `calendar.csv` row.
2. Open its editable source file, for example `main_output/assets/A01/A01_source.json`.
3. Read the `facts_used` list. Each ID maps directly to `facts.<ID>` in `engine/brand.json`; check the fact text and evidence field there.
4. An empty `facts_used` list means the asset does not cite a product fact. Do not infer a fact from the copy alone.

## Run the engine on a new input

Put the new source file in `engine/content/` (or use its actual path), then run this from the `engine` directory:

```bat
python run.py run --input content\new_input.txt --out gtest_new_input
```

With no Gemini key, the offline extractive generator is used. The engine regenerates the output calendar from stored rendered assets after each run.

## Logs and rejected assets

- Run summary and run-level errors: `<output>\logs\run_summary.jsonl` and `<output>\logs\engine.log` (for example, `gtest_offline\logs\...`).
- Rejected items: `<output>\rejected.jsonl`.
- Rendered files and source JSON: `<output>\assets\<asset ID>\`.

Each summary line includes its run ID, input name, produced/rejected counts, runtime in seconds, tokens, estimated cost, source counts and error lines.

## Dedupe and refresh behavior

The engine compares four-word shingles from each asset's hook plus caption. Similarity at or above `dedupe_similarity` (currently `0.80`) rejects a duplicate against existing accepted content and other assets in the current run. An unchanged input hash and slot reuses the existing asset without generating a duplicate. Editing an input refreshes the matching slots in place; a distinct input is also checked against previously stored assets.

## Cost and runtime

The summary file reports `runtime_seconds`, `tokens_in`, `tokens_out` and `estimated_cost_usd`. Cost is estimated from the token counts and `cost_per_1k_tokens_usd` rates in `engine/config.json`; with the current zero rates, that estimate is `$0.0000`, not a claim about a paid API plan. Offline runs report zero Gemini tokens and a source count of `offline`.
