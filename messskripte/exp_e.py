"""
exp_e.py <Zeitlimit>
Testpartien des Programms (bester_zug mit <Zeitlimit> Sekunden pro Zug)
gegen drei Gegner, jeweils mit und ohne Anzugsrecht des Programms:
  Zufall   20 Partien pro Rolle
  Gierig   20 Partien pro Rolle
  Perfekt  10 Partien pro Rolle
Ein gemeinsamer Zufallsgenerator mit Seed 7 fuer alle Gegner.
"""

import random
import sys

from harness import out
from partien import serie, zusammenfassung

SEED = 7
SERIEN = [("Zufall", 20), ("Gierig", 20), ("Perfekt", 10)]   # Partien pro Rolle


def main():
    if len(sys.argv) < 2:
        out("Aufruf: python exp_e.py <Zeitlimit in Sekunden>")
        sys.exit(1)
    zeitlimit = float(sys.argv[1])
    rng = random.Random(SEED)
    out(f"Testpartien, Zeitlimit {zeitlimit:g} s pro Programmzug, Seed {SEED}")

    alle = []
    try:
        for name, anzahl in SERIEN:
            for programm_beginnt in (True, False):
                alle += serie(name, anzahl, programm_beginnt, zeitlimit, rng, start_nr=len(alle) + 1)
    except KeyboardInterrupt:
        out("\nAbgebrochen (Strg+C) - Zusammenfassung der fertigen Partien:")
    zusammenfassung(alle)


if __name__ == "__main__":
    main()
