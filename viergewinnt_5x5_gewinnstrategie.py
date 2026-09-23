import sys
import time
import math
import pygame



# Einstellungen 
SPALTEN = 5          # Anzahl Spalten
ZEILEN = 5          # Anzahl Zeilen
VERBINDEN = 4        # 4 gleiche Steine in einer Reihe = Sieg
FELD = 100           # Kantenlänge eines Feldes in Pixeln
RADIUS = FELD // 2 - 10

BREITE = SPALTEN * FELD
HOEHE = (ZEILEN + 1) * FELD          # eine Extra-Zeile oben für die Vorschau 

# Farben (RGB) 
SCHWARZ = (0, 0, 0)
WEISS = (255, 255, 255)
BLAU = (30, 100, 200)                 # Spielfeld
ROT = (220, 50, 50)                   # Spieler 1
GELB = (230, 200, 0)                  # Spieler 2
GRAU = (50, 50, 50)                   # leeres Feld
GRUEN = (0, 160, 80)                  # Gewinn-Hervorhebung

SPIELER_1 = 1
SPIELER_2 = 2

ICH = SPIELER_1
GEGNER = SPIELER_2

ICH_BEGINNT = True

ZEIT_LIMIT_SEKUNDEN = 5.0
GEWINN_WERT = 100_000
SIEG_SCHWELLE = GEWINN_WERT - 2_000
FENSTER_WERT = {0: 0, 1: 1, 2: 10, 3: 50, 4:1000}






#  1. SPIELLOGIK

def erstelle_brett():
    """Leeres Feld (ZEILEN x SPALTEN) als 2D-Liste. 0 = leer."""
    return [[0] * SPALTEN for _ in range(ZEILEN)]


def spalte_frei(brett, spalte):
    """True, wenn in dieser Spalte noch Platz ist (oberste Zeile leer)."""
    return brett[0][spalte] == 0


def stein_setzen(brett, spalte, spieler):
    """Stein fällt bis zur untersten freien Zeile. Gibt (zeile, spalte) zurück."""
    for zeile in range(ZEILEN - 1, -1, -1):
        if brett[zeile][spalte] == 0:
            brett[zeile][spalte] = spieler
            return zeile, spalte
    return None


def stein_zurueckziehen(brett, zeile, spalte):
    """
    Gegenstück zu Stein setzen. Wird nur von der Engine gebraucht,welche die Steine platziert, dann mögliche Züge durchrechnet und den Stein dann wieder entfernt.
    """
    brett[zeile][spalte] = 0


def hat_gewonnen(brett, spieler):
    """
    Prüft alle 4 Richtungen auf VERBINDEN gleiche Steine. Gibt die Gewinnfelder als Liste zurück, sonst None.
    """
    richtungen = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for zeile in range(ZEILEN):
        for spalte in range(SPALTEN):
            for dz, ds in richtungen:
                felder = []
                for i in range(VERBINDEN):
                    z = zeile + dz * i
                    s = spalte +ds *i
                    if 0 <= z < ZEILEN and 0 <= s < SPALTEN and brett[z][s] == spieler:
                        felder.append((z, s))
                    else:
                        break
                if len(felder) == VERBINDEN:
                    return felder
    return None


def gewinn_durch_letzten_zug(brett, zeile, spalte, spieler):
    """
    Prüft nur die 4 Linien durch das zuletzt gesetzte Feld auf VERBINDEN. Das genügt, weil sich ein neuer Sieg durch einen Zug nur über Linien ergeben, dir durch genau dieses neue Feld verlaufen. Diese Version ist viel schneller als hat_gewonnen().
    """
    richtungen = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dz, ds in richtungen:
        anzahl = 1 # Das neu gesetzte Feld zählt schon mit

        z, s = zeile +dz, spalte + ds
        while 0 <= z < ZEILEN and 0 <= s < SPALTEN and brett[z][s] == spieler:
            anzahl += 1
            z += dz
            s += ds

        z, s = zeile - dz, spalte - ds
        while 0 <= z < ZEILEN and 0 <= s < SPALTEN and brett[z][s] == spieler:
            anzahl += 1
            z -= dz
            s -= ds

        if anzahl >= VERBINDEN:
            return True
    return False


