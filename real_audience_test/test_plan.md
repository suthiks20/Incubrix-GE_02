# Real-audience test: preference test (20+ people)

**What it is.** 8 pairs of hooks. In each pair, one is from the 30-asset library and one is a plain baseline. Each person picks the one they would stop to read, and says why in a few words.

**Who.** At least 20 people who make or edit content (podcasters, YouTubers, expert-led creators, editors, small content teams). Ask people you already know through normal channels. Do not offer anything in return for a particular answer, do not contact brands or creators you do not know, and do not collect names or emails (answers are anonymous).

**How (about 3 minutes per person).**
1. Make a free Google Form. Add one multiple-choice question per row of `pairs.csv` (options A / B, in the order shown), plus a short "who are you" question (podcaster / YouTuber / expert creator / editor or team / other) and one optional text box.
2. Send the link. Keep it open until you have 20 or more answers.
3. Download the responses as CSV and save it as `results.csv` next to `analyze_results.py`. Columns: `respondent_role`, `p01` ... `p08` where each answer is `A` or `B`.
4. Run: `python analyze_results.py` - it prints how often the library hook beat the baseline, per pair and overall, with n.

**Report honestly.** State n, who answered, how you found them, and the result even if the baseline wins some pairs. A result is only "beating a benchmark" if you can name a sourced benchmark; a 20-person preference test does not claim reach or engagement.

**Not done yet.** This file is the plan and the tooling. No responses have been collected, so the workbook marks this minimum as NOT MET until you have run it.
