# ESOP 2027: Einreichung und Zusatzmaterial

Geprüft am 30.09.2026. Maßgeblich ist ESOP 2027, 36th European Symposium on Programming, Runde 2. Die unten genannten 2027-Regeln sind veröffentlicht; Regeln früherer Ausgaben werden nicht als verbindlich übernommen.

## Umfang, Format und Begutachtung

Für **Research Papers** gilt bei der Einreichung **kein Seitenlimit**. Zulässig sind LNCS, PACMPL und TOPLAS. Die angenommene Endfassung muss dagegen LNCS verwenden und darf **25 Seiten ohne Literaturverzeichnis** umfassen. Das Ziel von ungefähr 25 Textseiten ist damit eine sinnvolle Vorbereitung auf die Endfassung, keine Einreichungsgrenze. ESOP begutachtet doppelt anonym; auch indirekte Identifikation soll vermieden werden. [1]

Die 2027-Seiten nennen **keine gesonderte Ausnahme für Anhänge**. Unsere konservative Planung zählt deshalb einen in der Endfassung enthaltenen Anhang zum 25-Seiten-Umfang. Das ist eine Planungsentscheidung aus dem veröffentlichten Wortlaut, keine ausdrücklich veröffentlichte Detailregel zu Anhängen. Die fehlende Einreichungsgrenze erlaubt einen längeren Begutachtungs-Draft; sie verspricht keine unbegrenzte Veröffentlichung zusätzlicher Beweise. [1, 2]

Das ETAPS-CFP verlangt für Proceedings-Papers eine **Data availability statement unmittelbar vor dem Literaturverzeichnis**; diese zählt nicht zum Seitenlimit. Autorennamen, Institutionen und identifizierende Danksagungen gehören nicht in die Begutachtungsfassung; eigene Vorarbeiten sind wie fremde Arbeiten in der dritten Person zu behandeln. Interessenkonflikte müssen im System angegeben werden. Paralleleinreichungen derselben Arbeit sind untersagt. [2]

Die offizielle Springer-Seite bietet die LNCS-Anleitung und das LaTeX-Template. Für dieses Projekt ist die Verwendung der Standardklasse `llncs` bereits die zweckmäßige Wahl. Schriftgröße, Satzspiegel und Abstände nicht zur Seitenoptimierung verändern. [5]

## Verifizierte Termine

Alle offiziellen Fristen sind **AoE**. [2]

| Vorgang | Termin |
|---|---|
| Research Paper, Runde 2 | 15.10.2026 |
| Rebuttal | 07.–09.12.2026 |
| Paper-Entscheidung | 22.12.2026 |
| Freiwillige Artifact-Einreichung | 11.01.2027 |
| Paper-Endfassung | 25.01.2027 |
| Artifact-Entscheidung | 11.02.2027 |

Praktische Umrechnung: Der Ablauf des 15.10. in AoE liegt in Aachen am **16.10.2026 um 13:59 Uhr MESZ**; rechtzeitig davor fertig einreichen.

## Paper-Supplement und Artifact Evaluation unterscheiden

**Zur Paper-Einreichung:** Der spezielle ESOP-Link führt zu **HotCRP**, https://esop27.hotcrp.com/. Dieser konkrete Link ist maßgeblich gegenüber dem allgemeinen EasyChair-Satz im gemeinsamen CFP. [1, 2] Ein zusätzliches Code-ZIP, dessen erlaubte Dateitypen, Größe oder ein gesondertes Supplement-Feld sind in den öffentlich geprüften 2027-Hinweisen **nicht verifiziert**. Ein vorbereitetes ZIP ist deshalb noch kein bestätigtes Uploadformat. Ebenso wurde keine Pflicht zum Hochladen des LaTeX-Projekts bei der Paper-Einreichung festgestellt.

**Nach Paper-Annahme:** Die freiwillige Artifact Evaluation ist ein separates Verfahren und ändert die Paper-Entscheidung nicht. [1] Laut gemeinsamem CFP kann ein Artifact von einem kurzen Experience Report mit fünf Seiten einschließlich einer Literaturseite begleitet werden. [2] Die spezielle 2027-AE-Seite enthält zum Prüfzeitpunkt jedoch nur eine allgemeine Überschrift/Beschreibung, noch keine technischen Einreichungsanweisungen. **Uploadsystem, Archivformat, Größengrenze und Verpackungsanforderungen sind dort noch nicht veröffentlicht.** [3] Frühere Vorgaben, etwa VM-Anforderungen oder Größenlimits, werden hier nicht übernommen.

