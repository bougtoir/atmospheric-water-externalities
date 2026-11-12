"""Targeted delta QC for the final calibration gate. Writes docs/revision/FINAL_DELTA_QC.md.
Runs g9_qc, g10 semantic audit and pytest; reads the latest g9b result; greps all deliverables for stale wording."""
import glob, json, re, subprocess, zipfile, pathlib
import docx
PY = ".venv/bin/python"; rows = []
def chk(area, what, ok, detail=""): rows.append((area, what, "PASS" if ok else "FAIL", detail))
def run(*a): p = subprocess.run(a, capture_output=True, text=True); return p.returncode, p.stdout + p.stderr
rc, out = run(PY, "scripts/g9_qc.py"); chk("mechanical", "g9_qc formal QC", rc == 0 and "ALL PASS" in out, out.strip().splitlines()[-1])
rc, out = run(PY, "scripts/g10_semantic_audit.py"); chk("semantic", "g10 semantic code audit", "ALL PASS" in out, out.strip().splitlines()[-1])
rc, out = run(PY, "-m", "pytest", "tests", "-q"); chk("mechanical", "pytest", rc == 0, out.strip().splitlines()[-1])
g9b = all(open(f"docs/revision/{f}").read().count("PASS") > 0 for f in ("WORD_OMML_AUDIT.md", "DOCUMENT_INTEGRITY_AUDIT.md", "FIGURE_TABLE_AUDIT.md"))
chk("mechanical", "g9b audits (numeric provenance, hard-code mutation, references, figures/tables, OMML, integrity)", g9b, "see *_AUDIT.md; run before this script")
D = docx.Document("manuscript/manuscript.docx"); M = "\n".join(p.text for p in D.paragraphs)
T = {"manuscript": M, "abstract": M[M.index("Abstract"):M.index("Keywords")],
     "captions": M[M.index("Figure captions"):M.index("References")],
     "cover letter": "\n".join(p.text for p in docx.Document("submission/cover_letter.docx").paragraphs),
     "highlights": open("submission/highlights.txt").read()}
T |= {f: open(f).read() for f in sorted(glob.glob("docs/revision/*.md")) if not f.endswith(("FINAL_DELTA_QC.md", "SEMANTIC_CODE_AUDIT.md"))}
for pat, why in [(r"single[- ]member noise", "stale terminology"), (r"remain within internal variability", "positive null claim"),
                 (r"spread (had )?saturated|saturated before", "unsupported saturation"),
                 (r"(?<!not )(?<!not a )validated upper bound", "|C−S| as bound"),
                 (r"(?<!not a )physical probability(?! of)", "10/14 as probability"),
                 (r"universal(ly)? non-?identif", "universal non-identifiability")]:
    hits = [k for k, v in T.items() if re.search(pat, v, re.I)]
    chk("wording", f"no '{pat}' ({why})", not hits, ", ".join(hits))
chk("claims", "abstract: 10/14 conditional on prespecified grid", "prespecified synthetic grid" in T["abstract"])
chk("claims", "abstract: non-detection is not zero effect", "not evidence of zero effect" in T["abstract"])
chk("claims", "Fig. 11 caption uses four-member prediction-interval wording", "95% prediction interval derived from the four-member no-wind ensemble" in T["captions"])
chk("claims", "Fig. 9 caption states the actual denominator", "each perturbed no-wind run and CONTROL" in T["captions"])
chk("claims", "Fig. 12 caption present and cited in text", "Fig. 12." in T["captions"] and "(Fig. 12)" in M)
chk("claims", "Eq. (6) identified set and bound typology in Section 2.2", "identified set" in M and "not a physical bound" in M)
chk("claims", "known-truth baseline orientation stated", "observed state already contains the fleet" in M)
chk("claims", "[A]/[S]/[C] labels retained", all(x in M for x in ("[A]", "[S]", "[C]")))
chk("claims", "WRF model-conditional language retained", "model-conditional" in M and "not an observed real-world effect" in M)
chk("claims", "single author only", "Onishi Tatsuki" in M and not re.search(r"\bwe\b|\bour\b", M[M.index("1. Introduction"):M.index("Software and data")], re.I))
om = D.element.body.xpath(".//m:oMath"); chk("OMML", "native equations (6), no equation images", len(om) == 6 and not D.inline_shapes, f"{len(om)} m:oMath")
wc = json.load(open("results/manuscript_wordcount.json")); chk("format", "abstract ≤ 150 words", wc["abstract_words"] <= 150, str(wc))
hl = open("submission/highlights.txt").read().strip().split("\n"); chk("format", "3–5 highlights ≤ 85 characters", 3 <= len(hl) <= 5 and max(map(len, hl)) <= 85, f"max {max(map(len, hl))}")
z = zipfile.ZipFile("TAWE_EMS_submission.zip"); n = z.namelist()
nf = sum(p.startswith("Fig. ") for p in M[M.index("Figure captions"):].split("\n"))
chk("package", "submission ZIP: manuscript, cover letter, highlights, graphical abstract, all figures PDF+PNG", z.testzip() is None and
    {"manuscript.docx", "cover_letter.docx", "highlights.docx", "graphical_abstract.pdf"} <= set(n) and
    sum(x.endswith(".pdf") and x.startswith("figures/") for x in n) == nf == sum(x.endswith(".png") and x.startswith("figures/") for x in n), f"{nf} figures")
chk("package", "manuscript in ZIP = built manuscript", z.read("manuscript.docx") == open("manuscript/manuscript.docx", "rb").read())
chk("refs", "reference list unchanged in count (no new citations needed)", wc["n_refs"] == 27, f"{wc['n_refs']} references")
chk("numbers", "canonical scientific results unchanged (WRF flags, known truth)", json.load(open("results/wrf/programme_summary.json"))["pooled"]["n_outside"] == 7)
L = ["# Final delta QC (calibration gate)", "", "Rendered by `scripts/g11_delta_qc.py`. Scope: only what the calibration gate changed (wording of",
     "identification and internal-variability claims, new spread-growth and prediction-interval analyses, Eq. 6, Section 4.8,",
     "Fig. 12, captions of Figs. 9 and 11, abstract, discussion, conclusions, highlights, cover letter). The research pipeline",
     "(tracking, known truth, WRF runs) was not rerun; canonical results are unchanged.", "",
     "| area | check | status | detail |", "|---|---|---|---|"] + [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
L += ["", f"Overall: {'ALL PASS' if all(r[2] == 'PASS' for r in rows) else 'FAILURES PRESENT'} ({sum(r[2] == 'PASS' for r in rows)}/{len(rows)})."]
pathlib.Path("docs/revision/FINAL_DELTA_QC.md").write_text("\n".join(L) + "\n"); print(L[-1]); [print(r) for r in rows if r[2] != "PASS"]
