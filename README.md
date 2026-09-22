# AST Proof Rules on Program Level - ESOP project

Current entry point: **`main_esop.tex`**. Build commands must be run in this
directory. In Overleaf, select `main_esop.tex` as the main document.
The included `main_esop.pdf` is a fresh build of this project, with sections
and subsections in the PDF navigation.

## Build

```bash
latexmk -pdf main_esop.tex
```

Use pdfLaTeX and BibTeX with a current TeX Live or MiKTeX installation.
The supplied `llncs.cls` and `splncs04.bst` are used unchanged. The package
dependencies are listed in `packages.tex`; in TeX Live, the science collection
supplies `stmaryrd`, `backnaur`, `siunitx`, and `bussproofs`.

If `latexmk` is unavailable:

```bash
pdflatex main_esop.tex
bibtex main_esop
pdflatex main_esop.tex
pdflatex main_esop.tex
```

Appendices are enabled by default. Change `\appendixversiontrue` to
`\appendixversionfalse` in `main_esop.tex` for the main text only.

## Main text

| Section | File | Contents |
| --- | --- | --- |
| 1 | `1_Introduction.tex` | Problem, approach, contributions, scope, outline |
| 2 | `2_Preliminaries_and_Background.tex` | Language, semantics, invariants, certificates, pCFG rule |
| 3 | `3_Program_Level_AST_Rule.tex` | Rule, random walk (3.2), abstraction and modularity |
| 4 | `4_Soundness_and_Completeness.tex` | Contraction, soundness, relative completeness |
| 5 | `5_Sampling_Algorithms.tex` | FDR comparison, FLDR, Han--Hoshi |
| 6 | `6_Certificate_Synthesis.tex` | Restricted template method, CEGIS, worked examples |
| 7 | `7_Related_Work.tex` | Related work |
| 8 | `8_Conclusion.tex` | Results, limitations, nondeterminism, synthesis and future work |

The four active appendices are in `appendices/`. The synthesis prototype,
solver requirement, recorded outputs, and detailed explanation are in
`synthesis/`. Submission and build notes are in `docs/SUBMISSION_NOTES.md`.

## Run the synthesis prototype

```bash
cd synthesis
python3 -m pip install -r requirements.txt
python3 synthesis_examples.py --output results.json
```

The source and recorded results were retained. The method uses supplied
invariants, manually encoded one-iteration semantics, and a finite coefficient
domain. See `synthesis/README.md` for the scope of the claims.

## Import into the existing Git repository

Read **`docs/GIT_MIGRATION.md`** before copying this project into an existing
checkout. It lists the exact old filenames to remove and the Git commands to
record the new names and deletions together. Merely copying new files over old
ones does not remove files that have been renamed or merged.

The `.gitignore` excludes compilation products; `synthesis/results.json`
remains tracked. If the repository already has a `.gitignore`, merge these
patterns into it rather than replacing unrelated rules.
