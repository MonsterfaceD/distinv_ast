# ESOP draft: build and submission notes

Main file: `main_esop.tex` in the project root.

- Anonymous Springer LNCS layout with the supplied, unmodified `llncs.cls`.
- Standard fonts, type size, margins, and spacing; no ACM review line numbers.
- Bibliography style: the included `splncs04.bst`; database: `references.bib`.
- Working length target: about 25 pages excluding references. Check the current
  official call before submission: https://etaps.org/2027/conferences/esop/.
- Eight numbered main sections. The symmetric random walk is Section 3.2;
  the restricted certificate synthesis procedure is Section 6.
- Appendices are enabled by default. Set `\appendixversionfalse` in
  `main_esop.tex` for a main-text-only build.
- Keep the anonymous author block and disabled author comments for review.
- Build from the project root with `latexmk -pdf main_esop.tex`.
- Auxiliary files and generated manuscript PDFs are ignored by Git.

The synthesis prototype, pinned dependency, and recorded outputs are in
`synthesis/`. See its README for the assumptions and limits of the method.
