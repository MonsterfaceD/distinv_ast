# Zwei Synthesebeispiele für die Program-Level-AST-Regel

Stand: 22. September 2026. Die Beispiele beziehen sich auf die rein
probabilistische Regel des aktuellen AST-Manuskripts. Sie sind ein
Machbarkeitstest mit einem gemeinsamen Synthesekern.

## Dateien und Ausführung

- `synthesis_examples.py`: gemeinsamer CEGIS-Kern und zwei Programmeingaben.
- `requirements.txt`: verwendete Solverversion.
- `results.json`: aufgezeichnete Kandidaten, Gegenbeispiele und Prüfergebnisse.
- `6_CertificateSynthesis_Draft.tex`: englischer Entwurf für eine eigenständige
  Synthese-Section. Er verwendet den bestehenden Verweis `thm:program-rule`.
- Dieses Dokument: Schritte, Herleitungen und Einordnung.

```bash
python3 -m pip install -r requirements.txt
python3 synthesis_examples.py --output results.json
```

Der LaTeX-Entwurf kann nach `5_SP.tex` und vor `6_Nim.tex` eingebunden werden.
Er enthält beide Beispiele zunächst an einem Ort. Für die spätere Paperfassung
sollte man deren Darstellung mit den bestehenden Beispielabschnitten
zusammenführen, um die AST-Beweise nicht zweimal zu erklären. Die Hauptdatei
des Manuskripts wird durch dieses Paket nicht ersetzt.

## 1. Was vorgegeben wird und was synthetisiert wird

**Vorgegeben:** Variablen und deren ganzzahliger Wertebereich, Schleifenguard,
Semantik einer vollständigen Rumpfausführung, Zustandsinvariant, affine
Templateklasse, ganzzahlige Koeffizienten in `[-2,2]` und die hinreichende
Beschränktheitsbedingung `U <= V`.

**Synthetisiert:** sämtliche Koeffizienten von V und U, unabhängig voneinander.
Kein Koeffizient wird auf den Wert aus dem manuellen Beweis festgelegt.
Eine Minimierung der Summe der Koeffizientenbeträge bevorzugt einfache
Kandidaten; sie ist für die Soundness irrelevant.

**Verifiziert:** Positivität von V und U auf aktiven Zuständen, die
Supermartingal-Ungleichung, probabilistischer Abstieg, U <= V,
Initialisierung und Erhaltung des Zustandsinvarianten. Die Nullwerte auf
terminalen Zuständen und die Ganzzahligkeit von U gelten durch die
Templatekonstruktion.

Die Koeffizienten sind beschränkt; die Programmzustände sind es nicht.
Insbesondere gibt es weder ein Testmaximum für x noch eines für n.
Die Implementierung erwartet die Rumpfsemantik als Eingabe; sie enthält
keinen LaTeX- oder Programmiersprachenparser und keine Invariantensynthese.

## 2. Gemeinsame Constraints

Für ein Zustandsprädikat S und den Guard b verwenden wir

\[
 V_{\theta}(s)=[b(s)](a_0+a_1s_1+\cdots+a_ds_d),\qquad
 U_{\eta}(s)=[b(s)](c_0+c_1s_1+\cdots+c_ds_d).
\]

Die Iversonklammer bedeutet eine Fallunterscheidung: auf terminalen
Zuständen werden beide Funktionen auf null gesetzt. Diese Funktionen
sind daher **guarded affine**, also stückweise affin.

Für beide Programme gibt es zwei Ergebnisse T0(s), T1(s), jeweils mit
Wahrscheinlichkeit 1/2. Für alle s mit S(s) und b(s) fordern wir:

\[
\begin{gathered}
 V(s)\ge1,\qquad U(s)\ge1,\qquad U(s)\le V(s),\\
 V(T_0(s))+V(T_1(s))\le2V(s),\\
 U(T_0(s))\le U(s)-1\quad\lor\quad U(T_1(s))\le U(s)-1.
\end{gathered}
\]

Die Disjunktion garantiert Abstieg mit Wahrscheinlichkeit mindestens 1/2.
Es wird nicht verlangt, dass derselbe Ausgang in allen Zuständen absteigt.
Im FDR-Ergebnis stellt sich nachträglich heraus, dass immer Bit 0 genügt.

