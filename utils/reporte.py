"""
Generación de reportes detallados con los resultados.

Crea reportes completos con tablas de formulaciones,
análisis nutricional y proyecciones económicas.
"""

import json
from datetime import datetime
from genetic.fitness.nutricion import evaluar_balance_nutricional, calcular_score_nutricional
from genetic.fitness.costo import calcular_costo_por_ingrediente, estimar_ahorro_vs_formula_tradicional
from genetic.fitness.eficiencia import proyectar_rendimiento_periodo
from genetic.fitness.disponibilidad import evaluar_riesgo_suministro, generar_recomendaciones_suministro
from conocimiento.proveedores import generar_resumen_compras

def generar_reporte_completo(resultados, ingredientes_data, config_evaluacion, restricciones_usuario=None):
    """
    Genera el reporte completo del sistema
    
    Args:
        resultados: Resultado del algoritmo genético
        ingredientes_data: Lista de datos de ingredientes
        config_evaluacion: Configuración de evaluación
        restricciones_usuario: Restricciones del usuario
        
    Returns:
        Diccionario con reporte completo
    """
    print("📊 Generando reporte completo...")
    
    reporte = {
        "metadatos": generar_metadatos(config_evaluacion, restricciones_usuario),
        "resumen_ejecutivo": generar_resumen_ejecutivo(resultados),
        "mejores_soluciones": [],
        "analisis_algoritmo": analizar_rendimiento_algoritmo(resultados),
        "recomendaciones_generales": generar_recomendaciones_generales(resultados, ingredientes_data)
    }
    
    # Generar análisis detallado para cada una de las 3 mejores soluciones
    mejores_individuos = resultados.get("mejores_individuos", [])[:3]
    
    for i, individuo in enumerate(mejores_individuos):
        print(f"   • Analizando solución {i+1}...")
        
        analisis_solucion = {
            "ranking": i + 1,
            "formula": generar_tabla_formula(individuo, ingredientes_data),
            "analisis_nutricional": generar_analisis_nutricional(individuo, config_evaluacion, ingredientes_data),
            "analisis_economico": generar_analisis_economico(individuo, config_evaluacion, ingredientes_data),
            "plan_implementacion": generar_plan_implementacion(individuo, config_evaluacion, ingredientes_data),
            "analisis_riesgo": generar_analisis_riesgo(individuo, ingredientes_data),
            "ventajas_desventajas": generar_ventajas_desventajas(individuo, mejores_individuos, i, ingredientes_data)
        }
        
        reporte["mejores_soluciones"].append(analisis_solucion)
    
    print("✅ Reporte completo generado")
    return reporte

def generar_metadatos(config_evaluacion, restricciones_usuario):
    """
    Genera metadatos del reporte
    """
    return {
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "parametros_produccion": {
            "raza": config_evaluacion.get("raza", "No especificada"),
            "edad_dias": config_evaluacion.get("edad_dias", 0),
            "peso_actual": config_evaluacion.get("peso_actual", 0),
            "peso_objetivo": config_evaluacion.get("peso_objetivo", 0),
            "cantidad_pollos": config_evaluacion.get("cantidad_pollos", 0)
        },
        "restricciones_aplicadas": generar_resumen_restricciones(restricciones_usuario),
        "version_sistema": "boilerNutri v1.0.0"
    }

def generar_resumen_restricciones(restricciones_usuario):
    """
    Genera resumen de restricciones aplicadas
    """
    if not restricciones_usuario:
        return "Ninguna restricción especial aplicada"
    
    resumen = []
    
    if restricciones_usuario.ingredientes_excluidos:
        resumen.append(f"Ingredientes excluidos: {len(restricciones_usuario.ingredientes_excluidos)}")
    
    if restricciones_usuario.limites_personalizados:
        resumen.append(f"Límites personalizados: {len(restricciones_usuario.limites_personalizados)}")
    
    if restricciones_usuario.presupuesto_maximo:
        resumen.append(f"Presupuesto máximo: ${restricciones_usuario.presupuesto_maximo:.2f}/kg")
    
    return "; ".join(resumen) if resumen else "Sin restricciones especiales"

