"""
Utilidades para la interfaz gráfica
"""

import random
from config import ALGORITMO_CONFIG
from conocimiento import INGREDIENTES, RAZAS_POLLOS


def preparar_configuracion_algoritmo(main_window):
    """Prepara la configuración para el algoritmo genético"""
    config = ALGORITMO_CONFIG.copy()
    
    # Actualizar parámetros modificables desde la GUI
    config['tamano_poblacion'] = main_window.poblacion_var.get()
    config['num_generaciones'] = main_window.generaciones_var.get()
    
    # Agregar parámetros del usuario
    config['config_evaluacion'] = {
        'raza': main_window.raza_var.get(),
        'edad_dias': main_window.edad_var.get(),
        'peso_actual': main_window.peso_actual_var.get(),
        'peso_objetivo': main_window.peso_objetivo_var.get(),
        'cantidad_pollos': main_window.cantidad_var.get()
    }
    
    # Datos del problema
    config['ingredientes_data'] = INGREDIENTES
    config['restricciones_usuario'] = None  # Por ahora sin restricciones personalizadas
    
    return config


def generar_resultados_simulados(config):
    """Genera resultados simulados realistas para testing"""
    # Crear 3 formulaciones simuladas
    formulaciones = []
    
    for i in range(3):
        # Generar porcentajes realistas para cada ingrediente
        porcentajes = generar_formulacion_realista()
        
        # Calcular métricas simuladas
        costo_kg = sum(porcentajes[j] * INGREDIENTES[j].get('precio_base', 10) 
                      for j in range(len(porcentajes)))
        
        proteina_total = sum(porcentajes[j] * INGREDIENTES[j].get('nutrientes', {}).get('proteina', 0) 
                           for j in range(len(porcentajes))) * 100
        
        energia_total = sum(porcentajes[j] * INGREDIENTES[j].get('nutrientes', {}).get('energia', 0) 
                          for j in range(len(porcentajes)))
        
        fitness = costo_kg + abs(proteina_total - 20) + abs(energia_total - 3000) / 100
        
        formulacion = {
            'rank': i + 1,
            'porcentajes': porcentajes,
            'fitness': fitness + random.uniform(-2, 2),
            'costo_kg': costo_kg,
            'proteina_total': proteina_total,
            'energia_total': energia_total,
            'eficiencia_estimada': 1.6 + random.uniform(-0.1, 0.1),
            'dias_objetivo': random.randint(35, 45)
        }
        formulaciones.append(formulacion)
    
    # Ordenar por fitness (mejor = menor)
    formulaciones.sort(key=lambda x: x['fitness'])
    
    return {
        'formulaciones': formulaciones,
        'tiempo_ejecucion': random.uniform(8, 15),
        'generaciones_ejecutadas': config['num_generaciones'],
        'convergencia': {
            'generacion_convergencia': config['num_generaciones'] - random.randint(20, 50),
            'fitness_final': formulaciones[0]['fitness']
        }
    }


def generar_formulacion_realista():
    """Genera porcentajes realistas para una formulación de pollos"""
    if len(INGREDIENTES) == 0:
        return []
    
    # Inicializar porcentajes
    porcentajes = [0.0] * len(INGREDIENTES)
    
    # Asignar porcentajes base según tipo de ingrediente
    for i, ingrediente in enumerate(INGREDIENTES):
        nombre = ingrediente.get('nombre', '').lower()
        
        # Maíz: base energética (40-60%)
        if 'maíz' in nombre or 'maiz' in nombre:
            porcentajes[i] = random.uniform(0.40, 0.60)
        
        # Pasta de soya: fuente proteica (15-25%)
        elif 'soya' in nombre or 'soja' in nombre:
            porcentajes[i] = random.uniform(0.15, 0.25)
        
        # DDG: subproducto (5-15%)
        elif 'ddg' in nombre:
            porcentajes[i] = random.uniform(0.05, 0.15)
        
        # Otros ingredientes: pequeñas cantidades
        else:
            if random.random() > 0.3:  # 70% probabilidad de usar
                porcentajes[i] = random.uniform(0.001, 0.08)
    
    # Normalizar para que sume 1.0
    suma_total = sum(porcentajes)
    if suma_total > 0:
        porcentajes = [p / suma_total for p in porcentajes]
    
    # Eliminar ingredientes con menos del 0.5%
    porcentajes = [p if p >= 0.005 else 0.0 for p in porcentajes]
    
    # Renormalizar
    suma_total = sum(porcentajes)
    if suma_total > 0:
        porcentajes = [p / suma_total for p in porcentajes]
    
    return porcentajes


def buscar_raza_por_nombre(nombre):
    """Busca una raza por nombre en la lista"""
    for raza in RAZAS_POLLOS:
        if raza["nombre"] == nombre:
            return raza
    return None


def buscar_ingrediente_por_nombre(nombre):
    """Busca un ingrediente por nombre en la lista"""
    for ingrediente in INGREDIENTES:
        if ingrediente["nombre"] == nombre:
            return ingrediente
    return None