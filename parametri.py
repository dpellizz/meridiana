
# ============================================================
# MERIDIANA FREECAD - PARAMETRI GENERALI
# ============================================================

import datetime
from pprint import pprint


PARAMETRI = {

    # --------------------------------------------------------
    # POSIZIONE GEOGRAFICA
    # --------------------------------------------------------
    # Latitudine geografica in gradi decimali (-90, 90).
    # Nord positivo, Sud negativo.
    #
    # Longitudine geografica in gradi decimali (-180, 180).
    # Est positivo, Ovest negativo.
    #
    "latitudine": 45.759280,
    "longitudine": 11.956828,
    
    # 45.759202, 11.956828 C
    # 45.715410, 11.957949 N

    # --------------------------------------------------------
    # ORIENTAMENTO
    # SUD / EST / OVEST / ORIZZONTALE
    # --------------------------------------------------------

    # Parete o piano del quadrante:
    # SUD, EST, OVEST oppure ORIZZONTALE.
    "orientamento": "SUD",

    # --------------------------------------------------------
    # DIMENSIONI QUADRANTE (mm)
    # --------------------------------------------------------

    # Larghezza del quadrante lungo l'asse X, in mm.
    "larghezza": 200.0,

    # Altezza del quadrante lungo l'asse Y, in mm.
    "altezza": 200.0,

    # Spessore della piastra, in mm.
    "spessore": 2.0,

    # --------------------------------------------------------
    # POSIZIONE ATTACCO GNOMONE
    # --------------------------------------------------------

    # Quota verticale dell'attacco per SUD, EST e OVEST.
    # E' una frazione dell'altezza: 0 = bordo inferiore,
    # 1 = bordo superiore.
    "quota_attacco": 0.95,

    # Quota verticale dell'attacco per ORIZZONTALE.
    # E' una frazione dell'altezza del quadrante.
    "quota_attacco_orizzontale": 0.05,

    # Posizione orizzontale dell'attacco come frazione
    # della larghezza: 0 = bordo sinistro, 1 = destro.
    "x_attacco": 0.50,

    # --------------------------------------------------------
    # GNOMONE (mm)
    # --------------------------------------------------------

    # Lunghezza dell'asta dello gnomone, in mm.
    "lunghezza_gnomone": 60.0,

    # Raggio del cilindro dello gnomone, in mm.
    "raggio_gnomone": 1.0,

    # Distanza del nodus dalla parete per EST/OVEST, in mm.
    # Per le altre configurazioni non determina l'inclinazione.
    "stacco_gnomone": 60.0,

    # --------------------------------------------------------
    # CURVE CALENDARIALI
    # --------------------------------------------------------

    # Anno usato per declinazione solare, analemmi e date.
    "anno": 2026,

    # Elenco delle curve calendariali da disegnare.
    # Ogni elemento e':
    # (etichetta, mese, giorno, declinazione_gradi).
    #
    # Se declinazione_gradi e' None, viene calcolata dalla
    # data. Se e' un numero, viene usata quella declinazione
    # in gradi; 0.0 rappresenta la curva teorica degli
    # equinozi.
    #
    # Le date non devono essere duplicate.
    "date_curve": [

        ("EQUI PRIMAVERA", 3, 20, 0.0),
        
        ("SOLSTIZIO ESTIVO", 6, 21, None),

        ("EQUI AUTUNNO", 9, 23, 0.0),

        ("SOLSTIZIO INVERNALE", 12, 21, None),

    ],

    # Numero di campioni per ogni curva calendariale.
    # Valori maggiori producono curve piu' regolari ma
    # richiedono piu' tempo per la generazione.
    "campioni_curve": 2000,

    # Se True, estende le curve secondo la geometria solare
    # anche oltre i periodi di illuminazione effettiva.
    # I tratti fuori dalla piastra vengono comunque esclusi.
    "estendi_curve_calendariali": True,

    # --------------------------------------------------------
    # ANALEMMA
    # --------------------------------------------------------

    # Se True, disegna l'analemma.
    "crea_analemma": True,

    # Se True, crea un analemma separato per ogni ora
    # in cui la superficie e' illuminata almeno un giorno
    # dell'anno. Se False, usa solo ora_analemma.
    "analemma_tutte_ore_luce": True,

    # Ora dell'analemma singolo, in ore decimali.
    # None seleziona automaticamente:
    # SUD = 12
    # EST = 9
    # OVEST = 15
    # ORIZZONTALE = 12
    "ora_analemma": 12,

    # Intervallo tra gli analemmi quando sono attive tutte
    # le ore illuminate. Valori consigliati: 60, 30 oppure
    # 5 minuti.
    "passo_analemma_minuti": 60,

    # Periodo dell'analemma:
    # anno_intero, solstizio_invernale_estivo oppure
    # solstizio_estivo_invernale. Gli estremi sono inclusi.
    "periodo_analemma": "anno_intero",

    # Riferimento temporale dell'analemma:
    # solare_medio_locale, CET oppure CEST.
    "riferimento_analemma": "CET",

    # Meridiano centrale del fuso, in gradi di longitudine.
    # Usato solo con CET o CEST; per l'Italia e' 15 gradi Est.
    "meridiano_fuso": 15.0,

    # Riferimento temporale delle linee orarie:
    # solare_medio_locale, CET oppure CEST.
    "riferimento_linee_orarie": "CET",

    # --------------------------------------------------------
    # CREAZIONE OGGETTI
    # --------------------------------------------------------

    # Se True, crea le linee orarie.
    "crea_linee_orarie": False,

    # Se True, crea la piastra del quadrante.
    "crea_piastra": True,

    # Se True, crea lo gnomone 3D.
    "crea_gnomone": True,

    # Se True, evidenzia in 2D i punti di attacco dello gnomone.
    "crea_riferimento_gnomone": True,

    # Interruttore generale per tutte le etichette testuali.
    "crea_etichette": True,

    # Se True e crea_etichette e' True, crea le ore.
    "crea_etichette_ore": True,

    # Se True e crea_etichette e' True, crea le etichette
    # di equinozi, solstizi e date calendariali.
    "crea_etichette_curve": True,

    # --------------------------------------------------------
    # VISUALIZZAZIONE
    # --------------------------------------------------------

    # Quota Z comune di linee, curve e testi stampabili, in mm.
    "quota_linee": 0.0,

    # Spessore grafico delle linee in FreeCAD.
    "spessore_linee": 0.5,

    # Spessore grafico degli analemmi in FreeCAD.
    "spessore_analemma": 2.0,

    # Distanza aggiuntiva delle etichette dalle geometrie, in mm.
    "margine_etichette": 1.0,

    # Dimensione delle etichette di ore e curve, in mm.
    "dimensione_testo": 5.0,

    # Dimensione del titolo e delle informazioni del quadrante, in mm.
    "dimensione_titolo": 5.0,

    # Se True, stampa nel report le ore illuminate e le
    # principali scelte geometriche e temporali.
    "modalita_diagnostica": False,

    # Colore RGB della piastra, componenti tra 0 e 1.
    "colore_piastra": (1.00, 1.00, 1.00),

    # Colore RGB delle linee orarie.
    "colore_ore": (0.12, 0.20, 0.38),

    # Colore RGB della linea di mezzogiorno.
    "colore_mezzogiorno": (0.80, 0.12, 0.08),

    # Colore RGB delle curve calendariali.
    "colore_mesi": (0.15, 0.48, 0.24),

    # Colore RGB degli analemmi.
    "colore_analemma": (0.75, 0.08, 0.60),

    # Colori RGB per distinguere mezzore e intervalli di
    # cinque minuti quando vengono disegnati più analemmi.
    "colore_analemma_mezzore": (0.10, 0.35, 0.80),
    "colore_analemma_5_minuti": (0.45, 0.45, 0.45),

    # Colore RGB dello gnomone.
    "colore_gnomone": (0.72, 0.72, 0.76),

}


