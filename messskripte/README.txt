MESSSKRIPTE ZUM 4-GEWINNT-PROGRAMM (5x5)
========================================

Voraussetzungen
---------------
- Python 3.8 oder neuer, keine Zusatzpakete (auch kein pygame).
- Alle Dateien im selben Ordner lassen. Im Ordner eine Eingabeaufforderung
  oder PowerShell oeffnen und die Skripte wie unten starten
  ("py" ist der Windows-Python-Starter; "python" geht ebenso).
- Jedes Skript gibt laufend im Terminal aus. Abbruch mit Strg+C
  (die meisten Skripte zeigen dann noch, was bis dahin fertig ist).
- Ausgabe in eine Datei speichern:  py exp_c.py > exp_c.txt

Dateien (keine Messskripte)
---------------------------
engine.py    Dein Programm, unveraendert kopiert.
harness.py   Ersetzt pygame per sys.modules durch ein leeres Platzhaltermodul,
             importiert engine.py und zaehlt jeden Aufruf von minimax
             ("Knoten", auch rekursive und solche aus bester_zug).
             Dazu Hilfsfunktionen (Ausgabe, Zufallsstellungen, Fortschritt).
loeser.py    Unabhaengiger exakter Loeser: Negamax mit Alpha-Beta und Memo,
             eigene Bitboard-Darstellung und eigene Siegpruefung, benutzt
             keine Funktion der Engine. Werte +1/0/-1 = Sieg/Remis/Niederlage
             fuer den Spieler am Zug. Spiegelstellungen teilen einen Eintrag.
partien.py   Gemeinsame Logik fuer exp_e.py und exp_h.py (Gegner, Partien).

Wichtig zur Deutung: Die Engine bewertet IMMER aus Sicht von Spieler 1
(ICH, Rot). Positive Werte = gut fuer Spieler 1. Werte ab 98'000
(SIEG_SCHWELLE) sind bewiesene Siege, kleinere Werte sind heuristisch.


1. full.py
----------
Aufruf:   py full.py <Sekunden>          Beispiel: py full.py 3600
Exakte Loesung des leeren Feldes mit minimax: Tiefe 25, Nullfenster
alpha=-1, beta=1, Cache vorher geleert. Alle 10 s eine Fortschrittszeile.
Ausgabe: Wert (>=1 Sieg Sp.1, 0 Remis, <=-1 Sieg Sp.2), Spalte, Zeit,
Knoten, Cache-Groesse. Bei Zeitueberschreitung: Knoten und Cache bis dahin.
Laufzeit: unbekannt, kann sehr lang sein (Minuten bis Stunden).

2. exp_b.py
-----------
Aufruf:   py exp_b.py
Exakter Wert nach jedem der 5 Eroeffnungszuege von Spieler 1 (danach rechnet
minimax mit Spieler 2 am Zug bis zum Spielende, Nullfenster -1/1). Die fuenf
Rechnungen teilen sich engine.CACHE (nur zu Beginn geleert) - spaetere
Spalten profitieren also von frueheren. Ausgabe je Spalte: Ergebnis aus
Sicht Spieler 1, Wert, Antwortspalte von Spieler 2, Knoten, Zeit, Cache.
Kein Zeitlimit; ebenfalls potenziell sehr lang.

3. exp_c.py
-----------
Aufruf:   py exp_c.py
Leeres Feld, feste Tiefe 2 bis 10. Pro Tiefe vier Varianten:
  A  reines Minimax, Spalten 0..4 (nur bis Tiefe 8)
  B  Alpha-Beta, Spalten 0..4
  C  Alpha-Beta, Mittelreihenfolge 2,1,3,0,4
  D  Engine-minimax mit Cache (Cache vor jeder Tiefe geleert)
A bis C sind im Skript nachgebaut, benutzen aber die Engine-Bausteine
(Siegpruefung, bewerte_stellung usw.). Ausgabe: Knoten, Zeit, Bewertung,
Spalte und ob alle Bewertungen gleich sind (sie muessen es sein), am Ende
eine Knoten-/Zeit-Tabelle. Variante A bei Tiefe 8 dauert am laengsten.

4. exp_d1.py
------------
Aufruf:   py exp_d1.py
bester_zug auf dem leeren Feld, 5 s, dreimal hintereinander. Der Cache wird
nur vor dem ersten Lauf geleert. Ausgabe je Lauf: Wert, Spalte, erreichte
Tiefe, Cache-Groesse, Knoten, Zeit. Laufzeit ca. 15 s.

