"""
Operadores de cruza para el algoritmo genético.

Implementa diferentes métodos de cruza adaptados
a la representación de porcentajes de ingredientes.
"""

import random
import numpy as np
from genetic.individuo import Individuo

def cruza_blx_alpha(padre1, padre2, alpha=0.5, ingredientes_data=None, restricciones_usuario=None):
    """
    Cruza BLX- para fase inicial (exploración)
    
    Genera un hijo en el espacio continuo cercano a los padres
    con diversidad controlada por el parámetro .
    
    Args:
        padre1: Primer padre
        padre2: Segundo padre
        alpha: Parámetro de extensión del rango (0.5 recomendado para exploración)
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo hijo generado
    """
    hijo = Individuo(len(padre1.porcentajes))
    
    for i in range(len(padre1.porcentajes)):
        # Obtener valores de los padres
        val1 = padre1.porcentajes[i]
        val2 = padre2.porcentajes[i]
        
        # Calcular rango y extensión
        min_val = min(val1, val2)
        max_val = max(val1, val2)
        rango = max_val - min_val
        extension = alpha * rango
        
        # Calcular límites extendidos
        limite_inferior = min_val - extension
        limite_superior = max_val + extension
        
        # Aplicar restricciones de ingredientes si están disponibles
        if ingredientes_data and i < len(ingredientes_data):
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            # Respetar límites del ingrediente
            limite_inferior = max(limite_inferior, limites["min"])
            limite_superior = min(limite_superior, limites["max"])
        
        # Generar valor aleatorio en el rango extendido
        if limite_inferior <= limite_superior:
            hijo.porcentajes[i] = random.uniform(limite_inferior, limite_superior)
        else:
            # Si los límites se cruzan, usar el valor promedio de los padres
            hijo.porcentajes[i] = (val1 + val2) / 2
    
    # Normalizar para que sumen 1
    hijo.normalizar(ingredientes_data, restricciones_usuario)
    
    return hijo

def cruza_aritmetica(padre1, padre2, ingredientes_data=None, restricciones_usuario=None):
    """
    Cruza aritmética para fase final (explotación)
    
    Combina proporcionalmente los padres garantizando que la suma sigue siendo 1.
    
    Args:
        padre1: Primer padre
        padre2: Segundo padre
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo hijo generado
    """
    hijo = Individuo(len(padre1.porcentajes))
    
    # Factor de mezcla aleatorio
    beta = random.random()
    
    # Combinar proporcionalmente
    for i in range(len(padre1.porcentajes)):
        hijo.porcentajes[i] = beta * padre1.porcentajes[i] + (1 - beta) * padre2.porcentajes[i]
    
    # Aplicar límites si están disponibles
    if ingredientes_data:
        hijo.aplicar_limites(ingredientes_data, restricciones_usuario)
    
    # Normalizar para mantener suma = 1
    hijo.normalizar(ingredientes_data, restricciones_usuario)
    
    return hijo

def cruza_un_punto(padre1, padre2, ingredientes_data=None, restricciones_usuario=None):
    """
    Cruza de un punto alternativa
    
    Intercambia segmentos de ingredientes entre los padres.
    
    Args:
        padre1: Primer padre
        padre2: Segundo padre
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo hijo generado
    """
    hijo = Individuo(len(padre1.porcentajes))
    
    # Punto de corte aleatorio (evitar extremos)
    if len(padre1.porcentajes) > 2:
        punto = random.randint(1, len(padre1.porcentajes) - 1)
    else:
        punto = 1
    
    # Combinar segmentos
    for i in range(len(padre1.porcentajes)):
        if i < punto:
            hijo.porcentajes[i] = padre1.porcentajes[i]
        else:
            hijo.porcentajes[i] = padre2.porcentajes[i]
    
    # Aplicar límites si están disponibles
    if ingredientes_data:
        hijo.aplicar_limites(ingredientes_data, restricciones_usuario)
    
    # Normalizar para mantener suma = 1
    hijo.normalizar(ingredientes_data, restricciones_usuario)
    
    return hijo

