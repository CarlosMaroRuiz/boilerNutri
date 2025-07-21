"""
Base de datos de ingredientes disponibles para formulaciones de alimentos.

Contiene información nutricional, precios y limitaciones de uso
para cada ingrediente disponible en la localidad.
"""

# Base de datos de ingredientes
INGREDIENTES = [
    {
        "id": 1,
        "nombre": "Maíz",
        "nutrientes": {
            "proteina": 0.085,  # 8.5% de proteína
            "energia": 3350,    # 3350 kcal/kg de energía metabolizable
            "lisina": 0.0026,   # 0.26% de lisina
            "metionina": 0.0018, # 0.18% de metionina
            "calcio": 0.0002,   # 0.02% de calcio
            "fosforo": 0.0008,  # 0.08% de fósforo disponible
            "fibra": 0.025,     # 2.5% de fibra cruda
        },
        "precios": {
            "veterinaria_buenavista": 7.3,     # $7.3 por kg
            "veterinaria_don_paco": 7.1,       # $7.1 por kg
            "veterinaria_don_edilberto": 7.2   # $7.2 por kg
        },
        "limitaciones": {
            "min": 0.00,       # Sin mínimo requerido
            "max": 1.00,       # Sin máximo específico
            "comentario": "Puede usarse en cualquier cantidad"
        },
        "disponibilidadLocal": 1.0,  # Muy disponible (100%)
        "precio_base": 7.125
    },
    {
        "id": 2,
        "nombre": "Pasta de Soya",
        "nutrientes": {
            "proteina": 0.46,    # 46% de proteína
            "energia": 2230,     # 2230 kcal/kg
            "lisina": 0.0280,    # 2.8% de lisina
            "metionina": 0.0065, # 0.65% de metionina
            "calcio": 0.0025,    # 0.25% de calcio
            "fosforo": 0.0060,   # 0.6% de fósforo disponible
            "fibra": 0.035,      # 3.5% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 12.9,
            "veterinaria_don_paco": 12.7,
            "veterinaria_don_edilberto": 12.8
        },
        "limitaciones": {
            "min": 0.05,        # Mínimo 5% en la formulación
            "max": 0.30,        # Máximo 30% en la formulación
            "comentario": "En exceso genera diarrea, usar con moderación"
        },
        "disponibilidadLocal": 0.8,
        "precio_base": 12.75
    },
    {
        "id": 3,
        "nombre": "DDG (Granos Secos de Destilería)",
        "nutrientes": {
            "proteina": 0.27,    # 27% de proteína
            "energia": 2480,     # 2480 kcal/kg
            "lisina": 0.0078,    # 0.78% de lisina
            "metionina": 0.0050, # 0.5% de metionina
            "calcio": 0.0020,    # 0.2% de calcio
            "fosforo": 0.0077,   # 0.77% de fósforo disponible
            "fibra": 0.075,      # 7.5% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 10.4,
            "veterinaria_don_paco": 10.2,
            "veterinaria_don_edilberto": 10.3
        },
        "limitaciones": {
            "min": 0.00,
            "max": 0.15,        # Máximo 15% en la formulación
            "comentario": "Alto contenido de fibra limita su uso"
        },
        "disponibilidadLocal": 0.7,
        "precio_base": 10.25
    },
    {
        "id": 4,
        "nombre": "Sorgo",
        "nutrientes": {
            "proteina": 0.09,    # 9% de proteína
            "energia": 3250,     # 3250 kcal/kg
            "lisina": 0.0022,    # 0.22% de lisina
            "metionina": 0.0017, # 0.17% de metionina
            "calcio": 0.0003,    # 0.03% de calcio
            "fosforo": 0.0009,   # 0.09% de fósforo disponible
            "fibra": 0.028,      # 2.8% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 6.35,
            "veterinaria_don_paco": 6.15,
            "veterinaria_don_edilberto": 6.25
        },
        "limitaciones": {
            "min": 0.00,
            "max": 0.60,        # Máximo 60% en la formulación
            "comentario": "Buena alternativa al maíz"
        },
        "disponibilidadLocal": 0.9,
        "precio_base": 6.25
    },
    {
        "id": 5,
        "nombre": "Premezcla Micro/Macro Minerales Económica",
        "nutrientes": {
            "proteina": 0.00,
            "energia": 0,
            "lisina": 0.0000,
            "metionina": 0.0000,
            "calcio": 0.18,      # 18% de calcio
            "fosforo": 0.12,     # 12% de fósforo disponible
            "fibra": 0.00,
        },
        "precios": {
            "veterinaria_buenavista": 30.5,
            "veterinaria_don_paco": 30.0,
            "veterinaria_don_edilberto": 30.2
        },
        "limitaciones": {
            "min": 0.02,        # Exactamente 2%
            "max": 0.02,
            "comentario": "Usar exactamente 20kg por tonelada de alimento (2%)"
        },
        "disponibilidadLocal": 0.8,
        "precio_base": 30.0
    },
    {
        "id": 6,
        "nombre": "Premezcla Micro/Macro Minerales Premium",
        "nutrientes": {
            "proteina": 0.00,
            "energia": 0,
            "lisina": 0.0000,
            "metionina": 0.0000,
            "calcio": 0.20,      # 20% de calcio
            "fosforo": 0.15,     # 15% de fósforo disponible
            "fibra": 0.00,
        },
        "precios": {
            "veterinaria_buenavista": 40.5,
            "veterinaria_don_paco": 40.0,
            "veterinaria_don_edilberto": 40.2
        },
        "limitaciones": {
            "min": 0.02,        # Exactamente 2%
            "max": 0.02,
            "comentario": "Usar exactamente 20kg por tonelada de alimento (2%)"
        },
        "disponibilidadLocal": 0.7,
        "precio_base": 40.0
    },
    # =====================================================
    # NUEVOS INGREDIENTES PARA RESOLVER DÉFICITS CRÍTICOS
    # =====================================================
    {
        "id": 7,
        "nombre": "L-Lisina HCl (98%)",
        "nutrientes": {
            "proteina": 0.00,    # 0% de proteína
            "energia": 0,        # 0 kcal/kg
            "lisina": 0.784,     # 78.4% de lisina (98% pureza × 80% lisina)
            "metionina": 0.0000, # 0% de metionina
            "calcio": 0.0000,    # 0% de calcio
            "fosforo": 0.0000,   # 0% de fósforo
            "fibra": 0.00,       # 0% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 3.7,      # $3.7 por kg
            "veterinaria_don_paco": 3.5,        # $3.5 por kg (mejor precio)
            "veterinaria_don_edilberto": 3.6    # $3.6 por kg
        },
        "limitaciones": {
            "min": 0.001,       # Mínimo 0.1% (1kg por tonelada)
            "max": 0.008,       # Máximo 0.8% (8kg por tonelada)
            "comentario": "Aminoácido sintético - usar solo lo necesario"
        },
        "disponibilidadLocal": 0.85,  # Buena disponibilidad en veterinarias especializadas
        "precio_base": 3.6
    },
    {
        "id": 8,
        "nombre": "DL-Metionina (99%)",
        "nutrientes": {
            "proteina": 0.00,    # 0% de proteína
            "energia": 0,        # 0 kcal/kg
            "lisina": 0.0000,    # 0% de lisina
            "metionina": 0.594,  # 59.4% de metionina (99% pureza × 60% metionina)
            "calcio": 0.0000,    # 0% de calcio
            "fosforo": 0.0000,   # 0% de fósforo
            "fibra": 0.00,       # 0% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 4.4,      # $4.4 por kg
            "veterinaria_don_paco": 4.2,        # $4.2 por kg (mejor precio)
            "veterinaria_don_edilberto": 4.3    # $4.3 por kg
        },
        "limitaciones": {
            "min": 0.001,       # Mínimo 0.1% (1kg por tonelada)
            "max": 0.005,       # Máximo 0.5% (5kg por tonelada)
            "comentario": "Aminoácido sintético - pequeñas cantidades son muy efectivas"
        },
        "disponibilidadLocal": 0.85,  # Buena disponibilidad en veterinarias especializadas
        "precio_base": 4.3
    },
    {
        "id": 9,
        "nombre": "Aceite de Soya",
        "nutrientes": {
            "proteina": 0.00,    # 0% de proteína
            "energia": 8800,     # 8800 kcal/kg (muy alto en energía)
            "lisina": 0.0000,    # 0% de lisina
            "metionina": 0.0000, # 0% de metionina
            "calcio": 0.0000,    # 0% de calcio
            "fosforo": 0.0000,   # 0% de fósforo
            "fibra": 0.00,       # 0% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 1.9,      # $1.9 por kg
            "veterinaria_don_paco": 1.8,        # $1.8 por kg (mejor precio)
            "veterinaria_don_edilberto": 1.85   # $1.85 por kg
        },
        "limitaciones": {
            "min": 0.01,        # Mínimo 1% (10kg por tonelada)
            "max": 0.06,        # Máximo 6% (60kg por tonelada)
            "comentario": "Fuente concentrada de energía - no exceder 6%"
        },
        "disponibilidadLocal": 0.9,  # Muy disponible
        "precio_base": 1.85
    },
    {
        "id": 10,
        "nombre": "Fosfato Dicálcico",
        "nutrientes": {
            "proteina": 0.00,    # 0% de proteína
            "energia": 0,        # 0 kcal/kg
            "lisina": 0.0000,    # 0% de lisina
            "metionina": 0.0000, # 0% de metionina
            "calcio": 0.24,      # 24% de calcio
            "fosforo": 0.18,     # 18% de fósforo disponible
            "fibra": 0.00,       # 0% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 2.9,      # $2.9 por kg
            "veterinaria_don_paco": 2.8,        # $2.8 por kg (mejor precio)
            "veterinaria_don_edilberto": 2.85   # $2.85 por kg
        },
        "limitaciones": {
            "min": 0.005,       # Mínimo 0.5% (5kg por tonelada)
            "max": 0.025,       # Máximo 2.5% (25kg por tonelada)
            "comentario": "Fuente balanceada de calcio y fósforo"
        },
        "disponibilidadLocal": 0.8,  # Buena disponibilidad
        "precio_base": 2.85
    },
    {
        "id": 11,
        "nombre": "Harina de Gluten de Maíz",
        "nutrientes": {
            "proteina": 0.60,    # 60% de proteína (muy alta)
            "energia": 4200,     # 4200 kcal/kg (alta energía)
            "lisina": 0.0090,    # 0.9% de lisina (bajo)
            "metionina": 0.0180, # 1.8% de metionina (alto)
            "calcio": 0.0005,    # 0.05% de calcio
            "fosforo": 0.0050,   # 0.5% de fósforo
            "fibra": 0.020,      # 2% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 9.2,      # $9.2 por kg
            "veterinaria_don_paco": 9.0,        # $9.0 por kg (mejor precio)
            "veterinaria_don_edilberto": 9.1    # $9.1 por kg
        },
        "limitaciones": {
            "min": 0.00,        # Sin mínimo requerido
            "max": 0.15,        # Máximo 15% (150kg por tonelada)
            "comentario": "Rica en proteína y energía, complementa aminoácidos"
        },
        "disponibilidadLocal": 0.75,  # Disponibilidad media-alta
        "precio_base": 9.1
    },
    {
        "id": 12,
        "nombre": "Carbonato de Calcio",
        "nutrientes": {
            "proteina": 0.00,    # 0% de proteína
            "energia": 0,        # 0 kcal/kg
            "lisina": 0.0000,    # 0% de lisina
            "metionina": 0.0000, # 0% de metionina
            "calcio": 0.38,      # 38% de calcio (muy alto, sin fósforo)
            "fosforo": 0.0000,   # 0% de fósforo
            "fibra": 0.00,       # 0% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 1.2,      # $1.2 por kg
            "veterinaria_don_paco": 1.1,        # $1.1 por kg (mejor precio)
            "veterinaria_don_edilberto": 1.15   # $1.15 por kg
        },
        "limitaciones": {
            "min": 0.005,       # Mínimo 0.5% (5kg por tonelada)
            "max": 0.020,       # Máximo 2% (20kg por tonelada)
            "comentario": "Fuente pura de calcio sin fósforo - para balancear Ca:P"
        },
        "disponibilidadLocal": 0.95,  # Muy disponible
        "precio_base": 1.15
    }
]