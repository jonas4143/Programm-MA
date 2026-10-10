"""
exp_h.py
Nur gegen den perfekten Gegner: 5 s pro Programmzug, je 6 Partien mit und
ohne Anzugsrecht des Programms (Seed 7).
"""

import random

from harness import out
from partien import serie, zusammenfassung

SEED = 7
ZEITLIMIT = 5.0
PARTIEN_PRO_ROLLE = 6


def main():
    rng = random.Random(SEED)
    out(f"Programm vs. perfekter Gegner, {ZEITLIMIT:g} s pro Programmzug, Seed {SEED}")
    alle = []
    try:
        for programm_beginnt in (True, False):
            alle += serie("Perfekt", PARTIEN_PRO_ROLLE, programm_beginnt, ZEITLIMIT, rng,
                          start_nr=len(alle) + 1)
    except KeyboardInterrupt:
        out("\nAbgebrochen (Strg+C) - Zusammenfassung der fertigen Partien:")
    zusammenfassung(alle)


if __name__ == "__main__":
    main()