# ============================================================
# CONFIGURAZIONE ORGANIZZATA
# ============================================================

CONFIGURAZIONE = {
    "luogo": {
        "latitudine": PARAMETRI["latitudine"],
        "longitudine": PARAMETRI["longitudine"],
        "anno": PARAMETRI["anno"],
    },
    "quadrante": {
        "orientamento": PARAMETRI["orientamento"],
        "larghezza": PARAMETRI["larghezza"],
        "altezza": PARAMETRI["altezza"],
        "spessore": PARAMETRI["spessore"],
    },
    "gnomone": {
        "lunghezza": PARAMETRI["lunghezza_gnomone"],
        "raggio": PARAMETRI["raggio_gnomone"],
        "stacco": PARAMETRI["stacco_gnomone"],
        "posizione": {
            "x": PARAMETRI["x_attacco"],
            "verticale": PARAMETRI["quota_attacco"],
            "verticale_orizzontale": PARAMETRI["quota_attacco_orizzontale"],
        },
    },
    "curve": {
        "date": [
            {
                "etichetta": etichetta,
                "mese": mese,
                "giorno": giorno,
                "declinazione": declinazione,
            }
            for etichetta, mese, giorno, declinazione
            in PARAMETRI["date_curve"]
        ],
        "campioni": PARAMETRI["campioni_curve"],
        "estese": PARAMETRI["estendi_curve_calendariali"],
    },
    "analemma": {
        "abilitato": PARAMETRI["crea_analemma"],
        "tutte_le_ore_illuminate": PARAMETRI["analemma_tutte_ore_luce"],
        "ora": None,
        "passo_minuti": PARAMETRI["passo_analemma_minuti"],
        "periodo": PARAMETRI["periodo_analemma"],
        "riferimento_temporale": PARAMETRI["riferimento_analemma"],
    },
    "tempo": {
        "riferimento_linee_orarie": PARAMETRI["riferimento_linee_orarie"],
        "meridiano_fuso": PARAMETRI["meridiano_fuso"],
    },
    "output": {
        "linee_orarie": PARAMETRI["crea_linee_orarie"],
        "piastra": PARAMETRI["crea_piastra"],
        "gnomone": PARAMETRI["crea_gnomone"],
        "riferimento_gnomone": PARAMETRI["crea_riferimento_gnomone"],
    },
    "etichette": {
        "abilitate": PARAMETRI["crea_etichette"],
        "ore": PARAMETRI["crea_etichette_ore"],
        "curve": PARAMETRI["crea_etichette_curve"],
    },
    "stile": {
        "quota_linee": PARAMETRI["quota_linee"],
        "spessore_linee": PARAMETRI["spessore_linee"],
        "spessore_analemma": PARAMETRI["spessore_analemma"],
        "margine_etichette": PARAMETRI["margine_etichette"],
        "dimensione_testo": PARAMETRI["dimensione_testo"],
        "dimensione_titolo": PARAMETRI["dimensione_titolo"],
        "diagnostica": PARAMETRI["modalita_diagnostica"],
        "colori": {
            "piastra": PARAMETRI["colore_piastra"],
            "ore": PARAMETRI["colore_ore"],
            "mezzogiorno": PARAMETRI["colore_mezzogiorno"],
            "curve": PARAMETRI["colore_mesi"],
            "analemma": PARAMETRI["colore_analemma"],
            "analemma_mezzore": PARAMETRI["colore_analemma_mezzore"],
            "analemma_5_minuti": PARAMETRI["colore_analemma_5_minuti"],
            "gnomone": PARAMETRI["colore_gnomone"],
        },
    },
}


