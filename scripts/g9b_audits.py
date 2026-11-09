"""Gate 9 audits: numeric provenance ledger, hard-code mutation tests, references, figures/tables, Word OMML, document integrity.
Writes docs/revision/{NUMERIC_PROVENANCE.csv, NUMERIC_CONSISTENCY_AUDIT.md, HARDCODE_AUDIT.md, REFERENCE_AUDIT.md,
FIGURE_TABLE_AUDIT.md, WORD_OMML_AUDIT.md, DOCUMENT_INTEGRITY_AUDIT.md}. Mutation tests edit tracked canonical results in place,
rebuild, and restore them with `git checkout`; run only on a clean tree."""
import json, re, pathlib, subprocess, zipfile, hashlib, sys, numpy as np, pandas as pd
from docx import Document
PY = sys.executable; D = pathlib.Path("docs/revision"); R = pathlib.Path("results")
sh = lambda *a: subprocess.run(a, check=True, capture_output=True, text=True).stdout
def build(): [sh(PY, f"scripts/{s}.py") for s in ("g8_build_manuscript", "g8_package")]
def texts():
    d = Document("manuscript/manuscript.docx"); P = [p.text for p in d.paragraphs]
    cap = P[P.index("Figure captions") + 1:P.index("References")]
    tab = "\n".join(c.text for t in d.tables for row in t.rows for c in row.cells)
    return {"abstract": P[P.index("Abstract") + 1], "results": "\n".join(P[P.index("4. Results"):P.index("5. Discussion")]),
            "discussion": "\n".join(P[P.index("5. Discussion"):P.index("6. Conclusions")]),
            "conclusions": "\n".join(P[P.index("6. Conclusions"):P.index("Software and data availability")]),
            "captions": "\n".join(cap), "tables": tab, "highlights": pathlib.Path("submission/highlights.txt").read_text(),
            "cover_letter": pathlib.Path("submission/cover_letter.md").read_text()}
assert sh("git", "status", "--porcelain", "results").strip() == "", "results/ must be clean for mutation tests"
V = json.load(open(R / "manuscript_values.json")); T0 = texts()

# 1. numeric provenance ledger
rows = []
num = lambda v: float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None
VN = {k: num(v) for k, v in V.items() if num(v) is not None}
for loc, s in T0.items():
    s2 = re.sub(r"\((?:[^()]*?\d{4}[a-z]?;?\s*)+\)|Figs?\. \d+(?:, \d+)*|Table \d|Eq\. \(\d\)|\b(19|20)\d\d\b|\b\d\.\d\. ", " ", s)
    for tok in re.findall(r"(?<![\w.])[-−]?\d[\d,]*\.?\d*(?:e[-+]?\d+)?%?", s2):
        t = tok.replace("−", "-").replace(",", ""); x = float(t.rstrip("%"))
        cand = [x / 100] if t.endswith("%") else [x, x / 100, x * 1000, x / 1000, x * 1e9]
        hit = [k for k, v in VN.items() if any(abs(c - v) <= max(abs(v) * 0.051, 1e-12) for c in cand) or abs(x - 100 * v) < 0.51]
        rows.append(dict(location=loc, token=tok, matched_keys=";".join(hit[:5]), n_matches=len(hit),
                         status="canonical" if hit else "design-constant-or-unmatched"))
prov = pd.DataFrame(rows); prov.to_csv(D / "NUMERIC_PROVENANCE.csv", index=False)
qc = json.load(open(R / "qc_report.json"))

# 2. mutation tests: change a canonical result, rebuild, require the rendering to change everywhere it appears
muts = []
def mutate(name, path, edit, expect):
    orig = pathlib.Path(path).read_text(); pathlib.Path(path).write_text(edit(orig))
    try:
        build(); T = texts()
        for loc, (old, new) in expect.items():
            muts.append(dict(test=name, location=loc, before_present=old in T0[loc], after_old_absent=old not in T[loc], after_new_present=new in T[loc]))
    finally:
        sh("git", "checkout", "--", path)
pj = "results/wrf/programme_summary.json"
def m1(s):
    j = json.loads(s); j["pooled"]["n_outside"] = j["pooled"]["n_outside"] + 2; return json.dumps(j, indent=1)
