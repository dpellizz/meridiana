
# ============================================================
# MERIDIANA FREECAD - GENERATORE PRINCIPALE
# ============================================================

import FreeCAD as App
import Part

import math
import calendar
import datetime
import os
import re
import tempfile

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


def crea_etichetta_ora(
    doc,
    gruppo,
    ora,
    x,
    y,
    z,
    p,
    offset_x=0.0,
    offset_y=0.0
):

    dimensione = p["dimensione_testo"]
    larghezza = len(str(ora)) * dimensione * 0.6

    return crea_testo_nel_quadrante(
        doc,
        gruppo,
        "%02d" % ora,
        x - larghezza / 2.0 + offset_x,
        y - dimensione / 2.0 + offset_y,
        z,
        dimensione,
        p
    )


def crea_etichetta_curva(
    doc,
    gruppo,
    etichetta,
    punto,
    tangente_x,
    tangente_y,
    lato,
    z,
    p
):

    dimensione = p["dimensione_testo"]
    larghezza = len(etichetta) * dimensione * 0.6
    lunghezza = math.hypot(tangente_x, tangente_y)

    if lunghezza < 0.00001:
        normale_x = 0.0
        normale_y = 1.0

    else:
        normale_x = -tangente_y / lunghezza
        normale_y = tangente_x / lunghezza

    distanza = dimensione + 2.0 * p["margine_etichette"]

    return crea_testo_nel_quadrante(
        doc,
        gruppo,
        etichetta,
        punto.x - larghezza / 2.0 + lato * distanza * normale_x,
        punto.y - dimensione / 2.0 + lato * distanza * normale_y,
        z,
        dimensione,
        p
    )


