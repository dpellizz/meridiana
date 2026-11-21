
# ============================================================
# MERIDIANA FREECAD - GENERATORE PRINCIPALE
# ============================================================

import FreeCAD as App
import Part

import math
import calendar
import datetime

from parametri import get_parametri

from astronomia import (
    declinazione_solare,
    angolo_orario_analemma
)

from geometria import (
    punto_ombra,
    punto_nel_quadrante,
    crea_linea,
    crea_curva,
    crea_segmenti_curva,
    crea_testo
)


# ============================================================
# CREAZIONE GRUPPI
# ============================================================

def crea_gruppo(doc, genitore, nome, etichetta):

    gruppo = doc.addObject(
        "App::DocumentObjectGroup",
        nome
    )

    gruppo.Label = etichetta

    genitore.addObject(gruppo)

    return gruppo


# ============================================================
# PIASTRA
# ============================================================

def crea_piastra(doc, gruppo, p):

    shape = Part.makeBox(

        p["larghezza"],
        p["altezza"],
        p["spessore"],

        App.Vector(
            0,
            0,
            -p["spessore"]
        )

    )

    obj = doc.addObject(
        "Part::Feature",
        "Piastra"
    )

    obj.Label = "Piastra quadrante"

    obj.Shape = shape

    obj.ViewObject.ShapeColor = p["colore_piastra"]

    gruppo.addObject(obj)

    return obj


# ============================================================
# COORDINATE ATTACCO GNOMONE
# ============================================================

def coordinate_attacco(p):

    x = p["x_attacco"]

    if p["orientamento"] == "ORIZZONTALE":

        quota = p["quota_attacco_orizzontale"]

    else:

        quota = p["quota_attacco"]

    y = p["altezza"] * quota

    return x, y


# ============================================================
# INTERSEZIONE RETTA CON BORDO QUADRANTE
# ============================================================

def punto_bordo_retta(x0, y0, dx, dy, p):

    candidati = []

    eps = 0.000001

    if dx > eps:

        candidati.append(
            (p["larghezza"] - x0) / dx
        )

    elif dx < -eps:

        candidati.append(
            (0.0 - x0) / dx
        )

    if dy > eps:

        candidati.append(
            (p["altezza"] - y0) / dy
        )

    elif dy < -eps:

        candidati.append(
            (0.0 - y0) / dy
        )

    validi = []

    for t in candidati:

        if t <= eps:
            continue

        x = x0 + t * dx
        y = y0 + t * dy

        if (

            -0.0001 <= x <= p["larghezza"] + 0.0001

            and

            -0.0001 <= y <= p["altezza"] + 0.0001

        ):

            validi.append((t, x, y))

    if not validi:
        return None

    validi.sort(key=lambda item: item[0])

    return validi[0][1], validi[0][2]


# ============================================================
# LINEE ORARIE - PARETE SUD
# ============================================================

def crea_linee_orarie_sud(
    doc,
    gruppo,
    p,
    x0,
    y0
):

    phi = math.radians(p["latitudine"])

    z = p["quota_linee"]

    for ora in range(
        p["ora_inizio"],
        p["ora_fine"] + 1
    ):

        H = math.radians(
            15.0 * (ora - 12)
        )

        theta = math.atan2(
            math.cos(phi) * math.sin(H),
            math.cos(H)
        )

        # X positivo verso Ovest,
        # Y positivo verso l'alto.

        dx = -math.sin(theta)

        dy = -math.cos(theta)

        estremo = punto_bordo_retta(
            x0,
            y0,
            dx,
            dy,
            p
        )

        if estremo is None:
            continue

        x1, y1 = estremo

        colore = (
            p["colore_mezzogiorno"]
            if ora == 12
            else p["colore_ore"]
        )

        spessore = (
            p["spessore_linee"] + 0.8
            if ora == 12
            else p["spessore_linee"]
        )

        crea_linea(

            doc,
            gruppo,

            "Ora_%02d" % ora,

            App.Vector(x0, y0, z),
            App.Vector(x1, y1, z),

            colore,
            spessore

        )

        if p["crea_etichette"]:

            xt = x0 + 0.87 * (x1 - x0)

            yt = y0 + 0.87 * (y1 - y0)

            crea_testo(

                doc,
                gruppo,

                "%02d" % ora,

                xt + 5,
                yt + 5,

                z + 0.1,
                12

            )


