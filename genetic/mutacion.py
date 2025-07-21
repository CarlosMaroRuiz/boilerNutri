"""
Operadores de mutación para el algoritmo genético.

Implementa diferentes métodos de mutación que preservan
la restricción de suma = 1 en los porcentajes.
"""

import random
import math
from genetic.individuo import Individuo

def mutar_no_uniforme(individuo, generacion_actual, max_generaciones, intensidad=0.1, 
                     ingredientes_data=None, restricciones_usuario=None):
    """
    Mutación no uniforme para fases iniciales
    
    La intensidad de mutación decrece exponencialmente con el tiempo.
    Ideal para exploración agresiva inicial que se vuelve más conservadora.
    
    Args:
        individuo: Individuo a mutar
        generacion_actual: Generación actual del algoritmo
        max_generaciones: Número máximo de generaciones
        intensidad: Factor de intensidad base
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo mutado
    """
    resultado = individuo.clonar()
    
    # Identificar ingredientes con porcentaje fijo
    indices_fijos = []
    if ingredientes_data:
        for i in range(min(len(resultado.porcentajes), len(ingredientes_data))):
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            if abs(limites["min"] - limites["max"]) < 1e-6:
                indices_fijos.append(i)
    
    # Identificar ingredientes variables
    indices_variables = [i for i in range(len(resultado.porcentajes)) if i not in indices_fijos]
    
    if len(indices_variables) == 0:
        return resultado
    
    # Calcular factor de reducción temporal
    if max_generaciones > 0:
        t = generacion_actual / max_generaciones
        factor_temporal = (1 - t) ** 3  # Función cúbica para reducción más agresiva
    else:
        factor_temporal = 1.0
    
    # Seleccionar ingredientes a mutar (1-3 ingredientes)
    num_ingredientes_a_mutar = min(random.randint(1, 3), len(indices_variables))
    indices_mutacion = random.sample(indices_variables, num_ingredientes_a_mutar)
    
    # Aplicar mutación no uniforme
    for indice in indices_mutacion:
        valor_actual = resultado.porcentajes[indice]
        
        # Obtener límites del ingrediente
        if ingredientes_data and indice < len(ingredientes_data):
            limites_originales = ingredientes_data[indice]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(indice, limites_originales)
            else:
                limites = limites_originales
            
            min_val = limites["min"]
            max_val = limites["max"]
        else:
            min_val = 0.0
            max_val = 1.0
        
        # Calcular rangos de mutación
        rango_superior = max_val - valor_actual
        rango_inferior = valor_actual - min_val
        
        # Generar delta usando distribución no uniforme
        if random.random() < 0.5:
            # Mutación hacia arriba
            if rango_superior > 0:
                delta = rango_superior * (1 - random.random() ** factor_temporal) * intensidad
                nuevo_valor = valor_actual + delta
            else:
                nuevo_valor = valor_actual
        else:
            # Mutación hacia abajo
            if rango_inferior > 0:
                delta = rango_inferior * (1 - random.random() ** factor_temporal) * intensidad
                nuevo_valor = valor_actual - delta
            else:
                nuevo_valor = valor_actual
        
        # Asegurar que está dentro de límites
        nuevo_valor = max(min_val, min(nuevo_valor, max_val))
        resultado.porcentajes[indice] = nuevo_valor
    
    # Normalizar para mantener suma = 1
    resultado.normalizar(ingredientes_data, restricciones_usuario)
    
    return resultado