def cruza_uniforme(padre1, padre2, prob_intercambio=0.5, ingredientes_data=None, restricciones_usuario=None):
    """
    Cruza uniforme con probabilidad de intercambio por gen
    
    Args:
        padre1: Primer padre
        padre2: Segundo padre
        prob_intercambio: Probabilidad de intercambio para cada gen
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo hijo generado
    """
    hijo = Individuo(len(padre1.porcentajes))
    
    # Para cada gen, decidir de qué padre heredar
    for i in range(len(padre1.porcentajes)):
        if random.random() < prob_intercambio:
            hijo.porcentajes[i] = padre2.porcentajes[i]
        else:
            hijo.porcentajes[i] = padre1.porcentajes[i]
    
    # Aplicar límites si están disponibles
    if ingredientes_data:
        hijo.aplicar_limites(ingredientes_data, restricciones_usuario)
    
    # Normalizar para mantener suma = 1
    hijo.normalizar(ingredientes_data, restricciones_usuario)
    
    return hijo

def cruza_sbx(padre1, padre2, eta=20, ingredientes_data=None, restricciones_usuario=None):
    """
    Cruza SBX (Simulated Binary Crossover) para exploración controlada
    
    Args:
        padre1: Primer padre
        padre2: Segundo padre
        eta: Parámetro de distribución (mayor valor = menor diversidad)
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo hijo generado
    """
    hijo = Individuo(len(padre1.porcentajes))
    
    for i in range(len(padre1.porcentajes)):
        # Obtener valores de los padres
        x1 = padre1.porcentajes[i]
        x2 = padre2.porcentajes[i]
        
        # Asegurar que x1 <= x2
        if x1 > x2:
            x1, x2 = x2, x1
        
        # Calcular límites
        xl = 0.0  # límite inferior por defecto
        xu = 1.0  # límite superior por defecto
        
        if ingredientes_data and i < len(ingredientes_data):
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            xl = limites["min"]
            xu = limites["max"]
        
        # Aplicar SBX
        if abs(x2 - x1) < 1e-14:
            # Padres idénticos
            hijo.porcentajes[i] = x1
        else:
            # Calcular betas
            if (x1 - xl) > (xu - x2):
                beta_max = (xu - x1) / (x2 - x1)
            else:
                beta_max = (x1 - xl) / (x2 - x1)
            
            # Generar número aleatorio
            u = random.random()
            
            if u <= 0.5:
                beta = (2 * u) ** (1 / (eta + 1))
            else:
                beta = (1 / (2 * (1 - u))) ** (1 / (eta + 1))
            
            # Limitar beta
            if beta > beta_max:
                beta = beta_max
            if beta < -beta_max:
                beta = -beta_max
            
            # Calcular hijo
            child_value = 0.5 * ((1 + beta) * x1 + (1 - beta) * x2)
            
            # Asegurar que esté dentro de límites
            child_value = max(xl, min(xu, child_value))
            hijo.porcentajes[i] = child_value
    
    # Normalizar para mantener suma = 1
    hijo.normalizar(ingredientes_data, restricciones_usuario)
    
    return hijo

def seleccionar_operador_cruza(fase_actual, ingredientes_data=None, restricciones_usuario=None):
    """
    Selecciona el operador de cruza según la fase del algoritmo
    
    Args:
        fase_actual: Fase actual ("inicial", "intermedia", "final")
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Función de cruza apropiada para la fase
    """
    def operador_cruza(padre1, padre2):
        if fase_actual == "inicial":
            # Fase inicial: exploración amplia
            if random.random() < 0.7:
                return cruza_blx_alpha(padre1, padre2, alpha=0.7, 
                                     ingredientes_data=ingredientes_data,
                                     restricciones_usuario=restricciones_usuario)
            else:
                return cruza_uniforme(padre1, padre2, prob_intercambio=0.6,
                                    ingredientes_data=ingredientes_data,
                                    restricciones_usuario=restricciones_usuario)
        
        elif fase_actual == "intermedia":
            # Fase intermedia: balance entre exploración y explotación
            rand = random.random()
            if rand < 0.4:
                return cruza_blx_alpha(padre1, padre2, alpha=0.5,
                                     ingredientes_data=ingredientes_data,
                                     restricciones_usuario=restricciones_usuario)
            elif rand < 0.7:
                return cruza_aritmetica(padre1, padre2,
                                      ingredientes_data=ingredientes_data,
                                      restricciones_usuario=restricciones_usuario)
            else:
                return cruza_sbx(padre1, padre2, eta=15,
                               ingredientes_data=ingredientes_data,
                               restricciones_usuario=restricciones_usuario)
        
        else:  # fase final
            # Fase final: explotación y refinamiento
            if random.random() < 0.8:
                return cruza_aritmetica(padre1, padre2,
                                      ingredientes_data=ingredientes_data,
                                      restricciones_usuario=restricciones_usuario)
            else:
                return cruza_sbx(padre1, padre2, eta=30,
                               ingredientes_data=ingredientes_data,
                               restricciones_usuario=restricciones_usuario)
    
    return operador_cruza

