# ============================================================
# PROFILI DELLE MERIDIANE
# ============================================================

# Specificare qui solo i valori diversi dalla configurazione
# generale definita in parametri.py.
PROFILI = {
    "fanzolo_sud": {
        "luogo": {
            "latitudine": 45.759280,
            "longitudine": 11.956828,
        },
        "quadrante": {
            "orientamento": "SUD",
            "larghezza": 300.0,
            "altezza": 300.0,
        },
        "gnomone": {
            "lunghezza": 10.0,
        },
    },
    "meridiana_est": {
        "luogo": {
            "latitudine": 45.759280,
            "longitudine": 11.956828,
        },
        "quadrante": {
            "orientamento": "EST",
            "larghezza": 300.0,
            "altezza": 300.0,
        },
        "gnomone": {
            "lunghezza": 100.0,
        },
    },
}

# Profilo usato da avvia_meridiana.FCMacro.
# None mantiene il comportamento della configurazione generale.
PROFILO_ATTIVO = "meridiana_est"
