"""
exp_f.py <Anzahl> <max. Sekunden>
Vergleicht die Engine (minimax bis Spielende, Nullfenster -1/1) mit dem
unabhaengigen Negamax-Loeser (loeser.py) auf Zufallsstellungen mit
9 bis 17 Steinen (Seed 2026). Entschiedene und volle Stellungen werden
verworfen. <max. Sekunden> = Zeitlimit der Engine pro Stellung; wird es
ueberschritten, zaehlt die Stellung als "Zeitlimit" und nicht als Vergleich.
"""

import random
import sys
import time

from harness import (engine, loeser, out, fmt, knoten, knoten_reset, zufallsstellung,
                     freie_felder, vorzeichen, WDL, WDL_KURZ)

SEED = 2026
MIN_STEINE, MAX_STEINE = 9, 17


def main():
    if len(sys.argv) < 3:
        out("Aufruf: python exp_f.py <Anzahl> <max. Sekunden>")
        sys.exit(1)
    anzahl = int(sys.argv[1])
    max_sek = float(sys.argv[2])

    rng = random.Random(SEED)
    cache = {}                       # eigener Engine-Cache fuer diesen Lauf
    gleich = verglichen = zeitlimit = verworfen = 0
    verteilung = {1: 0, 0: 0, -1: 0}
    abweichungen = []

    out(f"Engine vs. unabhaengiger Loeser, {anzahl} Stellungen, {MIN_STEINE}-{MAX_STEINE} Steine, "
        f"Seed {SEED}, Engine-Limit {max_sek:g} s")
    out("Werte aus Sicht des Spielers am Zug (S/R/N)\n")

    nr = 0
    while nr < anzahl:
        steine = rng.randint(MIN_STEINE, MAX_STEINE)
        pos = zufallsstellung(rng, steine)
        if pos is None:
            verworfen += 1
            continue
        nr += 1
        brett, spieler = pos

        # unabhaengiger Loeser
        cur, mask = loeser.aus_brett(brett, spieler)
        loeser.STAT["knoten"] = 0
        t0 = time.perf_counter()
        w_loeser = loeser.wert(cur, mask)
        dt_l = time.perf_counter() - t0
        verteilung[w_loeser] += 1

        # Engine (volle Tiefe)
        frei = freie_felder(brett)
        knoten_reset()
        t0 = time.perf_counter()
        try:
            w_eng, _ = engine.minimax(brett, spieler, -1, 1, 0, frei, None,
                                      time.time() + max_sek, cache)
        except engine.Zeitlimit:
            w_eng = None
        dt_e = time.perf_counter() - t0

        kopf = (f"  {nr:4d} | {steine:2d} Steine | Sp.{spieler} am Zug | "
                f"Loeser {WDL_KURZ[w_loeser]} ({dt_l:6.2f} s)")
        if w_eng is None:
            zeitlimit += 1
            out(f"{kopf} | Engine Zeitlimit ({dt_e:6.2f} s, {fmt(knoten())} Knoten)")
            continue

        # Engine-Wert ist aus Sicht von Spieler 1 -> auf Spieler am Zug umrechnen
        w_eng_rel = vorzeichen(w_eng) if spieler == engine.ICH else -vorzeichen(w_eng)
        verglichen += 1
        ok = w_eng_rel == w_loeser
        if ok:
            gleich += 1
        else:
            abweichungen.append((nr, steine, spieler, w_loeser, w_eng_rel, brett))
        out(f"{kopf} | Engine {WDL_KURZ[w_eng_rel]} ({dt_e:6.2f} s, {fmt(knoten()):>10} Knoten) | "
            f"{'ok' if ok else 'ABWEICHUNG'}")

    out("\nZusammenfassung")
    out(f"  Stellungen:             {anzahl}  (verworfen: {verworfen})")
    out(f"  verglichen:             {verglichen}  (Zeitlimit: {zeitlimit})")
    out(f"  Uebereinstimmungen:     {gleich} / {verglichen}")
    out("  Verteilung (Loeser, Sicht Spieler am Zug):")
    for w in (1, 0, -1):
        anteil = 100 * verteilung[w] / anzahl if anzahl else 0
        out(f"    {WDL[w]:10s} {verteilung[w]:5d}  ({anteil:5.1f} %)")
    out(f"  Engine-Cache: {fmt(len(cache))} | Loeser-Memo: {fmt(len(loeser.MEMO))}")
    for nr, steine, spieler, wl, we, brett in abweichungen:
        out(f"\n  Abweichung Stellung {nr} ({steine} Steine, Sp.{spieler} am Zug): "
            f"Loeser {WDL[wl]}, Engine {WDL[we]}")
        out("    Brett (Zeile 0 oben): " + str(brett))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out("\nAbgebrochen (Strg+C).")
