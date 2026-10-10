"""
partien.py - gemeinsame Logik fuer exp_e.py und exp_h.py (kein eigenes Messskript).

Das Programm spielt immer mit den Steinen von Spieler 1 (ICH, Rot), so wie
engine.py es vorsieht. "Ohne Anzugsrecht" bedeutet: der Gegner (Spieler 2)
setzt den ersten Stein - wie ICH_BEGINNT = False im Originalprogramm.
Vor jeder Partie wird engine.CACHE geleert (wie ein frischer Programmstart).
Ob eine Partie gewonnen ist, prueft der unabhaengige Loeser (Schiedsrichter).
"""

import time

from harness import engine, loeser, out, fmt, Fortschritt

PROGRAMM = engine.ICH       # 1
GEGNER = engine.GEGNER      # 2


def freie_spalten(brett):
    return [s for s in range(engine.SPALTEN) if engine.spalte_frei(brett, s)]


# --- Gegner --------------------------------------------------------------
def gegner_zufall(brett, spieler, rng):
    return rng.choice(freie_spalten(brett))


def gegner_gierig(brett, spieler, rng):
    """Gewinnt sofort, wenn moeglich; blockiert sonst einen Sofortsieg; sonst zufaellig."""
    cur, mask = loeser.aus_brett(brett, spieler)
    sieg = loeser.gewinnzuege(cur, mask)
    if sieg:
        return rng.choice(sieg)
    block = loeser.gewinnzuege(cur ^ mask, mask)
    if block:
        return rng.choice(block)
    return rng.choice(freie_spalten(brett))


def gegner_perfekt(brett, spieler, rng):
    """Zufaellig unter den Zuegen mit dem besten exakten Wert (unabhaengiger Loeser)."""
    cur, mask = loeser.aus_brett(brett, spieler)
    info = lambda: f"perfekter Gegner rechnet: {fmt(loeser.STAT['knoten'])} Knoten, Memo {fmt(len(loeser.MEMO))}"
    with Fortschritt(15, info):
        werte = loeser.zugwerte(cur, mask)
    best = max(werte.values())
    return rng.choice(sorted(c for c, v in werte.items() if v == best))


GEGNER_FUNKTIONEN = {
    "Zufall": gegner_zufall,
    "Gierig": gegner_gierig,
    "Perfekt": gegner_perfekt,
}


# --- eine Partie ---------------------------------------------------------
def spiele_partie(gegner_fn, programm_beginnt, zeitlimit, rng):
    engine.CACHE.clear()
    brett = engine.erstelle_brett()
    am_zug = PROGRAMM if programm_beginnt else GEGNER
    tiefen = []
    folge = []
    notfall = 0
    t0 = time.perf_counter()

    while True:
        if am_zug == PROGRAMM:
            _, spalte, tiefe = engine.bester_zug(brett, PROGRAMM, zeitlimit)
            if spalte is None or not engine.spalte_frei(brett, spalte):
                # sollte nie vorkommen; nur damit die Partie weiterlaeuft
                spalte = next(s for s in engine.SPALTEN_REIHENFOLGE if engine.spalte_frei(brett, s))
                notfall += 1
            tiefen.append(tiefe)
        else:
            spalte = gegner_fn(brett, GEGNER, rng)

        engine.stein_setzen(brett, spalte, am_zug)
        folge.append(spalte)

        cur, mask = loeser.aus_brett(brett, am_zug)
        if loeser.vier(cur):
            ergebnis = "Sieg" if am_zug == PROGRAMM else "Niederlage"
            break
        if mask == loeser.VOLL:
            ergebnis = "Remis"
            break
        am_zug = GEGNER if am_zug == PROGRAMM else PROGRAMM

    return {
        "ergebnis": ergebnis,
        "zuege": len(folge),
        "tiefe": sum(tiefen) / len(tiefen) if tiefen else 0.0,
        "folge": folge,
        "notfall": notfall,
        "zeit": time.perf_counter() - t0,
    }


def serie(name, anzahl, programm_beginnt, zeitlimit, rng, start_nr=1):
    rolle = "Programm beginnt" if programm_beginnt else "Gegner beginnt"
    out(f"\n{name}, {rolle} ({anzahl} Partien)")
    ergebnisse = []
    for i in range(anzahl):
        p = spiele_partie(GEGNER_FUNKTIONEN[name], programm_beginnt, zeitlimit, rng)
        p["gegner"] = name
        p["rolle"] = rolle
        ergebnisse.append(p)
        extra = f" | Notfallzuege {p['notfall']}" if p["notfall"] else ""
        out(f"  Partie {start_nr + i:3d} | {name:7s} | {rolle:16s} | {p['ergebnis']:10s} | "
            f"{p['zuege']:2d} Zuege | Tiefe {p['tiefe']:5.1f} | {p['zeit']:6.1f} s | "
            f"Zugfolge {' '.join(map(str, p['folge']))}{extra}")
    return ergebnisse


def zusammenfassung(ergebnisse):
    out("\nZusammenfassung (Ergebnisse aus Sicht des Programms)")
    out(f"  {'Gegner':7s} | {'Rolle':16s} | {'Partien':>7} | {'Sieg':>4} | {'Remis':>5} | "
        f"{'Niederl.':>8} | {'Zuege':>5} | {'Tiefe':>5}")
    gruppen = {}
    for p in ergebnisse:
        gruppen.setdefault((p["gegner"], p["rolle"]), []).append(p)
    for (gegner, rolle), liste in gruppen.items():
        n = len(liste)
        s = sum(p["ergebnis"] == "Sieg" for p in liste)
        r = sum(p["ergebnis"] == "Remis" for p in liste)
        v = sum(p["ergebnis"] == "Niederlage" for p in liste)
        z = sum(p["zuege"] for p in liste) / n
        t = sum(p["tiefe"] for p in liste) / n
        out(f"  {gegner:7s} | {rolle:16s} | {n:>7} | {s:>4} | {r:>5} | {v:>8} | {z:>5.1f} | {t:>5.1f}")
    out("  (Zuege = durchschnittliche Anzahl Steine bei Partieende,")
    out("   Tiefe = durchschnittliche erreichte Suchtiefe von bester_zug)")