def brett_voll(brett):
    """True, wenn keine Spalte mehr frei ist (Unentschieden)."""
    return all(not spalte_frei(brett, s) for s in range(SPALTEN))





# 2. ENGINE

# 2.1 Bewertungsfunktion

# Da es zu lange gehen würde bei einem leeren Spielfeld alle möglichen Züge durchzurechnen, gibt es den Befehl in diesem Abschnitt, welcher abschätzt wie gut die Stellungen für einen stehen

def bewerte_stellung(brett):
    punkte = 0
    richtungen = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for zeile in range(ZEILEN):
        for spalte in range(SPALTEN):
            for dz, ds in richtungen:
                fenster = [(zeile + dz * i, spalte + ds * i) for i in range(VERBINDEN)]
                if not all (0 <= z < ZEILEN and 0 <= s < SPALTEN for z, s in fenster):
                    continue

                ich_steine = sum(1 for z, s in fenster if brett[z][s] == ICH)
                gegner_steine = sum(1 for z, s in fenster if brett[z][s] == GEGNER)

                if ich_steine > 0 and gegner_steine > 0:
                    continue    # totes Fenster

                punkte += FENSTER_WERT[ich_steine] - FENSTER_WERT[gegner_steine]

    return punkte


# 2.2 Minimax mit Alpha-Beta-Pruning

class Zeitlimit(Exception):
    pass

EXAKT = 0
UNTERE_SCHRANKE = 1
OBERE_SCHRANKE = 2

CACHE = {}  # Transpositionstabelle
# Bewusst ausserhalb jeder Funktion angelegt, da ihr Inhalt nur von der jeweiligen Brett-Stellung abhängt. Je länger das Programm läuft desto mehr schon bekannte Stellungen sind gespeichert und desto schneller werden spätere Empfehlungen berechnet.