def generar_resumen_ejecutivo(resultados):
    """
    Genera resumen ejecutivo con conclusiones principales
    """
    mejor_individuo = resultados.get("mejor_individuo")
    mejores_individuos = resultados.get("mejores_individuos", [])
    
    if not mejor_individuo:
        return {"error": "No se encontraron soluciones válidas"}
    
    # Calcular métricas clave
    tiempo_ejecucion = resultados.get("tiempo_ejecucion", 0)
    generaciones = resultados.get("generaciones_ejecutadas", 0)
    convergencia = resultados.get("convergencia_detectada", False)
    
    # Análisis de mejora
    historico_fitness = resultados.get("historico_fitness", [])
    mejora_fitness = 0
    if len(historico_fitness) >= 2:
        mejora_fitness = historico_fitness[0] - historico_fitness[-1]
    
    return {
        "conclusiones_principales": [
            f"Se encontraron {len(mejores_individuos)} soluciones óptimas diferentes",
            f"Mejor costo obtenido: ${mejor_individuo.costo_total:.2f} por kilogramo",
            f"Optimización completada en {tiempo_ejecucion:.1f} segundos",
            f"Algoritmo {'convergió' if convergencia else 'ejecutó'} en {generaciones} generaciones"
        ],
        "metricas_clave": {
            "mejor_fitness": mejor_individuo.fitness,
            "mejor_costo": mejor_individuo.costo_total,
            "mejora_algoritmo": mejora_fitness,
            "numero_soluciones": len(mejores_individuos),
            "tiempo_ejecucion": tiempo_ejecucion
        },
        "recomendacion_principal": generar_recomendacion_principal(mejores_individuos)
    }

def generar_recomendacion_principal(mejores_individuos):
    """
    Genera la recomendación principal basada en los mejores individuos
    """
    if not mejores_individuos:
        return "No se pueden generar recomendaciones sin soluciones válidas"
    
    mejor = mejores_individuos[0]
    
    if len(mejores_individuos) == 1:
        return f"Se recomienda implementar la solución única encontrada con costo de ${mejor.costo_total:.2f}/kg"
    
    # Comparar soluciones
    diferencia_costo = (mejores_individuos[1].costo_total - mejor.costo_total) / mejor.costo_total * 100
    
    if diferencia_costo < 5:  # Menos del 5% de diferencia
        return f"Las primeras 2 soluciones son muy similares en costo. Se recomienda evaluar otros factores como disponibilidad de ingredientes."
    else:
        return f"Se recomienda la primera solución por su ventaja de costo ({diferencia_costo:.1f}% más económica que la siguiente mejor)."

def generar_tabla_formula(individuo, ingredientes_data):
    """
    Genera tabla con la fórmula optimizada
    """
    tabla = []
    costo_total = 0
    
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.001 and i < len(ingredientes_data):  # Más de 0.1%
            ingrediente = ingredientes_data[i]
            proveedor_info = individuo.proveedor_recomendado.get(i, {})
            
            if proveedor_info:
                # Obtener nombre del proveedor
                from conocimiento.proveedores import obtener_proveedor
                proveedor_data = obtener_proveedor(proveedor_info["proveedor"])
                proveedor_nombre = proveedor_data["nombre"] if proveedor_data else proveedor_info["proveedor"]
                
                costo_por_kg = porcentaje * proveedor_info["precio"]
                costo_por_tonelada = costo_por_kg * 1000
                
                tabla.append({
                    "ingrediente": ingrediente["nombre"],
                    "porcentaje": round(porcentaje * 100, 2),
                    "kg_por_tonelada": round(porcentaje * 1000, 1),
                    "proveedor": proveedor_nombre,
                    "precio_unitario": proveedor_info["precio"],
                    "costo_por_kg_formula": round(costo_por_kg, 4),
                    "costo_por_tonelada": round(costo_por_tonelada, 2)
                })
                
                costo_total += costo_por_kg
    
    # Ordenar por porcentaje descendente
    tabla.sort(key=lambda x: x["porcentaje"], reverse=True)
    
    # Añadir fila de totales
    tabla.append({
        "ingrediente": "TOTAL",
        "porcentaje": 100.0,
        "kg_por_tonelada": 1000.0,
        "proveedor": "-",
        "precio_unitario": "-",
        "costo_por_kg_formula": round(costo_total, 4),
        "costo_por_tonelada": round(costo_total * 1000, 2)
    })
    
    return tabla

