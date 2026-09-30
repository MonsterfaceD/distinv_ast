# Program-Level AST — supervisor draft, 30 September 2026

The authoritative starting point was the uploaded `3009.zip`. This revision
includes checked metatheory, corrected sampler certificates, and an executable
shared certificate-synthesis artifact.

## Read and build

- `main_esop.pdf`: full anonymous draft, including all proof appendices.
- `main_esop.tex`: main file; select this file in Overleaf.
- `docs/UEBERGABE.txt`: German audit summary, scope and remaining limitations.
- `docs/SUBMISSION_NOTES.md`: verified ESOP 2027 rules and submission steps.
- `docs/EMAIL_ENTWURF.txt`: unsent supervisor email.

Build with pdfLaTeX and BibTeX, using a normal TeX Live or MiKTeX installation:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main_esop.tex
```

Alternatively run `pdflatex main_esop.tex`, `bibtex main_esop`, then pdfLaTeX
twice. The included LNCS class and bibliography style are unchanged. Install
TeX Live's `texlive-latex-extra`, `texlive-science`, and recommended fonts
(or equivalent MiKTeX packages) if dependencies in `packages.tex` are missing.
No custom margins, text size, or spacing changes are used.

Keep the appendices enabled for the complete proof draft: the main text refers
to their arguments. Disabling them is a reading option, not a self-contained
submission package. The official Research Paper submission has no page limit;
the 25-page limit excluding bibliography applies to the proceedings version.
The complete delivered draft is therefore not yet a 25-page camera-ready paper.

## Source map

| File | Content |
| --- | --- |
| `1_Introduction.tex` | Motivation, contributions, provenance and scope |
| `2_Preliminaries_and_Background.tex` | Semantics, invariants and pCFG rule |
| `3_Program_Level_AST_Rule.tex` | Rule and random walk |
| `4_Soundness_and_Completeness.tex` | Both certificate translations |
| `5_Sampling_Algorithms.tex` | FDR, FLDR and Han–Hoshi |
| `6_Certificate_Synthesis.tex` | Exact implemented synthesis procedure and results |
| `7_Related_Work.tex` | Focused comparison with prior work |
| `8_Conclusion.tex` | Results and limits |
| `appendices/A_Translation_and_AST_Preservation.tex` | Semantics, common initial-set certificates and arithmetic representation |
| `appendices/B_One_Iteration_Calculations.tex` | FDR support, FLDR preprocessing proof and Han–Hoshi bound |
| `appendices/C_Proof_Obligation_Comparison.tex` | Full FDR pCFG certificate and edge checks |
| `appendices/D_Artifact_and_Proof_Notes.tex` | Reproduction and scope of computational checks |

## Reproduce the artifact

The `synthesis/` folder is independently usable; the separate artifact ZIP
contains the same files without manuscript or internal notes. Start with its
README. The complete suite takes about 15 seconds in the recorded environment,
excluding installation; timings depend on the machine.

```bash
cd synthesis
python3 -m pip install -r requirements.txt
python3 synthesis_examples.py --output reproduced_results.json
python3 diagnostics.py --output reproduced_diagnostics.json
python3 audit_sampler_certificates.py --output reproduced_audit.json
```

The code trusts supplied semantic encodings and Z3. It checks fixed candidates
universally on their supplied domains; finite coefficient search is incomplete.
Neither the AST metatheory nor the FLDR preprocessing theorem is mechanized.

The `docs/` folder is an internal handover: do not include the German email and
handover in an anonymous supplement. Bibliographic attribution is retained in
the manuscript. Update the data availability statement to the actual review or
archival access route once that route is established.