K, N = V["w_K"], V["w_N"]
mutate("WRF pooled flags +2", pj, m1, {"results": (f"{N} country–event contrasts, {K} lay", f"{N} country–event contrasts, {K+2} lay"),
                                       "cover_letter": (f"{K} of {N} country", f"{K+2} of {N} country")})
def m2(s):
    df = pd.read_csv(pathlib.Path("results/placebo_test.csv")); df.loc[df.index[0], "real_inside_placebo_range"] = False
    return df.to_csv(index=False)
pn, pi = V["pl_n"], V["pl_inside"]
mutate("placebo inside −1", "results/placebo_test.csv", m2,
       {"abstract": (f"{pi} of {pn}", f"{pi-1} of {pn}"), "highlights": (f"{pi} of {pn}", f"{pi-1} of {pn}"),
        "results": (f"{pi} of {pn}", f"{pi-1} of {pn}"), "conclusions": (f"{pi} of {pn}", f"{pi-1} of {pn}")})
def m3(s):
    kt = pd.read_csv(pathlib.Path("results/known_truth.csv"))
    i = kt[((kt.delta_k != 0) | (kt.delta_u != 0)) & (kt.receptor == "C2") & (np.sign(kt.truth_kg) == np.sign(kt.supply_kg))].index[0]
    kt.loc[i, "truth_kg"] *= -1; return kt.to_csv(index=False)
f2, n2 = V["kt_flip_c2"], V["kt_n_c2"]
mutate("known-truth far-receptor reversal +1", "results/known_truth.csv", m3, {"abstract": (f"{f2} of {n2}", f"{f2+1} of {n2}")})
tb0 = pd.read_csv("results/transboundary_share.csv").groupby("owner").own_land.mean(); o0 = tb0.index[0]
def m4(s):
    t = pd.read_csv(pathlib.Path("results/transboundary_share.csv")); t.loc[t.owner == o0, "own_land"] *= 2; return t.to_csv(index=False)
mutate(f"Table 1 own-land share x2 ({o0})", "results/transboundary_share.csv", m4, {"tables": (f"{tb0[o0]:.4f}", f"{2*tb0[o0]:.4f}")})
build()
M = pd.DataFrame(muts); mut_ok = bool((M.before_present & M.after_old_absent & M.after_new_present).all())

# 3. references
d = Document("manuscript/manuscript.docx"); P = [p.text for p in d.paragraphs]
body = "\n".join(P[:P.index("References")]); refp = P[P.index("References") + 1:]
refs = pd.read_csv("references/references_verified.csv"); rr = []
for r in refs.itertuples():
    sur = r.authors.split(";")[0].split()[0].rstrip(","); m = json.load(open(f"references/crossref_raw/{r.key}.json"))["message"]
    in_list = any(f"https://doi.org/{r.doi}" in p for p in refp)
    cited = bool(re.search(rf"{re.escape(sur)}[^()]*?{r.year}", body))
    rr.append(dict(key=r.key, doi=r.doi, in_list=in_list, cited_in_text=cited, crossref_doi_match=m["DOI"].lower() == r.doi.lower(),
                   crossref_title_match=re.sub(r"\W", "", (m.get("title") or [""])[0].lower())[:40] == re.sub(r"\W", "", r.title.lower())[:40]))
RF = pd.DataFrame(rr); RF = RF[RF.in_list]
uncited_list = [p[:60] for p in refp if not any(f"https://doi.org/{x}" in p for x in refs.doi)]
ref_ok = bool(RF.cited_in_text.all() and RF.crossref_doi_match.all() and not uncited_list) and qc["ref list alphabetical"]

# 4. figures/tables
NF = sum(p.startswith("Fig. ") for p in P[P.index("Figure captions"):])
fr = []
from PIL import Image
for i in range(1, NF + 1):
    png, pdf = pathlib.Path(f"figures/Figure_{i}.png"), pathlib.Path(f"figures/Figure_{i}.pdf")
    w, h = Image.open(png).size
    fr.append(dict(figure=i, png=png.exists(), pdf=pdf.exists() and pdf.read_bytes()[:4] == b"%PDF", px=f"{w}x{h}",
                   cited=bool(re.search(rf"Figs?\. (?:\d+, )*{i}\b", body)), caption=any(p.startswith(f"Fig. {i}.") for p in P)))
