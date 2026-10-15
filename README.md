# Distribution-Based AST — revised draft, 15 October 2026

This project contains the program-level AST manuscript, sampler certificates,
and an executable shared certificate-synthesis artifact. The synthesis results
reported in the manuscript and artifact README refer to the supplied
`AST_Synthesis_Artifact/results.json`.

## Read and build

- `main_esop.pdf`: generated anonymous draft, including all proof appendices.
- `main_esop.tex`: main file; select this file in Overleaf.
- `AST_Synthesis_Artifact/README.md`: artifact setup, inputs, results, and limits.

This revision incorporates JPK's remaining comments from Section 6.2 onward.
Sections 6.2–6.3 focus on the search principle and synthesized certificates;
Appendix D contains the detailed procedure, loop models, certificate analyses,
and artifact checks. The bibliography precedes the appendices.
`AENDERUNGEN_1510.txt` lists the changes and validation performed.

Build with pdfLaTeX and BibTeX, using a normal TeX Live or MiKTeX installation:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error main_esop.tex
```

Alternatively run the complete sequence:

```bash
pdflatex -interaction=nonstopmode -halt-on-error main_esop.tex
bibtex main_esop
pdflatex -interaction=nonstopmode -halt-on-error main_esop.tex
pdflatex -interaction=nonstopmode -halt-on-error main_esop.tex
```

A single pdfLaTeX pass does not resolve all citations and cross-references.
Before sharing the PDF, check that it includes the bibliography and that the
final log reports no undefined citations or references. The included LNCS class
and bibliography style are unchanged. Install
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
| `2_Preliminaries_and_Background.tex` | Semantics and distributional invariants |
| `3_Program_Level_AST_Rule.tex` | Program-level rule, random walk and short FDR illustration |
| `4_Soundness_and_Completeness.tex` | Complete pCFG rule, interface comparison and both certificate translations |
| `5_Sampling_Algorithms.tex` | FDR, FLDR and Han–Hoshi |
| `6_Certificate_Synthesis.tex` | Synthesis constraints, concise search overview and experimental results |
| `7_Related_Work.tex` | Focused comparison with prior work |
| `8_Conclusion.tex` | Results and limits |
| `appendices/A_Translation_and_AST_Preservation.tex` | Semantics, common initial-set certificates and arithmetic representation |
| `appendices/B_One_Iteration_Calculations.tex` | FDR support and logarithmic variant, FLDR preprocessing proof and Han–Hoshi bound |
| `appendices/C_Proof_Obligation_Comparison.tex` | Full FDR pCFG certificate and edge checks |
| `appendices/D_Artifact_and_Proof_Notes.tex` | Detailed search procedure, loop models, certificate analyses, reproduction and computational checks |

## Reproduce the artifact

The `AST_Synthesis_Artifact/` folder is independently usable. Start with its
README. The supplied synthesis run used Python 3.13.0 and Z3 4.15.4 and took
approximately 16 seconds, excluding installation and the separate diagnostics.
Timings and solver-selected certificates can vary across systems.

```bash
cd AST_Synthesis_Artifact
python3 -m pip install -r requirements.txt
python3 synthesis_examples.py --output reproduced_results.json
python3 diagnostics.py --output reproduced_diagnostics.json
python3 audit_sampler_certificates.py --output reproduced_audit.json
```

The code trusts supplied semantic encodings and Z3. It checks fixed candidates
universally on their supplied domains; finite coefficient search is incomplete.
Neither the AST metatheory nor the FLDR preprocessing theorem is mechanized.

The data availability statement identifies `AST_Synthesis_Artifact.zip`,
included in this project alongside the unpacked artifact directory. Include that anonymous package with
the manuscript when making it available to reviewers; it contains no build
logs or local path metadata. For a proceedings version, replace this access
route with the permanent archival identifier.

When sharing LaTeX sources, include only the `.tex`, `.bib`, class and style
files required to build the manuscript. Exclude `.aux`, `.log`, SyncTeX,
Python caches and other machine-generated files.