def mutar_intercambio(individuo, intensidad=0.1, ingredientes_data=None, restricciones_usuario=None):
    """
    Mutación por intercambio para fases finales
    
    Intercambia proporciones entre ingredientes nutricionalmente similares.
    Mantiene automáticamente la suma = 1.
    
    Args:
        individuo: Individuo a mutar
        intensidad: Intensidad del intercambio (0-1)
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo mutado
    """
    resultado = individuo.clonar()
    
    # Identificar ingredientes con porcentaje fijo
    indices_fijos = []
    if ingredientes_data:
        for i in range(min(len(resultado.porcentajes), len(ingredientes_data))):
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            if abs(limites["min"] - limites["max"]) < 1e-6:
                indices_fijos.append(i)
    
    # Identificar ingredientes variables con uso significativo
    indices_variables = []
    for i in range(len(resultado.porcentajes)):
        if i not in indices_fijos and resultado.porcentajes[i] > 0.01:  # Al menos 1%
            indices_variables.append(i)
    
    if len(indices_variables) < 2:
        return resultado  # No hay suficientes ingredientes para intercambiar
    
    # Seleccionar dos ingredientes para intercambiar
    indice1, indice2 = random.sample(indices_variables, 2)
    
    # Calcular cantidad a intercambiar
    valor1 = resultado.porcentajes[indice1]
    valor2 = resultado.porcentajes[indice2]
    
    # Determinar cantidad máxima intercambiable
    if ingredientes_data:
        # Obtener límites de ambos ingredientes
        limites1_orig = ingredientes_data[indice1]["limitaciones"] if indice1 < len(ingredientes_data) else {"min": 0.0, "max": 1.0}
        limites2_orig = ingredientes_data[indice2]["limitaciones"] if indice2 < len(ingredientes_data) else {"min": 0.0, "max": 1.0}
        
        if restricciones_usuario:
            limites1 = restricciones_usuario.obtener_limites(indice1, limites1_orig)
            limites2 = restricciones_usuario.obtener_limites(indice2, limites2_orig)
        else:
            limites1 = limites1_orig
            limites2 = limites2_orig
        
        # Calcular límites para el intercambio
        max_transferencia_1_a_2 = min(valor1 - limites1["min"], limites2["max"] - valor2)
        max_transferencia_2_a_1 = min(valor2 - limites2["min"], limites1["max"] - valor1)
        
        max_intercambio = min(max_transferencia_1_a_2, max_transferencia_2_a_1)
    else:
        max_intercambio = min(valor1, valor2) * 0.5
    
    if max_intercambio > 0:
        # Calcular cantidad a intercambiar basada en intensidad
        cantidad_intercambio = random.uniform(0, max_intercambio * intensidad)
        
        # Decidir dirección del intercambio
        if random.random() < 0.5:
            # Transferir de ingrediente 1 a ingrediente 2
            resultado.porcentajes[indice1] -= cantidad_intercambio
            resultado.porcentajes[indice2] += cantidad_intercambio
        else:
            # Transferir de ingrediente 2 a ingrediente 1
            resultado.porcentajes[indice1] += cantidad_intercambio
            resultado.porcentajes[indice2] -= cantidad_intercambio
    
    return resultado

def mutar_diferencial(individuo, intensidad=0.1, ingredientes_data=None, restricciones_usuario=None):
    """
    Mutación diferencial alternativa
    
    Modifica aleatoriamente algunos ingredientes y ajusta otros para mantener suma = 1.
    
    Args:
        individuo: Individuo a mutar
        intensidad: Factor que controla la magnitud de las mutaciones
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo mutado
    """
    resultado = individuo.clonar()
    
    # Identificar ingredientes con porcentaje fijo
    indices_fijos = []
    if ingredientes_data:
        for i in range(min(len(resultado.porcentajes), len(ingredientes_data))):
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            if abs(limites["min"] - limites["max"]) < 1e-6:
                indices_fijos.append(i)
    
    # Identificar ingredientes variables
    indices_variables = [i for i in range(len(resultado.porcentajes)) if i not in indices_fijos]
    
    if len(indices_variables) == 0:
        return resultado
    
    # Seleccionar número aleatorio de ingredientes a mutar
    num_ingredientes_a_mutar = min(random.randint(1, 3), len(indices_variables))
    indices_mutacion = random.sample(indices_variables, num_ingredientes_a_mutar)
    
    # Aplicar mutación
    deltas = []
    for indice in indices_mutacion:
        valor_actual = resultado.porcentajes[indice]
        
        # Obtener límites del ingrediente
        if ingredientes_data and indice < len(ingredientes_data):
            limites_originales = ingredientes_data[indice]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(indice, limites_originales)
            else:
                limites = limites_originales
            
            min_val = limites["min"]
            max_val = limites["max"]
        else:
            min_val = 0.0
            max_val = 1.0
        
        # Generar delta aleatorio proporcional al valor actual
        delta_max = min(valor_actual - min_val, max_val - valor_actual) * intensidad
        delta = (random.random() - 0.5) * 2 * delta_max
        
        # Aplicar delta
        nuevo_valor = valor_actual + delta
        nuevo_valor = max(min_val, min(nuevo_valor, max_val))
        
        delta_real = nuevo_valor - valor_actual
        resultado.porcentajes[indice] = nuevo_valor
        deltas.append(delta_real)
    
    # Compensar el cambio total distribuyendo entre los demás ingredientes variables
    delta_total = sum(deltas)
    otros_indices = [i for i in indices_variables if i not in indices_mutacion]
    
    if otros_indices and abs(delta_total) > 1e-6:
        compensacion_por_ingrediente = -delta_total / len(otros_indices)
        
        for indice in otros_indices:
            valor_actual = resultado.porcentajes[indice]
            nuevo_valor = valor_actual + compensacion_por_ingrediente
            
            # Aplicar límites
            if ingredientes_data and indice < len(ingredientes_data):
                limites_originales = ingredientes_data[indice]["limitaciones"]
                if restricciones_usuario:
                    limites = restricciones_usuario.obtener_limites(indice, limites_originales)
                else:
                    limites = limites_originales
                
                nuevo_valor = max(limites["min"], min(nuevo_valor, limites["max"]))
            else:
                nuevo_valor = max(0.0, min(nuevo_valor, 1.0))
            
            resultado.porcentajes[indice] = nuevo_valor
    
    # Normalizar para asegurar suma = 1
    resultado.normalizar(ingredientes_data, restricciones_usuario)
    
    return resultado

