"""
exp_d1.py
bester_zug auf dem leeren Feld, Zeitlimit 5 s, dreimal hintereinander.
Der Cache wird nur VOR dem ersten Lauf geleert, danach waechst er weiter.
"""

import time

from harness import engine, out, fmt, knoten, knoten_reset, bewertung_text

ZEITLIMIT = 5.0
LAEUFE = 3


def main():
    engine.CACHE.clear()
    brett = engine.erstelle_brett()
    out(f"bester_zug auf leerem Feld, {ZEITLIMIT:g} s, {LAEUFE} Laeufe ohne Cache-Leerung\n")
    for lauf in range(1, LAEUFE + 1):
        knoten_reset()
        t0 = time.perf_counter()
        wert, spalte, tiefe = engine.bester_zug(brett, engine.ICH, ZEITLIMIT)
        dt = time.perf_counter() - t0
        out(f"  Lauf {lauf}: Wert {wert:>7} ({bewertung_text(wert)}) | Spalte {spalte} | "
            f"Tiefe {tiefe:2d} | Cache {fmt(len(engine.CACHE)):>11} | "
            f"{fmt(knoten()):>11} Knoten | {dt:.2f} s")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out("\nAbgebrochen (Strg+C).")
