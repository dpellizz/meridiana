
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
    angolo_orario_analemma,
    angolo_orario_ora
)

from geometria import (
    punto_ombra,
    sole_illumina_superficie,
    punto_nel_quadrante,
    segmento_nel_quadrante,
    crea_linea,
    crea_curva,
    crea_segmenti_curva,
    crea_testo as crea_testo_base
)


# ============================================================
# CREAZIONE GRUPPI
# ============================================================

def crea_testo_nel_quadrante(
    doc,
    gruppo,
    testo,
    x,
    y,
    z,
    dimensione,
    p
):

    larghezza_stimata = len(str(testo)) * dimensione * 0.6
    margine = p["margine_etichette"]

    x = max(
        margine,
        min(
            x,
            p["larghezza"] - larghezza_stimata - margine
        )
    )

    y = max(
        margine,
        min(
            y,
            p["altezza"] - dimensione - margine
        )
    )

    return crea_testo_base(
        doc,
        gruppo,
        testo,
        x,
        y,
        z,
        dimensione
    )


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

    x = p["larghezza"] * p["x_attacco"]

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
# VERIFICA ORE ILLUMINATE
# ============================================================

def ora_illuminata(p, angolo_orario):

    giorni_anno = (
        366 if calendar.isleap(p["anno"]) else 365
    )

    for giorno in range(1, giorni_anno + 1):

        delta = declinazione_solare(
            giorno,
            p["anno"]
        )

        if sole_illumina_superficie(
            p,
            delta,
            angolo_orario
        ):

            return True

    return False


def ore_illuminate(p):

    return [
        ora for ora in range(24)
        if ora_illuminata(
            p,
            angolo_orario_ora(ora, p)
        )
    ]


# ============================================================
# LINEE ORARIE - PARETE SUD
# ============================================================

