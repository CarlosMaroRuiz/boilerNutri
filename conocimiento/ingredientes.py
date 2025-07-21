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
            "max": 1.00,       # Sin máximo específico (según tus datos: "maiz puede ser cualquier cantidad")
            "comentario": "Puede usarse en cualquier cantidad"
        },
        "disponibilidadLocal": 1.0,  # Muy disponible (100%)
        "precio_base": 7.125    # Precio promedio: $285 ÷ 40kg = $7.125 por kg
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
            "veterinaria_buenavista": 12.9,     # $12.9 por kg
            "veterinaria_don_paco": 12.7,       # $12.7 por kg
            "veterinaria_don_edilberto": 12.8   # $12.8 por kg
        },
        "limitaciones": {
            "min": 0.05,        # Mínimo 5% en la formulación
            "max": 0.30,        # Máximo 30% en la formulación (según tus datos: "soya muy cargada genera diarrea")
            "comentario": "En exceso genera diarrea, usar con moderación"
        },
        "disponibilidadLocal": 0.8,  # Buena disponibilidad (80%)
        "precio_base": 12.75    # Precio promedio: $510 ÷ 40kg = $12.75 por kg
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
            "veterinaria_buenavista": 10.4,     # $10.4 por kg
            "veterinaria_don_paco": 10.2,       # $10.2 por kg
            "veterinaria_don_edilberto": 10.3   # $10.3 por kg
        },
        "limitaciones": {
            "min": 0.00,        # Sin mínimo requerido
            "max": 0.15,        # Máximo 15% en la formulación
            "comentario": "Alto contenido de fibra limita su uso"
        },
        "disponibilidadLocal": 0.7,  # Disponibilidad media (70%)
        "precio_base": 10.25    # Precio promedio: $410 ÷ 40kg = $10.25 por kg
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
            "veterinaria_buenavista": 6.35,     # $6.35 por kg
            "veterinaria_don_paco": 6.15,       # $6.15 por kg
            "veterinaria_don_edilberto": 6.25   # $6.25 por kg
        },
        "limitaciones": {
            "min": 0.00,        # Sin mínimo requerido
            "max": 0.60,        # Máximo 60% en la formulación
            "comentario": "Buena alternativa al maíz"
        },
        "disponibilidadLocal": 0.9,  # Muy disponible (90%)
        "precio_base": 6.25     # Precio promedio: $250 ÷ 40kg = $6.25 por kg
    },
    {
        "id": 5,
        "nombre": "Premezcla Micro/Macro Minerales Económica",
        "nutrientes": {
            "proteina": 0.00,    # 0% de proteína
            "energia": 0,        # 0 kcal/kg
            "lisina": 0.0000,    # 0% de lisina
            "metionina": 0.0000, # 0% de metionina
            "calcio": 0.18,      # 18% de calcio
            "fosforo": 0.12,     # 12% de fósforo disponible
            "fibra": 0.00,       # 0% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 30.5,     # $30.5 por kg
            "veterinaria_don_paco": 30.0,       # $30.0 por kg
            "veterinaria_don_edilberto": 30.2   # $30.2 por kg
        },
        "limitaciones": {
            "min": 0.02,        # Exactamente 2% en la formulación
            "max": 0.02,        # Exactamente 2% en la formulación
            "comentario": "Usar exactamente 20kg por tonelada de alimento (2%)"
        },
        "disponibilidadLocal": 0.8,  # Buena disponibilidad (80%)
        "precio_base": 30.0     # Precio: $600 ÷ 20kg = $30 por kg
    },
    {
        "id": 6,
        "nombre": "Premezcla Micro/Macro Minerales Premium",
        "nutrientes": {
            "proteina": 0.00,    # 0% de proteína
            "energia": 0,        # 0 kcal/kg
            "lisina": 0.0000,    # 0% de lisina
            "metionina": 0.0000, # 0% de metionina
            "calcio": 0.20,      # 20% de calcio
            "fosforo": 0.15,     # 15% de fósforo disponible
            "fibra": 0.00,       # 0% de fibra
        },
        "precios": {
            "veterinaria_buenavista": 40.5,     # $40.5 por kg
            "veterinaria_don_paco": 40.0,       # $40.0 por kg
            "veterinaria_don_edilberto": 40.2   # $40.2 por kg
        },
        "limitaciones": {
            "min": 0.02,        # Exactamente 2% en la formulación
            "max": 0.02,        # Exactamente 2% en la formulación
            "comentario": "Usar exactamente 20kg por tonelada de alimento (2%)"
        },
        "disponibilidadLocal": 0.7,  # Disponibilidad media (70%)
        "precio_base": 40.0     # Precio: $800 ÷ 20kg = $40 por kg
    }
]