Die Beschränktheitsbedingung folgt aus U <= V: Auf jeder Menge V <= r gilt
U <= floor(r). Das ist eine hinreichende Einschränkung der ursprünglichen
Regel. Auch ganzzahlige V-Koeffizienten und V >= 1 schränken die allgemeine
Regel ein, die reellwertiges, strikt positives V erlaubt.

Mit invariantem S können wir das distributionelle Invariant als Menge
aller Subdistributionen mit Support in S wählen. Dadurch passen die
geprüften Bedingungen unmittelbar zur Program-Level-Regel.

## 3. Warum CEGIS hier passt

1. Der Learner beginnt mit einem aktiven Beispielzustand.
2. Er wählt Koeffizienten, welche die Constraints für alle bislang
   gesammelten Zustände erfüllen.
3. Der Verifier setzt diese Koeffizienten fest ein und fragt nach einem
   beliebigen ganzzahligen Zustand, der S und b erfüllt, aber mindestens
   eine Bedingung verletzt.
4. Ein gefundenes Gegenbeispiel wird hinzugefügt. Bei UNSAT sind alle
   Bedingungen universell im Invariantenbereich erfüllt.

Die Aufteilung ist technisch nützlich: Im Learner sind die Zustände
konkret, daher sind die Constraints linear in den Koeffizienten. Im
Verifier sind die Koeffizienten konkret, daher sind die Constraints
Boolean-Kombinationen linearer Arithmetik über den Zustandsvariablen.
Es wird keine allgemeine Formel mit gleichzeitig unbekannten Faktoren
`Koeffizient * Zustandsvariable` direkt gelöst.

**UNSAT bedeutet nur bei der Gegenbeispielsuche Erfolg.** UNSAT beim Learner
bedeutet, dass das endliche Template keine Lösung mehr enthält. UNKNOWN
oder ein Ressourcenlimit begründen keine mathematische Aussage.

Ohne Ressourcenlimits und mit vollständigen, terminierenden Solvern ist
die endliche Templatesuche vollständig für genau diesen endlichen Raum:
Jedes Gegenbeispiel schließt mindestens den aktuellen Kandidaten aus;
ein gültiger Kandidat wird nie ausgeschlossen. Dies ist keine
Vollständigkeit für alle affinen Funktionen oder für alle AST-Programme.

## 4. Beispiel: unbeschränkter symmetrischer Random Walk

```text
while x > 0:
    x := x - 1  [1/2]  x := x + 1
```

**Domäne:** x ist ganzzahlig, S ist x >= 0. Vor einer Iteration gilt
x >= 1; beide Ausgänge bewahren S. Jeder nichtnegative Startzustand ist
zugelassen.

**Templates auf aktiven Zuständen:** V(x)=a*x+b und U(x)=c*x+d.
Bei x=0 werden beide auf null gesetzt.

**Aufgezeichneter Lauf:**

| Runde | Kandidat auf x > 0 | Verifikation |
|---|---|---|
| 1 | V=1, U=1 | Gegenbeispiel x=2: beide Nachfolger behalten U=1 |
| 2 | V=x, U=x | Kein Gegenbeispiel im unbeschränkten Zustandsraum |

Am anfänglichen Beispielzustand x=1 erscheint die konstante Variante
plausibel: Der linke Schritt terminiert, also sinkt U von 1 auf 0.
Das Gegenbeispiel x=2 zeigt genau, warum diese lokale Beobachtung nicht
genügt. Die Solverreihenfolge ist implementationsabhängig; `results.json`
zeichnet den tatsächlich ausgeführten Lauf auf.

**Analytische Verifikation des Ergebnisses:** Für alle x >= 1 gilt

\[
 \tfrac12 V(x-1)+\tfrac12 V(x+1)=x=V(x),\quad
 U(x-1)=x-1=U(x)-1,\quad U=V.
\]

Damit sind sämtliche Verpflichtungen erfüllt, einschließlich des
Randfalls x=1. V und U sind global unbeschränkt, aber auf V <= r gilt
U <= floor(r). Das ist genau der Zweck der Sublevel-Bedingung.

