"""Reads results.csv (respondent_role, p01..p08 with A/B) and pairs_KEY.csv; prints preference for the library hook."""
import csv
from collections import Counter
key = {r["pair"]: r for r in csv.DictReader(open("pairs_KEY.csv", encoding="utf-8"))}
rows = list(csv.DictReader(open("results.csv", encoding="utf-8")))
n = len(rows); print(f"respondents: {n}  (minimum 20)")
print("roles:", dict(Counter(r["respondent_role"] for r in rows)))
tot_w = tot = 0
for p, k in key.items():
    votes = [r[p].strip().upper() for r in rows if r.get(p, "").strip().upper() in ("A", "B")]
    w = sum(v == k["library_option"] for v in votes); tot_w += w; tot += len(votes)
    print(f"{p} {k['library_asset']}: library hook chosen {w}/{len(votes)} = {100*w/len(votes):.0f}%" if votes else f"{p}: no votes")
print(f"overall: library hook chosen {tot_w}/{tot} = {100*tot_w/tot:.0f}%" if tot else "no votes")
if n < 20: print("WARNING: fewer than 20 respondents, the minimum is NOT met.")
