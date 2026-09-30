# Diese Revision in den vorhandenen Checkout übernehmen

Diese Anleitung gilt für die Revision von `3009.zip`, nicht für die frühere
Umstellung vom POPL-Dateischema. `main_esop.tex` und die acht Sections behalten
ihre Namen. Die zusätzlichen Python-Module sind neu.

1. Im vorhandenen Repository `git status --short` prüfen. Eigene Änderungen
   vorher sichern oder committen; die `.git`-Datei bzw. der `.git`-Ordner bleibt.
2. Das neue ZIP außerhalb des Checkouts entpacken. Den Inhalt von
   `AST_ESOP_Prof_Draft` in den Paper-Ordner übernehmen; eigene, nicht zum Paper
   gehörende Dateien beibehalten. Bestehende `.gitignore`-Regeln zusammenführen.
3. Veraltete TeX-Kopien unter `synthesis/` nach Vergleich entfernen:
   `1_Introduction.tex`, `5_Sampling_Algorithms.tex`,
   `6_Certificate_Synthesis.tex`, `7_Related_Work.tex`, `8_Conclusion.tex`,
   `main_esop.tex` und `synthesis/appendices/`. Die maßgeblichen Fassungen stehen
   weiterhin im Projektwurzelverzeichnis beziehungsweise in `appendices/`.
4. `latexmk -pdf main_esop.tex` und die drei Befehle aus der Artifact-README
   ausführen. Buildprodukte und `__pycache__` nicht neu versionieren.
5. Im Paper-Ordner `git add -A .`, dann `git diff --cached --stat` und
   `git diff --cached --name-status` kontrollieren. Nur passende Änderungen
   committen und anschließend den normalen `git push` verwenden. Ein Force-Push
   ist nicht erforderlich.

Das ZIP enthält den vollständigen aktuellen Quellenstand; eine bloße Kopie
entfernt alte doppelte Dateien nicht automatisch. Entfernte Dateien bleiben in
der Git-Historie erhalten.
