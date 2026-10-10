"""
exp_b.py
Exakter Wert nach jedem der 5 Eroeffnungszuege von Spieler 1.
Danach ist Spieler 2 am Zug; minimax rechnet bis zum Spielende
(Tiefe 24, Nullfenster -1/1). Alle 5 Rechnungen teilen sich einen Cache
(engine.CACHE, nur zu Beginn einmal geleert).
"""

import math
import time

from harness import engine, out, fmt, knoten, knoten_reset, Fortschritt, ergebnis_p1


def main():
    engine.CACHE.clear()
    gesamt_tiefe = engine.ZEILEN * engine.SPALTEN - 1
    zeilen = []

    out("Exakter Wert nach jedem Eroeffnungszug (Sicht Spieler 1, gemeinsamer Cache)\n")
    for spalte in range(engine.SPALTEN):
        brett = engine.erstelle_brett()
        zeile, _ = engine.stein_setzen(brett, spalte, engine.ICH)

        out(f"Eroeffnung Spalte {spalte}: rechne ...")
        knoten_reset()
        t0 = time.perf_counter()
        with Fortschritt(10):
            wert, antwort = engine.minimax(
                brett, engine.GEGNER, -1, 1, 0, gesamt_tiefe,
                (zeile, spalte, engine.ICH), math.inf, engine.CACHE,
            )
        dt = time.perf_counter() - t0
        k = knoten()
        out(f"  Spalte {spalte}: {ergebnis_p1(wert):15s} (Wert {wert}, Antwort Sp.2: Spalte {antwort})"
            f" | {fmt(k)} Knoten | {dt:.1f} s | Cache {fmt(len(engine.CACHE))}\n")
        zeilen.append((spalte, ergebnis_p1(wert), wert, k, dt))

    out("Zusammenfassung")
    out(f"  {'Spalte':>6} | {'Ergebnis':15s} | {'Wert':>7} | {'Knoten':>15} | {'Zeit [s]':>9}")
    for spalte, erg, wert, k, dt in zeilen:
        out(f"  {spalte:>6} | {erg:15s} | {wert:>7} | {fmt(k):>15} | {dt:>9.1f}")
    out(f"  Cache am Ende: {fmt(len(engine.CACHE))}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out(f"\nAbgebrochen (Strg+C). Knoten in laufender Rechnung: {fmt(knoten())}")
