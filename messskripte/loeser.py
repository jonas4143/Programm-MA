"""
loeser.py - UNABHAENGIGER exakter Loeser fuer 4 gewinnt auf 5x5.

Benutzt keine einzige Funktion der Engine:
- eigene Darstellung (Bitboards statt 2D-Liste)
- eigene Siegpruefung (Bit-Verschiebungen)
- eigene Suche: Negamax mit Alpha-Beta auf den Werten
  +1 = Sieg, 0 = Remis, -1 = Niederlage (jeweils fuer den Spieler am Zug)
- eigenes Memo (Transpositionstabelle), Spiegelstellungen teilen einen Eintrag

Bit-Layout: Spalte c belegt die Bits c*6 .. c*6+5, Bit c*6 ist das unterste
Feld, Bit c*6+5 ist ein immer leeres Waechterbit (verhindert, dass eine
Viererreihe ueber den Spaltenrand "umbricht").
"""

B = 5                 # Spalten
H = 5                 # Zeilen
H1 = H + 1            # Bits pro Spalte (inkl. Waechterbit)
REIHENFOLGE = (2, 1, 3, 0, 4)   # Mitte zuerst (nur fuer Tempo, Ergebnis exakt)

UNTEN = [1 << (c * H1) for c in range(B)]
OBEN = [1 << (c * H1 + H - 1) for c in range(B)]
SPALTE = [((1 << H) - 1) << (c * H1) for c in range(B)]
VOLL = sum(SPALTE)

EXAKT, UNTERE, OBERE = 0, 1, 2
MEMO = {}
STAT = {"knoten": 0}


def vier(p):
    """True, wenn die Steinmenge p vier in einer Reihe enthaelt."""
    for s in (1, H1, H1 - 1, H1 + 1):   # senkrecht, waagrecht, 2 Diagonalen
        m = p & (p >> s)
        if m & (m >> (2 * s)):
            return True
    return False


def aus_brett(brett, spieler):
    """
    Wandelt eine 2D-Liste (Zeile 0 = oben, 0 leer, 1/2 Steine) in
    (cur, mask) um: cur = Steine von 'spieler', mask = alle Steine.
    """
    assert len(brett) == H and all(len(z) == B for z in brett), "nur 5x5"
    cur = mask = 0
    for r in range(H):
        for c in range(B):
            v = brett[r][c]
            if v:
                bit = 1 << (c * H1 + (H - 1 - r))
                mask |= bit
                if v == spieler:
                    cur |= bit
    return cur, mask


def entschieden(cur, mask):
    return vier(cur) or vier(cur ^ mask)


def _zugbit(mask, c):
    return (mask + UNTEN[c]) & SPALTE[c]


def gewinnzuege(cur, mask):
    """Spalten, mit denen der Spieler 'cur' sofort gewinnt."""
    return [c for c in range(B)
            if not mask & OBEN[c] and vier(cur | _zugbit(mask, c))]


def _spiegel(k):
    return (((k & 0x3F) << 24) | (((k >> 6) & 0x3F) << 18) | (k & (0x3F << 12))
            | (((k >> 18) & 0x3F) << 6) | ((k >> 24) & 0x3F))


def _loese(cur, mask, alpha, beta):
    """
    Negamax. Vorbedingung: der Gegner hat mit dem letzten Zug NICHT gewonnen.
    Rueckgabe aus Sicht des Spielers am Zug (cur).
    """
    STAT["knoten"] += 1
    if mask == VOLL:
        return 0
    opp = cur ^ mask

    zuege = []
    drohungen = []
    for c in REIHENFOLGE:
        if mask & OBEN[c]:
            continue
        mv = _zugbit(mask, c)
        if vier(cur | mv):
            return 1                      # sofortiger Sieg
        if vier(opp | mv):
            drohungen.append(mv)          # Gegner wuerde hier gewinnen
        zuege.append(mv)
    if len(drohungen) >= 2:
        return -1                         # zwei Drohungen: nicht zu halten
    if drohungen:
        zuege = drohungen                 # einziger sinnvoller Zug: blocken

    key = cur + mask                      # eindeutiger Schluessel
    sk = _spiegel(key)
    if sk < key:
        key = sk

    a0, b0 = alpha, beta
    eintrag = MEMO.get(key)
    if eintrag is not None:
        v, art = eintrag
        if art == EXAKT:
            return v
        if art == UNTERE:
            if v > alpha:
                alpha = v
        elif v < beta:
            beta = v
        if alpha >= beta:
            return v

    best = -2
    for mv in zuege:
        v = -_loese(opp, mask | mv, -beta, -alpha)
        if v > best:
            best = v
            if v > alpha:
                alpha = v
                if alpha >= beta:
                    break

    if best <= a0:
        art = OBERE
    elif best >= b0:
        art = UNTERE
    else:
        art = EXAKT
    MEMO[key] = (best, art)
    return best


def wert(cur, mask):
    """Exakter Wert (+1/0/-1) fuer den Spieler am Zug. Stellung darf nicht entschieden sein."""
    if mask == VOLL:
        return 0
    return _loese(cur, mask, -1, 1)


def zugwerte(cur, mask):
    """{Spalte: exakter Wert dieses Zuges fuer den Spieler am Zug}"""
    opp = cur ^ mask
    werte = {}
    for c in range(B):
        if mask & OBEN[c]:
            continue
        mv = _zugbit(mask, c)
        if vier(cur | mv):
            werte[c] = 1
        else:
            werte[c] = -_loese(opp, mask | mv, -1, 1)
    return werte


def memo_leeren():
    MEMO.clear()