def generar_analisis_nutricional(individuo, config_evaluacion, ingredientes_data):
    """
    Genera análisis nutricional comparativo
    """
    from conocimiento.requerimientos import obtener_etapa, obtener_requerimientos
    
    # Determinar etapa
    edad_dias = config_evaluacion.get("edad_dias", 35)
    etapa = obtener_etapa(edad_dias)
    requerimientos = obtener_requerimientos(edad_dias)
    
    # Evaluar balance nutricional
    balance = evaluar_balance_nutricional(individuo, etapa, ingredientes_data)
    score = calcular_score_nutricional(individuo, etapa, ingredientes_data)
    
    analisis = {
        "etapa_evaluacion": etapa,
        "score_nutricional": round(score, 1),
        "resumen_cumplimiento": generar_resumen_cumplimiento(balance),
        "detalle_nutrientes": []
    }
    
    for nutriente, info in balance.items():
        detalle = {
            "nutriente": nutriente.replace("_", " ").title(),
            "valor_obtenido": formatear_valor_nutriente(info["valor_obtenido"], nutriente),
            "valor_referencia": formatear_valor_nutriente(info["valor_referencia"], nutriente),
            "diferencia_porcentual": round(info["diferencia_pct"], 1),
            "estado": info["estado"],
            "evaluacion": generar_evaluacion_nutriente(info, nutriente)
        }
        analisis["detalle_nutrientes"].append(detalle)
    
    return analisis

def formatear_valor_nutriente(valor, nutriente):
    """
    Formatea valores de nutrientes según su tipo
    """
    if nutriente == "energia":
        return f"{valor:.0f} kcal/kg"
    elif nutriente in ["proteina", "fibra"]:
        return f"{valor*100:.1f}%"
    else:  # aminoácidos y minerales
        return f"{valor*100:.2f}%"

def generar_evaluacion_nutriente(info, nutriente):
    """
    Genera evaluación textual de un nutriente
    """
    estado = info["estado"]
    diferencia = info["diferencia_pct"]
    
    if estado == "Óptimo":
        return "✅ Cumple perfectamente con los requerimientos"
    elif estado == "Aceptable":
        if diferencia > 0:
            return f"⚠️ Ligero exceso ({abs(diferencia):.1f}%), pero dentro de rango aceptable"
        else:
            return f"⚠️ Ligero déficit ({abs(diferencia):.1f}%), pero dentro de rango aceptable"
    elif estado == "Deficiente":
        return f"❌ Déficit significativo ({abs(diferencia):.1f}%) - Requiere atención"
    elif estado == "Excesivo":
        return f"❌ Exceso problemático ({abs(diferencia):.1f}%) - Puede causar problemas"
    else:
        return f"⚠️ {estado} - Revisar formulación"

def generar_resumen_cumplimiento(balance):
    """
    Genera resumen del cumplimiento nutricional
    """
    total_nutrientes = len(balance)
    optimos = sum(1 for info in balance.values() if info["estado"] == "Óptimo")
    aceptables = sum(1 for info in balance.values() if info["estado"] == "Aceptable")
    problematicos = total_nutrientes - optimos - aceptables
    
    return {
        "total_nutrientes": total_nutrientes,
        "optimos": optimos,
        "aceptables": aceptables,
        "problematicos": problematicos,
        "porcentaje_cumplimiento": round((optimos + aceptables) / total_nutrientes * 100, 1),
        "evaluacion_general": "Excelente" if problematicos == 0 and optimos >= aceptables 
                            else "Buena" if problematicos == 0 
                            else "Regular" if problematicos <= 2 
                            else "Deficiente"
    }

def generar_analisis_economico(individuo, config_evaluacion, ingredientes_data):
    """
    Genera análisis económico y proyecciones
    """
    # Análisis de costos por ingrediente
    costos_ingrediente = calcular_costo_por_ingrediente(individuo, ingredientes_data)
    
    # Estimación de ahorro
    ahorro_info = estimar_ahorro_vs_formula_tradicional(individuo)
    
    # Proyección económica total
    cantidad_pollos = config_evaluacion.get("cantidad_pollos", 1000)
    peso_actual = config_evaluacion.get("peso_actual", 1.5)
    peso_objetivo = config_evaluacion.get("peso_objetivo", 2.5)
    raza = config_evaluacion.get("raza", "Ross")
    edad_dias = config_evaluacion.get("edad_dias", 35)
    
    # Estimar consumo total
    from conocimiento.razas import estimar_dias_hasta_peso
    dias_hasta_objetivo = estimar_dias_hasta_peso(peso_actual, peso_objetivo, raza, edad_dias)
    
    if dias_hasta_objetivo:
        consumo_total_estimado = estimar_consumo_total(cantidad_pollos, edad_dias, dias_hasta_objetivo)
        costo_total_alimentacion = consumo_total_estimado * individuo.costo_total
        ahorro_total = consumo_total_estimado * ahorro_info["ahorro_absoluto"]
    else:
        consumo_total_estimado = 0
        costo_total_alimentacion = 0
        ahorro_total = 0
    
    return {
        "costo_por_kg": round(individuo.costo_total, 4),
        "ahorro_vs_tradicional": {
            "porcentaje": round(ahorro_info["ahorro_porcentual"], 1),
            "absoluto_por_kg": round(ahorro_info["ahorro_absoluto"], 4)
        },
        "proyeccion_total": {
            "consumo_estimado_kg": round(consumo_total_estimado, 0),
            "costo_total_alimentacion": round(costo_total_alimentacion, 2),
            "ahorro_total_estimado": round(ahorro_total, 2),
            "costo_por_pollo": round(costo_total_alimentacion / cantidad_pollos, 2) if cantidad_pollos > 0 else 0
        },
        "distribucion_costos": costos_ingrediente[:5],  # Top 5 ingredientes más costosos
        "rentabilidad": generar_analisis_rentabilidad(individuo, config_evaluacion)
    }

