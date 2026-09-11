import sys
import pygame

# ── Einstellungen ──
GROESSE = 5          # 5 Zeilen x 5 Spalten
VERBINDEN = 4        # 4 gleiche Steine in einer Reihe = Sieg
FELD = 120           # Kantenlänge eines Feldes in Pixeln
RADIUS = FELD // 2 - 10

BREITE = GROESSE * FELD
HOEHE = (GROESSE + 1) * FELD          # eine Extra-Zeile oben für die Vorschau 

# ── Farben (RGB) ──
SCHWARZ = (0, 0, 0)
WEISS = (255, 255, 255)
BLAU = (30, 100, 200)                 # Spielfeld
ROT = (220, 50, 50)                   # Spieler 1
GELB = (230, 200, 0)                  # Spieler 2
GRAU = (50, 50, 50)                   # leeres Feld
GRUEN = (0, 160, 80)                  # Gewinn-Hervorhebung

SPIELER_1 = 1
SPIELER_2 = 2






#  SPIELLOGIK

def erstelle_brett():
    """Leeres 5x5-Feld als 2D-Liste. 0 = leer."""
    return [[0] * GROESSE for _ in range(GROESSE)]


def spalte_frei(brett, spalte):
    """True, wenn in dieser Spalte noch Platz ist (oberste Zeile leer)."""
    return brett[0][spalte] == 0


def stein_setzen(brett, spalte, spieler):
    """Stein fällt bis zur untersten freien Zeile. Gibt (zeile, spalte) zurück."""
    for zeile in range(GROESSE - 1, -1, -1):
        if brett[zeile][spalte] == 0:
            brett[zeile][spalte] = spieler
            return zeile, spalte
    return None


def hat_gewonnen(brett, spieler):
    """
    Prüft alle 4 Richtungen auf VERBINDEN gleiche Steine.
    Gibt die Gewinnfelder als Liste zurück, sonst None.
    """
    richtungen = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for zeile in range(GROESSE):
        for spalte in range(GROESSE):
            for dz, ds in richtungen:
                felder = []
                for i in range(VERBINDEN):
                    z, s = zeile + dz * i, spalte + ds * i
                    if 0 <= z < GROESSE and 0 <= s < GROESSE and brett[z][s] == spieler:
                        felder.append((z, s))
                    else:
                        break
                if len(felder) == VERBINDEN:
                    return felder
    return None


def brett_voll(brett):
    """True, wenn keine Spalte mehr frei ist (Unentschieden)."""
    return all(not spalte_frei(brett, s) for s in range(GROESSE))






#  GRAFIK

def zeichne_brett(fenster, brett, gewinn_felder=None):
    """Zeichnet das Spielfeld mit allen Steinen."""
    fenster.fill(BLAU)
    for zeile in range(GROESSE):
        for spalte in range(GROESSE):
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






#  HAUPTPROGRAMM

def main():
    pygame.init()
    fenster = pygame.display.set_mode((BREITE, HOEHE))
    pygame.display.set_caption("Vier gewinnt – 5x5")

    brett = erstelle_brett()
    aktueller_spieler = SPIELER_1
    maus_spalte = 0
    gewinn_felder = None
    spiel_laeuft = True

    def neu_zeichnen():
        zeichne_brett(fenster, brett, gewinn_felder)
        if spiel_laeuft:
            zeichne_vorschau(fenster, maus_spalte, aktueller_spieler)
        pygame.display.update()

    neu_zeichnen()

    while True:
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Neues Spiel mit R
            if ereignis.type == pygame.KEYDOWN and ereignis.key == pygame.K_r:
                brett = erstelle_brett()
                aktueller_spieler = SPIELER_1
                gewinn_felder = None
                spiel_laeuft = True
                neu_zeichnen()

            if ereignis.type == pygame.MOUSEMOTION and spiel_laeuft:
                maus_spalte = min(max(ereignis.pos[0] // FELD, 0), GROESSE - 1)
                neu_zeichnen()

            if ereignis.type == pygame.MOUSEBUTTONDOWN and spiel_laeuft:
                spalte = min(max(ereignis.pos[0] // FELD, 0), GROESSE - 1)
                if not spalte_frei(brett, spalte):
                    continue

                stein_setzen(brett, spalte, aktueller_spieler)

                gewinn_felder = hat_gewonnen(brett, aktueller_spieler)
                if gewinn_felder:
                    spiel_laeuft = False
                    zeichne_brett(fenster, brett, gewinn_felder)
                    farbe = ROT if aktueller_spieler == SPIELER_1 else GELB
                    zeichne_nachricht(fenster, f"Spieler {aktueller_spieler} hat gewonnen!  (R = neu)", farbe)
                    pygame.display.update()
                    continue

                if brett_voll(brett):
                    spiel_laeuft = False
                    zeichne_brett(fenster, brett)
                    zeichne_nachricht(fenster, "Unentschieden!  (R = neu)", WEISS)
                    pygame.display.update()
                    continue

                aktueller_spieler = SPIELER_2 if aktueller_spieler == SPIELER_1 else SPIELER_1
                neu_zeichnen()


if __name__ == "__main__":
    main()
