
# ============================================================
# MERIDIANA FREECAD - PARAMETRI GENERALI
# ============================================================

import datetime


PARAMETRI = {

    # --------------------------------------------------------
    # POSIZIONE GEOGRAFICA
    # --------------------------------------------------------
    # lat 45.759280, long 11.956822 home
    # lat 45.715410, long 11.957977 grampa
    # 
    "latitudine": 45.759280,
    "longitudine": 11.956822,

    # --------------------------------------------------------
    # ORIENTAMENTO
    # SUD / EST / OVEST / ORIZZONTALE
    # --------------------------------------------------------

    "orientamento": "OVEST",

    # --------------------------------------------------------
    # DIMENSIONI QUADRANTE (mm)
    # --------------------------------------------------------

    "larghezza": 300.0,
    "altezza": 300.0,
    "spessore": 5.0,

    # --------------------------------------------------------
    # POSIZIONE ATTACCO GNOMONE
    # --------------------------------------------------------

    # quota nelle posisionei verticali (fra 0 e 1)
    "quota_attacco": 0.50,

    # quota nelle posisionei orizzontali (fra 0 e 1)
    "quota_attacco_orizzontale": 0.15,

    # None = centro della larghezza

    "x_attacco": None,

    # --------------------------------------------------------
    # GNOMONE (mm)
    # --------------------------------------------------------

    "lunghezza_gnomone": 100.0,
    
    # raggio del gnomone (mm) spessore/diametro del cilindro
    "raggio_gnomone": 2.5,

    # Distanza del nodus dalla parete EST/OVEST

    "stacco_gnomone": 45.0,

    # --------------------------------------------------------
    # INTERVALLO ORARIO
    # None = automatico in base all'orientamento
    # --------------------------------------------------------

    "ora_inizio": None,
    "ora_fine": None,

    # --------------------------------------------------------
    # CURVE CALENDARIALI
    # --------------------------------------------------------

    "anno": 2026,

    # Una curva per i due equinozi e due curve
    # per i solstizi.

    "date_curve": [

        ("EQUINOZI", 3, 20),

        ("SOLSTIZIO ESTIVO", 6, 21),

        ("SOLSTIZIO INVERNALE", 12, 21),

    ],

    # Numero di punti per ogni curva

    "campioni_curve": 321,

    # Campionamento delle linee orarie EST/OVEST

    "passo_giorni_ore": 1,

    # --------------------------------------------------------
    # ANALEMMA
    # --------------------------------------------------------

    "crea_analemma": True,

    # None = automatico:
    # SUD = 12
    # EST = 9
    # OVEST = 15
    # ORIZZONTALE = 12

    "ora_analemma": None,

    # solare_medio_locale / CET / CEST

    "riferimento_analemma": "solare_medio_locale",

    # Meridiano di riferimento CET/CEST

    "meridiano_fuso": 15.0,

    # --------------------------------------------------------
    # CREAZIONE OGGETTI
    # --------------------------------------------------------

    "crea_piastra": True,
    "crea_gnomone": True,
    "crea_etichette": True,

    # --------------------------------------------------------
    # VISUALIZZAZIONE
    # --------------------------------------------------------

    "quota_linee": 0.8,

    "spessore_linee": 1.5,

    "colore_piastra": (0.88, 0.84, 0.72),

    "colore_ore": (0.12, 0.20, 0.38),

    "colore_mezzogiorno": (0.80, 0.12, 0.08),

    "colore_mesi": (0.15, 0.48, 0.24),

    "colore_analemma": (0.75, 0.08, 0.60),

    "colore_gnomone": (0.72, 0.72, 0.76),

}


# ============================================================
# VALIDAZIONE E LETTURA PARAMETRI
# ============================================================

def get_parametri(**modifiche):

    p = PARAMETRI.copy()
    p.update(modifiche)

    p["orientamento"] = p["orientamento"].upper()

    orientamenti = (
        "SUD",
        "EST",
        "OVEST",
        "ORIZZONTALE"
    )

    if p["orientamento"] not in orientamenti:

        raise ValueError(
            "Orientamento ammesso: SUD, EST, OVEST, ORIZZONTALE"
        )

    # Coordinate geografiche

    if not -90 < p["latitudine"] < 90:
        raise ValueError("Latitudine non valida")

    if not -180 <= p["longitudine"] <= 180:
        raise ValueError("Longitudine non valida")

    # Dimensioni

    if p["larghezza"] <= 0 or p["altezza"] <= 0:
        raise ValueError("Dimensioni quadrante non valide")

    if p["spessore"] <= 0:
        raise ValueError("Spessore piastra non valido")

    # Posizione attacco

    if p["x_attacco"] is None:
        p["x_attacco"] = p["larghezza"] / 2.0

    if not 0 < p["quota_attacco"] < 1:
        raise ValueError("Quota attacco verticale non valida")

    if not 0 < p["quota_attacco_orizzontale"] < 1:
        raise ValueError("Quota attacco orizzontale non valida")

    # Gnomone

    if p["lunghezza_gnomone"] <= 0:
        raise ValueError("Lunghezza gnomone non valida")

    if p["raggio_gnomone"] <= 0:
        raise ValueError("Raggio gnomone non valido")

    if p["stacco_gnomone"] <= 0:
        raise ValueError("Stacco gnomone non valido")

    # Intervalli orari automatici

    intervalli = {

        "SUD": (7, 17),

        "EST": (6, 11),

        "OVEST": (14, 18),

        "ORIZZONTALE": (7, 17),

    }

    if p["ora_inizio"] is None:
        p["ora_inizio"] = intervalli[p["orientamento"]][0]

    if p["ora_fine"] is None:
        p["ora_fine"] = intervalli[p["orientamento"]][1]

    if not (
        0 <= p["ora_inizio"] < p["ora_fine"] <= 23
    ):
        raise ValueError("Intervallo orario non valido")

    if p["orientamento"] in ("SUD", "ORIZZONTALE"):

        if not (
            p["ora_inizio"] < 12 < p["ora_fine"]
        ):
            raise ValueError(
                "SUD e ORIZZONTALE devono comprendere le 12"
            )

    if p["orientamento"] == "EST" and p["ora_fine"] >= 12:

        raise ValueError(
            "Per EST utilizzare ore precedenti alle 12"
        )

    if p["orientamento"] == "OVEST" and p["ora_inizio"] <= 12:

        raise ValueError(
            "Per OVEST utilizzare ore successive alle 12"
        )

    # Analemma automatico

    orari_analemma = {

        "SUD": 12.0,

        "EST": 9.0,

        "OVEST": 15.0,

        "ORIZZONTALE": 12.0,

    }

    if p["ora_analemma"] is None:

        p["ora_analemma"] = orari_analemma[p["orientamento"]]

    # Campionamento

    if p["campioni_curve"] < 20:
        raise ValueError("Campioni curve insufficienti")

    if p["passo_giorni_ore"] < 1:
        raise ValueError("Passo giorni non valido")

    # Verifica date

    if not p["date_curve"]:
        raise ValueError("Specificare almeno una curva calendariale")

    for etichetta, mese, giorno in p["date_curve"]:

        datetime.date(
            p["anno"],
            mese,
            giorno
        )

    # Equazione del tempo

    if p["riferimento_analemma"] not in (
        "solare_medio_locale",
        "CET",
        "CEST"
    ):

        raise ValueError("Riferimento analemma non valido")

    return p


def stampa_parametri():

    for nome, valore in PARAMETRI.items():

        print(nome, "=", valore)
