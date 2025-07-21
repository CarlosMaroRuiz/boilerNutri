"""
Paquete del algoritmo genético para optimización de formulaciones.

Contiene la implementación completa del algoritmo genético multiobjetivo
con estrategia adaptativa por fases.
"""

from .ag import AlgoritmoGenetico
from .individuo import Individuo
from .inicializacion import crear_poblacion_inicial
from .seleccion import seleccionar_padre, seleccion_elitista
from .cruza import cruza_aritmetica, cruza_blx_alpha, cruza_un_punto
from .mutacion import mutar_no_uniforme, mutar_intercambio, mutar_diferencial

__all__ = [
    # Clase principal
    'AlgoritmoGenetico',
    
    # Representación
    'Individuo',
    
    # Inicialización
    'crear_poblacion_inicial',
    
    # Selección
    'seleccionar_padre',
    'seleccion_elitista',
    
    # Cruza
    'cruza_aritmetica',
    'cruza_blx_alpha', 
    'cruza_un_punto',
    
    # Mutación
    'mutar_no_uniforme',
    'mutar_intercambio',
    'mutar_diferencial'
]

# Versión del paquete
__version__ = "1.0.0"

# Información del paquete
__author__ = "Sistema boilerNutri"
__description__ = "Algoritmo genético para optimización de formulaciones de alimentos para pollos"