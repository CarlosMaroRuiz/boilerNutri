"""
Paquete de base de conocimiento para optimización de alimentos para pollos.

Este paquete contiene todos los datos del dominio específico:
ingredientes, requerimientos nutricionales, razas y proveedores.
"""

from .ingredientes import INGREDIENTES
from .requerimientos import REQUERIMIENTOS_NUTRICIONALES
from .razas import RAZAS_POLLOS
from .proveedores import PROVEEDORES

__all__ = [
    'INGREDIENTES',
    'REQUERIMIENTOS_NUTRICIONALES', 
    'RAZAS_POLLOS',
    'PROVEEDORES'
]
