
# ============================================================
# MERIDIANA FREECAD - ASTRONOMIA
# ============================================================

import math
import calendar


# ============================================================
# ANGOLO ANNUALE
# ============================================================

def angolo_gamma(giorno, anno):

    giorni_anno = 366 if calendar.isleap(anno) else 365

    return (
        2.0 * math.pi * (giorno - 1)
        / giorni_anno
    )


# ============================================================
# DECLINAZIONE SOLARE
# Risultato in radianti
# ============================================================

def declinazione_solare(giorno, anno):

    g = angolo_gamma(giorno, anno)

    delta = (

        0.006918

        - 0.399912 * math.cos(g)

        + 0.070257 * math.sin(g)

        - 0.006758 * math.cos(2 * g)

        + 0.000907 * math.sin(2 * g)

        - 0.002697 * math.cos(3 * g)

        + 0.001480 * math.sin(3 * g)

    )

    return delta


# ============================================================
# EQUAZIONE DEL TEMPO
# Risultato in minuti
# ============================================================

def equazione_del_tempo(giorno, anno):

    g = angolo_gamma(giorno, anno)

    E = 229.18 * (

        0.000075

        + 0.001868 * math.cos(g)

        - 0.032077 * math.sin(g)

        - 0.014615 * math.cos(2 * g)

        - 0.040849 * math.sin(2 * g)

    )

    return E


# ============================================================
# VETTORE SOLARE
#
# EST, NORD, ALTO
# Angolo orario positivo nel pomeriggio.
# ============================================================

def vettore_sole(declinazione, angolo_orario, latitudine):

    phi = math.radians(latitudine)

    delta = declinazione
    H = angolo_orario

    est = (
        -math.cos(delta) * math.sin(H)
    )

    nord = (

        math.cos(phi) * math.sin(delta)

        - math.sin(phi)
        * math.cos(delta)
        * math.cos(H)

    )

    alto = (

        math.sin(phi) * math.sin(delta)

        + math.cos(phi)
        * math.cos(delta)
        * math.cos(H)

    )

    return est, nord, alto


# ============================================================
# ANGOLO ORARIO PER L'ANALEMMA
# ============================================================

def correzione_riferimento_minuti(parametri, riferimento):

    if riferimento == "solare_medio_locale":
        return 0.0

    minuti = 4.0 * (
        parametri["longitudine"]
        - parametri["meridiano_fuso"]
    )

    if riferimento == "CEST":
        minuti -= 60.0

    return minuti


def angolo_orario_ora(ora, parametri):

    minuti = (
        (ora - 12.0) * 60.0
        + correzione_riferimento_minuti(
            parametri,
            parametri["riferimento_linee_orarie"]
        )
    )

    return math.radians(minuti * 0.25)


def angolo_orario_analemma(giorno, parametri):

    anno = parametri["anno"]

    ora = parametri["ora_analemma"]

    E = equazione_del_tempo(
        giorno,
        anno
    )

    # Riferimento: tempo solare medio locale

    minuti = (ora - 12.0) * 60.0 + E

    minuti += correzione_riferimento_minuti(
        parametri,
        parametri["riferimento_analemma"]
    )

    # 15 gradi per ora = 0.25 gradi per minuto

    return math.radians(minuti * 0.25)


# ============================================================
# CONVERSIONE ORA SOLARE APPARENTE -> ORA CIVILE
# ============================================================

def conversione_ora_civile(ora_solare, giorno, parametri):

    E = equazione_del_tempo(
        giorno,
        parametri["anno"]
    )

    riferimento = parametri["riferimento_analemma"]

    correzione_riferimento = correzione_riferimento_minuti(
        parametri,
        riferimento
    )

    return (

        ora_solare

        - E / 60.0

        - correzione_riferimento / 60.0

    )