def cruza_adaptativa(padre1, padre2, diversidad_poblacion, ingredientes_data=None, restricciones_usuario=None):
    """
    Cruza que se adapta según la diversidad de la población
    
    Args:
        padre1: Primer padre
        padre2: Segundo padre
        diversidad_poblacion: Medida de diversidad de la población (0-1)
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo hijo generado
    """
    if diversidad_poblacion > 0.7:
        # Alta diversidad: usar explotación
        return cruza_aritmetica(padre1, padre2, ingredientes_data, restricciones_usuario)
    elif diversidad_poblacion > 0.3:
        # Diversidad media: balance
        if random.random() < 0.5:
            return cruza_aritmetica(padre1, padre2, ingredientes_data, restricciones_usuario)
        else:
            return cruza_blx_alpha(padre1, padre2, alpha=0.3, 
                                 ingredientes_data=ingredientes_data, 
                                 restricciones_usuario=restricciones_usuario)
    else:
        # Baja diversidad: promover exploración
        return cruza_blx_alpha(padre1, padre2, alpha=0.8, 
                             ingredientes_data=ingredientes_data, 
                             restricciones_usuario=restricciones_usuario)

def generar_multiple_hijos(padre1, padre2, num_hijos=2, ingredientes_data=None, restricciones_usuario=None):
    """
    Genera múltiples hijos usando diferentes operadores de cruza
    
    Args:
        padre1: Primer padre
        padre2: Segundo padre
        num_hijos: Número de hijos a generar
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Lista de hijos generados
    """
    hijos = []
    operadores = [
        lambda: cruza_aritmetica(padre1, padre2, ingredientes_data, restricciones_usuario),
        lambda: cruza_blx_alpha(padre1, padre2, alpha=0.5, 
                               ingredientes_data=ingredientes_data, 
                               restricciones_usuario=restricciones_usuario),
        lambda: cruza_un_punto(padre1, padre2, ingredientes_data, restricciones_usuario),
        lambda: cruza_uniforme(padre1, padre2, prob_intercambio=0.5, 
                              ingredientes_data=ingredientes_data, 
                              restricciones_usuario=restricciones_usuario)
    ]
    
    for i in range(num_hijos):
        operador = operadores[i % len(operadores)]
        hijo = operador()
        hijos.append(hijo)
    
    return hijos

def validar_hijo(hijo, ingredientes_data=None, restricciones_usuario=None):
    """
    Valida que un hijo cumple con las restricciones básicas
    
    Args:
        hijo: Individuo hijo a validar
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        True si el hijo es válido, False en caso contrario
    """
    # Verificar que la suma sea aproximadamente 1
    if not hijo.validar_suma():
        return False
    
    # Verificar límites de ingredientes
    if ingredientes_data:
        for i, porcentaje in enumerate(hijo.porcentajes):
            if i < len(ingredientes_data):
                limites_originales = ingredientes_data[i]["limitaciones"]
                if restricciones_usuario:
                    limites = restricciones_usuario.obtener_limites(i, limites_originales)
                else:
                    limites = limites_originales
                
                if porcentaje < limites["min"] - 1e-6 or porcentaje > limites["max"] + 1e-6:
                    return False
    
    # Verificar restricciones del usuario
    if restricciones_usuario:
        for i, porcentaje in enumerate(hijo.porcentajes):
            if porcentaje > 1e-6 and not restricciones_usuario.es_ingrediente_valido(i):
                return False
    
    return True

def reparar_hijo(hijo, ingredientes_data=None, restricciones_usuario=None):
    """
    Intenta reparar un hijo que viola restricciones
    
    Args:
        hijo: Individuo hijo a reparar
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Hijo reparado
    """
    # Aplicar límites
    if ingredientes_data:
        hijo.aplicar_limites(ingredientes_data, restricciones_usuario)
    
    # Eliminar ingredientes excluidos
    if restricciones_usuario:
        for i in range(len(hijo.porcentajes)):
            if not restricciones_usuario.es_ingrediente_valido(i):
                hijo.porcentajes[i] = 0
    
    # Renormalizar
    hijo.normalizar(ingredientes_data, restricciones_usuario)
    
    return hijo