def estimar_consumo_total(cantidad_pollos, edad_inicial, dias_hasta_objetivo):
    """
    Estima el consumo total de alimento
    """
    consumo_total = 0
    
    for dia_offset in range(dias_hasta_objetivo + 1):
        edad_dia = edad_inicial + dia_offset
        
        # Consumo diario por ave según edad
        if edad_dia <= 7:
            consumo_diario_g = 20
        elif edad_dia <= 14:
            consumo_diario_g = 45
        elif edad_dia <= 21:
            consumo_diario_g = 80
        elif edad_dia <= 28:
            consumo_diario_g = 115
        elif edad_dia <= 35:
            consumo_diario_g = 150
        else:
            consumo_diario_g = 180
        
        consumo_total += (consumo_diario_g / 1000) * cantidad_pollos
    
    return consumo_total

def generar_analisis_rentabilidad(individuo, config_evaluacion):
    """
    Genera análisis de rentabilidad
    """
    peso_objetivo = config_evaluacion.get("peso_objetivo", 2.5)
    precio_venta_kg = 25.0  # Precio estimado por kg de pollo vivo (ajustar según mercado local)
    
    # Ingresos estimados por pollo
    ingreso_por_pollo = peso_objetivo * precio_venta_kg
    
    # Costo de alimentación por pollo (estimado)
    costo_alimentacion_por_pollo = individuo.costo_total * 4.5  # Asumiendo 4.5 kg de alimento por pollo
    
    # Margen bruto (solo considerando alimentación)
    margen_bruto = ingreso_por_pollo - costo_alimentacion_por_pollo
    margen_porcentual = (margen_bruto / ingreso_por_pollo) * 100
    
    return {
        "precio_venta_estimado": precio_venta_kg,
        "ingreso_por_pollo": round(ingreso_por_pollo, 2),
        "costo_alimentacion_por_pollo": round(costo_alimentacion_por_pollo, 2),
        "margen_bruto": round(margen_bruto, 2),
        "margen_porcentual": round(margen_porcentual, 1),
        "evaluacion": "Excelente" if margen_porcentual > 60 
                     else "Buena" if margen_porcentual > 50 
                     else "Regular" if margen_porcentual > 40 
                     else "Preocupante"
    }