# ============================================================
# LINEE ORARIE - PARETI EST E OVEST
#
# A ogni ora si calcola la posizione dell'ombra
# durante tutto l'anno.
# ============================================================

def crea_linee_orarie_est_ovest(
    doc,
    gruppo,
    p,
    x0,
    y0
):

    z = p["quota_linee"]

    anno = p["anno"]

    giorni_anno = (
        366 if calendar.isleap(anno) else 365
    )

    passo = p["passo_giorni_ore"]

    for ora in range(
        p["ora_inizio"],
        p["ora_fine"] + 1
    ):

        H = math.radians(
            15.0 * (ora - 12)
        )

        punti = []

        for giorno in range(
            1,
            giorni_anno + 1,
            passo
        ):

            delta = declinazione_solare(
                giorno,
                anno
            )

            ombra = punto_ombra(
                p,
                delta,
                H
            )

            if ombra is None:

                punti.append(None)

                continue

            x = x0 + ombra[0]

            y = y0 + ombra[1]

            if punto_nel_quadrante(x, y, p):

                punti.append(
                    App.Vector(x, y, z)
                )

            else:

                punti.append(None)

        crea_segmenti_curva(

            doc,
            gruppo,

            "Ora_%02d" % ora,

            punti,

            p["colore_mezzogiorno"]
            if ora == 12 else p["colore_ore"],

            p["spessore_linee"]

        )

        if p["crea_etichette"]:

            validi = [
                q for q in punti
                if q is not None
            ]

            if validi:

                q = validi[len(validi) // 2]

                crea_testo(

                    doc,
                    gruppo,

                    "%02d" % ora,

                    q.x + 6,
                    q.y + 6,

                    z + 0.1,
                    12

                )


# ============================================================
# LINEE ORARIE - MERIDIANA ORIZZONTALE
#
# Le linee sono rette convergenti nel piede dello gnomone.
# X positivo EST, Y positivo NORD.
# ============================================================

def crea_linee_orarie_orizzontale(
    doc,
    gruppo,
    p,
    x0,
    y0
):

    z = p["quota_linee"]

    for ora in range(
        p["ora_inizio"],
        p["ora_fine"] + 1
    ):

        H = math.radians(
            15.0 * (ora - 12)
        )

        # La declinazione zero è sufficiente
        # per determinare la direzione della retta oraria.

        ombra = punto_ombra(
            p,
            0.0,
            H
        )

        if ombra is None:
            continue

        dx, dy = ombra

        lunghezza = math.hypot(dx, dy)

        if lunghezza < 0.00001:
            continue

        dx /= lunghezza

        dy /= lunghezza

        estremo = punto_bordo_retta(
            x0,
            y0,
            dx,
            dy,
            p
        )

        if estremo is None:
            continue

        x1, y1 = estremo

        colore = (
            p["colore_mezzogiorno"]
            if ora == 12
            else p["colore_ore"]
        )

        spessore = (
            p["spessore_linee"] + 0.8
            if ora == 12
            else p["spessore_linee"]
        )

        crea_linea(

            doc,
            gruppo,

            "Ora_%02d" % ora,

            App.Vector(x0, y0, z),
            App.Vector(x1, y1, z),

            colore,
            spessore

        )

        if p["crea_etichette"]:

            xt = x0 + 0.85 * (x1 - x0)

            yt = y0 + 0.85 * (y1 - y0)

            crea_testo(

                doc,
                gruppo,

                "%02d" % ora,

                xt + 5,
                yt + 5,

                z + 0.1,
                12

            )


# ============================================================
# SELETTORE LINEE ORARIE
# ============================================================

def crea_linee_orarie(doc, gruppo, p, x0, y0):

    orientamento = p["orientamento"]

    if orientamento == "SUD":

        crea_linee_orarie_sud(
            doc,
            gruppo,
            p,
            x0,
            y0
        )

    elif orientamento == "ORIZZONTALE":

        crea_linee_orarie_orizzontale(
            doc,
            gruppo,
            p,
            x0,
            y0
        )

    else:

        crea_linee_orarie_est_ovest(
            doc,
            gruppo,
            p,
            x0,
            y0
        )


# ============================================================
# CURVE EQUINOZI E SOLSTIZI
# ============================================================

def crea_curve_mensili(
    doc,
    gruppo,
    p,
    x0,
    y0
):

    z = p["quota_linee"]

    numero = p["campioni_curve"]

    colore = p["colore_mesi"]

    spessore = max(
        1.0,
        p["spessore_linee"] - 0.5
    )

    # Limiti angolari delle curve

    H_inizio = math.radians(
        15.0 * (p["ora_inizio"] - 12)
    )

    H_fine = math.radians(
        15.0 * (p["ora_fine"] - 12)
    )

    for indice, voce in enumerate(p["date_curve"]):

        etichetta, mese, giorno_mese = voce

        giorno = datetime.date(
            p["anno"],
            mese,
            giorno_mese
        ).timetuple().tm_yday

        if "EQUINOZ" in etichetta.upper():

            delta = 0.0

        else:

            delta = declinazione_solare(
                giorno,
                p["anno"]
            )

        punti = []

        for i in range(numero):

            H = (

                H_inizio

                + (H_fine - H_inizio)
                * i / (numero - 1)

            )

            ombra = punto_ombra(
                p,
                delta,
                H
            )

            if ombra is None:

                punti.append(None)

                continue

            x = x0 + ombra[0]

            y = y0 + ombra[1]

            if punto_nel_quadrante(x, y, p):

                punti.append(
                    App.Vector(x, y, z)
                )

            else:

                punti.append(None)

        nome = etichetta.replace(" ", "_")

        crea_segmenti_curva(

            doc,
            gruppo,

            "Calendario_" + nome,

            punti,

            colore,
            spessore

        )

        # Riferimento a metà curva visibile

        validi = [
            q for q in punti
            if q is not None
        ]

        if not validi:
            continue

        q = validi[len(validi) // 2]

        crea_linea(

            doc,
            gruppo,

            "Tacca_" + nome,

            App.Vector(q.x - 20, q.y, z + 0.2),

            App.Vector(q.x + 20, q.y, z + 0.2),

            colore,
            2.0

        )

        if p["crea_etichette"]:

            if indice % 2 == 0:

                tx = q.x + 28

            else:

                tx = q.x - len(etichetta) * 6 - 28

            crea_testo(

                doc,
                gruppo,

                etichetta,

                tx,
                q.y + 6,

                z + 0.2,
                10

            )


# ============================================================
# ANALemma
# ============================================================

def crea_analemma(
    doc,
    gruppo,
    p,
    x0,
    y0
):

    if not p["crea_analemma"]:
        return

    anno = p["anno"]

    giorni_anno = (
        366 if calendar.isleap(anno) else 365
    )

    z = p["quota_linee"] + 0.5

    punti = []

    for giorno in range(
        1,
        giorni_anno + 1
    ):

        delta = declinazione_solare(
            giorno,
            anno
        )

        H = angolo_orario_analemma(
            giorno,
            p
        )

        ombra = punto_ombra(
            p,
            delta,
            H
        )

        if ombra is None:

            punti.append(None)

            continue

        x = x0 + ombra[0]

        y = y0 + ombra[1]

        if punto_nel_quadrante(x, y, p):

            punti.append(
                App.Vector(x, y, z)
            )

        else:

            punti.append(None)

    crea_segmenti_curva(

        doc,
        gruppo,

        "Analemma_12",

        punti,

        p["colore_analemma"],

        p["spessore_linee"] + 1.0

    )

    if p["crea_etichette"]:

        validi = [
            q for q in punti
            if q is not None
        ]

        if validi:

            q = validi[len(validi) // 2]

            crea_testo(

                doc,
                gruppo,

                "ANALEMMA %.0f" % p["ora_analemma"],

                q.x + 18,
                q.y + 5,

                z + 0.1,
                10

            )


# ============================================================
# GNOMONE
# ============================================================

def crea_gnomone(doc, gruppo, p, x0, y0):

    phi = math.radians(p["latitudine"])

    lunghezza = p["lunghezza_gnomone"]

    raggio = p["raggio_gnomone"]

    orientamento = p["orientamento"]

    # --------------------------------------------------------
    # SUD
    # --------------------------------------------------------

    if orientamento == "SUD":

        direzione = App.Vector(

            0,

            -math.sin(phi),

            math.cos(phi)

        )

        base = App.Vector(
            x0,
            y0,
            0
        )

        shape = Part.makeCylinder(

            raggio,
            lunghezza,

            base,
            direzione

        )

    # --------------------------------------------------------
    # ORIZZONTALE
    # --------------------------------------------------------

    elif orientamento == "ORIZZONTALE":

        segno_nord = (
            1.0 if p["latitudine"] >= 0 else -1.0
        )

        direzione = App.Vector(

            0,

            segno_nord * math.cos(phi),

            abs(math.sin(phi))

        )

        base = App.Vector(
            x0,
            y0,
            0
        )

        asta = Part.makeCylinder(

            raggio,
            lunghezza,

            base,
            direzione

        )

        punta = base + direzione * lunghezza

        nodus = Part.makeSphere(

            raggio * 1.8,

            punta

        )

        shape = Part.makeCompound([
            asta,
            nodus
        ])

    # --------------------------------------------------------
    # EST / OVEST
    # --------------------------------------------------------

    else:

        if orientamento == "EST":

            dx = math.cos(phi)

        else:

            dx = -math.cos(phi)

        direzione = App.Vector(

            dx,
            math.sin(phi),
            0

        )

        distanza = p["stacco_gnomone"]

        centro = App.Vector(
            x0,
            y0,
            distanza
        )

        punto1 = centro - direzione * (
            lunghezza / 2.0
        )

        punto2 = centro + direzione * (
            lunghezza / 2.0
        )

        asta = Part.makeCylinder(

            raggio,
            lunghezza,

            punto1,
            direzione

        )

        supporto1 = Part.makeCylinder(

            raggio * 0.8,
            distanza,

            App.Vector(
                punto1.x,
                punto1.y,
                0
            ),

            App.Vector(0, 0, 1)

        )

        supporto2 = Part.makeCylinder(

            raggio * 0.8,
            distanza,

            App.Vector(
                punto2.x,
                punto2.y,
                0
            ),

            App.Vector(0, 0, 1)

        )

        nodus = Part.makeSphere(
            raggio * 1.8,
            centro
        )

        shape = Part.makeCompound([

            asta,
            supporto1,
            supporto2,
            nodus

        ])

    obj = doc.addObject(
        "Part::Feature",
        "Gnomone"
    )

    obj.Label = "Gnomone - " + orientamento

    obj.Shape = shape

    obj.ViewObject.ShapeColor = p["colore_gnomone"]

    gruppo.addObject(obj)

    return obj


# ============================================================
# GENERAZIONE COMPLETA
# ============================================================

def crea(**modifiche):

    # Lettura parametri

    p = get_parametri(**modifiche)

    # Posizione attacco

    x0, y0 = coordinate_attacco(p)

    if not (

        0 <= x0 <= p["larghezza"]

        and

        0 <= y0 <= p["altezza"]

    ):

        raise ValueError(
            "Punto di attacco esterno al quadrante"
        )

    if (
        p["orientamento"] == "ORIZZONTALE"
        and abs(p["latitudine"]) < 0.0001
    ):

        raise ValueError(
            "La meridiana orizzontale richiede una latitudine diversa da zero"
        )

    # Nuovo documento

    doc = App.newDocument(
        "Meridiana_" + p["orientamento"]
    )

    root = doc.addObject(
        "App::DocumentObjectGroup",
        "Meridiana"
    )

    root.Label = "MERIDIANA - " + p["orientamento"]

    # Gruppi

    g_piastra = crea_gruppo(
        doc,
        root,
        "Quadrante",
        "01 - Quadrante"
    )

    g_ore = crea_gruppo(
        doc,
        root,
        "Ore",
        "02 - Linee orarie"
    )

    g_mesi = crea_gruppo(
        doc,
        root,
        "Mesi",
        "03 - Equinozi e solstizi"
    )

    g_analemma = crea_gruppo(
        doc,
        root,
        "Analemma",
        "04 - Analemma solare"
    )

    g_gnomone = crea_gruppo(
        doc,
        root,
        "Gnomone",
        "05 - Gnomone"
    )

    # Piastra

    if p["crea_piastra"]:

        crea_piastra(
            doc,
            g_piastra,
            p
        )

    # Linee orarie

    crea_linee_orarie(
        doc,
        g_ore,
        p,
        x0,
        y0
    )

    # Curve stagionali

    crea_curve_mensili(
        doc,
        g_mesi,
        p,
        x0,
        y0
    )

    # Analemma

    crea_analemma(
        doc,
        g_analemma,
        p,
        x0,
        y0
    )

    # Gnomone

    if p["crea_gnomone"]:

        crea_gnomone(
            doc,
            g_gnomone,
            p,
            x0,
            y0
        )

    # Titolo

    if p["crea_etichette"]:

        crea_testo(

            doc,
            g_piastra,

            "MERIDIANA SOLARE - ALTIVOLE",

            25,
            p["altezza"] - 40,

            1.0,
            20

        )

        crea_testo(

            doc,
            g_piastra,

            "Latitudine %.4f - Longitudine %.4f"
            % (
                p["latitudine"],
                p["longitudine"]
            ),

            25,
            p["altezza"] - 70,

            1.0,
            12

        )

        crea_testo(

            doc,
            g_piastra,

            "ORIENTAMENTO " + p["orientamento"],

            25,
            p["altezza"] - 95,

            1.0,
            11

        )

        crea_testo(

            doc,
            g_piastra,

            "ORE SOLARI APPARENTI",

            25,
            25,

            1.0,
            11

        )

    # Ricalcolo

    doc.recompute()

    # Visualizzazione

    try:

        view = Gui.activeDocument().activeView()

        if p["orientamento"] == "ORIZZONTALE":

            view.viewTop()

        else:

            view.viewAxonometric()

        view.fitAll()

    except Exception as errore:

        print("Visualizzazione:", errore)

    # Riepilogo

    phi = math.radians(p["latitudine"])

    print("")
    print("======================================")
    print("MERIDIANA GENERATA")
    print("======================================")

    print("Orientamento:", p["orientamento"])

    print("Latitudine:", p["latitudine"])

    print("Longitudine:", p["longitudine"])

    print(
        "Quadrante:",
        p["larghezza"],
        "x",
        p["altezza"],
        "mm"
    )

    print("Punto attacco:", x0, y0)

    print(
        "Intervallo orario:",
        p["ora_inizio"],
        "-",
        p["ora_fine"]
    )

    print("Ora analemma:", p["ora_analemma"])

    if p["orientamento"] == "SUD":

        print(
            "Sporgenza gnomone:",
            round(
                p["lunghezza_gnomone"] * math.cos(phi),
                2
            ),
            "mm"
        )

        print(
            "Abbassamento punta:",
            round(
                p["lunghezza_gnomone"] * math.sin(phi),
                2
            ),
            "mm"
        )

    elif p["orientamento"] == "ORIZZONTALE":

        print(
            "Proiezione nord gnomone:",
            round(
                p["lunghezza_gnomone"] * math.cos(phi),
                2
            ),
            "mm"
        )

        print(
            "Altezza punta:",
            round(
                p["lunghezza_gnomone"] * abs(math.sin(phi)),
                2
            ),
            "mm"
        )

    else:

        print(
            "Stacco nodus:",
            p["stacco_gnomone"],
            "mm"
        )

        print(
            "Lunghezza asta polare:",
            p["lunghezza_gnomone"],
            "mm"
        )

    print("======================================")

    return doc
