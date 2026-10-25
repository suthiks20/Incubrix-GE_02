# IncuBrix social growth launch kit

Prepared 24 Oct 2026. Start: **Monday 26 Oct 2026**. Everything below uses files in this submission; the 30 assets are in `main_output/` and `calendar.csv` is the single source of truth for the plan.

## 1. Who we target first
Creators (podcasters, YouTubers, expert-led creators) and the editors or small teams who help them, mainly in the US, Canada, UK, Ireland, Australia, New Zealand and Singapore. First focus: small expert-led creator teams who rework one video for several platforms.

## 2. Platforms and why
- **LinkedIn**: the only IncuBrix account with real traction (1.2K followers) and where small content teams read.
- **Instagram Reels**: vertical video, with an existing base of 69 followers to build on.
- **YouTube Shorts**: reaches creators directly and has no region problem for publishing.
- **Not used: TikTok.** It was unavailable in the tester's region on 24 Oct 2026 (recorded in the workbook).

## 3. Five content pillars
1. The reformatting problem and how to fix it (before and after).
2. The product in action (only features seen working).
3. Hooks and captions (practical tips).
4. Idea-to-published workflow breakdowns.
5. Honest tests (what worked, what broke, what it cost).

## 4. Brand voice rules
Calm, practical, first person. Put the answer in the first line. No hype and no numbers without a source. Claim only what was seen working in the product (the verified list is `engine/brand.json`, facts F1-F8). End with a question when it fits. Videos and graphics carry the line "Independent creator test. Not an official IncuBrix account." when posted from a personal test account; remove it when IncuBrix posts from its own account.

## 5. Posting frequency
Per week: LinkedIn 3-4, Instagram 2-3, YouTube Shorts 1-2. The 30 ready assets cover the first 3.5 weeks (26 Oct to 19 Nov); the engine refills the calendar from one new long input each week. Slot times are a starting hypothesis in UTC (LinkedIn 13:00, Instagram 17:00, Shorts 16:00) to be adjusted from week-2 data.

## 6. How posts turn into sign-ups
Every asset has a UTM link to incubrix.com: `utm_source` (linkedin, instagram, youtube), `utm_medium=social`, `utm_campaign=growth_engine_2026q4`, `utm_content` = asset ID. LinkedIn: link in the first comment. Instagram: link in bio. Shorts: link in the description. Sign-ups are counted per source and per asset ID, so we can see which post earned them.

## 7. Weekly plan, step by step
**Before Monday (30 min, owner: Growth Engineer):** confirm access to the three accounts; upload `scheduler.csv` and the files in `main_output/assets/` to the scheduler (or schedule natively); create the metrics sheet (columns: asset ID, impressions or views, reactions, comments, shares, clicks, sign-ups).
**Week 1 (26 Oct to 1 Nov):** publish C01, V02, C02, V01, C03, V04, C04, V06, V03. Reply to every comment within 24 hours.
**Weeks 2-4:** same rhythm. Friday each week: feed one long input to the engine (`python run.py run --input <file>`), read `rejected.jsonl`, approve new assets into the calendar.
**Day 14 review:** keep the formats with the highest engagement rate and clicks; drop the lowest two.
**Week 3:** optional creator-collaboration format, only with written consent from the creator.
**Week 4:** report reach, engagement rate, clicks and sign-ups against the targets below.

## 8. Daily workflow (about 20 minutes)
1. Check today's scheduled posts went out (2 min).
2. Reply to comments and questions (10 min).
3. Log yesterday's numbers in the metrics sheet (5 min).
4. Note any claim someone challenges and check it against `brand.json` (3 min).

## 9. Owners
| Task | Owner |
|---|---|
| Scheduling, comments, metrics | Growth Engineer |
| Approve product claims and new facts | IncuBrix product owner |
| Weekly engine run and review | Growth Engineer |
| Access to accounts, analytics, budget | IncuBrix |

## 10. Tools and monthly cost
Python, Pillow and ffmpeg (free); Gemini free tier is optional (without a key the engine uses its offline generator); any scheduler that takes `scheduler.csv`, or native scheduling; a spreadsheet for metrics. **Base cost: $0 per month.**
**Optional paid boost (a proposal, not required):** up to $150 in total on the two best organic LinkedIn posts after the day-14 review, tracked with the same UTM links.

## 11. Targets after 30 days
These are starting targets, not forecasts, and no sourced benchmark is claimed. Review at day 14.
| Metric | Target |
|---|---|
| Posts published | LinkedIn 14, Instagram 11, YouTube Shorts 5 |
| Reach (impressions or views, all platforms) | 25,000 |
| Engagement rate (reactions + comments + shares / impressions) | 3% |
| Tracked clicks to incubrix.com | 150 |
| Sign-ups from social | 8 |

