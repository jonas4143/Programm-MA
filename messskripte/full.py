"""
full.py <Sekunden>
Exakte Loesung des leeren 5x5-Feldes mit der Engine-Funktion minimax:
Tiefe 25 (ganzes Spiel), Nullfenster alpha=-1, beta=1, leerer Cache.
"""

import sys
import time

from harness import engine, out, fmt, knoten, knoten_reset, Fortschritt, ergebnis_p1


def main():
    if len(sys.argv) < 2:
        out("Aufruf: python full.py <Sekunden>")
        sys.exit(1)
    sekunden = float(sys.argv[1])
    tiefe = engine.ZEILEN * engine.SPALTEN

    brett = engine.erstelle_brett()
    engine.CACHE.clear()
    knoten_reset()

    out(f"Exakte Loesung des leeren {engine.SPALTEN}x{engine.ZEILEN}-Feldes")
    out(f"  Tiefe {tiefe}, Fenster (-1, 1), Zeitlimit {sekunden:g} s")
    out("  Fortschritt alle 10 s:")

    t0 = time.perf_counter()
    try:
        with Fortschritt(10):
            wert, spalte = engine.minimax(
                brett, engine.ICH, -1, 1, 0, tiefe, None, time.time() + sekunden, engine.CACHE,
            )
    except engine.Zeitlimit:
        dt = time.perf_counter() - t0
        out(f"\nZeitlimit erreicht nach {dt:.1f} s - keine Loesung.")
        out(f"  Knoten:      {fmt(knoten())}")
        out(f"  Cache-Groesse: {fmt(len(engine.CACHE))}")
        return
    dt = time.perf_counter() - t0

    out("\nErgebnis")
    out(f"  Wert:          {wert}  ->  {ergebnis_p1(wert)} (bei perfektem Spiel)")
    out(f"  Spalte:        {spalte}")
    out(f"  Zeit:          {dt:.1f} s")
    out(f"  Knoten:        {fmt(knoten())}")
    out(f"  Cache-Groesse: {fmt(len(engine.CACHE))}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out(f"\nAbgebrochen (Strg+C). Knoten bisher: {fmt(knoten())}")
