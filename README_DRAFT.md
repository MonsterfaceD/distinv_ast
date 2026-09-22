# ESOP 2027 paper draft

Main file: `main_popl.tex`

- Anonymous Springer LNCS layout using the supplied, unmodified `llncs.cls`.
- Standard fonts, type size, margins, and spacing; no ACM review line numbers.
- Bibliography style: `splncs04.bst` (included).
- Target: about 25 pages excluding references. ESOP 2027 research submissions
  have no fixed page limit; the final LNCS paper is limited to 25 pages
  excluding references. See https://etaps.org/2027/conferences/esop/.
- Appendices are enabled by default; set `\appendixversionfalse` in `main_popl.tex` for main-text only.
- Keep the anonymous author block and disabled author comments for submission.
  Add author names, affiliations, and acknowledgments only for the final version.
- Build with `latexmk -pdf main_popl.tex` (pdfLaTeX and BibTeX).
- Recompile after applying the format update; the PDF and auxiliary files in
  the original archive were generated with the previous ACM layout.
