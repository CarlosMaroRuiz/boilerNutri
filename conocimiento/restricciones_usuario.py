"""
Gestión de restricciones específicas del usuario.

Maneja limitaciones personalizadas, exclusiones de ingredientes
y configuraciones particulares del usuario.
"""

class RestriccionesUsuario:
    """
    Clase para gestionar restricciones específicas del usuario
    """
    
    def __init__(self):
        self.ingredientes_excluidos = []
        self.limites_personalizados = {}
        self.capacidad_planta = None
        self.ingredientes_disponibles = []
        self.presupuesto_maximo = None
        self.preferencias_proveedor = {}
        
    def agregar_exclusion(self, ingrediente_id):
        """
        Excluye un ingrediente de la formulación
        
        Args:
            ingrediente_id: ID del ingrediente a excluir
        """
        if ingrediente_id not in self.ingredientes_excluidos:
            self.ingredientes_excluidos.append(ingrediente_id)
    
    def remover_exclusion(self, ingrediente_id):
        """
        Remueve la exclusión de un ingrediente
        
        Args:
            ingrediente_id: ID del ingrediente a incluir nuevamente
        """
        if ingrediente_id in self.ingredientes_excluidos:
            self.ingredientes_excluidos.remove(ingrediente_id)
        
    def establecer_limite(self, ingrediente_id, min_val, max_val):
        """
        Establece límites personalizados para un ingrediente
        
        Args:
            ingrediente_id: ID del ingrediente
            min_val: Valor mínimo (porcentaje como decimal)
            max_val: Valor máximo (porcentaje como decimal)
        """
        self.limites_personalizados[ingrediente_id] = {
            "min": min_val,
            "max": max_val
        }
    
    def establecer_capacidad_planta(self, capacidad_kg_dia):
        """
        Establece la capacidad de producción de la planta
        
        Args:
            capacidad_kg_dia: Capacidad en kg por día
        """
        self.capacidad_planta = capacidad_kg_dia
    
    def establecer_presupuesto_maximo(self, presupuesto):
        """
        Establece el presupuesto máximo por kg de alimento
        
        Args:
            presupuesto: Presupuesto máximo en pesos por kg
        """
        self.presupuesto_maximo = presupuesto
    
    def agregar_ingrediente_disponible(self, ingrediente_id):
        """
        Marca un ingrediente como disponible para el usuario
        
        Args:
            ingrediente_id: ID del ingrediente disponible
        """
        if ingrediente_id not in self.ingredientes_disponibles:
            self.ingredientes_disponibles.append(ingrediente_id)
    
    def establecer_preferencia_proveedor(self, proveedor_clave, factor_preferencia):
        """
        Establece preferencia por un proveedor específico
        
        Args:
            proveedor_clave: Clave del proveedor
            factor_preferencia: Factor de preferencia (0.8-1.2, donde <1 es preferido)
        """
        self.preferencias_proveedor[proveedor_clave] = factor_preferencia
    
    def es_ingrediente_valido(self, ingrediente_id):
        """
        Verifica si un ingrediente es válido según las restricciones
        
        Args:
            ingrediente_id: ID del ingrediente a verificar
            
        Returns:
            True si el ingrediente es válido, False si está excluido
        """
        # Si hay lista de disponibles, solo permitir esos
        if self.ingredientes_disponibles:
            return ingrediente_id in self.ingredientes_disponibles
        
        # Si no hay lista de disponibles, solo excluir los que están en la lista de exclusión
        return ingrediente_id not in self.ingredientes_excluidos
    
    def obtener_limites(self, ingrediente_id, limites_originales):
        """
        Obtiene los límites efectivos para un ingrediente
        
        Args:
            ingrediente_id: ID del ingrediente
            limites_originales: Límites originales del ingrediente
            
        Returns:
            Diccionario con límites efectivos (min, max)
        """
        if ingrediente_id in self.limites_personalizados:
            return self.limites_personalizados[ingrediente_id]
        
        return {
            "min": limites_originales["min"],
            "max": limites_originales["max"]
        }
    
    def validar_restricciones(self, individuo, ingredientes_data):
        """
        Valida si un individuo cumple con todas las restricciones del usuario
        
        Args:
            individuo: Objeto individuo con porcentajes
            ingredientes_data: Lista de datos de ingredientes
            
        Returns:
            Tupla (es_valido, lista_violaciones)
        """
        violaciones = []
        
        # Verificar ingredientes excluidos
        for i, porcentaje in enumerate(individuo.porcentajes):
            if porcentaje > 0.001 and not self.es_ingrediente_valido(i):
                if i < len(ingredientes_data):
                    violaciones.append(f"Ingrediente excluido: {ingredientes_data[i]['nombre']}")
        
        # Verificar límites personalizados
        for i, porcentaje in enumerate(individuo.porcentajes):
            if i in self.limites_personalizados:
                limites = self.limites_personalizados[i]
                if porcentaje < limites["min"] or porcentaje > limites["max"]:
                    if i < len(ingredientes_data):
                        violaciones.append(
                            f"Límite violado en {ingredientes_data[i]['nombre']}: "
                            f"{porcentaje:.2%} (permitido: {limites['min']:.2%}-{limites['max']:.2%})"
                        )
        
        # Verificar presupuesto máximo
        if self.presupuesto_maximo and hasattr(individuo, 'costo_total'):
            if individuo.costo_total > self.presupuesto_maximo:
                violaciones.append(
                    f"Presupuesto excedido: ${individuo.costo_total:.2f} > ${self.presupuesto_maximo:.2f}"
                )
        
        return len(violaciones) == 0, violaciones
    
    def aplicar_restricciones_a_individuo(self, individuo, ingredientes_data):
        """
        Aplica las restricciones del usuario a un individuo, modificándolo si es necesario
        
        Args:
            individuo: Objeto individuo a modificar
            ingredientes_data: Lista de datos de ingredientes
        """
        # Eliminar ingredientes excluidos
        for i in range(len(individuo.porcentajes)):
            if not self.es_ingrediente_valido(i):
                individuo.porcentajes[i] = 0
        
        # Aplicar límites personalizados
        for i in range(len(individuo.porcentajes)):
            if i in self.limites_personalizados:
                limites = self.limites_personalizados[i]
                individuo.porcentajes[i] = max(limites["min"], 
                                             min(individuo.porcentajes[i], limites["max"]))
        
        # Renormalizar para que sume 1
        individuo.normalizar()
    
    def generar_resumen_restricciones(self, ingredientes_data):
        """
        Genera un resumen legible de todas las restricciones activas
        
        Args:
            ingredientes_data: Lista de datos de ingredientes
            
        Returns:
            String con resumen de restricciones
        """
        resumen = []
        
        if self.ingredientes_excluidos:
            nombres_excluidos = []
            for ingrediente_id in self.ingredientes_excluidos:
                if ingrediente_id < len(ingredientes_data):
                    nombres_excluidos.append(ingredientes_data[ingrediente_id]["nombre"])
            if nombres_excluidos:
                resumen.append(f"Ingredientes excluidos: {', '.join(nombres_excluidos)}")
        
        if self.ingredientes_disponibles:
            nombres_disponibles = []
            for ingrediente_id in self.ingredientes_disponibles:
                if ingrediente_id < len(ingredientes_data):
                    nombres_disponibles.append(ingredientes_data[ingrediente_id]["nombre"])
            if nombres_disponibles:
                resumen.append(f"Solo ingredientes disponibles: {', '.join(nombres_disponibles)}")
        
        if self.limites_personalizados:
            for ingrediente_id, limites in self.limites_personalizados.items():
                if ingrediente_id < len(ingredientes_data):
                    nombre = ingredientes_data[ingrediente_id]["nombre"]
                    resumen.append(
                        f"{nombre}: {limites['min']:.1%} - {limites['max']:.1%}"
                    )
        
        if self.capacidad_planta:
            resumen.append(f"Capacidad de planta: {self.capacidad_planta} kg/día")
        
        if self.presupuesto_maximo:
            resumen.append(f"Presupuesto máximo: ${self.presupuesto_maximo:.2f}/kg")
        
        return "\n".join(resumen) if resumen else "Sin restricciones adicionales"