**Warum das ein AST- und kein PAST-Beispiel ist:** Für festen Startwert
x > 0 und N > x sei tau die erste Ankunft in {0,N}. Die Funktion
h_N(x)=x(N-x) erfüllt h_N(0)=h_N(N)=0 und

\[
 h_N(x)=1+\tfrac12h_N(x-1)+\tfrac12h_N(x+1).
\]

Sie ist die erwartete Austrittszeit aus dem endlichen Intervall. Diese
Austrittszeit ist höchstens die Zeit T0 bis zum Erreichen von 0. Daher
E[T0] >= x(N-x) für jedes N > x, also E[T0]=unendlich. Unser Zertifikat
beweist dennoch AST. Insbesondere ist V ein Martingal ohne strikt
negativen Erwartungsdrift.

## 5. Beispiel: Fast Dice Roller mit symbolischem n

```text
v := 1; c := 0
while v < n:
    v := 2*v
    c := 2*c  [1/2]  c := 2*c+1
    if c >= n:
        v := v-n; c := c-n
```

**Domäne:** n,v,c sind ganzzahlig; n >= 1 bleibt konstant. Wir verwenden

\[
 S:\quad n\ge1,\quad 1\le v<2n,\quad0\le c<v,\quad c<n.
\]

Initialisierung und Erhaltung wurden unabhängig SMT-geprüft. Im
Randfall n=1 ist die Schleife schon am Anfang beendet.

**Ein-Schritt-Semantik:** Für Bit beta in {0,1} ist

\[
 T_\beta(n,v,c)=
 \begin{cases}
 (n,2v-n,2c+\beta-n),&2c+\beta\ge n,\\
 (n,2v,2c+\beta),&2c+\beta<n.
 \end{cases}
\]

Diese zwei Ausgänge enthalten bereits den gesamten Rumpf samt
bedingter Subtraktion. Es gibt keine Zertifikate für Zwischenpositionen.

**Templates:** je ein unabhängiger affiner Ausdruck über n,v,c, also
insgesamt acht unbekannte Koeffizienten; beide Funktionen sind außerhalb
des Guards null.

**Aufgezeichneter Lauf des gemeinsamen Synthesekerns:**

| Runde | V | U | Gegenbeispiel (n,v,c) / Ergebnis |
|---|---|---|---|
| 1 | 1 | v | (3,1,0): kein Abstieg |
| 2 | n | 1-c | (4,2,1): U=0 auf aktivem Zustand, kein Abstieg |
| 3 | n | n-c | (4,3,2): kein Abstieg |
| 4 | n | n-v+c | alle Verpflichtungen universell verifiziert |

Alle Tabellenformeln gelten auf aktiven Zuständen. Beispielsweise führt
das dritte Gegenbeispiel zu den Nachfolgern (4,2,0) und (4,2,1). Der
Kandidat U=n-c wächst dabei von 2 auf 4 beziehungsweise 3. Die
Gegenbeispiele sind deshalb auch didaktisch nützlich: Das Zählen über c
allein ignoriert die Rücksetzungen. Die Differenz v-c übersteht sie.

**Ergebnis:**

\[
 V=[v<n]n,\qquad U=[v<n](n-v+c),\qquad\varepsilon=1/2.
\]

**Analytische Verifikation:** Setze d=v-c. Auf aktiven Zuständen ist
1 <= d <= n-1, folglich 1 <= U=n-d <= n-1 < V=n.
Jeder Nachfolger besitzt V entweder n oder 0; deshalb gilt E[V'] <= V.

Für Bit 0 ist d'=2d, unabhängig davon, ob danach n von beiden Variablen
abgezogen wird. Läuft die Schleife weiter, ist

\[
 U'=n-2d=U-d\le U-1.
\]

Terminiert sie, ist U'=0 < U. Bit 0 hat Wahrscheinlichkeit 1/2.
Zusammen mit U <= V ist damit die gesamte AST-Regel erfüllt.

**Vorteil für die Synthese:** Ein einziges Template fester Größe liefert
Koeffizienten, die für alle n >= 1 funktionieren. Die logarithmische
Variante des manuellen Beweises ist für qualitative AST nicht nötig.
Die affine Variante hat allerdings eine gröbere Größenbeschränkung;
wir behaupten keine Verbesserung quantitativer Laufzeitschranken.

**Kritische Einordnung:** Für Bit 1 gilt bei Fortsetzung d'=2d-1 >= d,
also U' <= U. Deshalb gilt sogar E[U'] <= U-1/2. Dies wurde zusätzlich
SMT-geprüft. FDR zeigt somit noch nicht, dass zwei getrennte Zertifikate
gegenüber vorhandener Ranking-Supermartingal-Synthese notwendig sind.
Auch beim Random Walk fallen die zwei Funktionen zusammen. Ein weiteres
Beispiel, etwa FLDR mit einer bei Rücksetzung im Erwartungswert wachsenden
natürlichen Variante, wäre für diese spezifische Story aussagekräftiger.