def generar_plan_implementacion(individuo, config_evaluacion, ingredientes_data):
    """
    Genera plan detallado de implementación
    """
    cantidad_pollos = config_evaluacion.get("cantidad_pollos", 1000)
    edad_dias = config_evaluacion.get("edad_dias", 35)
    peso_actual = config_evaluacion.get("peso_actual", 1.5)
    peso_objetivo = config_evaluacion.get("peso_objetivo", 2.5)
    raza = config_evaluacion.get("raza", "Ross")
    
    # Calcular necesidades de producción
    from conocimiento.razas import estimar_dias_hasta_peso
    dias_hasta_objetivo = estimar_dias_hasta_peso(peso_actual, peso_objetivo, raza, edad_dias)
    
    if not dias_hasta_objetivo:
        dias_hasta_objetivo = 21  # Valor por defecto
    
    consumo_total_kg = estimar_consumo_total(cantidad_pollos, edad_dias, dias_hasta_objetivo)
    
    # Calcular cantidad de cada ingrediente
    ingredientes_a_comprar = []
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.001 and i < len(ingredientes_data):
            cantidad_kg = porcentaje * consumo_total_kg
            ingrediente = ingredientes_data[i]
            proveedor_info = individuo.proveedor_recomendado.get(i, {})
            
            if proveedor_info:
                from conocimiento.proveedores import obtener_proveedor
                proveedor_data = obtener_proveedor(proveedor_info["proveedor"])
                proveedor_nombre = proveedor_data["nombre"] if proveedor_data else "Proveedor desconocido"
                
                ingredientes_a_comprar.append({
                    "ingrediente": ingrediente["nombre"],
                    "cantidad_kg": round(cantidad_kg, 1),
                    "proveedor": proveedor_nombre,
                    "precio_unitario": proveedor_info["precio"],
                    "costo_total": round(cantidad_kg * proveedor_info["precio"], 2)
                })
    
    # Resumen por proveedor
    resumen_proveedores = generar_resumen_compras(individuo.proveedor_recomendado, consumo_total_kg)
    
    # Cronograma de alimentación
    cronograma = generar_cronograma_alimentacion(cantidad_pollos, edad_dias, dias_hasta_objetivo)
    
    return {
        "resumen_produccion": {
            "periodo_alimentacion": dias_hasta_objetivo,
            "consumo_total_estimado": round(consumo_total_kg, 0),
            "costo_total_alimento": round(sum(ing["costo_total"] for ing in ingredientes_a_comprar), 2),
            "capacidad_diaria_requerida": round(consumo_total_kg / max(1, dias_hasta_objetivo), 1)
        },
        "ingredientes_a_comprar": ingredientes_a_comprar,
        "resumen_por_proveedor": resumen_proveedores,
        "cronograma_alimentacion": cronograma[:10],  # Primeros 10 días como ejemplo
        "recomendaciones_implementacion": generar_recomendaciones_implementacion(individuo, config_evaluacion)
    }

def generar_cronograma_alimentacion(cantidad_pollos, edad_inicial, dias_periodo):
    """
    Genera cronograma diario de alimentación
    """
    cronograma = []
    
    for dia in range(min(dias_periodo, 30)):  # Máximo 30 días para el cronograma
        edad_dia = edad_inicial + dia
        
        # Consumo diario por ave
        if edad_dia <= 7:
            consumo_por_ave = 20
        elif edad_dia <= 14:
            consumo_por_ave = 45
        elif edad_dia <= 21:
            consumo_por_ave = 80
        elif edad_dia <= 28:
            consumo_por_ave = 115
        elif edad_dia <= 35:
            consumo_por_ave = 150
        else:
            consumo_por_ave = 180
        
        consumo_total_dia = (consumo_por_ave * cantidad_pollos) / 1000  # en kg
        
        cronograma.append({
            "dia": dia + 1,
            "edad_pollos": edad_dia,
            "consumo_por_ave_g": consumo_por_ave,
            "consumo_total_kg": round(consumo_total_dia, 1)
        })
    
    return cronograma

def generar_recomendaciones_implementacion(individuo, config_evaluacion):
    """
    Genera recomendaciones específicas para implementación
    """
    recomendaciones = []
    
    # Recomendaciones basadas en la composición
    ingredientes_principales = []
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.1:  # Más del 10%
            ingredientes_principales.append((i, porcentaje))
    
    if len(ingredientes_principales) <= 3:
        recomendaciones.append("Formulación simple con pocos ingredientes - fácil de implementar")
    else:
        recomendaciones.append("Formulación compleja - asegurar disponibilidad de todos los ingredientes")
    
    # Recomendaciones de almacenamiento
    recomendaciones.extend([
        "Almacenar ingredientes en lugar seco y ventilado",
        "Verificar fechas de vencimiento de premezclas vitamínicas",
        "Implementar sistema FIFO (primero en entrar, primero en salir)",
        "Realizar mezcla homogénea antes de servir"
    ])
    
    # Recomendaciones de monitoreo
    recomendaciones.extend([
        "Monitorear peso de los pollos semanalmente",
        "Registrar consumo diario de alimento",
        "Observar comportamiento alimenticio de las aves",
        "Ajustar cantidades según condiciones ambientales"
    ])
    
    return recomendaciones

def generar_analisis_riesgo(individuo, ingredientes_data):
    """
    Genera análisis de riesgo de la formulación
    """
    riesgo_suministro = evaluar_riesgo_suministro(individuo, ingredientes_data)
    recomendaciones_suministro = generar_recomendaciones_suministro(individuo, ingredientes_data)
    
    return {
        "riesgo_suministro": riesgo_suministro,
        "recomendaciones": recomendaciones_suministro,
        "factores_riesgo": identificar_factores_riesgo(individuo, ingredientes_data),
        "plan_contingencia": generar_plan_contingencia(individuo, ingredientes_data)
    }

