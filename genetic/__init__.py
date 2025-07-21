"""
Paquete del algoritmo genético para optimización de formulaciones.

Contiene la implementación completa del algoritmo genético multiobjetivo
con estrategia adaptativa por fases.
"""

from .ag import AlgoritmoGenetico
from .individuo import Individuo

__all__ = ['AlgoritmoGenetico', 'Individuo']