## 6. Platzierung im Paper

Sobald ein wohldefiniertes Verfahren für einen ausdrücklich beschriebenen
Programm- und Templatebereich samt Soundness-Aussage vorliegt, empfiehlt
sich eine eigene Section nach der Metatheorie:

1. Introduction
2. Preliminaries
3. AST Certificates for Probabilistic Control-Flow Graphs
4. A Program-Level Rule for AST
5. Soundness and Relative Completeness
6. Template-Based Certificate Synthesis
   - Supported Fragment and Certificate Templates
   - Constraint Generation and Soundness
   - Counterexample-Guided Synthesis
7. The One-Dimensional Random Walk
8. Case Studies: Exact Sampling from Fair Bits
9. Related Work
10. Conclusion and Future Work

Die beiden Beispiele sollten langfristig in den jeweiligen
Beispielabschnitten ihre gefundenen Zertifikate und Syntheseergebnisse
zeigen. Den allgemeinen Mechanismus erklären wir einmal in Section 6.
Umfassendere Messungen rechtfertigen später eine Evaluations-Subsection;
zwei sehr kleine Läufe allein sind noch keine breite Evaluation.

Zunächst etwa 2-3 Seiten für das Verfahren einplanen und die
Syntheseergebnisse in vorhandene Beweise integrieren. Vollständige
Kandidatenlisten, Implementierungsdetails und Solverprotokolle können
ins Supplement. Der hier beigelegte Entwurf enthält alle Ausführungen
zusammen, damit sie gemeinsam überprüfbar sind; er ist noch keine
auf das finale Seitenbudget gekürzte Fassung.

Wenn es bei zwei spezifischen Machbarkeitsbeispielen bleibt, passt eine
Subsection über vorläufige Automatisierung besser als eine als allgemeine
Contribution präsentierte große Section. Die allgemeine relative
Vollständigkeit der AST-Regel darf nicht auf die Synthese übertragen werden.

## 7. Bezug zu Darions Ansatz und offene Punkte

Darions Section 6.2 dient als Vorbild für das Prinzip Template, symbolischer
Semantikschritt, Parameterbedingungen, Validierung. Dort werden rationale
Generating Functions für Occupation Measures gesucht. Unsere endlichen
Ein-Schritt-Ausgänge und affinen Zustandsfunktionen erlauben einen anderen
Constraint-Backend. Der gemeinsame Kern ist die Zertifikatssuche über
eine ganze Iteration; Generating Functions werden hier nicht eingesetzt.

CEGIS und affine Zertifikatssynthese sind bestehende Techniken. Vor einem
Neuheitsanspruch muss der spezielle Beitrag der gemeinsamen V/U-Suche
mit probabilistischem Abstieg und Sublevel-Beschränktheit gegenüber
verwandten Verfahren abgegrenzt werden. Ein relevanter Ausgangspunkt ist
Batz et al., *Probabilistic Program Verification via Inductive Synthesis
of Inductive Invariants*, https://arxiv.org/abs/2205.06152.

Nächste Sachfragen: automatische Extraktion der Ein-Schritt-Semantik aus
dem gewählten Sprachfragment, ausdrucksstärkere Templates und
Beschränktheitszertifikate, FLDR mit expliziten Strukturannahmen sowie
Beispiele, an denen die separate Variante gegenüber einer einzelnen
Ranking-Supermartingalfunktion praktisch hilft.
