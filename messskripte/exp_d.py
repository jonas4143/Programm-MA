"""
exp_d.py
Erreichte Suchtiefe von bester_zug (5 s, Cache vor jeder Stellung geleert)
in den Stellungen der Beispielpartie 2, 2, 1, 3, 2, 1, 3, 0
nach 0 bis 8 Steinen. Spieler 1 beginnt; berechnet wird jeweils fuer den
Spieler, der gerade am Zug ist (Werte immer aus Sicht von Spieler 1).
"""

import time

from harness import (engine, out, fmt, knoten, knoten_reset, bewertung_text,
                     brett_aus_zuegen, brett_text, freie_felder)

ZEITLIMIT = 5.0
ZUGFOLGE = [2, 2, 1, 3, 2, 1, 3, 0]


def main():
    out(f"Suchtiefe in der Beispielpartie {ZUGFOLGE}, {ZEITLIMIT:g} s je Stellung, leerer Cache\n")
    tabelle = []
    for steine in range(len(ZUGFOLGE) + 1):
        brett, spieler = brett_aus_zuegen(ZUGFOLGE[:steine])
        frei = freie_felder(brett)
        out(f"Nach {steine} Steinen (Zuege {ZUGFOLGE[:steine]}), Spieler {spieler} am Zug:")
        out(brett_text(brett))

        engine.CACHE.clear()
        knoten_reset()
        t0 = time.perf_counter()
        wert, spalte, tiefe = engine.bester_zug(brett, spieler, ZEITLIMIT)
        dt = time.perf_counter() - t0
        out(f"  -> Tiefe {tiefe:2d} von max. {frei} | Spalte {spalte} | Wert {wert} ({bewertung_text(wert)}) | "
            f"{fmt(knoten())} Knoten | Cache {fmt(len(engine.CACHE))} | {dt:.2f} s\n")
        tabelle.append((steine, spieler, tiefe, frei, spalte, wert, dt))

    out("Zusammenfassung")
    out(f"  {'Steine':>6} | {'am Zug':>6} | {'Tiefe':>5} | {'frei':>4} | {'Spalte':>6} | {'Wert':>7} | {'Zeit':>6}")
    for steine, spieler, tiefe, frei, spalte, wert, dt in tabelle:
        out(f"  {steine:>6} | {spieler:>6} | {tiefe:>5} | {frei:>4} | {str(spalte):>6} | {wert:>7} | {dt:>6.2f}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out("\nAbgebrochen (Strg+C).")
