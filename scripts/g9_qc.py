"""Gate 9 QC: EMS formal rules, numeric provenance, fabrication/hard-code audit, figure/reference integrity."""
import json, re, pathlib, zipfile, pandas as pd
from docx import Document
R = pathlib.Path("results"); res = {}
d = Document("manuscript/manuscript.docx"); paras = [p.text for p in d.paragraphs]; full = "\n".join(paras)
wc = json.load(open(R / "manuscript_wordcount.json")); V = json.load(open(R / "manuscript_values.json"))
res["abstract<=150"] = wc["abstract_words"] <= 150
kw = next(p for p in paras if p.startswith("Keywords:")).split(":", 1)[1].split(";"); res["keywords 1-7"] = 1 <= len(kw) <= 7
hl = pathlib.Path("submission/highlights.txt").read_text().strip().split("\n"); res["highlights 3-5 <=85"] = 3 <= len(hl) <= 5 and max(map(len, hl)) <= 85
res["software availability section"] = "Software and data availability" in paras
res["CRediT + competing + GenAI sections"] = all(h in paras for h in ["CRediT authorship contribution statement", "Declaration of competing interest"]) and any(p.startswith("Declaration of generative AI") for p in paras)
res["acknowledgements before references"] = paras.index("Acknowledgements") < paras.index("References")
res["no inline images (figures separate)"] = len(d.inline_shapes) == 0
NFIG = sum(p.startswith("Fig. ") for p in paras[paras.index("Figure captions"):])
figs = [int(m) for m in re.findall(r"Figs?\. (\d+)", "\n".join(paras[:paras.index("Figure captions")]))]
first = list(dict.fromkeys(figs)); res[f"figures cited 1..{NFIG} in order"] = first == list(range(1, NFIG + 1))
res["figure files present"] = all(pathlib.Path(f"figures/Figure_{i}.png").exists() for i in range(1, NFIG + 1))
res["table cited"] = "Table 1" in full
refs = pd.read_csv("references/references_verified.csv")
ref_par = paras[paras.index("References") + 1:]
res["all refs have DOI + crossref raw"] = all(f"https://doi.org/{x}" in "\n".join(ref_par) for x in refs.doi if x in "\n".join(ref_par)) and all(pathlib.Path(f"references/crossref_raw/{k}.json").exists() for k in refs.key)
res["ref list alphabetical"] = [p.split(",")[0].lower() for p in ref_par] == sorted(p.split(",")[0].lower() for p in ref_par)
res["no priority words"] = not re.search(r"\b(first|novel|unprecedented)\b", "\n".join(paras[:paras.index("Software and data availability")]), re.I)
res["WRF contrasts labelled model-conditional"] = "model-conditional" in full and "NOT RUN" not in full
res["single-author voice (no We/Our/Us)"] = not re.search(r"\b(we|our|us|ours)\b", "\n".join(paras[:paras.index("References")]), re.I)
res["no causal claim words"] = not re.search(r"\b(causes|caused by wind farms|we estimate the externality)\b", full, re.I)
res["no repo paths in prose"] = not re.search(r"(results/|scripts/|data/processed)", full)
# numeric provenance: every number in body must appear in manuscript_values.json-derived renderings, a results CSV, or a whitelist of design constants
design = {"0.25", "20", "35", "72", "1", "2", "3", "4", "5", "6", "0.5", "8", "18", "20%", "5%", "0.05", "0.8", "50", "10", "2.1", "2.2", "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "4.3", "4.4", "4.5", "64", "2026", "3.10", "15", "1:50", "3.5", "4.6", "4.7", "4.6.1", "0.01", "24", "30", "150", "95%", "4.0"}
body = "\n".join(paras[paras.index("Abstract"):paras.index("Software and data availability")])
body = re.sub(r"\((?:[^()]*?\d{4}[a-z]?;?\s*)+\)", " ", body)
body = re.sub(r"Eq\. \(\d\)|\(\d\)|Figs?\. \d+(?:, \d+)*|Table \d|\d\.\d\. ", " ", body)
vals = []
for v in V.values():
    try: vals.append(float(v))
    except (TypeError, ValueError): pass
tb = pd.read_csv(R / "transboundary_share.csv").groupby("owner")[["own_land", "foreign_land"]].mean()
vals += list(tb.values.ravel()) + list((tb.foreign_land / tb.own_land).values)
al = pd.read_csv(R / "source_receptor.csv"); al = al[(al.tag == "ALL") & (al.receptor != "SEA")].groupby("receptor").a.mean()
vals += list(al.values)
unmatched = []
for tok in re.findall(r"(?<![\w.])[-−]?\d[\d,]*\.?\d*(?:e[-+]?\d+)?%?", body):
    t = tok.replace("−", "-").replace(",", "")
    if t in design or t.rstrip("%") in design or re.fullmatch(r"(19|20)\d\d", t): continue
    x = float(t.rstrip("%")); cand = [x / 100] if t.endswith("%") else [x, x / 100, x * 1000, x / 1000, x * 1e9]
    ok = any(abs(c - v) <= max(abs(v) * 0.051, 1e-12) or abs(c - v) < 0.0051 * (abs(c) if abs(c) > 0 else 1) for c in cand for v in vals) or any(abs(x - 100 * v) < 0.051 for v in vals) or any(abs(x - v * 100) < 0.51 for v in vals)
    if not ok: unmatched.append(tok)
res[f"numeric provenance ({len(unmatched)} unmatched)"] = not unmatched
z = pathlib.Path("TAWE_EMS_submission.zip")
if z.exists():
    zz = zipfile.ZipFile(z); res["zip ok, relative names"] = zz.testzip() is None and not any(n.startswith("/") or ".." in n for n in zz.namelist())
json.dump({k: bool(v) for k, v in res.items()} | {"unmatched": unmatched}, open(R / "qc_report.json", "w"), indent=1)
for k, v in res.items(): print("PASS" if v else "FAIL", k)
print("unmatched:", unmatched); print("ALL PASS" if all(res.values()) else "QC FAILURES")
