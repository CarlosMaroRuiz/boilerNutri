"""
Paquete de utilidades para el sistema boilerNutri.

Contiene funciones para visualización, generación de reportes
y procesamiento de entradas del usuario.
"""

from .visualizacion import generar_graficas
from .reporte import generar_reporte_completo
from .entrada_usuario import procesar_entradas

__all__ = ['generar_graficas', 'generar_reporte_completo', 'procesar_entradas']