def crea_linee_orarie_sud(
    doc,
    gruppo,
    p,
    x0,
    y0,
    disegna_linee=True
):

    phi = math.radians(p["latitudine"])

    z = p["quota_linee"]

    for ora in ore_illuminate(p):

        H = angolo_orario_ora(ora, p)

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

        if disegna_linee:

            crea_linea(

                doc,
                gruppo,

                "Ora_%02d" % ora,

                App.Vector(x0, y0, z),
                App.Vector(x1, y1, z),

                colore,
                spessore

            )

        if p["crea_etichette"] and p["crea_etichette_ore"]:

            xt = x0 + 0.87 * (x1 - x0)

            yt = y0 + 0.87 * (y1 - y0)

            crea_testo_nel_quadrante(

                doc,
                gruppo,

                "%02d" % ora,

                xt + p["margine_etichette"],
                yt + p["margine_etichette"],

                z,
                p["dimensione_testo"],
                p

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
    y0,
    disegna_linee=True
):

    z = p["quota_linee"]

    anno = p["anno"]

    giorno_inverno = datetime.date(
        anno,
        12,
        21
    ).timetuple().tm_yday

    giorno_estate = datetime.date(
        anno,
        6,
        21
    ).timetuple().tm_yday

    delta_inverno = declinazione_solare(
        giorno_inverno,
        anno
    )

    delta_estate = declinazione_solare(
        giorno_estate,
        anno
    )

    # Per EST/OVEST si valutano tutte le ore. L'intervallo
    # configurato indica le ore illuminate, non le sole linee
    # geometricamente contenute nel quadrante.
    for ora in ore_illuminate(p):

        H = angolo_orario_ora(ora, p)

        # Le linee orarie EST/OVEST sono parallele al gnomone.
        # I loro estremi sono fissati dalle due declinazioni
        # dei solstizi, non dai bordi del quadrante.
        ombra_inverno = punto_ombra(
            p,
            delta_inverno,
            H,
            controlla_illuminazione=False
        )

        ombra_estate = punto_ombra(
            p,
            delta_estate,
            H,
            controlla_illuminazione=False
        )

        if ombra_inverno is not None and ombra_estate is not None:

            segmento = segmento_nel_quadrante(
                x0 + ombra_inverno[0],
                y0 + ombra_inverno[1],
                x0 + ombra_estate[0],
                y0 + ombra_estate[1],
                p
            )

            if segmento is None:
                continue

            punto_inizio, punto_fine = segmento

            if disegna_linee:

                crea_linea(
                    doc,
                    gruppo,
                    "Ora_%02d" % ora,
                    App.Vector(
                        punto_inizio[0],
                        punto_inizio[1],
                        z
                    ),
                    App.Vector(
                        punto_fine[0],
                        punto_fine[1],
                        z
                    ),
                    p["colore_mezzogiorno"]
                    if ora == 12 else p["colore_ore"],
                    p["spessore_linee"]
                )

            qx = (
                punto_inizio[0] + punto_fine[0]
            ) / 2.0

            qy = (
                punto_inizio[1] + punto_fine[1]
            ) / 2.0

            if (
                p["crea_etichette"]
                and p["crea_etichette_ore"]
                and punto_nel_quadrante(qx, qy, p)
            ):

                crea_testo_nel_quadrante(

                    doc,
                    gruppo,

                    "%02d" % ora,

                    qx + 6,
                    qy + 6,

                    z,
                    p["dimensione_testo"],
                    p

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
    y0,
    disegna_linee=True
):

    z = p["quota_linee"]

    for ora in ore_illuminate(p):

        H = angolo_orario_ora(ora, p)

        # La declinazione zero è sufficiente
        # per determinare la direzione della retta oraria.

        ombra = punto_ombra(
            p,
            0.0,
            H,
            controlla_illuminazione=False
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

        if disegna_linee:

            crea_linea(

                doc,
                gruppo,

                "Ora_%02d" % ora,

                App.Vector(x0, y0, z),
                App.Vector(x1, y1, z),

                colore,
                spessore

            )

        if p["crea_etichette"] and p["crea_etichette_ore"]:

            xt = x0 + 0.85 * (x1 - x0)

            yt = y0 + 0.85 * (y1 - y0)

            crea_testo_nel_quadrante(

                doc,
                gruppo,

                "%02d" % ora,

                xt + 5,
                yt + 5,

                z,
                p["dimensione_testo"],
                p

            )


# ============================================================
# SELETTORE LINEE ORARIE
# ============================================================

def crea_linee_orarie(
    doc,
    gruppo,
    p,
    x0,
    y0,
    disegna_linee=True
):

    orientamento = p["orientamento"]

    if orientamento == "SUD":

        crea_linee_orarie_sud(
            doc,
            gruppo,
            p,
            x0,
            y0,
            disegna_linee
        )

    elif orientamento == "ORIZZONTALE":

        crea_linee_orarie_orizzontale(
            doc,
            gruppo,
            p,
            x0,
            y0,
            disegna_linee
        )

    else:

        crea_linee_orarie_est_ovest(
            doc,
            gruppo,
            p,
            x0,
            y0,
            disegna_linee
        )


# ============================================================
# CURVE EQUINOZI E SOLSTIZI
# ============================================================

def crea_curve_calendariali(
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

    # Le curve calendariali vengono estese sull'intero
    # intervallo geometrico della giornata. I punti fuori
    # dal quadrante vengono poi eliminati.
    if p["orientamento"] in (
        "SUD",
        "EST",
        "OVEST",
        "ORIZZONTALE"
    ):

        H_inizio = math.radians(-89.9)
        H_fine = math.radians(89.9)
        estesa = p["estendi_curve_calendariali"]

    for indice, voce in enumerate(p["date_curve"]):

        if len(voce) == 3:
            etichetta, mese, giorno_mese = voce
            declinazione_gradi = None

        else:
            (
                etichetta,
                mese,
                giorno_mese,
                declinazione_gradi
            ) = voce

        giorno = datetime.date(
            p["anno"],
            mese,
            giorno_mese
        ).timetuple().tm_yday

        if declinazione_gradi is None:
            delta = declinazione_solare(
                giorno,
                p["anno"]
            )

        else:
            delta = math.radians(
                declinazione_gradi
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
                H,
                controlla_illuminazione=not estesa
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

        if (
            p["crea_etichette"]
            and p["crea_etichette_curve"]
        ):

            if indice % 2 == 0:

                tx = q.x + 4 * p["margine_etichette"]

            else:

                tx = (
                    q.x
                    - len(etichetta) * 6
                    - 4 * p["margine_etichette"]
                )

            crea_testo_nel_quadrante(

                doc,
                gruppo,

                etichetta,

                tx,
                q.y + p["margine_etichette"],

                z,
                p["dimensione_testo"],
                p

            )


# ============================================================
# ANALemma
# ============================================================

def giorni_analemma(p):

    giorni_anno = (
        366 if calendar.isleap(p["anno"]) else 365
    )

    periodo = p["periodo_analemma"]

    if periodo == "anno_intero":
        return range(1, giorni_anno + 1)

    solstizio_estivo = datetime.date(
        p["anno"], 6, 21
    ).timetuple().tm_yday

    solstizio_invernale = datetime.date(
        p["anno"], 12, 21
    ).timetuple().tm_yday

    if periodo == "solstizio_estivo_invernale":
        return range(
            solstizio_estivo,
            solstizio_invernale + 1
        )

    # Questo intervallo attraversa il cambio di anno:
    # comprende dal solstizio invernale a fine anno e
    # dall'inizio dell'anno al solstizio estivo.
    return list(range(
        solstizio_invernale,
        giorni_anno + 1
    )) + list(range(
        1,
        solstizio_estivo + 1
    ))


def ore_analemma(p):

    if not p["analemma_tutte_ore_luce"]:
        return [p["ora_analemma"]]

    passo = p["passo_analemma_minuti"]

    return [
        minuti / 60.0
        for minuti in range(0, 24 * 60, passo)
        if ora_illuminata(
            p,
            angolo_orario_ora(minuti / 60.0, p)
        )
    ]


def suffisso_analemma(ora):

    minuti = round(ora * 60)

    if minuti % 60 == 0:
        return "%.0f" % ora

    return "%02d_%02d" % (
        minuti // 60,
        minuti % 60
    )


def colore_analemma(ora, p):

    minuti = round(ora * 60) % 60

    if minuti == 0:
        return p["colore_analemma"]

    if minuti == 30:
        return p["colore_analemma_mezzore"]

    return p["colore_analemma_5_minuti"]


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

    z = p["quota_linee"]

    orari = ore_analemma(p)

    for ora in orari:

        parametri_ora = p.copy()
        parametri_ora["ora_analemma"] = ora

        punti = []

        for giorno in giorni_analemma(p):

            delta = declinazione_solare(
                giorno,
                anno
            )

            H = angolo_orario_analemma(
                giorno,
                parametri_ora
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

        suffisso = suffisso_analemma(ora)

        crea_segmenti_curva(

            doc,
            gruppo,

            "Analemma_" + suffisso,

            punti,

            colore_analemma(ora, p),

            p["spessore_analemma"]

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


def crea_riferimento_gnomone(doc, gruppo, p, x0, y0):

    phi = math.radians(p["latitudine"])
    lunghezza = p["lunghezza_gnomone"]
    z = p["quota_linee"] + 0.05

    if p["orientamento"] in ("EST", "OVEST"):

        segno = 1.0 if p["orientamento"] == "EST" else -1.0
        dx = segno * math.cos(phi)
        dy = math.sin(phi)

        punti_base = (
            (
                x0 - dx * lunghezza / 2.0,
                y0 - dy * lunghezza / 2.0
            ),
            (
                x0 + dx * lunghezza / 2.0,
                y0 + dy * lunghezza / 2.0
            )
        )

    else:

        punti_base = ((x0, y0),)

    cerchi = [
        Part.makeCylinder(
            p["raggio_gnomone"],
            0.1,
            App.Vector(x, y, z),
            App.Vector(0, 0, 1)
        )
        for x, y in punti_base
    ]

    shape = Part.makeCompound(
        cerchi
    )

    obj = doc.addObject(
        "Part::Feature",
        "RiferimentoGnomone"
    )

    obj.Label = "Punti attacco gnomone"
    obj.Shape = shape
    obj.ViewObject.ShapeColor = p["colore_gnomone"]
    obj.ViewObject.LineColor = p["colore_gnomone"]
    obj.ViewObject.LineWidth = p["spessore_linee"] + 0.5

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

    crea_etichette_ore = (
        p["crea_etichette"]
        and p["crea_etichette_ore"]
    )

    if p["crea_linee_orarie"] or crea_etichette_ore:

        crea_linee_orarie(
            doc,
            g_ore,
            p,
            x0,
            y0,
            p["crea_linee_orarie"]
        )

    # Curve stagionali

    crea_curve_calendariali(
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

    if p["crea_riferimento_gnomone"]:

        crea_riferimento_gnomone(
            doc,
            g_gnomone,
            p,
            x0,
            y0
        )

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

        crea_testo_nel_quadrante(

            doc,
            g_piastra,

            "MERIDIANA SOLARE - ALTIVOLE",

            25,
            p["altezza"] - 40,

            p["quota_linee"],
            p["dimensione_titolo"],
            p

        )

        crea_testo_nel_quadrante(

            doc,
            g_piastra,

            "Latitudine %.4f - Longitudine %.4f"
            % (
                p["latitudine"],
                p["longitudine"]
            ),

            25,
            p["altezza"] - 70,

            p["quota_linee"],
            p["dimensione_testo"],
            p

        )

        crea_testo_nel_quadrante(

            doc,
            g_piastra,

            "ORIENTAMENTO " + p["orientamento"],

            25,
            p["altezza"] - 95,

            p["quota_linee"],
            p["dimensione_testo"],
            p

        )

        crea_testo_nel_quadrante(

            doc,
            g_piastra,

            "ORE SOLARI APPARENTI",

            25,
            25,

            p["quota_linee"],
            p["dimensione_testo"],
            p

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

    print("Ore disegnate:", ore_illuminate(p))

    print("Ora analemma:", p["ora_analemma"])

    print("Passo analemma:", p["passo_analemma_minuti"], "minuti")

    print("Periodo analemma:", p["periodo_analemma"])

    if p["modalita_diagnostica"]:

        print("Ore illuminate:", ore_illuminate(p))
        print(
            "Curve calendariali estese:",
            p["estendi_curve_calendariali"]
        )
        print(
            "Riferimento linee orarie:",
            p["riferimento_linee_orarie"]
        )

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
