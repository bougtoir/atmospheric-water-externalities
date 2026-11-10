# Final delta QC (calibration gate)

Rendered by `scripts/g11_delta_qc.py`. Scope: only what the calibration gate changed (wording of
identification and internal-variability claims, new spread-growth and prediction-interval analyses, Eq. 6, Section 4.8,
Fig. 12, captions of Figs. 9 and 11, abstract, discussion, conclusions, highlights, cover letter). The research pipeline
(tracking, known truth, WRF runs) was not rerun; canonical results are unchanged.

| area | check | status | detail |
|---|---|---|---|
| mechanical | g9_qc formal QC | PASS | ALL PASS |
| semantic | g10 semantic code audit | PASS | Overall: ALL PASS (21/21). |
| mechanical | pytest | PASS | 5 passed in 0.12s |
| mechanical | g9b audits (numeric provenance, hard-code mutation, references, figures/tables, OMML, integrity) | PASS | see *_AUDIT.md; run before this script |
| wording | no 'single[- ]member noise' (stale terminology) | PASS |  |
| wording | no 'remain within internal variability' (positive null claim) | PASS |  |
| wording | no 'spread (had )?saturated|saturated before' (unsupported saturation) | PASS |  |
| wording | no '(?<!not )(?<!not a )validated upper bound' (|C−S| as bound) | PASS |  |
| wording | no '(?<!not a )physical probability(?! of)' (10/14 as probability) | PASS |  |
| wording | no 'universal(ly)? non-?identif' (universal non-identifiability) | PASS |  |
| claims | abstract: 10/14 conditional on prespecified grid | PASS |  |
| claims | abstract: non-detection is not zero effect | PASS |  |
| claims | Fig. 11 caption uses four-member prediction-interval wording | PASS |  |
| claims | Fig. 9 caption states the actual denominator | PASS |  |
| claims | Fig. 12 caption present and cited in text | PASS |  |
| claims | Eq. (6) identified set and bound typology in Section 2.2 | PASS |  |
| claims | known-truth baseline orientation stated | PASS |  |
| claims | [A]/[S]/[C] labels retained | PASS |  |
| claims | WRF model-conditional language retained | PASS |  |
| claims | single author only | PASS |  |
| OMML | native equations (6), no equation images | PASS | 6 m:oMath |
| format | abstract ≤ 150 words | PASS | {'main_text_words': 2767, 'abstract_words': 145, 'n_refs': 27} |
| format | 3–5 highlights ≤ 85 characters | PASS | max 85 |
| package | submission ZIP: manuscript, cover letter, highlights, graphical abstract, all figures PDF+PNG | PASS | 12 figures |
| package | manuscript in ZIP = built manuscript | PASS |  |
| refs | reference list unchanged in count (no new citations needed) | PASS | 27 references |
| numbers | canonical scientific results unchanged (WRF flags, known truth) | PASS |  |

Overall: ALL PASS (27/27).
