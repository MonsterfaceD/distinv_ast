# Neue ESOP-Struktur in das bestehende Git-Repository übernehmen

Diese Anleitung bezieht sich auf den Projektstand aus `2209 13uhr.zip`.
Die Befehle funktionieren in Git Bash, PowerShell und einem Linux/macOS-Terminal.
Führe sie im bisherigen **Paper-Ordner** aus, in dem `main_popl.tex` liegt.
Bei einem größeren Repository müssen andere, bereits gestagte Änderungen vor
dem Commit getrennt behandelt werden.

## 1. Aktuellen Stand sichern

```bash
git status --short
```

Wenn die heutigen Änderungen noch nicht committed sind, sichere zuerst diesen
Stand. So sind insbesondere die alten Quelldateien bereits von Git erfasst:

```bash
git add -A .
git commit -m "Save current AST paper before ESOP restructuring"
```

Wenn der Arbeitsstand bereits sauber committed ist, entfällt dieser Commit.

## 2. Neue Dateien übernehmen

Entpacke das neue ZIP zunächst außerhalb des Repositorys. Kopiere dann den
**Inhalt** seines Ordners `AST_ESOP_Projekt` in den bisherigen Paper-Ordner und
überschreibe gleichnamige Projektdateien. Lege dort keinen zusätzlichen
`AST_ESOP_Projekt`-Unterordner an.

Die vorhandene `.git`-Datei bzw. das `.git`-Verzeichnis bleibt erhalten; damit
bleiben Historie, Branches und GitHub-Verbindung bestehen. Kein neues
`git init` ausführen. Falls eine `.gitignore` existiert, ergänze die neuen
Regeln, statt ihre bisherigen Regeln zu überschreiben.

Die neuen Dateien sind jetzt da, die alten Namen aber noch nicht entfernt.

## 3. Genau die ersetzten alten Dateien entfernen

Die folgenden Befehle entfernen die alten, bereits getrackten Dateien aus dem
Arbeitsverzeichnis und stagen ihre Löschung. Sie verwenden absichtlich weder
`--force` noch Wildcards. `--ignore-unmatch` erlaubt, dass einzelne Dateien
bereits fehlen oder zuvor nicht getrackt waren.

```bash
git rm --ignore-unmatch -- main_popl.tex 2_Preliminaries.tex 3_MDPs.tex 4_Nondet.tex 5_SP.tex 6_Nim.tex 7_NondetFDR.tex 6_CertificateSynthesis_Draft.tex 8_RelatedWork.tex 9_Conclusion.tex
git rm --ignore-unmatch -- appendixA.tex appendixB.tex appendixC.tex appendixD.tex appendixE.tex appendixF.tex acmart.cls README_DRAFT.md synthesis_examples.py requirements.txt results.json
git rm --ignore-unmatch -- main_popl.aux main_popl.log main_popl.out main_popl.pdf main_popl.synctex.gz 9_Conclusion.log
```

Sollte `git rm` wegen lokaler Änderungen abbrechen, vergleiche diese mit der
neuen Datei und übernimm sie gegebenenfalls; verwende nicht blind `-f`.
Noch vorhandene **ungetrackte** Dateien mit den oben aufgeführten alten Namen
werden von `git rm` nicht gelöscht. Entferne diese nach Vergleich über den
Dateimanager, damit sie beim nächsten `git add` nicht wieder auftauchen.

`1_Introduction.tex`, `README.md`, `references.bib`, `macros.tex`,
`packages.tex`, `llncs.cls` und `splncs04.bst` bleiben an ihren bisherigen
Pfaden. Die neue `README.md` darf also nicht gelöscht werden.

## 4. Änderungen gemeinsam stagen und prüfen

```bash
git add -A .
git diff --cached --name-status -M
git diff --cached --stat
git status --short
```

