"""
exp_c.py
Leeres Feld, feste Suchtiefe 2 bis 10, vier Varianten:
  A  reines Minimax, Spalten 0..4          (nur bis Tiefe 8)
  B  Alpha-Beta, Spalten 0..4
  C  Alpha-Beta, Mittelreihenfolge (2,1,3,0,4)
  D  Engine-minimax mit Cache (Cache vor jeder Tiefe geleert)
A-C sind hier nachgebaut, verwenden aber dieselben Engine-Bausteine
(stein_setzen, gewinn_durch_letzten_zug, brett_voll, bewerte_stellung)
und dieselben Siegwerte wie die Engine. Alle vier muessen dieselbe
Bewertung liefern; nur Knoten und Zeit unterscheiden sich.
"""

import math
import time

from harness import engine, out, fmt, knoten, knoten_reset

SPALTEN_LINKS = list(range(engine.SPALTEN))


def suche(brett, spieler_am_zug, alpha, beta, tiefe, max_tiefe, letzter_zug,
          reihenfolge, pruning, zaehler):
    zaehler[0] += 1
    if letzter_zug is not None:
        lz, ls, lsp = letzter_zug
        if engine.gewinn_durch_letzten_zug(brett, lz, ls, lsp):
            w = engine.GEWINN_WERT - tiefe
            return (w if lsp == engine.ICH else -w), None
    if engine.brett_voll(brett):
        return 0, None
    if tiefe >= max_tiefe:
        return engine.bewerte_stellung(brett), None

    maxi = spieler_am_zug == engine.ICH
    naechster = engine.GEGNER if maxi else engine.ICH
    wert = -math.inf if maxi else math.inf
    beste = None
    for s in reihenfolge:
        if not engine.spalte_frei(brett, s):
            continue
        zeile, _ = engine.stein_setzen(brett, s, spieler_am_zug)
        try:
            w, _ = suche(brett, naechster, alpha, beta, tiefe + 1, max_tiefe,
                         (zeile, s, spieler_am_zug), reihenfolge, pruning, zaehler)
        finally:
            engine.stein_zurueckziehen(brett, zeile, s)
        if maxi:
            if w > wert:
                wert, beste = w, s
            alpha = max(alpha, wert)
        else:
            if w < wert:
                wert, beste = w, s
            beta = min(beta, wert)
        if pruning and alpha >= beta:
            break
    return wert, beste


def variante_nachbau(tiefe, reihenfolge, pruning):
    brett = engine.erstelle_brett()
    z = [0]
    t0 = time.perf_counter()
    wert, spalte = suche(brett, engine.ICH, -math.inf, math.inf, 0, tiefe, None,
                         reihenfolge, pruning, z)
    return z[0], time.perf_counter() - t0, wert, spalte


def variante_engine(tiefe):
    brett = engine.erstelle_brett()
    engine.CACHE.clear()
    knoten_reset()
    t0 = time.perf_counter()
    wert, spalte = engine.minimax(brett, engine.ICH, -math.inf, math.inf, 0, tiefe,
                                  None, math.inf, engine.CACHE)
    return knoten(), time.perf_counter() - t0, wert, spalte


def zeile(kuerzel, name, k, dt, wert, spalte, extra=""):
    out(f"  {kuerzel}  {name:28s} | {fmt(k):>13} Knoten | {dt:9.3f} s | Bewertung {wert:>7} | Spalte {spalte}{extra}")


def main():
    out("Feste Suchtiefe auf dem leeren Feld: Knoten, Zeit, Bewertung (Sicht Spieler 1)")
    tabelle = []
    for tiefe in range(2, 11):
        out(f"\nTiefe {tiefe}")
        werte = []
        reihe = {"tiefe": tiefe}

        if tiefe <= 8:
            k, dt, w, s = variante_nachbau(tiefe, SPALTEN_LINKS, False)
            zeile("A", "Minimax", k, dt, w, s)
            werte.append(w)
            reihe["A"] = (k, dt)
        else:
            out("  A  Minimax                      | uebersprungen (nur bis Tiefe 8)")

        k, dt, w, s = variante_nachbau(tiefe, SPALTEN_LINKS, True)
        zeile("B", "Alpha-Beta, Spalten 0..4", k, dt, w, s)
        werte.append(w)
        reihe["B"] = (k, dt)

        k, dt, w, s = variante_nachbau(tiefe, engine.SPALTEN_REIHENFOLGE, True)
        zeile("C", "Alpha-Beta, Mitte zuerst", k, dt, w, s)
        werte.append(w)
        reihe["C"] = (k, dt)

        k, dt, w, s = variante_engine(tiefe)
        zeile("D", "Engine mit Cache", k, dt, w, s, f" | Cache {fmt(len(engine.CACHE))}")
        werte.append(w)
        reihe["D"] = (k, dt)

        out(f"  Bewertungen identisch: {'ja' if len(set(werte)) == 1 else 'NEIN ' + str(werte)}")
        tabelle.append(reihe)

    out("\nZusammenfassung Knoten (Zeit in s)")
    out(f"  {'Tiefe':>5} | " + " | ".join(f"{v:>24}" for v in "ABCD"))
    for reihe in tabelle:
        felder = []
        for v in "ABCD":
            if v in reihe:
                k, dt = reihe[v]
                felder.append(f"{fmt(k):>13} ({dt:7.2f})")
            else:
                felder.append(f"{'-':>24}")
        out(f"  {reihe['tiefe']:>5} | " + " | ".join(felder))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out("\nAbgebrochen (Strg+C).")