def mutar_gaussiana(individuo, sigma=0.1, ingredientes_data=None, restricciones_usuario=None):
    """
    Mutación gaussiana para ajustes finos
    
    Args:
        individuo: Individuo a mutar
        sigma: Desviación estándar de la distribución gaussiana
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo mutado
    """
    resultado = individuo.clonar()
    
    # Aplicar mutación gaussiana a cada gen
    for i in range(len(resultado.porcentajes)):
        # Verificar si es ingrediente fijo
        if ingredientes_data and i < len(ingredientes_data):
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            if abs(limites["min"] - limites["max"]) < 1e-6:
                continue  # Saltar ingredientes fijos
            
            min_val = limites["min"]
            max_val = limites["max"]
        else:
            min_val = 0.0
            max_val = 1.0
        
        # Generar perturbación gaussiana
        perturbacion = random.gauss(0, sigma)
        nuevo_valor = resultado.porcentajes[i] + perturbacion
        
        # Aplicar límites
        nuevo_valor = max(min_val, min(nuevo_valor, max_val))
        resultado.porcentajes[i] = nuevo_valor
    
    # Normalizar
    resultado.normalizar(ingredientes_data, restricciones_usuario)
    
    return resultado

def mutar_permutacion(individuo, ingredientes_data=None, restricciones_usuario=None):
    """
    Mutación por permutación entre ingredientes similares
    
    Args:
        individuo: Individuo a mutar
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo mutado
    """
    resultado = individuo.clonar()
    
    # Identificar grupos de ingredientes similares
    grupos_similares = identificar_grupos_similares(ingredientes_data)
    
    if not grupos_similares:
        # Si no hay grupos, aplicar intercambio simple
        return mutar_intercambio(resultado, 0.2, ingredientes_data, restricciones_usuario)
    
    # Seleccionar un grupo aleatorio y permutar dentro del grupo
    grupo = random.choice(grupos_similares)
    
    # Filtrar ingredientes del grupo que están activos y son variables
    ingredientes_activos = []
    for indice in grupo:
        if (indice < len(resultado.porcentajes) and 
            resultado.porcentajes[indice] > 0.01):  # Al menos 1%
            
            # Verificar que no sea ingrediente fijo
            if ingredientes_data and indice < len(ingredientes_data):
                limites_originales = ingredientes_data[indice]["limitaciones"]
                if restricciones_usuario:
                    limites = restricciones_usuario.obtener_limites(indice, limites_originales)
                else:
                    limites = limites_originales
                
                if abs(limites["min"] - limites["max"]) > 1e-6:
                    ingredientes_activos.append(indice)
            else:
                ingredientes_activos.append(indice)
    
    if len(ingredientes_activos) >= 2:
        # Intercambiar valores entre ingredientes del grupo
        indice1, indice2 = random.sample(ingredientes_activos, 2)
        
        # Intercambiar parcialmente
        valor1 = resultado.porcentajes[indice1]
        valor2 = resultado.porcentajes[indice2]
        factor = random.uniform(0.1, 0.5)
        
        transferencia = min(valor1, valor2) * factor
        
        resultado.porcentajes[indice1] = valor1 - transferencia + (valor2 * factor)
        resultado.porcentajes[indice2] = valor2 - transferencia + (valor1 * factor)
        
        # Normalizar
        resultado.normalizar(ingredientes_data, restricciones_usuario)
    
    return resultado

def identificar_grupos_similares(ingredientes_data):
    """
    Identifica grupos de ingredientes nutricionalmente similares
    
    Args:
        ingredientes_data: Lista de datos de ingredientes
        
    Returns:
        Lista de grupos (listas de índices)
    """
    if not ingredientes_data:
        return []
    
    grupos = []
    
    # Grupo de cereales (alta energía, proteína media)
    cereales = []
    # Grupo de proteínas (alta proteína)
    proteinas = []
    # Grupo de minerales
    minerales = []
    
    for i, ingrediente in enumerate(ingredientes_data):
        nombre = ingrediente["nombre"].lower()
        nutrientes = ingrediente.get("nutrientes", {})
        proteina = nutrientes.get("proteina", 0)
        
        if any(cereal in nombre for cereal in ["maíz", "sorgo", "trigo"]):
            cereales.append(i)
        elif proteina > 0.25:  # Más del 25% de proteína
            proteinas.append(i)
        elif any(mineral in nombre for mineral in ["mineral", "premezcla", "vitamina"]):
            minerales.append(i)
    
    if len(cereales) > 1:
        grupos.append(cereales)
    if len(proteinas) > 1:
        grupos.append(proteinas)
    if len(minerales) > 1:
        grupos.append(minerales)
    
    return grupos

