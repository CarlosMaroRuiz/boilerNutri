"""
Representación de una solución individual (formulación de alimento).

Define la estructura del genotipo, métodos de inicialización,
normalización y evaluación de un individuo.
"""

import numpy as np
import random
import copy

class Individuo:
    """
    Representa una formulación de alimento como solución individual
    """
    
    def __init__(self, num_ingredientes, semilla=None):
        """
        Inicializa un individuo con la cantidad especificada de ingredientes
        
        Args:
            num_ingredientes: Número de ingredientes en la formulación
            semilla: Semilla para reproducibilidad (opcional)
        """
        # Usar semilla para reproducibilidad si se proporciona
        if semilla is not None:
            np.random.seed(semilla)
            random.seed(semilla)
            
        # Vector de porcentajes (0-1) donde la suma = 1
        self.porcentajes = np.zeros(num_ingredientes)
        
        # Propiedades calculadas
        self.propiedades_nutricionales = {}
        self.costo_total = 0
        self.fitness = float('inf')
        self.proveedor_recomendado = {}
        
        # Métricas adicionales
        self.conversion_alimenticia = 0
        self.dias_peso_objetivo = 0
        self.disponibilidad_score = 0
        self.penalizacion_restricciones = 0
        
    def inicializar_aleatorio(self, ingredientes_data, restricciones_usuario=None):
        """
        Inicializa el individuo con valores aleatorios respetando límites
        
        Args:
            ingredientes_data: Lista con datos de ingredientes
            restricciones_usuario: Objeto con restricciones del usuario
        """
        for i in range(len(self.porcentajes)):
            if i >= len(ingredientes_data):
                continue
                
            # Verificar si el ingrediente está disponible según restricciones del usuario
            if restricciones_usuario and not restricciones_usuario.es_ingrediente_valido(i):
                self.porcentajes[i] = 0
                continue
            
            # Obtener límites del ingrediente
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            min_val = limites["min"]
            max_val = limites["max"]
            
            # Si min y max son iguales (ingrediente con porcentaje fijo)
            if abs(min_val - max_val) < 1e-6:
                self.porcentajes[i] = min_val
            else:
                # Generar valor aleatorio dentro de los límites
                self.porcentajes[i] = min_val + random.random() * (max_val - min_val)
        
        # Normalizar para que sumen 1, respetando ingredientes con porcentaje fijo
        self.normalizar(ingredientes_data, restricciones_usuario)
    
    def normalizar(self, ingredientes_data=None, restricciones_usuario=None):
        """
        Normaliza los porcentajes para que sumen 1, respetando ingredientes fijos
        
        Args:
            ingredientes_data: Lista con datos de ingredientes (opcional)
            restricciones_usuario: Objeto con restricciones del usuario (opcional)
        """
        # Identificar ingredientes con porcentaje fijo
        indices_fijos = []
        suma_fijos = 0
        
        if ingredientes_data:
            for i in range(min(len(self.porcentajes), len(ingredientes_data))):
                # Obtener límites efectivos
                limites_originales = ingredientes_data[i]["limitaciones"]
                if restricciones_usuario:
                    limites = restricciones_usuario.obtener_limites(i, limites_originales)
                else:
                    limites = limites_originales
                
                # Verificar si es un ingrediente con porcentaje fijo
                if abs(limites["min"] - limites["max"]) < 1e-6:
                    indices_fijos.append(i)
                    suma_fijos += self.porcentajes[i]
        
        # Calcular cuánto deben sumar los ingredientes variables
        suma_objetivo_variables = 1.0 - suma_fijos
        
        # Si la suma objetivo es negativa o muy pequeña, hay un problema con los ingredientes fijos
        if suma_objetivo_variables <= 0:
            # Redistribuir proporcionalmente todos los no fijos
            indices_variables = [i for i in range(len(self.porcentajes)) if i not in indices_fijos]
            if indices_variables:
                for i in indices_variables:
                    self.porcentajes[i] = suma_objetivo_variables / len(indices_variables)
            return
        
        # Calcular suma actual de ingredientes variables
        indices_variables = [i for i in range(len(self.porcentajes)) if i not in indices_fijos]
        suma_variables = sum(self.porcentajes[i] for i in indices_variables)
        
        # Normalizar ingredientes variables
        if suma_variables > 0:
            factor = suma_objetivo_variables / suma_variables
            for i in indices_variables:
                self.porcentajes[i] *= factor
        elif indices_variables:
            # Si la suma de variables es 0, distribuir uniformemente
            for i in indices_variables:
                self.porcentajes[i] = suma_objetivo_variables / len(indices_variables)
    
    def clonar(self):
        """
        Crea una copia profunda del individuo
        
        Returns:
            Nuevo objeto Individuo idéntico al actual
        """
        nuevo_individuo = Individuo(len(self.porcentajes))
        nuevo_individuo.porcentajes = self.porcentajes.copy()
        nuevo_individuo.propiedades_nutricionales = self.propiedades_nutricionales.copy()
        nuevo_individuo.costo_total = self.costo_total
        nuevo_individuo.fitness = self.fitness
        nuevo_individuo.proveedor_recomendado = copy.deepcopy(self.proveedor_recomendado)
        nuevo_individuo.conversion_alimenticia = self.conversion_alimenticia
        nuevo_individuo.dias_peso_objetivo = self.dias_peso_objetivo
        nuevo_individuo.disponibilidad_score = self.disponibilidad_score
        nuevo_individuo.penalizacion_restricciones = self.penalizacion_restricciones
        
        return nuevo_individuo
    
    def validar_suma(self, tolerancia=1e-6):
        """
        Valida que la suma de porcentajes sea 1
        
        Args:
            tolerancia: Tolerancia para la validación
            
        Returns:
            True si la suma es válida, False en caso contrario
        """
        suma = sum(self.porcentajes)
        return abs(suma - 1.0) <= tolerancia
    
    def aplicar_limites(self, ingredientes_data, restricciones_usuario=None):
        """
        Aplica los límites mínimos y máximos a todos los ingredientes
        
        Args:
            ingredientes_data: Lista con datos de ingredientes
            restricciones_usuario: Objeto con restricciones del usuario (opcional)
        """
        for i in range(min(len(self.porcentajes), len(ingredientes_data))):
            # Verificar disponibilidad según restricciones del usuario
            if restricciones_usuario and not restricciones_usuario.es_ingrediente_valido(i):
                self.porcentajes[i] = 0
                continue
            
            # Obtener límites efectivos
            limites_originales = ingredientes_data[i]["limitaciones"]
            if restricciones_usuario:
                limites = restricciones_usuario.obtener_limites(i, limites_originales)
            else:
                limites = limites_originales
            
            # Aplicar límites
            self.porcentajes[i] = max(limites["min"], 
                                    min(self.porcentajes[i], limites["max"]))
        
        # Renormalizar después de aplicar límites
        self.normalizar(ingredientes_data, restricciones_usuario)
    
    def obtener_ingredientes_activos(self, ingredientes_data, umbral=0.001):
        """
        Obtiene lista de ingredientes con porcentaje significativo
        
        Args:
            ingredientes_data: Lista con datos de ingredientes
            umbral: Porcentaje mínimo para considerar un ingrediente activo
            
        Returns:
            Lista de tuplas (indice, nombre, porcentaje)
        """
        ingredientes_activos = []
        
        for i, porcentaje in enumerate(self.porcentajes):
            if porcentaje > umbral and i < len(ingredientes_data):
                ingredientes_activos.append((
                    i,
                    ingredientes_data[i]["nombre"],
                    porcentaje
                ))
        
        return sorted(ingredientes_activos, key=lambda x: x[2], reverse=True)
    
    def generar_resumen(self, ingredientes_data):
        """
        Genera un resumen legible del individuo
        
        Args:
            ingredientes_data: Lista con datos de ingredientes
            
        Returns:
            String con resumen del individuo
        """
        resumen = []
        resumen.append(f"Fitness: {self.fitness:.4f}")
        resumen.append(f"Costo total: ${self.costo_total:.2f}/kg")
        
        if hasattr(self, 'conversion_alimenticia') and self.conversion_alimenticia > 0:
            resumen.append(f"Conversión alimenticia: {self.conversion_alimenticia:.2f}")
        
        resumen.append("\nIngredientes activos:")
        ingredientes_activos = self.obtener_ingredientes_activos(ingredientes_data)
        
        for _, nombre, porcentaje in ingredientes_activos:
            resumen.append(f"  {nombre}: {porcentaje:.1%}")
        
        if self.propiedades_nutricionales:
            resumen.append("\nPerfil nutricional:")
            for nutriente, valor in self.propiedades_nutricionales.items():
                if nutriente == "energia":
                    resumen.append(f"  {nutriente.capitalize()}: {valor:.0f} kcal/kg")
                else:
                    resumen.append(f"  {nutriente.capitalize()}: {valor:.2%}")
        
        return "\n".join(resumen)
    
    def __str__(self):
        """
        Representación en string del individuo
        """
        return f"Individuo(fitness={self.fitness:.4f}, costo=${self.costo_total:.2f})"
    
    def __repr__(self):
        """
        Representación detallada del individuo
        """
        return (f"Individuo(porcentajes={self.porcentajes}, "
                f"fitness={self.fitness:.4f}, costo={self.costo_total:.2f})")
    
    def __lt__(self, other):
        """
        Comparación para ordenamiento (menor fitness es mejor)
        """
        return self.fitness < other.fitness
    
    def __eq__(self, other):
        """
        Igualdad basada en fitness
        """
        return abs(self.fitness - other.fitness) < 1e-6