def _unisci_configurazione(base, modifiche):

    risultato = base.copy()

    for nome, valore in modifiche.items():

        if (
            nome in risultato
            and isinstance(risultato[nome], dict)
            and isinstance(valore, dict)
        ):
            risultato[nome] = _unisci_configurazione(
                risultato[nome],
                valore
            )
        else:
            risultato[nome] = valore

    return risultato


def _appiattisci_configurazione(configurazione):

    luogo = configurazione["luogo"]
    quadrante = configurazione["quadrante"]
    gnomone = configurazione["gnomone"]
    posizione = gnomone["posizione"]
    curve = configurazione["curve"]
    analemma = configurazione["analemma"]
    tempo = configurazione["tempo"]
    output = configurazione["output"]
    etichette = configurazione["etichette"]
    stile = configurazione["stile"]
    colori = stile["colori"]

    date_curve = [
        (
            voce["etichetta"],
            voce["mese"],
            voce["giorno"],
            voce["declinazione"],
        )
        for voce in curve["date"]
    ]

    return {
        "latitudine": luogo["latitudine"],
        "longitudine": luogo["longitudine"],
        "anno": luogo["anno"],
        "orientamento": quadrante["orientamento"],
        "larghezza": quadrante["larghezza"],
        "altezza": quadrante["altezza"],
        "spessore": quadrante["spessore"],
        "x_attacco": posizione["x"],
        "quota_attacco": posizione["verticale"],
        "quota_attacco_orizzontale": posizione["verticale_orizzontale"],
        "lunghezza_gnomone": gnomone["lunghezza"],
        "raggio_gnomone": gnomone["raggio"],
        "stacco_gnomone": gnomone["stacco"],
        "date_curve": date_curve,
        "campioni_curve": curve["campioni"],
        "estendi_curve_calendariali": curve["estese"],
        "crea_analemma": analemma["abilitato"],
        "analemma_tutte_ore_luce": analemma["tutte_le_ore_illuminate"],
        "ora_analemma": analemma["ora"],
        "passo_analemma_minuti": analemma["passo_minuti"],
        "periodo_analemma": analemma["periodo"],
        "riferimento_analemma": analemma["riferimento_temporale"],
        "riferimento_linee_orarie": (
            tempo["riferimento_linee_orarie"]
            or analemma["riferimento_temporale"]
        ),
        "meridiano_fuso": tempo["meridiano_fuso"],
        "crea_linee_orarie": output["linee_orarie"],
        "crea_piastra": output["piastra"],
        "crea_gnomone": output["gnomone"],
        "crea_riferimento_gnomone": output["riferimento_gnomone"],
        "crea_etichette": etichette["abilitate"],
        "crea_etichette_ore": etichette["ore"],
        "crea_etichette_curve": etichette["curve"],
        "quota_linee": stile["quota_linee"],
        "spessore_linee": stile["spessore_linee"],
        "spessore_analemma": stile["spessore_analemma"],
        "margine_etichette": stile["margine_etichette"],
        "dimensione_testo": stile["dimensione_testo"],
        "dimensione_titolo": stile["dimensione_titolo"],
        "modalita_diagnostica": stile["diagnostica"],
        "colore_piastra": colori["piastra"],
        "colore_ore": colori["ore"],
        "colore_mezzogiorno": colori["mezzogiorno"],
        "colore_mesi": colori["curve"],
        "colore_analemma": colori["analemma"],
        "colore_analemma_mezzore": colori["analemma_mezzore"],
        "colore_analemma_5_minuti": colori["analemma_5_minuti"],
        "colore_gnomone": colori["gnomone"],
    }