def seleccionar_operador_mutacion(fase_actual, diversidad_poblacion=0.5):
    """
    Selecciona el operador de mutación según la fase del algoritmo
    
    Args:
        fase_actual: Fase actual ("inicial", "intermedia", "final")
        diversidad_poblacion: Medida de diversidad de la población
        
    Returns:
        Función de mutación apropiada
    """
    if fase_actual == "inicial":
        # Fase inicial: mutación agresiva para exploración
        def mutacion_inicial(individuo, generacion, max_gen, ingredientes_data=None, restricciones_usuario=None):
            if random.random() < 0.7:
                return mutar_no_uniforme(individuo, generacion, max_gen, 0.3, 
                                       ingredientes_data, restricciones_usuario)
            else:
                return mutar_diferencial(individuo, 0.2, ingredientes_data, restricciones_usuario)
        return mutacion_inicial
    
    elif fase_actual == "intermedia":
        # Fase intermedia: balance entre exploración y explotación
        def mutacion_intermedia(individuo, generacion, max_gen, ingredientes_data=None, restricciones_usuario=None):
            rand = random.random()
            if rand < 0.4:
                return mutar_no_uniforme(individuo, generacion, max_gen, 0.2, 
                                       ingredientes_data, restricciones_usuario)
            elif rand < 0.7:
                return mutar_intercambio(individuo, 0.15, ingredientes_data, restricciones_usuario)
            else:
                return mutar_gaussiana(individuo, 0.1, ingredientes_data, restricciones_usuario)
        return mutacion_intermedia
    
    else:  # fase final
        # Fase final: mutación conservadora para ajuste fino
        def mutacion_final(individuo, generacion, max_gen, ingredientes_data=None, restricciones_usuario=None):
            if diversidad_poblacion < 0.3:  # Baja diversidad
                if random.random() < 0.6:
                    return mutar_diferencial(individuo, 0.1, ingredientes_data, restricciones_usuario)
                else:
                    return mutar_gaussiana(individuo, 0.05, ingredientes_data, restricciones_usuario)
            else:  # Diversidad normal
                if random.random() < 0.8:
                    return mutar_intercambio(individuo, 0.1, ingredientes_data, restricciones_usuario)
                else:
                    return mutar_gaussiana(individuo, 0.03, ingredientes_data, restricciones_usuario)
        return mutacion_final

def mutar_adaptativo(individuo, generacion_actual, max_generaciones, fitness_poblacion,
                    ingredientes_data=None, restricciones_usuario=None):
    """
    Mutación adaptativa que ajusta intensidad según el progreso del algoritmo
    
    Args:
        individuo: Individuo a mutar
        generacion_actual: Generación actual
        max_generaciones: Número máximo de generaciones
        fitness_poblacion: Lista de fitness de la población actual
        ingredientes_data: Lista de datos de ingredientes
        restricciones_usuario: Objeto con restricciones del usuario
        
    Returns:
        Individuo mutado
    """
    # Calcular diversidad de la población
    if len(fitness_poblacion) > 1:
        promedio = sum(fitness_poblacion) / len(fitness_poblacion)
        varianza = sum((f - promedio) ** 2 for f in fitness_poblacion) / len(fitness_poblacion)
        diversidad = math.sqrt(varianza)
    else:
        diversidad = 1.0
    
    # Calcular intensidad adaptativa
    progreso = generacion_actual / max_generaciones if max_generaciones > 0 else 0
    intensidad_base = 0.3 * (1 - progreso) + 0.05 * progreso  # Decrece de 0.3 a 0.05
    
    # Ajustar según diversidad
    if diversidad < 0.1:  # Muy poca diversidad
        intensidad = intensidad_base * 2  # Aumentar intensidad
        return mutar_diferencial(individuo, intensidad, ingredientes_data, restricciones_usuario)
    elif diversidad > 0.5:  # Mucha diversidad
        intensidad = intensidad_base * 0.5  # Reducir intensidad
        return mutar_intercambio(individuo, intensidad, ingredientes_data, restricciones_usuario)
    else:  # Diversidad normal
        return mutar_no_uniforme(individuo, generacion_actual, max_generaciones, 
                               intensidad_base, ingredientes_data, restricciones_usuario)