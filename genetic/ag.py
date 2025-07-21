"""
Implementación principal del algoritmo genético.

Coordina el proceso evolutivo con estrategia adaptativa por fases:
- Fase inicial: Exploración amplia
- Fase intermedia: Transición gradual
- Fase final: Explotación y refinamiento
"""

import time
import random
import copy
from genetic.inicializacion import crear_poblacion_inicial, generar_estadisticas_poblacion
from genetic.seleccion import seleccionar_padre, seleccion_elitista, calcular_metricas_seleccion
from genetic.cruza import seleccionar_operador_cruza, validar_hijo, reparar_hijo
from genetic.mutacion import seleccionar_operador_mutacion
from genetic.fitness.agregacion import calcular_fitness_adaptativo, evaluar_poblacion, detectar_convergencia

class AlgoritmoGenetico:
    """
    Algoritmo genético para optimización de formulaciones de alimentos
    """
    
    def __init__(self, config):
        """
        Inicializa el algoritmo genético
        
        Args:
            config: Diccionario con configuración del algoritmo
        """
        self.config = config
        self.poblacion = []
        self.mejores_individuos = []  # Mantener los 3 mejores individuos encontrados
        self.historico_fitness = []
        self.historico_metricas = []
        
        # Parámetros del algoritmo
        self.tamano_poblacion = config.get("tamano_poblacion", 100)
        self.num_generaciones = config.get("num_generaciones", 200)
        self.prob_cruza = config.get("prob_cruza", 0.8)
        self.prob_mutacion = config.get("prob_mutacion", 0.2)
        self.elitismo = config.get("elitismo", 5)
        
        # Datos del problema
        self.ingredientes_data = config.get("ingredientes_data", [])
        self.restricciones_usuario = config.get("restricciones_usuario", None)
        self.config_evaluacion = config.get("config_evaluacion", {})
        
        # Métricas de ejecución
        self.tiempo_inicio = None
        self.tiempo_ejecucion = 0
        self.generacion_actual = 0
        self.fase_actual = "inicial"
        self.convergencia_detectada = False
        
        # Configuración de fases
        self.fases_config = {
            "inicial": {"inicio": 0, "fin": 0.3},
            "intermedia": {"inicio": 0.3, "fin": 0.7},
            "final": {"inicio": 0.7, "fin": 1.0}
        }
    
    def ejecutar(self):
        """
        Ejecuta el algoritmo genético completo
        
        Returns:
            Diccionario con resultados de la ejecución
        """
        print("🧬 Iniciando algoritmo genético...")
        self.tiempo_inicio = time.time()
        
        try:
            # Inicializar población
            self._inicializar_poblacion()
            
            # Evaluar población inicial
            self._evaluar_poblacion_inicial()
            
            # Ciclo evolutivo principal
            for generacion in range(self.num_generaciones):
                self.generacion_actual = generacion
                
                # Actualizar fase actual
                self._actualizar_fase()
                
                # Mostrar progreso
                if generacion % 20 == 0:
                    mejor_fitness = self.poblacion[0].fitness
                    print(f"Generación {generacion}: Mejor fitness = {mejor_fitness:.4f} (Fase: {self.fase_actual})")
                
                # Crear nueva generación
                nueva_poblacion = self._crear_nueva_generacion()
                
                # Evaluar nueva población
                self.poblacion = nueva_poblacion
                evaluar_poblacion(self.poblacion, self.config_evaluacion, self.ingredientes_data,
                                self.fase_actual, self.restricciones_usuario)
                
                # Ordenar por fitness
                self.poblacion.sort(key=lambda ind: ind.fitness)
                
                # Actualizar mejores individuos
                self._actualizar_mejores_individuos()
                
                # Registrar métricas
                self._registrar_metricas()
                
                # Verificar convergencia
                if self._verificar_convergencia():
                    print(f"Convergencia detectada en generación {generacion}")
                    self.convergencia_detectada = True
                    break
            
            # Finalizar ejecución
            self._finalizar_ejecucion()
            
            return self._generar_resultado_final()
        
        except Exception as e:
            print(f"Error durante la ejecución del algoritmo: {e}")
            return {"error": str(e)}
    
    def _inicializar_poblacion(self):
        """Inicializa la población inicial"""
        print("📊 Creando población inicial...")
        
        self.poblacion = crear_poblacion_inicial(
            self.tamano_poblacion,
            self.ingredientes_data,
            self.restricciones_usuario,
            estrategia="mixta"
        )
        
        # Generar estadísticas de población inicial
        estadisticas = generar_estadisticas_poblacion(self.poblacion, self.ingredientes_data)
        print(f"   • Población creada: {estadisticas['tamano_poblacion']} individuos")
        print(f"   • Individuos válidos: {estadisticas['suma_valida']}")
        print(f"   • Diversidad inicial: {estadisticas.get('diversidad_poblacion', 0):.3f}")
    
    def _evaluar_poblacion_inicial(self):
        """Evalúa la población inicial"""
        print("🔍 Evaluando población inicial...")
        
        evaluar_poblacion(self.poblacion, self.config_evaluacion, self.ingredientes_data,
                         self.fase_actual, self.restricciones_usuario)
        
        # Ordenar por fitness (menor es mejor)
        self.poblacion.sort(key=lambda ind: ind.fitness)
        
        # Inicializar mejores individuos
        self._actualizar_mejores_individuos()
        
        mejor_fitness = self.poblacion[0].fitness
        print(f"   • Mejor fitness inicial: {mejor_fitness:.4f}")
        print(f"   • Peor fitness inicial: {self.poblacion[-1].fitness:.4f}")
    
    def _actualizar_fase(self):
        """Actualiza la fase actual del algoritmo según el progreso"""
        progreso = self.generacion_actual / self.num_generaciones
        
        if progreso <= self.fases_config["inicial"]["fin"]:
            self.fase_actual = "inicial"
        elif progreso <= self.fases_config["intermedia"]["fin"]:
            self.fase_actual = "intermedia"
        else:
            self.fase_actual = "final"
    
    def _crear_nueva_generacion(self):
        """Crea una nueva generación mediante operadores genéticos"""
        nueva_poblacion = []
        
        # Elitismo: conservar los mejores individuos
        elite = seleccion_elitista(self.poblacion, self.elitismo)
        nueva_poblacion.extend([ind.clonar() for ind in elite])
        
        # Obtener operadores adaptativos para la fase actual
        operador_cruza = seleccionar_operador_cruza(self.fase_actual, self.ingredientes_data, self.restricciones_usuario)
        operador_mutacion = seleccionar_operador_mutacion(self.fase_actual, self._calcular_diversidad_poblacion())
        
        # Generar resto de la población
        while len(nueva_poblacion) < self.tamano_poblacion:
            # Seleccionar padres
            padre1 = seleccionar_padre(self.poblacion, metodo="torneo", tamano_torneo=self._obtener_tamano_torneo())
            padre2 = seleccionar_padre(self.poblacion, metodo="torneo", tamano_torneo=self._obtener_tamano_torneo())
            
            # Aplicar cruza
            if random.random() < self.prob_cruza:
                hijo = operador_cruza(padre1, padre2)
                
                # Validar y reparar hijo si es necesario
                if not validar_hijo(hijo, self.ingredientes_data, self.restricciones_usuario):
                    hijo = reparar_hijo(hijo, self.ingredientes_data, self.restricciones_usuario)
            else:
                # Sin cruza, clonar uno de los padres
                hijo = padre1.clonar() if random.random() < 0.5 else padre2.clonar()
            
            # Aplicar mutación
            if random.random() < self.prob_mutacion:
                hijo = operador_mutacion(hijo, self.generacion_actual, self.num_generaciones,
                                       self.ingredientes_data, self.restricciones_usuario)
            
            nueva_poblacion.append(hijo)
        
        return nueva_poblacion
    
    def _obtener_tamano_torneo(self):
        """Obtiene el tamaño del torneo según la fase actual"""
        if self.fase_actual == "inicial":
            return 3
        elif self.fase_actual == "intermedia":
            return 4
        else:  # fase final
            return 5
    
    def _calcular_diversidad_poblacion(self):
        """Calcula la diversidad de la población actual"""
        if len(self.poblacion) < 2:
            return 1.0
        
        fitness_values = [ind.fitness for ind in self.poblacion]
        promedio = sum(fitness_values) / len(fitness_values)
        
        if promedio == 0:
            return 1.0
        
        varianza = sum((f - promedio) ** 2 for f in fitness_values) / len(fitness_values)
        coef_variacion = (varianza ** 0.5) / promedio if promedio > 0 else 0
        
        # Normalizar a rango 0-1
        return min(1.0, coef_variacion)
    
    def _actualizar_mejores_individuos(self):
        """Actualiza la lista de mejores individuos encontrados"""
        # Añadir el mejor individuo actual si no está ya en la lista
        mejor_actual = self.poblacion[0]
        
        # Verificar si ya existe un individuo similar
        es_nuevo = True
        for mejor in self.mejores_individuos:
            if abs(mejor.fitness - mejor_actual.fitness) < 1e-6:
                es_nuevo = False
                break
        
        if es_nuevo:
            self.mejores_individuos.append(mejor_actual.clonar())
        
        # Mantener solo los 3 mejores únicos
        self.mejores_individuos.sort(key=lambda ind: ind.fitness)
        
        # Eliminar duplicados manteniendo diversidad
        mejores_unicos = []
        for individuo in self.mejores_individuos:
            es_suficientemente_diferente = True
            
            for unico in mejores_unicos:
                # Calcular similitud basada en porcentajes
                similitud = self._calcular_similitud(individuo, unico)
                if similitud > 0.95:  # Muy similares
                    es_suficientemente_diferente = False
                    break
            
            if es_suficientemente_diferente:
                mejores_unicos.append(individuo)
            
            if len(mejores_unicos) >= 3:
                break
        
        self.mejores_individuos = mejores_unicos
    
    def _calcular_similitud(self, individuo1, individuo2):
        """Calcula similitud entre dos individuos (0-1)"""
        if len(individuo1.porcentajes) != len(individuo2.porcentajes):
            return 0
        
        suma_diferencias = 0
        for i in range(len(individuo1.porcentajes)):
            suma_diferencias += abs(individuo1.porcentajes[i] - individuo2.porcentajes[i])
        
        similitud = 1 - (suma_diferencias / 2)  # Normalizar a 0-1
        return max(0, similitud)
    
    def _registrar_metricas(self):
        """Registra métricas de la generación actual"""
        mejor_fitness = self.poblacion[0].fitness
        self.historico_fitness.append(mejor_fitness)
        
        # Calcular métricas adicionales
        fitness_values = [ind.fitness for ind in self.poblacion]
        costos = [ind.costo_total for ind in self.poblacion if hasattr(ind, 'costo_total')]
        
        metricas = {
            "generacion": self.generacion_actual,
            "fase": self.fase_actual,
            "mejor_fitness": mejor_fitness,
            "peor_fitness": max(fitness_values),
            "fitness_promedio": sum(fitness_values) / len(fitness_values),
            "diversidad": self._calcular_diversidad_poblacion(),
            "num_mejores_encontrados": len(self.mejores_individuos)
        }
        
        if costos:
            metricas["mejor_costo"] = min(costos)
            metricas["costo_promedio"] = sum(costos) / len(costos)
        
        self.historico_metricas.append(metricas)
    
    def _verificar_convergencia(self):
        """Verifica si el algoritmo ha convergido"""
        if len(self.historico_fitness) < 50:  # Mínimo 50 generaciones
            return False
        
        return detectar_convergencia(self.historico_fitness, ventana=30, tolerancia=1e-6)
    
    def _finalizar_ejecucion(self):
        """Finaliza la ejecución y calcula métricas finales"""
        self.tiempo_ejecucion = time.time() - self.tiempo_inicio
        
        print(f"\n✅ Algoritmo finalizado!")
        print(f"   • Tiempo de ejecución: {self.tiempo_ejecucion:.2f} segundos")
        print(f"   • Generaciones ejecutadas: {self.generacion_actual + 1}")
        print(f"   • Mejores individuos encontrados: {len(self.mejores_individuos)}")
        
        if self.mejores_individuos:
            mejor_global = self.mejores_individuos[0]
            print(f"   • Mejor fitness global: {mejor_global.fitness:.4f}")
            if hasattr(mejor_global, 'costo_total'):
                print(f"   • Mejor costo: ${mejor_global.costo_total:.2f}/kg")
    
    def _generar_resultado_final(self):
        """Genera el resultado final del algoritmo"""
        resultado = {
            "mejor_individuo": self.mejores_individuos[0] if self.mejores_individuos else None,
            "mejores_individuos": self.mejores_individuos[:3],  # Top 3
            "historico_fitness": self.historico_fitness,
            "historico_metricas": self.historico_metricas,
            "tiempo_ejecucion": self.tiempo_ejecucion,
            "generaciones_ejecutadas": self.generacion_actual + 1,
            "convergencia_detectada": self.convergencia_detectada,
            "fase_final": self.fase_actual,
            "poblacion_final": self.poblacion[:10] if self.poblacion else []  # Top 10 de población final
        }
        
        return resultado
    
    def determinar_fase(self, generacion_actual):
        """
        Determina la fase actual del algoritmo (método público para compatibilidad)
        
        Args:
            generacion_actual: Generación actual
            
        Returns:
            String con la fase actual
        """
        progreso = generacion_actual / self.num_generaciones if self.num_generaciones > 0 else 0
        
        if progreso <= 0.3:
            return "inicial"
        elif progreso <= 0.7:
            return "intermedia"
        else:
            return "final"
    
    def obtener_mejor_individuo(self):
        """
        Obtiene el mejor individuo encontrado hasta el momento
        
        Returns:
            Mejor individuo o None si no hay población
        """
        if self.mejores_individuos:
            return self.mejores_individuos[0]
        elif self.poblacion:
            return min(self.poblacion, key=lambda ind: ind.fitness)
        else:
            return None
    
    def obtener_estadisticas_ejecucion(self):
        """
        Obtiene estadísticas detalladas de la ejecución
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.historico_metricas:
            return {}
        
        estadisticas = {
            "progreso_fitness": {
                "inicial": self.historico_fitness[0] if self.historico_fitness else 0,
                "final": self.historico_fitness[-1] if self.historico_fitness else 0,
                "mejora_total": 0,
                "mejora_porcentual": 0
            },
            "fases_ejecutadas": set(m["fase"] for m in self.historico_metricas),
            "convergencia": {
                "detectada": self.convergencia_detectada,
                "generacion": self.generacion_actual if self.convergencia_detectada else None
            },
            "diversidad": {
                "inicial": self.historico_metricas[0].get("diversidad", 0),
                "final": self.historico_metricas[-1].get("diversidad", 0)
            },
            "rendimiento": {
                "tiempo_total": self.tiempo_ejecucion,
                "tiempo_por_generacion": self.tiempo_ejecucion / max(1, self.generacion_actual + 1),
                "evaluaciones_totales": (self.generacion_actual + 1) * self.tamano_poblacion
            }
        }
        
        # Calcular mejora
        if len(self.historico_fitness) >= 2:
            inicial = self.historico_fitness[0]
            final = self.historico_fitness[-1]
            estadisticas["progreso_fitness"]["mejora_total"] = inicial - final
            if inicial > 0:
                estadisticas["progreso_fitness"]["mejora_porcentual"] = ((inicial - final) / inicial) * 100
        
        return estadisticas
    
    def exportar_configuracion(self):
        """
        Exporta la configuración actual del algoritmo
        
        Returns:
            Diccionario con configuración
        """
        return {
            "tamano_poblacion": self.tamano_poblacion,
            "num_generaciones": self.num_generaciones,
            "prob_cruza": self.prob_cruza,
            "prob_mutacion": self.prob_mutacion,
            "elitismo": self.elitismo,
            "fases_config": self.fases_config,
            "num_ingredientes": len(self.ingredientes_data),
            "tiene_restricciones_usuario": self.restricciones_usuario is not None
        }