def identificar_factores_riesgo(individuo, ingredientes_data):
    """
    Identifica factores de riesgo específicos
    """
    factores = []
    
    # Verificar dependencia de pocos proveedores
    proveedores_utilizados = set()
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.05 and i < len(ingredientes_data):  # Más del 5%
            proveedor_info = individuo.proveedor_recomendado.get(i, {})
            if proveedor_info:
                proveedores_utilizados.add(proveedor_info["proveedor"])
    
    if len(proveedores_utilizados) <= 2:
        factores.append("Alta dependencia de pocos proveedores")
    
    # Verificar ingredientes con baja disponibilidad
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.1 and i < len(ingredientes_data):  # Más del 10%
            ingrediente = ingredientes_data[i]
            disponibilidad = ingrediente.get("disponibilidadLocal", 0.5)
            if disponibilidad < 0.7:
                factores.append(f"Dependencia de {ingrediente['nombre']} con disponibilidad limitada")
    
    return factores

def generar_plan_contingencia(individuo, ingredientes_data):
    """
    Genera plan de contingencia para problemas de suministro
    """
    plan = []
    
    # Identificar sustitutos para ingredientes principales
    for i, porcentaje in enumerate(individuo.porcentajes):
        if porcentaje > 0.15 and i < len(ingredientes_data):  # Más del 15%
            ingrediente = ingredientes_data[i]
            sustitutos = identificar_sustitutos(ingrediente, ingredientes_data)
            if sustitutos:
                plan.append(f"Para {ingrediente['nombre']}: usar {sustitutos[0]} como sustituto")
    
    # Recomendaciones generales
    plan.extend([
        "Mantener inventario de seguridad de 7-10 días",
        "Establecer acuerdos con proveedores alternativos",
        "Tener formulación de emergencia preparada"
    ])
    
    return plan

def identificar_sustitutos(ingrediente_principal, ingredientes_data):
    """
    Identifica posibles sustitutos para un ingrediente
    """
    nombre_principal = ingrediente_principal["nombre"].lower()
    sustitutos = []
    
    # Reglas de sustitución básicas
    if "maíz" in nombre_principal:
        for ing in ingredientes_data:
            if "sorgo" in ing["nombre"].lower():
                sustitutos.append(ing["nombre"])
    elif "sorgo" in nombre_principal:
        for ing in ingredientes_data:
            if "maíz" in ing["nombre"].lower():
                sustitutos.append(ing["nombre"])
    
    return sustitutos[:2]  # Máximo 2 sustitutos

def generar_ventajas_desventajas(individuo, todos_individuos, posicion, ingredientes_data):
    """
    Genera análisis de ventajas y desventajas comparando con otras soluciones
    """
    ventajas = []
    desventajas = []
    
    if posicion == 0:  # Mejor solución
        ventajas.extend([
            "Menor costo por kilogramo",
            "Mejor fitness global",
            "Solución óptima encontrada"
        ])
        
        if len(todos_individuos) > 1:
            diferencia_costo = (todos_individuos[1].costo_total - individuo.costo_total) / individuo.costo_total * 100
            ventajas.append(f"Ahorro del {diferencia_costo:.1f}% vs segunda mejor opción")
    
    else:  # Otras soluciones
        mejor = todos_individuos[0]
        diferencia_costo = (individuo.costo_total - mejor.costo_total) / mejor.costo_total * 100
        desventajas.append(f"Costo {diferencia_costo:.1f}% mayor que la mejor opción")
        
        # Buscar ventajas específicas
        if hasattr(individuo, 'disponibilidad_score') and hasattr(mejor, 'disponibilidad_score'):
            if individuo.disponibilidad_score < mejor.disponibilidad_score:
                ventajas.append("Mejor disponibilidad de ingredientes")
        
        # Analizar composición
        if any(individuo.porcentajes[i] > mejor.porcentajes[i] * 1.2 for i in range(len(individuo.porcentajes))):
            ventajas.append("Composición más diversificada")
    
    # Análisis nutricional comparativo
    from genetic.fitness.nutricion import calcular_score_nutricional
    from conocimiento.requerimientos import obtener_etapa
    
    etapa = obtener_etapa(35)  # Usar etapa por defecto
    score = calcular_score_nutricional(individuo, etapa, ingredientes_data)
    
    if score >= 85:
        ventajas.append("Excelente balance nutricional")
    elif score >= 70:
        ventajas.append("Buen balance nutricional")
    else:
        desventajas.append("Balance nutricional mejorable")
    
    return {
        "ventajas": ventajas,
        "desventajas": desventajas,
        "recomendacion_uso": generar_recomendacion_uso(individuo, posicion, ventajas, desventajas)
    }

