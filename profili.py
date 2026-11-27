# ============================================================
# PROFILI DELLE MERIDIANE
# ============================================================

# Specificare qui solo i valori diversi dalla configurazione
# generale definita in parametri.py.
PROFILI = {
    #####################
    # Fanzolo Sud
    #####################
    "fanzolo_sud": {
        "luogo": {
            "latitudine": 45.71540860064957, 
            "longitudine": 11.957945888782218,
        },
        "quadrante": {
            "orientamento": "SUD",
            "larghezza": 300.0,
            "altezza": 300.0,
        },
        "gnomone": {
            "lunghezza": 100.0,
            "raggio": 1.0,
            "posizione": {
                "x": 0.5,
                "verticale": 0.99,
                "verticale_orizzontale": 0.01,
            },
        },
    },
    
    #####################
    # Fanzolo Est
    #####################
    "fanzolo_est": {
        "luogo": {
            "latitudine": 45.71540860064957, 
            "longitudine": 11.957945888782218,
        },
        "quadrante": {
            "orientamento": "EST",
            "larghezza": 300.0,
            "altezza": 300.0,
        },
        "gnomone": {
            "lunghezza": 100.0,
            "stacco": 60,
            "raggio": 1.0,
            "posizione": {
                "x": 0.25,
                "verticale": 0.75,
                "verticale_orizzontale": 0.01,
            },
        },
    },
    
    #####################
    # Fanzolo Ovest
    #####################
    "fanzolo_ovest": {
        "luogo": {
            "latitudine": 45.71540860064957, 
            "longitudine": 11.957945888782218,
        },
        "quadrante": {
            "orientamento": "OVEST",
            "larghezza": 300.0,
            "altezza": 300.0,
        },
        "gnomone": {
            "lunghezza": 100.0,
            "stacco": 60,
            "raggio": 1.0,
            "posizione": {
                "x": 0.75,
                "verticale": 0.75,
                "verticale_orizzontale": 0.01,
            },
        },
    },
    
    #####################
    # Fanzolo Orizzontale
    #####################
    "fanzolo_orizzontale": {
        "luogo": {
            "latitudine": 45.71540860064957, 
            "longitudine": 11.957945888782218,
        },
        "quadrante": {
            "orientamento": "ORIZZONTALE",
            "larghezza": 300.0,
            "altezza": 300.0,
        },
        "gnomone": {
            "lunghezza": 100.0,
            "stacco": 60,
            "raggio": 1.0,
            "posizione": {
                "x": 0.50,
                "verticale": 0.75,
                "verticale_orizzontale": 0.01,
            },
        },
    },
        
    #####################
    # Altivole Sud
    #####################
    "altivole_sud": {
        "luogo": {
            "latitudine": 45.75929145458597, 
            "longitudine": 11.956792151351774,
        },
        "quadrante": {
            "orientamento": "SUD",
            "larghezza": 300.0,
            "altezza": 300.0,
        },
        "gnomone": {
            "lunghezza": 100.0,
            "raggio": 1.0,
            "posizione": {
                "x": 0.5,
                "verticale": 0.99,
                "verticale_orizzontale": 0.01,
            },
        },
        "analemma": {
            "abilitato": True,
            "tutte_le_ore_illuminate": True,
            "ora": None,
            "passo_minuti": 60,
            "periodo": "anno_intero",
            "riferimento_temporale": "CET",
        },
    },
}

# Profilo usato da avvia_meridiana.FCMacro.
# None mantiene il comportamento della configurazione generale.
PROFILO_ATTIVO = "altivole_sud"