Das öffentlich abrufbare beziehungsweise indexierte HotCRP-Frontend meldete eine geschlossene Registrierung; die offizielle Konferenzseite nennt weiterhin Runde 2. [4] Ohne Zugriff auf das angemeldete Einreichungsformular lässt sich nicht feststellen, ob diese Frontend-Meldung noch Runde 1 betrifft. Sie wird hier nicht als Änderung der offiziellen Frist interpretiert.

## Konkrete Schritte für dieses Projekt

1. **Prof-Draft prüfen lassen.** PDF, vollständiges Quellenprojekt und getrenntes Reproduktionspaket an die Koautoren geben. Noch offene mathematische Fragen aus dem Übergabebericht vor der Einreichung entscheiden. Die Versandfassung an den Betreuer ist nicht automatisch die anonyme Reviewfassung.
2. **Reviewfassung herstellen.** Namen, Institutionen, Danksagungen, PDF-Metadaten sowie identifizierende Repository-Links und Kommentare kontrollieren. Nur zur Begutachtung gehörende Dateien weitergeben; die deutsche Betreuer-Mail und interne Übergabenotizen gehören nicht ins Supplement. Quellen und fremde Urheberschaft weiterhin korrekt nennen.
3. **Reproduktion erneut ausführen.** Die Befehle der Artifact-README in einer frischen Umgebung ausführen. Ergebnisse, Garantien und Einschränkungen mit Section 6 vergleichen; keine nur lokal erfolgreichen oder nicht dokumentierten Schritte voraussetzen.
4. **HotCRP über den offiziellen ESOP-Link öffnen.** Research-Paper-Eintrag anlegen, Metadaten und Interessenkonflikte nach dem dortigen Formular ausfüllen und die anonyme PDF hochladen. Falls Runde 2 dort noch nicht auswählbar ist, frühzeitig beim PC-Chair nachfragen; keinen alternativen Einreichungskanal erraten.
5. **Zusatzmaterial nur über bestätigte Möglichkeiten übergeben.** Im tatsächlichen Formular prüfen, ob ein Supplement-Feld oder anonymer Materiallink vorgesehen ist. Falls ja, dessen aktuelle Anleitung für das getrennte Reproduktionspaket beachten. Falls nein, beim PC-Chair klären, wie der Code den Gutachtern zugänglich gemacht werden darf. Die mathematischen Hauptargumente müssen im Paper nachvollziehbar bleiben. Nicht behaupten, ein ZIP sei allein aufgrund allgemeiner HotCRP-Funktionen zulässig.
6. **Einreichung abschließen.** Den endgültigen Status, die hochgeladene PDF und gegebenenfalls das tatsächlich angehängte Supplement im System kontrollieren; Bestätigung sichern. Nachträglich geänderten Code nicht stillschweigend als die begutachtete Version ausgeben.
7. **Bei Annahme AE vorbereiten.** Die dann vollständigen 2027-AE-Anweisungen erneut lesen und das vorhandene Reproduktionspaket entsprechend verpacken. Die Termine stehen oben. Ein zusätzliches Experience-Report-Paper nur verfassen, wenn dieser separate Beitrag sinnvoll ist und die dann geltenden Detailvorgaben geklärt sind.
8. **Endfassung herstellen.** LNCS-Umfang einschließlich veröffentlichter Anhänge kontrollieren, Autorendaten wieder aufnehmen und die Data availability statement mit dem tatsächlich verfügbaren Material vervollständigen. Die dann mitgeteilten Proceedings-Anweisungen für Quelldateien, Rechteformular und Veröffentlichung befolgen.

## Offizielle Quellen

1. ESOP 2027, insbesondere „Submission Categories“, „Important Dates“ und „Artifact Evaluation“: https://etaps.org/2027/conferences/esop/
2. ETAPS 2027 Joint Call for Papers, insbesondere Termintabelle, Submission Instructions und Artifact Submission and Evaluation: https://etaps.org/2027/cfp/
3. ESOP, FoSSaCS and iFS Artifact Evaluation 2027: https://etaps.org/2027/conferences/ae-esop-fossacs-ifs/
4. Von ESOP verlinktes Einreichungssystem: https://esop27.hotcrp.com/
5. Springer, LNCS Information for authors and editors, mit Vorlagen und Autorenanleitung: https://www.springer.com/gp/computer-science/lncs/forthcoming-proceedings

Die Quellen [1]–[4] wurden am 30.09.2026 öffentlich recherchiert. Ein angemeldetes HotCRP-Formular wurde nicht eingesehen; keine Einreichung wurde vorgenommen.
