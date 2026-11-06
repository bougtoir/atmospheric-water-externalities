"""Graphical abstract, cover letter (md+docx) and EMS submission/reproducibility ZIPs."""
import json, pathlib, zipfile, hashlib, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from docx import Document
V = json.load(open("results/manuscript_values.json")); W = json.load(open("results/manuscript_wordcount.json"))
S = pathlib.Path("submission")
fig, ax = plt.subplots(figsize=(8, 3)); ax.axis("off")
items = [("Accounting [A]", f"{100*V['land_mean']:.0f}% of farm-cell\nevaporation rains on land,\nmostly abroad"),
         ("Placebo test", f"{V['pl_inside']}/{V['pl_n']} receptors inside\nplacebo range"),
         ("Known truth", f"supply estimator: median\nerror {100*V['kt_dyn_med']:.0f}% with dynamics"),
         ("Externality [C]", "requires counterfactual\nsimulations: NOT RUN")]
for i, (h, t) in enumerate(items):
    x = 0.02 + i * 0.245; ax.add_patch(plt.Rectangle((x, 0.15), 0.22, 0.7, fill=False, lw=1.2))
    ax.text(x + 0.11, 0.72, h, ha="center", weight="bold", fontsize=10); ax.text(x + 0.11, 0.42, t, ha="center", va="center", fontsize=8.5)
ax.text(0.5, 0.03, "Accounting is not attribution", ha="center", fontsize=11, style="italic")
fig.savefig(S / "graphical_abstract.pdf", bbox_inches="tight"); fig.savefig(S / "graphical_abstract.png", dpi=300, bbox_inches="tight"); plt.close(fig)
cl = f"""Dear Editor,

Please consider our research article "Accounting is not attribution: a conservation-closed tagging and identifiability framework for transboundary atmospheric water externalities of offshore wind energy" for Environmental Modelling & Software.

The paper defines transboundary atmospheric water externalities as counterfactual precipitation differences, separates a supply channel that moisture tagging can compute from a dynamic channel that it cannot, and releases an open, mass-conserving tagging tool with verification tests, known-truth experiments, placebo sources and a detectability analysis. Applied to European offshore wind farms with ERA5 ({V['y0']}–{V['y1']}), it shows that source–receptor accounting is strongly transboundary but is not an externality estimate. A coupled counterfactual simulation suite was designed but not run; this is stated explicitly, and no causal magnitude is claimed.

The work fits the journal's scope on model development, evaluation and identification. The manuscript has {W['main_text_words']:,} words in the main text, {W['abstract_words']} words in the abstract, 6 figures, 1 table and {W['n_refs']} references. Software and data are openly available (see the Software and data availability section). The manuscript is not under consideration elsewhere. All authors approved the submission and declare no competing interests.

Sincerely,
[Corresponding author]
"""
(S / "cover_letter.md").write_text(cl); d = Document()
for para in cl.split("\n\n"): d.add_paragraph(para.replace("\n", " ") if not para.startswith("Sincerely") else para)
d.save(S / "cover_letter.docx")
def mk(name, files):
    with zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED) as z:
        for f, arc in files: z.write(f, arc)
    zz = zipfile.ZipFile(name); assert zz.testzip() is None and not any(n.startswith("/") or ".." in n for n in zz.namelist())
    print(name, pathlib.Path(name).stat().st_size, hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest())
sub = [("manuscript/manuscript.docx", "manuscript.docx"), ("submission/highlights.docx", "highlights.docx"),
       ("submission/graphical_abstract.pdf", "graphical_abstract.pdf"), ("submission/cover_letter.docx", "cover_letter.docx")]
sub += [(str(p), f"figures/{p.name}") for p in sorted(pathlib.Path("figures").glob("Figure_*.pdf"))]
sub += [(str(p), f"figures/{p.name}") for p in sorted(pathlib.Path("figures").glob("Figure_*.png"))]
mk("TAWE_EMS_submission.zip", sub)
rep = [(str(p), str(p)) for pat in ["tawe/*.py", "scripts/*.py", "tests/*.py", "results/*", "data/raw/LEDGER.csv", "data/raw/era5/LEDGER.csv",
       "data/raw/boundaries/*", "data/raw/turbines_from_ecm_wind_heatwave.csv", "data/processed/grid_masks.npz", "data/processed/grid_masks_log.json",
       "references/*.csv", "references/crossref_raw/*", "Makefile", "requirements.lock.txt", "README.md", "LICENSE"] for p in sorted(pathlib.Path(".").glob(pat))]
mk("TAWE_reproducibility.zip", rep)