5. exp_d.py
-----------
Aufruf:   py exp_d.py
Beispielpartie 2, 2, 1, 3, 2, 1, 3, 0 (Spieler 1 beginnt). Fuer die Stellung
nach 0, 1, ..., 8 Steinen: bester_zug fuer den Spieler am Zug, 5 s, Cache
jeweils vorher geleert. Ausgabe: Brett (X = Sp.1, O = Sp.2), erreichte
Tiefe, maximal moegliche Tiefe (freie Felder), Spalte, Wert, Knoten.
Laufzeit ca. 45 s.

6. exp_f.py
-----------
Aufruf:   py exp_f.py <Anzahl> <max. Sekunden>     Beispiel: py exp_f.py 100 60
Zufallsstellungen mit 9 bis 17 Steinen (Seed 2026, Spieler 1 hat begonnen);
entschiedene (4 in einer Reihe) und volle Stellungen werden verworfen.
Jede Stellung wird vom unabhaengigen Loeser und von der Engine (minimax bis
Spielende, Nullfenster -1/1, eigener Cache fuer den ganzen Lauf) geloest.
<max. Sekunden> ist das Zeitlimit der Engine pro Stellung; wird es
ueberschritten, zaehlt die Stellung als "Zeitlimit" statt als Vergleich.
Ausgabe je Stellung: Steine, Spieler am Zug, Ergebnis Loeser und Engine
(S/R/N aus Sicht des Spielers am Zug), Zeiten, ok/ABWEICHUNG.
Am Ende: Uebereinstimmungen, Verteilung Sieg/Remis/Niederlage, Bretter
allfaelliger Abweichungen.

7. exp_g.py
-----------
Aufruf:   py exp_g.py
24 Zufallsstellungen (Seed 11) mit 4, 6, ..., 14 Steinen, also immer
Spieler 1 am Zug. Der Loeser berechnet den exakten Wert jedes Zuges (Zeile
"Werte [S R N - ...]" fuer Spalten 0..4, '-' = voll). Dann bester_zug mit
5 s (Cache vorher geleert); "optimal" heisst: die empfohlene Spalte hat
den besten Wert. Am Ende die Summe und alle nicht optimalen Faelle.
Hinweis: Stellungen mit wenig Steinen koennen fuer den Loeser einige
Minuten dauern; das Memo wird weiterverwendet, spaeter geht es schneller.

8. exp_e.py
-----------
Aufruf:   py exp_e.py <Zeitlimit>          Beispiel: py exp_e.py 5
Testpartien, Programm = bester_zug mit <Zeitlimit> s pro Zug. Gegner:
  Zufall   zufaelliger legaler Zug
  Gierig   gewinnt sofort, sonst blockiert einen Sofortsieg, sonst zufaellig
  Perfekt  zufaellig unter den besten Zuegen laut exaktem Loeser
Partien PRO ROLLE: Zufall 20, Gierig 20, Perfekt 10 - also je einmal mit
und einmal ohne Anzugsrecht des Programms (insgesamt 100 Partien).
Seed 7 (ein gemeinsamer Zufallsgenerator).
Das Programm spielt immer die Steine von Spieler 1 (wie in engine.py);
"ohne Anzugsrecht" = der Gegner setzt zuerst (wie ICH_BEGINNT = False).
engine.CACHE wird vor jeder Partie geleert (wie ein frischer Programmstart).
Ausgabe je Partie: Ergebnis aus Sicht des Programms, Anzahl Steine bei
Partieende, durchschnittliche erreichte Suchtiefe, Dauer, Zugfolge.
Am Ende eine Tabelle pro Gegner und Rolle.
Laufzeit bei 5 s: grob 1-2 Stunden (plus Rechenzeit des perfekten Gegners;
dessen erster Zug kann einige Minuten brauchen, danach hilft das Memo).
Die Anzahl Partien laesst sich oben im Skript (SERIEN) aendern.

   exp_h.py
   --------
Aufruf:   py exp_h.py
Nur gegen den perfekten Gegner, 5 s pro Programmzug, je 6 Partien mit und
ohne Anzugsrecht (Seed 7). Ausgabe wie exp_e.py.

Speicherbedarf: Cache und Memo werden bei langen Laeufen (full.py, exp_b.py,
exp_f.py, perfekter Gegner) gross - einige hundert MB sind moeglich.