## 12. Risks and how to handle them
- **Product output is not publish-ready.** The test clip had about 70% black bars, no captions and quiet audio, so these videos are generated text videos, not raw product clips. Never post a product clip without checking bars, captions and audio.
- **Claims drift.** Only facts F1-F8 in `brand.json` may be claimed. Add a fact only after seeing it work and saving evidence.
- **Gemini free-tier limit.** The free tier allows 20 requests per day per model. The engine stops using Gemini after a daily-quota error and falls back to the offline generator, so a run never fails. For weekly runs of 20 or more assets, use a paid key or the offline generator.
- **Low Instagram base (69).** Expect slow early reach; judge Instagram on engagement rate and clicks, not follower count.
- **Rights.** All media is generated from text with free fonts; no music is used. Add licensed audio inside the platform app only.
- **Platform and privacy rules.** Post only from accounts IncuBrix owns; do not buy engagement; follow each platform's rules and the DPDP Act, GDPR and CAN-SPAM when collecting sign-ups.

## 13. What IncuBrix must provide
Owned accounts and posting access, analytics or sign-up source reporting so `utm_source` and `utm_content` can be matched to sign-ups, approval of the verified product facts, source videos of 2+ minutes with consent, and a yes or no on the optional boost.

## 14. The 30-day calendar (first 30 assets)
| Date (UTC) | Platform | ID | Format | Hook |
|---|---|---|---|---|
| 2026-10-26 13:00 | LinkedIn | C01 | Carousel | Stop pasting one graphic on every platform |
| 2026-10-27 17:00 | Instagram | V02 | Short video | I asked for under 150 words. I got 175. |
| 2026-10-28 13:00 | LinkedIn | C02 | Carousel | Five hook patterns that work for creators |
| 2026-10-28 16:00 | YouTube Shorts | V01 | Short video | One video, three platforms, three shapes |
| 2026-10-29 13:00 | LinkedIn | C03 | Carousel | My idea-to-published workflow |
| 2026-10-29 17:00 | Instagram | V04 | Short video | Your first line is the whole post |
| 2026-10-30 13:00 | LinkedIn | C04 | Carousel | Honest notes from my first session in IncuBrix |
| 2026-10-31 17:00 | Instagram | V06 | Short video | My idea-to-post routine, in five steps |
| 2026-11-01 16:00 | YouTube Shorts | V03 | Short video | My clip came out with black bars on most of the frame |
| 2026-11-02 13:00 | LinkedIn | T01 | Text post | Posting one video everywhere is not the same as posting well. |
| 2026-11-03 17:00 | Instagram | V08 | Short video | I edited a draft by talking to it |
| 2026-11-04 13:00 | LinkedIn | T02 | Text post | My first draft from an AI template ran long and cited numbers I could not source. |
| 2026-11-04 16:00 | YouTube Shorts | V05 | Short video | Add captions. It costs nothing. |
| 2026-11-05 13:00 | LinkedIn | T03 | Text post | The first line decides whether anyone reads the second. |
| 2026-11-05 17:00 | Instagram | V10 | Short video | One idea. Three shapes. |
| 2026-11-06 13:00 | LinkedIn | T04 | Text post | I keep one routine for every idea: draft, edit, format, schedule. |
| 2026-11-07 17:00 | Instagram | C05 | Carousel | A caption checklist before you post |
| 2026-11-08 16:00 | YouTube Shorts | V07 | Short video | Resizing is not repurposing |
| 2026-11-09 13:00 | LinkedIn | T05 | Text post | A clip finder found my moment but I would not post the file. |
| 2026-11-10 17:00 | Instagram | G01 | Graphic | Resized is not reformatted |
| 2026-11-11 13:00 | LinkedIn | T06 | Text post | Captions are the cheapest fix for a vertical video. |
| 2026-11-11 16:00 | YouTube Shorts | V09 | Short video | What 17 credits bought me |
| 2026-11-12 13:00 | LinkedIn | T07 | Text post | Editing a draft by chat is the part of IncuBrix I would use again. |
| 2026-11-12 17:00 | Instagram | G02 | Graphic | Answer first. Warm-up never. |
| 2026-11-13 13:00 | LinkedIn | T08 | Text post | Resizing a video is not the same as reframing it. |
| 2026-11-14 17:00 | Instagram | G03 | Graphic | Check before you post: bars, captions, audio |
| 2026-11-16 13:00 | LinkedIn | T09 | Text post | Know what each step costs before you plan a month of posts. |
| 2026-11-17 17:00 | Instagram | G04 | Graphic | Idea, draft, edit, format, schedule |
| 2026-11-18 13:00 | LinkedIn | T10 | Text post | Turn one idea into three formats instead of three ideas. |
| 2026-11-19 17:00 | Instagram | G05 | Graphic | Edit by instruction, not by hand |
