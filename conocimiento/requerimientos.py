"""
Requerimientos nutricionales para pollos según etapa de crecimiento.

Define los valores objetivo de nutrientes para cada fase:
iniciación, crecimiento y finalización.
"""

# Requerimientos nutricionales por etapa
REQUERIMIENTOS_NUTRICIONALES = {
    "iniciacion": {  # 1-10 días
        # TODO: Implementar requerimientos completos
        "proteina": 0.22,       # 22% de proteína
        "energia": 3000,        # 3000 kcal/kg
        # ... otros nutrientes
    },
    "crecimiento": { # 11-24 días
        # TODO: Implementar requerimientos completos
        "proteina": 0.21,       # 21% de proteína
        "energia": 3050,        # 3050 kcal/kg
        # ... otros nutrientes
    },
    "finalizacion": { # 25-42 días
        # TODO: Implementar requerimientos completos
        "proteina": 0.19,       # 19% de proteína
        "energia": 3100,        # 3100 kcal/kg
        # ... otros nutrientes
    }
}