`git add -A .` erfasst neue und geänderte Dateien sowie Löschungen innerhalb
des Paper-Ordners. Eine `.gitignore` entfernt keine schon getrackten Dateien;
deshalb wurden die alten Buildprodukte oben ausdrücklich mit `git rm` entfernt.
Siehe die [Dokumentation zu git add](https://git-scm.com/docs/git-add).

Git erkennt Umbenennungen anhand der Ähnlichkeit der Inhalte. In der Übersicht
steht dann beispielsweise `R100` für eine unveränderte umbenannte Datei.
Zusammenführungen und stärkere Überarbeitungen können als `D` plus `A`
erscheinen. Das ist korrekt: Entscheidend ist, dass der neue Snapshot nur die
gewünschten Pfade enthält. Die alten Fassungen bleiben in der Commit-Historie.
Siehe die [Dokumentation zur Rename-Erkennung](https://git-scm.com/docs/git-diff#Documentation/git-diff.txt--Mltngt).

Eine separate Runde mit `git mv` ist für dieses bereits umstrukturierte Projekt
nicht erforderlich.

## 5. Commit und Push

```bash
git commit -m "Restructure AST paper for ESOP and rename source files"
git push
```

`git push` verwendet den konfigurierten Upstream des aktuellen Branches.
Falls ein neuer Branch noch keinen Upstream hat, ersetze `BRANCHNAME` durch
den Namen aus `git branch --show-current`:

```bash
git push -u origin BRANCHNAME
```

Danach zeigt GitHub die neuen Namen und die achtteilige Struktur. Ein Force-Push
ist hierfür nicht erforderlich. In Overleaf bzw. dem LaTeX-Editor noch
`main_esop.tex` als Hauptdatei einstellen.

## Zuordnung der alten zu den neuen Dateien

| Bisher | Jetzt |
| --- | --- |
| `main_popl.tex` | `main_esop.tex` |
| `1_Introduction.tex` | unverändert benannt; Beiträge, Scope und Outline aktualisiert |
| `2_Preliminaries.tex` + `3_MDPs.tex` | `2_Preliminaries_and_Background.tex` |
| `4_Nondet.tex` + `6_Nim.tex` | `3_Program_Level_AST_Rule.tex`; Random Walk in Subsection 3.2 |
| `5_SP.tex` | `4_Soundness_and_Completeness.tex` |
| `7_NondetFDR.tex` | `5_Sampling_Algorithms.tex` |
| `6_CertificateSynthesis_Draft.tex` | `6_Certificate_Synthesis.tex` |
| `8_RelatedWork.tex` | `7_Related_Work.tex` |
| `9_Conclusion.tex` | `8_Conclusion.tex` |
| `appendixA.tex` | `appendices/A_Translation_and_AST_Preservation.tex` |
| `appendixB.tex` | `appendices/B_One_Iteration_Calculations.tex` |
| `appendixC.tex` | `appendices/C_Proof_Obligation_Comparison.tex` |
| `appendixD.tex` | `appendices/D_Artifact_and_Proof_Notes.tex` |
| `README.md` (Synthesenotizen) | `synthesis/README.md`; neue Projektübersicht in `README.md` |
| `README_DRAFT.md` | `docs/SUBMISSION_NOTES.md` |
| `synthesis_examples.py` | `synthesis/synthesis_examples.py` |
| `requirements.txt` | `synthesis/requirements.txt` |
| `results.json` | `synthesis/results.json` |
| `appendixE.tex`, `appendixF.tex` | unbenutzte leere Anhangsplatzhalter entfernt |
| `acmart.cls` | unbenutzte ACM-Klasse entfernt; LNCS bleibt enthalten |
| alte `main_popl`-Buildprodukte, `9_Conclusion.log` | entfernt; neuer Build heißt `main_esop` |

Die bestehenden semantischen Labels wurden erhalten. Der Integer-Wertebereich
des Random-Walk-Invarianten ist jetzt explizit, damit die natürliche Variante
auch auf der gesamten angegebenen Invariantendomäne wohldefiniert ist.
Die Synthese wird in Abstract, Introduction und Conclusion im Umfang des
vorhandenen eingeschränkten Prototyps beschrieben. Die zwei ursprünglichen
Synthesebeispiele und ihre aufgezeichneten Ergebnisse sind erhalten.
