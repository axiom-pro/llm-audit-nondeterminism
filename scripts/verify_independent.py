#!/usr/bin/env python3
"""独立検証: aggregate.py を import せず、生fixturesから素朴に再計算して m2_summary.json と照合。"""
import json, os, csv, itertools, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, "fixtures", "audit_logs.jsonl")
SUM = os.path.join(ROOT, "results", "m2_summary.json")
GTF = os.path.join(ROOT, "results", "gt.csv")

cells = collections.defaultdict(list); prov = {}
for l in open(FIX, encoding="utf-8"):
    l = l.strip()
    if not l: continue
    try: r = json.loads(l)
    except: continue
    if r.get("type") == "run": cells[r["cell"]].append(r)
    elif r.get("type") == "provenance": prov[r["cell"]] = r

def keyset(run):
    s = set()
    if run.get("schema_valid") and run.get("issues"):
        for it in run["issues"]:
            ln = it.get("line_number")
            if ln is None: continue
            s.add((int(ln), str(it.get("category","")).strip()))
    return s

def strict_jac(runs):
    ks = [keyset(r) for r in runs]
    ps = list(itertools.combinations(range(len(ks)), 2))
    vals = []
    for i, j in ps:
        u = ks[i] | ks[j]
        vals.append(len(ks[i] & ks[j]) / len(u) if u else 1.0)
    return sum(vals)/len(vals)

gts = collections.defaultdict(list)
for row in csv.DictReader(open(GTF, encoding="utf-8")):
    gts[row["target"]].append((row["gt_id"], int(row["line_lo"]), int(row["line_hi"])))

summ = json.load(open(SUM, encoding="utf-8"))

def check(name, got, exp, tol=0.005):
    ok = (exp is not None) and abs(got - exp) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: independent={got:.4f} summary={exp}")
    return ok

allok = True
# 1) strict Jaccard 数セル
for cell in ["d_7b_a", "d_15b_a", "d_7b_easy", "d_7b_decoy"]:
    got = strict_jac(cells[cell]); exp = summ[cell]["jaccard"]["strict"]
    allok &= check(f"{cell} strict Jaccard", got, exp)

# 2) d_7b_decoy 多数決 survivors at w=0, k>=N//2+1  -> FP
runs = cells["d_7b_decoy"]; N = len(runs); k = N//2+1
freq = collections.Counter()
for r in runs:
    for key in keyset(r): freq[key] += 1
surv = [key for key, v in freq.items() if v >= k]
fp_indep = len(surv)  # decoy: no gt -> all survivors are FP
fp_sum = summ["d_7b_decoy"]["surface"]["0"][k-1]["FP"]
ok = fp_indep == fp_sum
print(f"  [{'PASS' if ok else 'FAIL'}] d_7b_decoy majority FP(w0,k>={k}): independent={fp_indep} {surv} summary={fp_sum}")
allok &= ok

# 3) d_15b_a recall_line_only (category不問・行のみ, val_w=2, per-run平均)
def recall_lineonly(cell, tgt, w=2):
    g = gts[tgt]; tot = len(g); vals = []
    for r in cells[cell]:
        cov = set()
        for (ln, c) in keyset(r):
            for gid, lo, hi in g:
                if lo - w <= ln <= hi + w:
                    cov.add(gid); break   # first-match（aggregate.match_finding_gt_line と同一規約・窓重複時の多重計上を回避）
        vals.append(len(cov)/tot)
    return sum(vals)/len(vals)
got = recall_lineonly("d_15b_a", "target_a.py"); exp = summ["d_15b_a"]["recall_line_only"]
allok &= check("d_15b_a recall_line_only", got, exp)

# 4) temp0 baselines strict Jaccard == 1.0
for cell in ["a_15b_a", "a_7b_a", "a_15b_easy", "a_7b_easy"]:
    got = strict_jac(cells[cell]); exp = summ[cell]["jaccard"]["strict"]
    allok &= check(f"{cell} strict Jaccard(=1?)", got, exp)

print("\nRESULT:", "ALL PASS" if allok else "MISMATCH FOUND")
import sys; sys.exit(0 if allok else 1)