FT = pd.DataFrame(fr); ft_ok = bool(FT[["png", "pdf", "cited", "caption"]].all().all()) and len(d.inline_shapes) == 0 and len(d.tables) >= 1

# 5. OMML
X = d.element.body; om = X.xpath(".//m:oMath"); omp = X.xpath(".//m:oMathPara")
imgs_eq = len(X.xpath(".//w:drawing")); om_ok = len(om) >= 1 and imgs_eq == 0
# 6. document integrity
di = {}
for f in ["manuscript/manuscript.docx", "submission/highlights.docx", "submission/cover_letter.docx", "TAWE_EMS_submission.zip", "TAWE_reproducibility.zip"]:
    z = zipfile.ZipFile(f); names = z.namelist()
    di[f] = dict(bytes=pathlib.Path(f).stat().st_size, sha256=hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(), zip_ok=z.testzip() is None,
                 comments="word/comments.xml" in names, tracked_changes=any(b"<w:ins " in z.read(n) or b"<w:del " in z.read(n) for n in names if n.startswith("word/document")))
sub = zipfile.ZipFile("TAWE_EMS_submission.zip").namelist()
di_ok = all(v["zip_ok"] and not v["comments"] and not v["tracked_changes"] for v in di.values()) and \
        sum(n.startswith("figures/Figure_") and n.endswith(".pdf") for n in sub) == NF and "manuscript.docx" in sub

tick = lambda b: "PASS" if b else "FAIL"; md = lambda df: "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)] + ["| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False)])
w = lambda n, s: (D / n).write_text(f"# {n[:-3].replace('_', ' ').title()}\n\nGenerated by `scripts/g9b_audits.py` from the built documents; do not edit by hand.\n\n" + s + "\n")
w("NUMERIC_CONSISTENCY_AUDIT.md", f"Status: **{tick(qc[[k for k in qc if k.startswith('numeric provenance')][0]])}** (g9_qc numeric provenance; unmatched: {qc['unmatched']}).\n\n"
  f"Ledger: `NUMERIC_PROVENANCE.csv` ({len(prov)} numeric tokens across {prov.location.nunique()} locations). Tokens with no canonical key are design constants "
  f"(grid spacing, years, section numbers, ensemble size, interval level) whitelisted in `scripts/g9_qc.py`.\n\n" + md(prov.groupby(["location", "status"]).size().rename("n").reset_index()))
w("HARDCODE_AUDIT.md", f"Status: **{tick(mut_ok)}**. Each test edits one canonical result file, rebuilds the manuscript, highlights and cover letter, "
  "and requires the old rendering to disappear and the mutated value to appear; the file is then restored with `git checkout` and the package rebuilt.\n\n" + md(M))
w("REFERENCE_AUDIT.md", f"Status: **{tick(ref_ok)}**. {len(RF)} listed references; all carry DOIs resolved against stored Crossref records "
  f"(`references/crossref_raw/`). Citation style is author–year (journal style), list alphabetical: {qc['ref list alphabetical']}. "
  f"List entries without a verified record: {uncited_list or 'none'}.\n\n" + md(RF))
w("FIGURE_TABLE_AUDIT.md", f"Status: **{tick(ft_ok)}**. {NF} figures supplied as separate PDF+PNG files, none embedded (inline shapes: {len(d.inline_shapes)}); "
  f"first-citation order 1..{NF}: {qc[[k for k in qc if k.startswith('figures cited')][0]]}; tables in manuscript: {len(d.tables)} (Table 1 cited: {qc['table cited']}).\n\n" + md(FT))
w("WORD_OMML_AUDIT.md", f"Status: **{tick(om_ok)}**. Native Office Math: {len(om)} `m:oMath` elements in {len(omp)} display paragraphs; "
  f"drawing objects in manuscript body: {imgs_eq} (no equation images).")
w("DOCUMENT_INTEGRITY_AUDIT.md", f"Status: **{tick(di_ok)}**.\n\n" + md(pd.DataFrame(di).T.reset_index(names="file")) +
  f"\n\nSubmission ZIP entries: {len(sub)}.")
res = dict(numeric=qc[[k for k in qc if k.startswith('numeric provenance')][0]], hardcode=mut_ok, refs=ref_ok, figtab=ft_ok, omml=om_ok, integrity=di_ok)
print(res); print("G9B ALL PASS" if all(res.values()) else "G9B FAILURES")