def generar_recomendacion_uso(individuo, posicion, ventajas, desventajas):
    """
    Genera recomendación de cuándo usar esta solución
    """
    if posicion == 0:
        return "Recomendada como primera opción por su óptimo balance costo-beneficio"
    
    elif len(ventajas) > len(desventajas):
        return "Recomendada cuando las ventajas específicas sean prioritarias"
    
    elif "disponibilidad" in str(ventajas).lower():
        return "Recomendada cuando hay problemas de suministro con ingredientes de la primera opción"
    
    else:
        return "Usar como opción de respaldo o cuando la primera opción no esté disponible"

def generar_recomendaciones_generales(resultados, ingredientes_data):
    """
    Genera recomendaciones generales del sistema
    """
    mejores_individuos = resultados.get("mejores_individuos", [])
    
    if not mejores_individuos:
        return ["No se pudieron generar recomendaciones sin soluciones válidas"]
    
    recomendaciones = []
    
    # Análisis de consistencia entre soluciones
    if len(mejores_individuos) >= 2:
        ingredientes_comunes = analizar_ingredientes_comunes(mejores_individuos, ingredientes_data)
        if ingredientes_comunes:
            recomendaciones.append(f"Ingredientes clave en todas las soluciones: {', '.join(ingredientes_comunes)}")
    
    # Recomendaciones de mejora continua
    recomendaciones.extend([
        "Revisar precios de ingredientes mensualmente para mantener optimización",
        "Monitorear rendimiento real vs proyectado para ajustar modelo",
        "Considerar ingredientes estacionales para futuras optimizaciones",
        "Evaluar nuevos proveedores para ampliar opciones"
    ])
    
    # Recomendaciones según convergencia
    if resultados.get("convergencia_detectada", False):
        recomendaciones.append("Algoritmo convergió exitosamente - soluciones son estables")
    else:
        recomendaciones.append("Considerar ejecutar más generaciones para explorar mejores soluciones")
    
    return recomendaciones

def analizar_ingredientes_comunes(individuos, ingredientes_data):
    """
    Analiza ingredientes comunes entre todas las soluciones
    """
    if not individuos:
        return []
    
    ingredientes_comunes = []
    
    for i in range(len(ingredientes_data)):
        presente_en_todos = True
        for individuo in individuos:
            if i >= len(individuo.porcentajes) or individuo.porcentajes[i] < 0.05:  # Menos del 5%
                presente_en_todos = False
                break
        
        if presente_en_todos:
            ingredientes_comunes.append(ingredientes_data[i]["nombre"])
    
    return ingredientes_comunes

def analizar_rendimiento_algoritmo(resultados):
    """
    Analiza el rendimiento del algoritmo genético
    """
    historico_fitness = resultados.get("historico_fitness", [])
    tiempo_ejecucion = resultados.get("tiempo_ejecucion", 0)
    generaciones = resultados.get("generaciones_ejecutadas", 0)
    
    analisis = {
        "eficiencia_temporal": {
            "tiempo_total": round(tiempo_ejecucion, 2),
            "tiempo_por_generacion": round(tiempo_ejecucion / max(1, generaciones), 3),
            "evaluaciones_por_segundo": round((generaciones * 100) / max(1, tiempo_ejecucion), 0)
        },
        "calidad_convergencia": "No determinada"
    }
    
    if len(historico_fitness) >= 10:
        mejora_inicial = historico_fitness[0] - historico_fitness[9]  # Primeras 10 generaciones
        mejora_total = historico_fitness[0] - historico_fitness[-1]
        
        analisis["mejora_algoritmo"] = {
            "mejora_inicial": round(mejora_inicial, 4),
            "mejora_total": round(mejora_total, 4),
            "porcentaje_mejora": round((mejora_total / historico_fitness[0]) * 100, 1) if historico_fitness[0] > 0 else 0
        }
        
        # Evaluar calidad de convergencia
        if mejora_total > mejora_inicial * 2:
            analisis["calidad_convergencia"] = "Excelente - mejora sostenida"
        elif mejora_total > mejora_inicial:
            analisis["calidad_convergencia"] = "Buena - mejora gradual"
        else:
            analisis["calidad_convergencia"] = "Regular - mejora principalmente inicial"
    
    return analisis

