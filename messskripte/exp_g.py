"""
exp_g.py
24 Zufallsstellungen (Seed 11), Spieler 1 am Zug, 4 bis 14 Steine
(gerade Anzahl, da Spieler 1 beginnt und am Zug sein soll).
Der unabhaengige Loeser berechnet den exakten Wert jedes Zuges; geprueft
wird, ob die Empfehlung von bester_zug (5 s, Cache vor jeder Stellung
geleert) einer der besten Zuege ist.
"""

import random
import time

from harness import (engine, loeser, out, fmt, knoten, knoten_reset, zufallsstellung,
                     bewertung_text, WDL, WDL_KURZ)

SEED = 11
ANZAHL = 24
STEINE = [4, 6, 8, 10, 12, 14]
ZEITLIMIT = 5.0


def main():
    rng = random.Random(SEED)
    optimal_anz = 0
    verworfen = 0
    fehler = []

    out(f"Optimalitaet von bester_zug ({ZEITLIMIT:g} s), {ANZAHL} Stellungen, Seed {SEED}")
    out("Zugwerte je Spalte 0..4 aus Sicht von Spieler 1 (S/R/N, '-' = Spalte voll)\n")

    nr = 0
    while nr < ANZAHL:
        steine = rng.choice(STEINE)
        pos = zufallsstellung(rng, steine)
        if pos is None:
            verworfen += 1
            continue
        nr += 1
        brett, spieler = pos           # spieler ist hier immer 1

        cur, mask = loeser.aus_brett(brett, spieler)
        t0 = time.perf_counter()
        werte = loeser.zugwerte(cur, mask)
        dt_l = time.perf_counter() - t0
        best = max(werte.values())
        wertzeile = " ".join(WDL_KURZ[werte[c]] if c in werte else "-" for c in range(engine.SPALTEN))

        engine.CACHE.clear()
        knoten_reset()
        t0 = time.perf_counter()
        wert, spalte, tiefe = engine.bester_zug(brett, engine.ICH, ZEITLIMIT)
        dt_e = time.perf_counter() - t0

        ok = spalte in werte and werte[spalte] == best
        if ok:
            optimal_anz += 1
        else:
            fehler.append((nr, steine, best, werte.get(spalte), spalte))
        gewaehlt = WDL_KURZ[werte[spalte]] if spalte in werte else "?"
        out(f"  {nr:2d} | {steine:2d} Steine | Werte [{wertzeile}] bestes {WDL_KURZ[best]} | "
            f"Engine Spalte {spalte} ({gewaehlt}), Tiefe {tiefe:2d}, Wert {wert} ({bewertung_text(wert)}) | "
            f"Loeser {dt_l:5.2f} s, Engine {dt_e:4.2f} s | {'optimal' if ok else 'NICHT optimal'}")

    out("\nSumme")
    out(f"  optimal:        {optimal_anz} / {ANZAHL}  (verworfene Zufallsstellungen: {verworfen})")
    out(f"  nicht optimal:  {len(fehler)}")
    for nr, steine, best, gew, spalte in fehler:
        gew_txt = WDL[gew] if gew is not None else "?"
        out(f"    Stellung {nr} ({steine} Steine): bestes {WDL[best]}, Engine waehlte Spalte {spalte} -> {gew_txt}")
    out(f"  Loeser-Memo: {fmt(len(loeser.MEMO))}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out("\nAbgebrochen (Strg+C).")