def esporta_pdf_1_1(doc, p):

    try:
        import importSVG
    except ImportError as errore:
        raise RuntimeError(
            "L'esportazione PDF richiede il modulo importSVG"
        ) from errore

    larghezza = p["larghezza"]
    altezza = p["altezza"]
    percorso = p["percorso_pdf"]
    svg_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".svg",
            delete=False
        ) as file_template:
            svg_path = file_template.name

        sorgenti = [
            oggetto
            for oggetto in doc.Objects
            if hasattr(oggetto, "Shape")
            and not oggetto.Shape.isNull()
            and not hasattr(oggetto, "Text")
        ]
        if not sorgenti:
            raise RuntimeError(
                "Nessun oggetto geometrico disponibile per il PDF"
            )

        importSVG.export(sorgenti, svg_path)

        with open(svg_path, encoding="utf-8") as file_svg:
            contenuto_svg = file_svg.read()

        contenuto_svg = re.sub(
            r'(<svg\b[^>]*\bwidth=")[^"]*(")',
            r'\g<1>%.6fmm\g<2>' % larghezza,
            contenuto_svg,
            count=1
        )
        contenuto_svg = re.sub(
            r'(<svg\b[^>]*\bheight=")[^"]*(")',
            r'\g<1>%.6fmm\g<2>' % altezza,
            contenuto_svg,
            count=1
        )

        with open(svg_path, "w", encoding="utf-8") as file_svg:
            file_svg.write(contenuto_svg)

        try:
            from PySide import QtCore, QtGui, QtSvg
            from PySide.QtPrintSupport import QPrinter
        except ImportError:
            from PySide6 import QtCore, QtGui, QtSvg
            from PySide6.QtPrintSupport import QPrinter

        renderer = QtSvg.QSvgRenderer(svg_path)
        if not renderer.isValid():
            raise RuntimeError("SVG del quadrante non valido")

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(percorso)
        printer.setFullPage(True)

        if hasattr(QtGui, "QPageSize"):
            printer.setPageSize(
                QtGui.QPageSize(
                    QtCore.QSizeF(larghezza, altezza),
                    QtGui.QPageSize.Millimeter
                )
            )
        else:
            printer.setPaperSize(
                QtCore.QSizeF(larghezza, altezza),
                QPrinter.Millimeter
            )

        painter = QtGui.QPainter(printer)
        try:
            if not renderer.render(painter):
                raise RuntimeError("Rendering SVG nel PDF non riuscito")
        finally:
            painter.end()

    finally:
        if svg_path is not None and os.path.exists(svg_path):
            os.unlink(svg_path)


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

        # X positivo verso Est,
        # Y positivo verso l'alto.

        dx = math.sin(theta)

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

        if p["crea_etichette_ore"]:

            posizione = 0.90
            xt = x0 + posizione * (x1 - x0)

            yt = y0 + posizione * (y1 - y0)

            dx = x1 - x0
            dy = y1 - y0
            lunghezza = math.hypot(dx, dy)

            crea_etichetta_ora(

                doc,
                gruppo,
                ora,
                xt,
                yt,
                z,
                p,
                -dy / lunghezza * p["dimensione_testo"],
                dx / lunghezza * p["dimensione_testo"]

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
                p["crea_etichette_ore"]
                and punto_nel_quadrante(qx, qy, p)
            ):

                crea_etichetta_ora(

                    doc,
                    gruppo,
                    ora,
                    qx,
                    qy,
                    z,
                    p,
                    p["dimensione_testo"],
                    p["dimensione_testo"]

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

        if p["crea_etichette_ore"]:

            posizione = 0.90
            xt = x0 + posizione * (x1 - x0)

            yt = y0 + posizione * (y1 - y0)

            dx = x1 - x0
            dy = y1 - y0
            lunghezza = math.hypot(dx, dy)

            crea_etichetta_ora(

                doc,
                gruppo,
                ora,
                xt,
                yt,
                z,
                p,
                -dy / lunghezza * p["dimensione_testo"],
                dx / lunghezza * p["dimensione_testo"]

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

        indici_validi = [
            indice_punto
            for indice_punto, punto in enumerate(punti)
            if punto is not None
        ]

        if not indici_validi:
            continue

        posizione = len(indici_validi) // 2
        indice_punto = indici_validi[posizione]
        q = punti[indice_punto]

        if (
            p["crea_etichette_curve"]
        ):

            indice_precedente = indici_validi[max(0, posizione - 1)]
            indice_successivo = indici_validi[
                min(len(indici_validi) - 1, posizione + 1)
            ]
            precedente = punti[indice_precedente]
            successivo = punti[indice_successivo]

            crea_etichetta_curva(

                doc,
                gruppo,
                etichetta,
                q,
                successivo.x - precedente.x,
                successivo.y - precedente.y,
                1.0 if indice % 2 == 0 else -1.0,
                z,
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
# PUNTI SU DATE E ORARI SPECIFICI
# ============================================================

def crea_punti_orari(doc, gruppo, p, x0, y0):

    for indice, voce in enumerate(p["date_punti"], start=1):

        mese, giorno_mese, ora, minuto = voce

        giorno = datetime.date(
            p["anno"],
            mese,
            giorno_mese
        ).timetuple().tm_yday

        delta = declinazione_solare(
            giorno,
            p["anno"]
        )

        parametri_istante = p.copy()
        parametri_istante["ora_analemma"] = (
            ora + minuto / 60.0
        )

        H = angolo_orario_analemma(
            giorno,
            parametri_istante
        )

        ombra = punto_ombra(p, delta, H)

        if ombra is None:
            continue

        x = x0 + ombra[0]
        y = y0 + ombra[1]

        if not punto_nel_quadrante(x, y, p):
            continue

        punto = Part.makeCylinder(
            p["diametro_punti"] / 2.0,
            max(0.01, p["spessore"] * 0.1),
            App.Vector(x, y, p["quota_linee"])
        )

        oggetto = doc.addObject(
            "Part::Feature",
            "Punto_orario_%02d" % indice
        )

        oggetto.Label = (
            "Punto %02d/%02d %02d:%02d"
            % (giorno_mese, mese, ora, minuto)
        )
        oggetto.Shape = punto
        oggetto.ViewObject.ShapeColor = p["colore_mesi"]
        gruppo.addObject(oggetto)



def crea_informazioni_gnomone(doc, gruppo, p):

    if p["orientamento"] not in ("SUD", "ORIZZONTALE"):
        return

    lunghezza = p["lunghezza_gnomone"]
    latitudine = abs(p["latitudine"])
    phi = math.radians(latitudine)

    if p["orientamento"] == "SUD":
        cateto_orizzontale = lunghezza * math.sin(phi)
        cateto_verticale = lunghezza * math.cos(phi)
        angolo = latitudine
        riferimento_angolo = "verticale"
        angolo_complementare = 90.0 - angolo
        riferimento_complementare = "quadrante"
    else:
        cateto_orizzontale = lunghezza * math.cos(phi)
        cateto_verticale = lunghezza * math.sin(phi)
        angolo = latitudine
        riferimento_angolo = "quadrante"
        angolo_complementare = 90.0 - angolo
        riferimento_complementare = "verticale"

    righe = (
        "GNOMONE: lunghezza %.1f mm" % lunghezza,
        "Cateto orizzontale: %.1f mm" % cateto_orizzontale,
        "Cateto verticale: %.1f mm" % cateto_verticale,
        "Angolo dalla %s: %.1f gradi"
        % (riferimento_angolo, angolo),
        "Angolo dal %s: %.1f gradi"
        % (riferimento_complementare, angolo_complementare),
    )

    dimensione = p["dimensione_testo"]
    distanza = dimensione + 2.0
    y = p["altezza"] - 125.0

    for riga in righe:
        crea_testo_nel_quadrante(
            doc,
            gruppo,
            riga,
            25.0,
            y,
            p["quota_linee"],
            dimensione,
            p
        )
        y -= distanza


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

    g_punti = crea_gruppo(
        doc,
        root,
        "Punti",
        "05 - Punti orari"
    )

    g_gnomone = crea_gruppo(
        doc,
        root,
        "Gnomone",
        "06 - Gnomone"
    )

    # Piastra

    if p["crea_piastra"]:

        crea_piastra(
            doc,
            g_piastra,
            p
        )

    # Linee orarie

    crea_etichette_ore = p["crea_etichette_ore"]

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

    # Punti su date e orari specifici

    crea_punti_orari(
        doc,
        g_punti,
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

    if p["crea_etichette_descrittive"]:

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

        crea_informazioni_gnomone(
            doc,
            g_piastra,
            p
        )

    # Ricalcolo

    doc.recompute()

    if p["esporta_pdf_1_1"]:

        esporta_pdf_1_1(doc, p)

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