# ============================================================
# VALIDAZIONE E LETTURA PARAMETRI
# ============================================================

def get_parametri(**modifiche):

    if any(nome in PARAMETRI for nome in modifiche):
        configurazione = CONFIGURAZIONE
        p = PARAMETRI.copy()
        p.update(modifiche)
    else:
        configurazione = _unisci_configurazione(
            CONFIGURAZIONE,
            modifiche
        )
        p = _appiattisci_configurazione(configurazione)

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

    if not 0 < p["x_attacco"] < 1:
        raise ValueError("Quota attacco orizzontale non valida")

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

    # Analemma automatico

    orari_analemma = {

        "SUD": 12.0,

        "EST": 9.0,

        "OVEST": 15.0,

        "ORIZZONTALE": 12.0,

    }

    if p["ora_analemma"] is None:

        p["ora_analemma"] = orari_analemma[p["orientamento"]]

    if not isinstance(p["ora_analemma"], (int, float)):
        raise ValueError("Ora analemma non valida")

    # Campionamento

    if (
        not isinstance(p["campioni_curve"], int)
        or p["campioni_curve"] < 20
    ):
        raise ValueError("Campioni curve insufficienti")

    if not isinstance(p["anno"], int) or not 1 <= p["anno"] <= 9999:
        raise ValueError("Anno non valido")

    if not isinstance(p["estendi_curve_calendariali"], bool):
        raise ValueError("Estensione curve non valida")

    if not isinstance(p["crea_analemma"], bool):
        raise ValueError("Parametro crea_analemma non valido")

    if not isinstance(p["crea_linee_orarie"], bool):
        raise ValueError("Parametro crea_linee_orarie non valido")

    if not isinstance(p["analemma_tutte_ore_luce"], bool):
        raise ValueError("Parametro analemma_tutte_ore_luce non valido")

    if p["periodo_analemma"] not in (
        "anno_intero",
        "solstizio_invernale_estivo",
        "solstizio_estivo_invernale"
    ):
        raise ValueError("Periodo analemma non valido")

    if p["passo_analemma_minuti"] not in (60, 30, 5):
        raise ValueError(
            "Passo analemma ammesso: 60, 30 oppure 5 minuti"
        )

    if not isinstance(p["crea_etichette"], bool):
        raise ValueError("Parametro crea_etichette non valido")

    if not isinstance(p["crea_gnomone"], bool):
        raise ValueError("Parametro crea_gnomone non valido")

    if not isinstance(p["crea_riferimento_gnomone"], bool):
        raise ValueError(
            "Parametro crea_riferimento_gnomone non valido"
        )

    if not isinstance(p["crea_etichette_ore"], bool):
        raise ValueError("Parametro crea_etichette_ore non valido")

    if not isinstance(p["crea_etichette_curve"], bool):
        raise ValueError("Parametro crea_etichette_curve non valido")

    if not isinstance(p["modalita_diagnostica"], bool):
        raise ValueError("Parametro modalita_diagnostica non valido")

    if (
        not isinstance(p["margine_etichette"], (int, float))
        or p["margine_etichette"] < 0
    ):
        raise ValueError("Margine etichette non valido")

    for nome in ("dimensione_testo", "dimensione_titolo"):

        if (
            not isinstance(p[nome], (int, float))
            or p[nome] <= 0
        ):
            raise ValueError("Dimensione testo non valida: " + nome)

    for nome in ("spessore_linee", "spessore_analemma"):

        if (
            not isinstance(p[nome], (int, float))
            or p[nome] <= 0
        ):
            raise ValueError("Spessore non valido: " + nome)

    if (
        not isinstance(p["meridiano_fuso"], (int, float))
        or not -180 <= p["meridiano_fuso"] <= 180
    ):
        raise ValueError("Meridiano di riferimento non valido")

    # Verifica date

    if not p["date_curve"]:
        raise ValueError("Specificare almeno una curva calendariale")

    date_verificate = set()

    for voce in p["date_curve"]:

        if len(voce) == 3:
            etichetta, mese, giorno = voce
            declinazione_gradi = None

        elif len(voce) == 4:
            (
                etichetta,
                mese,
                giorno,
                declinazione_gradi
            ) = voce

        else:
            raise ValueError("Formato date_curve non valido")

        if not isinstance(etichetta, str) or not etichetta.strip():
            raise ValueError("Etichetta curva non valida")

        data = datetime.date(
            p["anno"],
            mese,
            giorno
        )

        if data in date_verificate:
            raise ValueError("Date curve duplicate")

        date_verificate.add(data)

        if (
            declinazione_gradi is not None
            and not isinstance(
                declinazione_gradi,
                (int, float)
            )
        ):
            raise ValueError(
                "Declinazione curva non valida"
            )

    # Equazione del tempo

    if p["riferimento_analemma"] not in (
        "solare_medio_locale",
        "CET",
        "CEST"
    ):

        raise ValueError("Riferimento analemma non valido")

    if p["riferimento_linee_orarie"] not in (
        "solare_medio_locale",
        "CET",
        "CEST"
    ):

        raise ValueError("Riferimento linee orarie non valido")

    colori = (
        "colore_piastra",
        "colore_ore",
        "colore_mezzogiorno",
        "colore_mesi",
        "colore_analemma",
        "colore_analemma_mezzore",
        "colore_analemma_5_minuti",
        "colore_gnomone"
    )

    for nome in colori:

        colore = p[nome]

        if (
            not isinstance(colore, (tuple, list))
            or len(colore) != 3
            or any(
                not isinstance(componente, (int, float))
                or not 0 <= componente <= 1
                for componente in colore
            )
        ):
            raise ValueError("Colore non valido: " + nome)

    return p


def stampa_parametri(**modifiche):

    configurazione = _unisci_configurazione(
        CONFIGURAZIONE,
        modifiche
    )

    pprint(configurazione, sort_dicts=False)