def exportar_reporte_texto(reporte, nombre_archivo="reporte_optimizacion.txt"):
    """
    Exporta el reporte a archivo de texto legible
    """
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("REPORTE DE OPTIMIZACIÓN DE FORMULACIÓN DE ALIMENTOS\n")
        f.write("Sistema boilerNutri v1.0.0\n")
        f.write("=" * 80 + "\n\n")
        
        # Metadatos
        metadatos = reporte["metadatos"]
        f.write(f"Fecha de generación: {metadatos['fecha_generacion']}\n")
        f.write(f"Parámetros de producción:\n")
        for clave, valor in metadatos["parametros_produccion"].items():
            f.write(f"  - {clave.replace('_', ' ').title()}: {valor}\n")
        f.write(f"Restricciones: {metadatos['restricciones_aplicadas']}\n\n")
        
        # Resumen ejecutivo
        resumen = reporte["resumen_ejecutivo"]
        f.write("RESUMEN EJECUTIVO\n")
        f.write("-" * 40 + "\n")
        for conclusion in resumen["conclusiones_principales"]:
            f.write(f"• {conclusion}\n")
        f.write(f"\nRecomendación principal: {resumen['recomendacion_principal']}\n\n")
        
        # Mejores soluciones
        for i, solucion in enumerate(reporte["mejores_soluciones"]):
            f.write(f"SOLUCIÓN #{i+1}\n")
            f.write("-" * 40 + "\n")
            
            # Fórmula
            f.write("Fórmula:\n")
            for ingrediente in solucion["formula"][:-1]:  # Excluir total
                f.write(f"  {ingrediente['ingrediente']}: {ingrediente['porcentaje']:.1f}% "
                       f"({ingrediente['proveedor']})\n")
            
            total = solucion["formula"][-1]
            f.write(f"\nCosto total: ${total['costo_por_kg_formula']:.4f}/kg\n")
            
            # Análisis nutricional
            nutricional = solucion["analisis_nutricional"]
            f.write(f"Score nutricional: {nutricional['score_nutricional']}/100\n")
            f.write(f"Cumplimiento: {nutricional['resumen_cumplimiento']['porcentaje_cumplimiento']:.1f}%\n")
            
            # Ventajas y desventajas
            ventajas = solucion["ventajas_desventajas"]
            f.write("Ventajas:\n")
            for ventaja in ventajas["ventajas"]:
                f.write(f"  + {ventaja}\n")
            
            if ventajas["desventajas"]:
                f.write("Desventajas:\n")
                for desventaja in ventajas["desventajas"]:
                    f.write(f"  - {desventaja}\n")
            
            f.write(f"Recomendación: {ventajas['recomendacion_uso']}\n\n")
    
    print(f"✅ Reporte exportado a: {nombre_archivo}")

def exportar_reporte_json(reporte, nombre_archivo="reporte_optimizacion.json"):
    """
    Exporta el reporte completo a JSON
    """
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"✅ Reporte JSON exportado a: {nombre_archivo}")

def imprimir_resumen_consola(reporte):
    """
    Imprime un resumen del reporte en consola
    """
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    
    resumen = reporte["resumen_ejecutivo"]
    print(f"💰 Mejor costo encontrado: ${resumen['metricas_clave']['mejor_costo']:.2f}/kg")
    print(f"🎯 Soluciones encontradas: {resumen['metricas_clave']['numero_soluciones']}")
    print(f"⏱️  Tiempo de ejecución: {resumen['metricas_clave']['tiempo_ejecucion']:.1f} segundos")
    
    print(f"\n🔍 Recomendación principal:")
    print(f"   {resumen['recomendacion_principal']}")
    
    # Mostrar top 3 soluciones
    print(f"\n📋 MEJORES SOLUCIONES:")
    for i, solucion in enumerate(reporte["mejores_soluciones"][:3]):
        formula = solucion["formula"]
        costo = formula[-1]["costo_por_kg_formula"]  # Total
        nutricional = solucion["analisis_nutricional"]
        
        print(f"   {i+1}. Costo: ${costo:.3f}/kg | Score nutricional: {nutricional['score_nutricional']}/100")
    
    print("\n" + "="*60)