SPALTEN_REIHENFOLGE = sorted(range(SPALTEN), key=lambda s: abs(s - SPALTEN // 2))
# Spalten sortiert nach Abstand von der Mitte, da zentrale Züge bei 4 Gewinnt grundsätzlich immer die stärksten sind

def minimax(brett, spieler_am_zug, alpha, beta, tiefe, max_tiefe, letzter_zug, zeitpunkt_ende, cache):
    if time.time() > zeitpunkt_ende:
        raise Zeitlimit()

    if letzter_zug is not None:
        letzte_zeile, letzte_spalte, letzter_spieler = letzter_zug
        if gewinn_durch_letzten_zug(brett, letzte_zeile, letzte_spalte, letzter_spieler):
            if letzter_spieler == ICH:
                return GEWINN_WERT - tiefe, None
            else:
                return -(GEWINN_WERT - tiefe), None

    if brett_voll(brett):
        return 0, None

    if tiefe >= max_tiefe:
        return bewerte_stellung(brett), None

    schluessel = (tuple(tuple(zeile) for zeile in brett), spieler_am_zug, max_tiefe - tiefe)

    urspruengliches_alpha, urspruengliches_beta = alpha, beta

    if schluessel in cache:
        gespeicherter_wert, gecachte_spalte, art = cache[schluessel]

        if gespeicherter_wert >= SIEG_SCHWELLE:
            wert = gespeicherter_wert - tiefe
        elif gespeicherter_wert <= -SIEG_SCHWELLE:
            wert = gespeicherter_wert + tiefe
        else:
            wert = gespeicherter_wert

        if art == EXAKT:
            return wert, gecachte_spalte
        elif art == UNTERE_SCHRANKE:
            alpha = max(alpha, wert)
        elif art == OBERE_SCHRANKE:
            beta = min(beta, wert)
        if alpha >= beta:
            return wert, gecachte_spalte

    beste_spalte = None
    if spieler_am_zug == ICH:
        wert = -math.inf
        for spalte in SPALTEN_REIHENFOLGE:
            if not spalte_frei(brett, spalte):
                continue

            zeile, _ = stein_setzen(brett, spalte, spieler_am_zug)
            try:
                folge_wert, _ = minimax(
                    brett, GEGNER, alpha, beta, tiefe + 1, max_tiefe,
                    (zeile, spalte, spieler_am_zug), zeitpunkt_ende, cache,
                )
            finally:
                stein_zurueckziehen(brett, zeile, spalte)

            if folge_wert > wert:
                wert = folge_wert
                beste_spalte = spalte
            alpha = max(alpha, wert)
            if alpha >= beta:
                break

    else:       # spieler_am_zug == GEGNER
        wert = math.inf
        for spalte in SPALTEN_REIHENFOLGE:
            if not spalte_frei(brett, spalte):
                continue

            zeile, _ = stein_setzen(brett, spalte, spieler_am_zug)
            try:
                folge_wert, _ = minimax(
                    brett, ICH, alpha, beta, tiefe + 1, max_tiefe,
                    (zeile, spalte, spieler_am_zug), zeitpunkt_ende, cache,
                )
            finally:
                stein_zurueckziehen(brett, zeile, spalte)

            if folge_wert < wert:
                wert = folge_wert
                beste_spalte = spalte
            beta = min(beta, wert)
            if alpha >= beta:
                break

    if wert >= SIEG_SCHWELLE:
        zu_speichern = wert + tiefe
    elif wert <= -SIEG_SCHWELLE:
        zu_speichern = wert - tiefe
    else:
        zu_speichern = wert

    if wert <= urspruengliches_alpha:
        art = OBERE_SCHRANKE
    elif wert >= urspruengliches_beta:
        art = UNTERE_SCHRANKE
    else:
        art = EXAKT
    cache[schluessel] = (zu_speichern, beste_spalte, art)

    return wert, beste_spalte


def bester_zug(brett, spieler, zeitlimit=ZEIT_LIMIT_SEKUNDEN):
    freie_felder = sum(1 for zeile in brett for feld in zeile if feld == 0)
    zeitpunkt_ende = time.time() + zeitlimit

    bestes_ergebnis = (0, None, 0)
    max_tiefe = 1
    while max_tiefe <= freie_felder:
        try:
            wert, spalte = minimax(
                brett, spieler, -math.inf, math.inf, 0, max_tiefe, None, zeitpunkt_ende, CACHE,
            )
        except Zeitlimit:
            break

        bestes_ergebnis = (wert, spalte, max_tiefe)

        if abs(wert) >= GEWINN_WERT - freie_felder:
            break   # bewiesener Sieg/Niederlage gefunden -> weitersuchen bringt nichts mehr

        max_tiefe += 1

    return bestes_ergebnis






#  3. GRAFIK

def zeichne_brett(fenster, brett, gewinn_felder=None):
    """Zeichnet das Spielfeld mit allen Steinen."""
    fenster.fill(BLAU)

    for zeile in range(ZEILEN):
        for spalte in range(SPALTEN):
            x = spalte * FELD + FELD // 2
            y = (zeile + 1) * FELD + FELD // 2      # +1 wegen Vorschau-Zeile

            ist_gewinn = gewinn_felder and (zeile, spalte) in gewinn_felder
            wert = brett[zeile][spalte]
            if wert == SPIELER_1:
                farbe = GRUEN if ist_gewinn else ROT
            elif wert == SPIELER_2:
                farbe = GRUEN if ist_gewinn else GELB
            else:
                farbe = GRAU

            pygame.draw.circle(fenster, farbe, (x, y), RADIUS)


def zeichne_vorschau(fenster, spalte, spieler):
    """Zeigt oben einen Stein über der Spalte, auf die die Maus zeigt."""
    pygame.draw.rect(fenster, SCHWARZ, (0, 0, BREITE, FELD))
    farbe = ROT if spieler == SPIELER_1 else GELB
    x = spalte * FELD + FELD // 2
    pygame.draw.circle(fenster, farbe, (x, FELD // 2), RADIUS)


def zeichne_nachricht(fenster, text, farbe):
    """Zeigt einen Text in der oberen Leiste an."""
    pygame.draw.rect(fenster, SCHWARZ, (0, 0, BREITE, FELD))
    schrift = pygame.font.SysFont("Arial", 34, bold=True)
    flaeche = schrift.render(text, True, farbe)
    fenster.blit(flaeche, (BREITE // 2 - flaeche.get_width() // 2,
                           FELD // 2 - flaeche.get_height() // 2))

def zeichne_empfehlung(fenster, spalte):
    x = spalte * FELD + FELD // 2
    spitze = [(x - 25, 8), (x + 25, 8), (x, FELD -12)]
    pygame.draw.polygon(fenster, GRUEN, spitze)





#  4. HAUPTPROGRAMM

def main():
    pygame.init()
    fenster = pygame.display.set_mode((BREITE, HOEHE))
    pygame.display.set_caption(f"Vier gewinnt – {SPALTEN}x{ZEILEN}")

    brett = erstelle_brett()
    aktueller_spieler = ICH if ICH_BEGINNT else GEGNER
    maus_spalte = 0
    gewinn_felder = None
    spiel_laeuft = True
    empfehlung_spalte = None

    def neu_zeichnen():
        zeichne_brett(fenster, brett, gewinn_felder)
        if spiel_laeuft:
            zeichne_vorschau(fenster, maus_spalte, aktueller_spieler)
            if aktueller_spieler == ICH and empfehlung_spalte is not None:
                zeichne_empfehlung(fenster, empfehlung_spalte)
        pygame.display.update()

    def empfehlung_berechnen():
        nonlocal empfehlung_spalte

        zeichne_brett(fenster, brett, gewinn_felder)
        zeichne_nachricht(fenster, "Denke nach ...", WEISS)
        pygame.display.update()

        wert, spalte, erreichte_tiefe = bester_zug(brett, ICH, ZEIT_LIMIT_SEKUNDEN)
        empfehlung_spalte = spalte
        print(f"Empfehlung: Spalte {spalte}  "
              f"(Bewertung {wert}, {erreichte_tiefe} Halbzüge vorausberechnet)")

        neu_zeichnen()

    def neues_spiel():
        nonlocal brett, aktueller_spieler, gewinn_felder, spiel_laeuft, empfehlung_spalte
        brett = erstelle_brett()
        aktueller_spieler = ICH if ICH_BEGINNT else GEGNER
        gewinn_felder = None
        spiel_laeuft = True
        empfehlung_spalte = None
        if aktueller_spieler == ICH:
            empfehlung_berechnen()
        else:
            neu_zeichnen()

    neues_spiel()


    while True:
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Neues Spiel mit R
            if ereignis.type == pygame.KEYDOWN and ereignis.key == pygame.K_r:
                neues_spiel()
            
            # Maus wurde bewegt: Nur die Vorschau aktualisieren
            if ereignis.type == pygame.MOUSEMOTION and spiel_laeuft:
                maus_spalte = min(max(ereignis.pos[0] // FELD, 0), SPALTEN - 1)
                neu_zeichnen()
            
            # Maustaste geklickt: Den echten Zug protokollieren
            if ereignis.type == pygame.MOUSEBUTTONDOWN and spiel_laeuft:
                spalte = min(max(ereignis.pos[0] // FELD, 0), SPALTEN - 1)
                if not spalte_frei(brett, spalte):
                    continue

                stein_setzen(brett, spalte, aktueller_spieler)
                empfehlung_spalte = None

                gewinn_felder = hat_gewonnen(brett, aktueller_spieler)
                if gewinn_felder:
                    spiel_laeuft = False
                    zeichne_brett(fenster, brett, gewinn_felder)
                    farbe = ROT if aktueller_spieler == SPIELER_1 else GELB
                    wer = "Ich" if aktueller_spieler == ICH else "Gegner"
                    zeichne_nachricht(fenster, f"{wer} gewinne!    (R = neu)"
                                      if wer == "Ich" else f"{wer} gewinnt!    (R = neu)",
                                      farbe)
                    pygame.display.update()
                    continue

                if brett_voll(brett):
                    spiel_laeuft = False
                    zeichne_brett(fenster, brett)
                    zeichne_nachricht(fenster, "Unentschieden!  (R = neu)", WEISS)
                    pygame.display.update()
                    continue

                aktueller_spieler = GEGNER if aktueller_spieler == ICH else ICH

                if aktueller_spieler == ICH:
                    empfehlung_berechnen()
                else:
                    neu_zeichnen()


if __name__ == "__main__":
    main()
