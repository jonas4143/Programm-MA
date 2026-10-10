"""
harness.py - gemeinsame Grundlage aller Messskripte.

- ersetzt pygame durch ein leeres Platzhaltermodul (sys.modules),
  damit engine.py ohne installiertes pygame importiert werden kann
- importiert engine.py (unveraendertes Original)
- zaehlt alle Aufrufe von engine.minimax mit (auch die rekursiven)
- Hilfsfunktionen fuer Ausgabe, Stellungen und Fortschrittsanzeige
"""

import os
import sys
import threading
import time
import types

# Windows-Konsole: nicht darstellbare Zeichen ersetzen statt abzustuerzen
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

# --- pygame durch leeres Platzhaltermodul ersetzen ----------------------
sys.modules["pygame"] = types.ModuleType("pygame")

_ORDNER = os.path.dirname(os.path.abspath(__file__))
if _ORDNER not in sys.path:
    sys.path.insert(0, _ORDNER)

import engine  # noqa: E402  (muss nach dem Platzhalter importiert werden)
import loeser  # noqa: E402  (unabhaengiger Loeser, nutzt die Engine nicht)

# --- Knotenzaehler fuer minimax -----------------------------------------
# minimax ruft sich selbst ueber den globalen Namen "minimax" im Modul
# engine auf, ebenso bester_zug(). Ersetzt man engine.minimax durch eine
# zaehlende Huelle, laufen deshalb ALLE Aufrufe (auch rekursive) durch sie.
ZAEHLER = {"minimax": 0}
_minimax_original = engine.minimax


def _minimax_gezaehlt(*args, **kwargs):
    ZAEHLER["minimax"] += 1
    return _minimax_original(*args, **kwargs)


engine.minimax = _minimax_gezaehlt


def knoten():
    return ZAEHLER["minimax"]


def knoten_reset():
    ZAEHLER["minimax"] = 0


# --- Ausgabe -------------------------------------------------------------
def out(*args, **kwargs):
    """print mit sofortigem flush (fortlaufende Ausgabe im Terminal)."""
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)


def fmt(n):
    """Tausendertrennzeichen im Schweizer Stil: 1'234'567"""
    return f"{n:,}".replace(",", "'")


WDL = {1: "Sieg", 0: "Remis", -1: "Niederlage"}
WDL_KURZ = {1: "S", 0: "R", -1: "N"}


def ergebnis_p1(wert):
    """Deutet einen EXAKTEN Engine-Wert (Engine rechnet immer aus Sicht von Spieler 1)."""
    if wert is None:
        return "?"
    if wert >= 1:
        return "Sieg Spieler 1"
    if wert <= -1:
        return "Sieg Spieler 2"
    return "Remis"


def vorzeichen(wert):
    return (wert > 0) - (wert < 0)


def bewertung_text(wert):
    """Deutet einen Wert aus bester_zug(): bewiesen oder heuristisch."""
    if wert is None:
        return "?"
    if wert >= engine.SIEG_SCHWELLE:
        return "bewiesener Sieg Sp.1"
    if wert <= -engine.SIEG_SCHWELLE:
        return "bewiesener Sieg Sp.2"
    return "heuristisch"


# --- Stellungen ----------------------------------------------------------
def freie_felder(brett):
    return sum(1 for zeile in brett for feld in zeile if feld == 0)


def am_zug(brett):
    """Spieler am Zug unter der Annahme, dass Spieler 1 begonnen hat."""
    n1 = sum(1 for zeile in brett for feld in zeile if feld == 1)
    n2 = sum(1 for zeile in brett for feld in zeile if feld == 2)
    return 1 if n1 == n2 else 2


def brett_aus_zuegen(zuege):
    """Spielt eine Zugfolge (Spalten) ab, Spieler 1 beginnt. -> (brett, am_zug)"""
    brett = engine.erstelle_brett()
    spieler = 1
    for spalte in zuege:
        engine.stein_setzen(brett, spalte, spieler)
        spieler = 3 - spieler
    return brett, spieler


def brett_text(brett, einrueckung="    "):
    zeichen = {0: ".", 1: "X", 2: "O"}
    zeilen = [einrueckung + " ".join(zeichen[f] for f in zeile) for zeile in brett]
    zeilen.append(einrueckung + " ".join(str(s) for s in range(engine.SPALTEN)))
    return "\n".join(zeilen)


def zufallsstellung(rng, steine):
    """
    Spielt 'steine' zufaellige Zuege (Spieler 1 beginnt).
    Gibt (brett, am_zug) zurueck oder None, wenn die Stellung entschieden
    (4 in einer Reihe) oder voll ist -> verwerfen.
    """
    brett = engine.erstelle_brett()
    spieler = 1
    for _ in range(steine):
        frei = [s for s in range(engine.SPALTEN) if engine.spalte_frei(brett, s)]
        if not frei:
            return None
        engine.stein_setzen(brett, rng.choice(frei), spieler)
        spieler = 3 - spieler
    cur, mask = loeser.aus_brett(brett, spieler)
    if loeser.entschieden(cur, mask) or mask == loeser.VOLL:
        return None
    return brett, spieler


# --- Fortschrittsanzeige -------------------------------------------------
class Fortschritt:
    """
    Gibt waehrend einer langen Rechnung alle 'intervall' Sekunden eine
    Statuszeile aus (Hintergrund-Thread). Verwendung:
        with Fortschritt(10):
            ... lange Rechnung ...
    """

    def __init__(self, intervall=10.0, info=None):
        self.intervall = intervall
        self.info = info or (lambda: f"{fmt(knoten())} Knoten, Cache {fmt(len(engine.CACHE))}")

    def __enter__(self):
        self.start = time.perf_counter()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._lauf, daemon=True)
        self._thread.start()
        return self

    def _lauf(self):
        while not self._stop.wait(self.intervall):
            dt = time.perf_counter() - self.start
            out(f"      ... {dt:7.0f} s: {self.info()}")

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        return False
