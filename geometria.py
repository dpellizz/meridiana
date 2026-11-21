
# ============================================================
# MERIDIANA FREECAD - GEOMETRIA
# ============================================================

import FreeCAD as App
import Part
import math

from astronomia import vettore_sole


# ============================================================
# CALCOLO DEL PUNTO D'OMBRA
#
# Restituisce X,Y relative al piede dello gnomone.
# Restituisce None se il Sole non illumina la superficie.
# ============================================================

def punto_ombra(parametri, declinazione, angolo_orario):

    phi = math.radians(parametri["latitudine"])

    orientamento = parametri["orientamento"]

    L = parametri["lunghezza_gnomone"]

    H = angolo_orario
    delta = declinazione

    est, nord, alto = vettore_sole(
        delta,
        H,
        parametri["latitudine"]
    )

    # Il Sole deve essere sopra l'orizzonte

    if alto <= 0.00001:
        return None

    # --------------------------------------------------------
    # MERIDIANA SUD
    # --------------------------------------------------------

    if orientamento == "SUD":

        # Normale esterna della parete verso sud

        D = -nord

        if D <= 0.00001:
            return None

        # Altezza della punta dello gnomone

        K = L * math.cos(phi) / D

        # X positivo verso OVEST nella vista frontale

        x = -K * math.cos(delta) * math.sin(H)

        # Y positivo verso l'alto

        y = -L * math.sin(phi) - K * alto

        return x, y

    # --------------------------------------------------------
    # MERIDIANA ORIZZONTALE
    #
    # X positivo EST
    # Y positivo NORD
    # --------------------------------------------------------

    if orientamento == "ORIZZONTALE":

        segno_nord = (
            1.0 if parametri["latitudine"] >= 0 else -1.0
        )

        # Coordinate della punta dello gnomone

        tip_y = (
            L * math.cos(phi) * segno_nord
        )

        tip_z = (
            L * abs(math.sin(phi))
        )

        if tip_z <= 0.00001:
            return None

        # Intersezione del raggio con il piano orizzontale

        t = tip_z / alto

        x = -t * est

        y = tip_y - t * nord

        return x, y

    # --------------------------------------------------------
    # MERIDIANA EST
    # --------------------------------------------------------

    distanza = parametri["stacco_gnomone"]

    if orientamento == "EST":

        normale = est

        orizzontale = nord

    # --------------------------------------------------------
    # MERIDIANA OVEST
    # --------------------------------------------------------

    elif orientamento == "OVEST":

        normale = -est

        orizzontale = -nord

    else:

        raise ValueError(
            "Orientamento non riconosciuto"
        )

    if normale <= 0.00001:
        return None

    x = -distanza * orizzontale / normale
    y = -distanza * alto / normale

    return x, y


# ============================================================
# CONTROLLO DEI LIMITI DEL QUADRANTE
# ============================================================

def punto_nel_quadrante(x, y, parametri):

    return (

        0.0 <= x <= parametri["larghezza"]

        and

        0.0 <= y <= parametri["altezza"]

    )


# ============================================================
# CREAZIONE LINEA
# ============================================================

def crea_linea(
    doc,
    gruppo,
    nome,
    p1,
    p2,
    colore=(0, 0, 0),
    spessore=1.0
):

    shape = Part.makeLine(p1, p2)

    obj = doc.addObject(
        "Part::Feature",
        nome
    )

    obj.Shape = shape

    obj.ViewObject.LineColor = colore

    obj.ViewObject.LineWidth = spessore

    gruppo.addObject(obj)

    return obj


# ============================================================
# CREAZIONE CURVA BSPLINE
# ============================================================

def crea_curva(
    doc,
    gruppo,
    nome,
    punti,
    colore=(0, 0.5, 0),
    spessore=2.0
):

    punti_puliti = []

    for punto in punti:

        if not punti_puliti:

            punti_puliti.append(punto)

            continue

        if (
            punto - punti_puliti[-1]
        ).Length > 0.001:

            punti_puliti.append(punto)

    if len(punti_puliti) < 2:
        return None

    if len(punti_puliti) == 2:

        shape = Part.makeLine(
            punti_puliti[0],
            punti_puliti[1]
        )

    else:

        spline = Part.BSplineCurve()

        spline.interpolate(
            Points=punti_puliti
        )

        shape = spline.toShape()

    obj = doc.addObject(
        "Part::Feature",
        nome
    )

    obj.Shape = shape

    obj.ViewObject.LineColor = colore

    obj.ViewObject.LineWidth = spessore

    gruppo.addObject(obj)

    return obj


# ============================================================
# CREAZIONE CURVE SUDDIVISE IN SEGMENTI
# Evita collegamenti artificiali fuori dal quadrante.
# ============================================================

def crea_segmenti_curva(
    doc,
    gruppo,
    nome,
    punti,
    colore,
    spessore
):

    segmenti = []

    segmento = []

    for punto in punti:

        if punto is None:

            if len(segmento) >= 2:
                segmenti.append(segmento)

            segmento = []

        else:

            segmento.append(punto)

    if len(segmento) >= 2:
        segmenti.append(segmento)

    risultato = []

    for indice, segmento in enumerate(segmenti):

        obj = crea_curva(
            doc,
            gruppo,
            nome + "_" + str(indice + 1),
            segmento,
            colore,
            spessore
        )

        if obj:
            risultato.append(obj)

    return risultato


# ============================================================
# CREAZIONE TESTI
# ============================================================

def crea_testo(
    doc,
    gruppo,
    testo,
    x,
    y,
    z=1.0,
    dimensione=12
):

    try:

        import Draft

        obj = Draft.make_text(
            [str(testo)],
            App.Vector(x, y, z)
        )

        gruppo.addObject(obj)

        try:
            obj.ViewObject.FontSize = dimensione
        except Exception:
            pass

        try:
            obj.ViewObject.TextColor = (
                0.05, 0.05, 0.05
            )
        except Exception:
            pass

        return obj

    except Exception as errore:

        print(
            "Impossibile creare testo:",
            testo,
            errore
        )

        return None
