"""
Procesamiento y validación de entradas del usuario.

Maneja la captura, validación y procesamiento de todos
los parámetros proporcionados por el usuario.
"""

import json
from conocimiento import INGREDIENTES, RAZAS_POLLOS, PROVEEDORES
from conocimiento.restricciones_usuario import RestriccionesUsuario

def procesar_entradas():
    """
    Procesa todas las entradas del usuario de forma interactiva
    
    Returns:
        Diccionario con parámetros validados del usuario
    """
    print("🐔 Sistema de Optimización de Alimentos para Pollos")
    print("=" * 60)
    print("Por favor proporcione la siguiente información:\n")
    
    parametros = {}
    
    try:
        # 1. Parámetros de producción
        parametros.update(capturar_parametros_produccion())
        
        # 2. Ingredientes disponibles
        parametros["ingredientes_disponibles"] = capturar_ingredientes_disponibles()
        
        # 3. Restricciones especiales
        parametros["restricciones_usuario"] = definir_restricciones_especiales()
        
        # 4. Validar coherencia
        validar_coherencia_entradas(parametros)
        
        print("\n✅ Todos los parámetros han sido validados correctamente")
        return parametros
        
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
        return None
    except Exception as e:
        print(f"\n❌ Error procesando entradas: {e}")
        return None

def capturar_parametros_produccion():
    """
    Captura y valida los parámetros básicos de producción
    
    Returns:
        Diccionario con parámetros de producción validados
    """
    print("📊 PARÁMETROS DE PRODUCCIÓN")
    print("-" * 30)
    
    parametros = {}
    
    # 1. Raza de pollos
    parametros["raza"] = capturar_raza()
    
    # 2. Edad actual
    parametros["edad_dias"] = capturar_edad_dias()
    
    # 3. Peso actual
    parametros["peso_actual"] = capturar_peso_actual(parametros["raza"], parametros["edad_dias"])
    
    # 4. Peso objetivo
    parametros["peso_objetivo"] = capturar_peso_objetivo(parametros["peso_actual"])
    
    # 5. Cantidad de pollos
    parametros["cantidad_pollos"] = capturar_cantidad_pollos()
    
    return parametros

def capturar_raza():
    """
    Captura la raza de pollos
    """
    print("Razas disponibles:")
    for i, raza in enumerate(RAZAS_POLLOS, 1):
        print(f"  {i}. {raza['nombre']} - {raza['descripcion']}")
    
    while True:
        try:
            opcion = input(f"\nSeleccione la raza (1-{len(RAZAS_POLLOS)}): ").strip()
            
            if opcion.isdigit():
                indice = int(opcion) - 1
                if 0 <= indice < len(RAZAS_POLLOS):
                    raza_seleccionada = RAZAS_POLLOS[indice]["nombre"]
                    print(f"✓ Raza seleccionada: {raza_seleccionada}")
                    return raza_seleccionada
            
            # Permitir entrada por nombre
            for raza in RAZAS_POLLOS:
                if raza["nombre"].lower() == opcion.lower():
                    print(f"✓ Raza seleccionada: {raza['nombre']}")
                    return raza["nombre"]
            
            print("❌ Opción inválida. Intente nuevamente.")
            
        except (ValueError, KeyboardInterrupt):
            raise

def capturar_edad_dias():
    """
    Captura la edad actual de los pollos en días
    """
    while True:
        try:
            edad = input("Edad actual de los pollos (días): ").strip()
            edad_dias = int(edad)
            
            if 1 <= edad_dias <= 70:
                # Determinar etapa
                if edad_dias <= 10:
                    etapa = "iniciación"
                elif edad_dias <= 24:
                    etapa = "crecimiento"
                else:
                    etapa = "finalización"
                
                print(f"✓ Edad: {edad_dias} días (etapa: {etapa})")
                return edad_dias
            else:
                print("❌ La edad debe estar entre 1 y 70 días")
                
        except ValueError:
            print("❌ Ingrese un número válido")
        except KeyboardInterrupt:
            raise

def capturar_peso_actual(raza, edad_dias):
    """
    Captura el peso actual promedio
    """
    from conocimiento.razas import obtener_peso_esperado
    
    # Obtener peso esperado como referencia
    peso_esperado = obtener_peso_esperado(raza, edad_dias)
    
    if peso_esperado:
        print(f"Peso esperado para {raza} a los {edad_dias} días: {peso_esperado:.2f} kg")
    
    while True:
        try:
            peso = input("Peso actual promedio por pollo (kg): ").strip()
            peso_actual = float(peso)
            
            if 0.02 <= peso_actual <= 5.0:  # Entre 20g y 5kg
                if peso_esperado and abs(peso_actual - peso_esperado) > peso_esperado * 0.3:
                    print(f"⚠️  El peso actual ({peso_actual:.2f} kg) difiere significativamente del esperado ({peso_esperado:.2f} kg)")
                    confirmar = input("¿Desea continuar? (s/n): ").strip().lower()
                    if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                        continue
                
                print(f"✓ Peso actual: {peso_actual:.2f} kg")
                return peso_actual
            else:
                print("❌ El peso debe estar entre 0.02 y 5.0 kg")
                
        except ValueError:
            print("❌ Ingrese un número válido")
        except KeyboardInterrupt:
            raise

def capturar_peso_objetivo(peso_actual):
    """
    Captura el peso objetivo
    """
    print(f"Peso actual: {peso_actual:.2f} kg")
    
    while True:
        try:
            peso = input("Peso objetivo por pollo (kg): ").strip()
            peso_objetivo = float(peso)
            
            if peso_objetivo <= peso_actual:
                print("❌ El peso objetivo debe ser mayor al peso actual")
                continue
            
            if peso_objetivo > 4.0:
                print("⚠️  Peso objetivo muy alto (>4kg). Pollos de engorda típicamente no superan 3kg")
                confirmar = input("¿Desea continuar? (s/n): ").strip().lower()
                if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                    continue
            
            ganancia_necesaria = peso_objetivo - peso_actual
            print(f"✓ Peso objetivo: {peso_objetivo:.2f} kg (ganancia requerida: {ganancia_necesaria:.2f} kg)")
            return peso_objetivo
            
        except ValueError:
            print("❌ Ingrese un número válido")
        except KeyboardInterrupt:
            raise

def capturar_cantidad_pollos():
    """
    Captura la cantidad total de pollos
    """
    while True:
        try:
            cantidad = input("Cantidad total de pollos: ").strip()
            cantidad_pollos = int(cantidad)
            
            if cantidad_pollos < 1:
                print("❌ La cantidad debe ser mayor a 0")
                continue
            
            if cantidad_pollos > 100000:
                print("⚠️  Cantidad muy grande (>100,000). Esto requerirá grandes volúmenes de alimento")
                confirmar = input("¿Desea continuar? (s/n): ").strip().lower()
                if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                    continue
            
            print(f"✓ Cantidad de pollos: {cantidad_pollos:,}")
            return cantidad_pollos
            
        except ValueError:
            print("❌ Ingrese un número entero válido")
        except KeyboardInterrupt:
            raise

def capturar_ingredientes_disponibles():
    """
    Captura los ingredientes disponibles y sus precios actuales
    
    Returns:
        Lista de índices de ingredientes disponibles
    """
    print("\n🥜 INGREDIENTES DISPONIBLES")
    print("-" * 30)
    print("Marque los ingredientes que tiene disponibles en su región:")
    
    # Mostrar todos los ingredientes
    for i, ingrediente in enumerate(INGREDIENTES):
        precio_promedio = ingrediente.get("precio_base", 0)
        print(f"  {i+1}. {ingrediente['nombre']} (aprox. ${precio_promedio:.2f}/kg)")
    
    ingredientes_disponibles = []
    
    while True:
        try:
            print(f"\nOpciones:")
            print("  - Ingrese números separados por comas (ej: 1,2,4)")
            print("  - Escriba 'todos' para seleccionar todos")
            print("  - Escriba 'ninguno' para no usar ingredientes específicos")
            
            entrada = input("Ingredientes disponibles: ").strip().lower()
            
            if entrada == "todos":
                ingredientes_disponibles = list(range(len(INGREDIENTES)))
                break
            elif entrada == "ninguno":
                ingredientes_disponibles = []
                break
            else:
                # Parsear números
                numeros = [x.strip() for x in entrada.split(",")]
                indices = []
                
                for num in numeros:
                    if num.isdigit():
                        indice = int(num) - 1
                        if 0 <= indice < len(INGREDIENTES):
                            indices.append(indice)
                        else:
                            print(f"❌ Número {num} fuera de rango")
                            raise ValueError("Número inválido")
                    else:
                        print(f"❌ '{num}' no es un número válido")
                        raise ValueError("Entrada inválida")
                
                ingredientes_disponibles = sorted(list(set(indices)))
                break
                
        except ValueError:
            print("❌ Entrada inválida. Intente nuevamente.")
        except KeyboardInterrupt:
            raise
    
    # Mostrar selección
    if ingredientes_disponibles:
        print(f"\n✓ Ingredientes seleccionados:")
        for i in ingredientes_disponibles:
            print(f"   • {INGREDIENTES[i]['nombre']}")
    else:
        print(f"\n✓ Se usarán todos los ingredientes disponibles")
    
    return ingredientes_disponibles

def definir_restricciones_especiales():
    """
    Permite al usuario definir restricciones especiales
    
    Returns:
        Objeto RestriccionesUsuario configurado
    """
    print(f"\n🚫 RESTRICCIONES ESPECIALES")
    print("-" * 30)
    print("¿Desea establecer restricciones especiales?")
    print("  1. No, usar configuración estándar")
    print("  2. Sí, configurar restricciones personalizadas")
    
    while True:
        try:
            opcion = input("Seleccione opción (1-2): ").strip()
            
            if opcion == "1":
                print("✓ Se usará configuración estándar")
                return None
            
            elif opcion == "2":
                return configurar_restricciones_personalizadas()
            
            else:
                print("❌ Opción inválida. Ingrese 1 o 2.")
                
        except KeyboardInterrupt:
            raise

def configurar_restricciones_personalizadas():
    """
    Configura restricciones personalizadas
    """
    restricciones = RestriccionesUsuario()
    
    print(f"\nConfiguración de restricciones personalizadas:")
    
    # 1. Ingredientes a excluir
    if preguntar_si_no("¿Desea excluir algún ingrediente específico?"):
        excluir_ingredientes(restricciones)
    
    # 2. Límites personalizados
    if preguntar_si_no("¿Desea establecer límites personalizados para algún ingrediente?"):
        establecer_limites_personalizados(restricciones)
    
    # 3. Presupuesto máximo
    if preguntar_si_no("¿Desea establecer un presupuesto máximo por kilogramo?"):
        establecer_presupuesto_maximo(restricciones)
    
    # 4. Capacidad de planta
    if preguntar_si_no("¿Desea especificar la capacidad de su planta de alimentos?"):
        establecer_capacidad_planta(restricciones)
    
    return restricciones

def preguntar_si_no(pregunta):
    """
    Hace una pregunta de sí/no al usuario
    """
    while True:
        respuesta = input(f"{pregunta} (s/n): ").strip().lower()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            return True
        elif respuesta in ['n', 'no']:
            return False
        else:
            print("❌ Responda 's' para sí o 'n' para no")

def excluir_ingredientes(restricciones):
    """
    Permite excluir ingredientes específicos
    """
    print("\nIngredientes disponibles para exclusión:")
    for i, ingrediente in enumerate(INGREDIENTES):
        print(f"  {i+1}. {ingrediente['nombre']}")
    
    while True:
        try:
            entrada = input("Ingredientes a excluir (números separados por comas): ").strip()
            
            if not entrada:
                break
            
            numeros = [x.strip() for x in entrada.split(",")]
            
            for num in numeros:
                if num.isdigit():
                    indice = int(num) - 1
                    if 0 <= indice < len(INGREDIENTES):
                        restricciones.agregar_exclusion(indice)
                        print(f"✓ {INGREDIENTES[indice]['nombre']} excluido")
                    else:
                        print(f"❌ Número {num} fuera de rango")
                        continue
                else:
                    print(f"❌ '{num}' no es un número válido")
                    continue
            break
            
        except ValueError:
            print("❌ Entrada inválida")

def establecer_limites_personalizados(restricciones):
    """
    Permite establecer límites personalizados para ingredientes
    """
    print("\nEstablecer límites personalizados:")
    print("(Ingrese porcentajes como números decimales, ej: 10.5 para 10.5%)")
    
    for i, ingrediente in enumerate(INGREDIENTES):
        print(f"\n{ingrediente['nombre']}:")
        print(f"  Límites actuales: {ingrediente['limitaciones']['min']*100:.1f}% - {ingrediente['limitaciones']['max']*100:.1f}%")
        
        if preguntar_si_no(f"¿Desea cambiar los límites para {ingrediente['nombre']}?"):
            establecer_limite_ingrediente(restricciones, i, ingrediente)

def establecer_limite_ingrediente(restricciones, indice, ingrediente):
    """
    Establece límites para un ingrediente específico
    """
    while True:
        try:
            min_actual = ingrediente['limitaciones']['min'] * 100
            max_actual = ingrediente['limitaciones']['max'] * 100
            
            print(f"Límites actuales: {min_actual:.1f}% - {max_actual:.1f}%")
            
            min_str = input(f"Nuevo mínimo (%) [{min_actual:.1f}]: ").strip()
            min_nuevo = float(min_str) / 100 if min_str else ingrediente['limitaciones']['min']
            
            max_str = input(f"Nuevo máximo (%) [{max_actual:.1f}]: ").strip()
            max_nuevo = float(max_str) / 100 if max_str else ingrediente['limitaciones']['max']
            
            if min_nuevo > max_nuevo:
                print("❌ El mínimo no puede ser mayor que el máximo")
                continue
            
            if min_nuevo < 0 or max_nuevo > 1:
                print("❌ Los porcentajes deben estar entre 0 y 100%")
                continue
            
            restricciones.establecer_limite(indice, min_nuevo, max_nuevo)
            print(f"✓ Límites establecidos: {min_nuevo*100:.1f}% - {max_nuevo*100:.1f}%")
            break
            
        except ValueError:
            print("❌ Ingrese números válidos")

def establecer_presupuesto_maximo(restricciones):
    """
    Establece presupuesto máximo por kilogramo
    """
    while True:
        try:
            presupuesto = input("Presupuesto máximo por kilogramo ($): ").strip()
            presupuesto_max = float(presupuesto)
            
            if presupuesto_max <= 0:
                print("❌ El presupuesto debe ser mayor a 0")
                continue
            
            if presupuesto_max > 50:
                print("⚠️  Presupuesto muy alto (>$50/kg)")
                if not preguntar_si_no("¿Desea continuar?"):
                    continue
            
            restricciones.establecer_presupuesto_maximo(presupuesto_max)
            print(f"✓ Presupuesto máximo: ${presupuesto_max:.2f}/kg")
            break
            
        except ValueError:
            print("❌ Ingrese un número válido")

def establecer_capacidad_planta(restricciones):
    """
    Establece la capacidad de la planta
    """
    while True:
        try:
            capacidad = input("Capacidad de producción diaria (kg/día): ").strip()
            capacidad_diaria = float(capacidad)
            
            if capacidad_diaria <= 0:
                print("❌ La capacidad debe ser mayor a 0")
                continue
            
            restricciones.establecer_capacidad_planta(capacidad_diaria)
            print(f"✓ Capacidad establecida: {capacidad_diaria:,.0f} kg/día")
            break
            
        except ValueError:
            print("❌ Ingrese un número válido")

def validar_parametros_produccion(raza, edad_dias, peso_actual, peso_objetivo):
    """
    Valida los parámetros de producción básicos
    
    Args:
        raza: Nombre de la raza
        edad_dias: Edad en días
        peso_actual: Peso actual en kg
        peso_objetivo: Peso objetivo en kg
        
    Returns:
        Tupla (es_valido, lista_errores)
    """
    errores = []
    
    # Validar raza
    razas_validas = [r["nombre"] for r in RAZAS_POLLOS]
    if raza not in razas_validas:
        errores.append(f"Raza '{raza}' no reconocida. Razas válidas: {', '.join(razas_validas)}")
    
    # Validar edad
    if not isinstance(edad_dias, int) or edad_dias < 1 or edad_dias > 70:
        errores.append("La edad debe ser un número entero entre 1 y 70 días")
    
    # Validar pesos
    if not isinstance(peso_actual, (int, float)) or peso_actual <= 0:
        errores.append("El peso actual debe ser un número positivo")
    
    if not isinstance(peso_objetivo, (int, float)) or peso_objetivo <= peso_actual:
        errores.append("El peso objetivo debe ser mayor al peso actual")
    
    # Validar coherencia peso-edad
    if edad_dias > 0 and peso_actual > 0:
        from conocimiento.razas import obtener_peso_esperado
        peso_esperado = obtener_peso_esperado(raza, edad_dias)
        
        if peso_esperado and abs(peso_actual - peso_esperado) > peso_esperado * 0.5:
            errores.append(f"Peso actual ({peso_actual:.2f} kg) muy diferente al esperado ({peso_esperado:.2f} kg) para {raza} a los {edad_dias} días")
    
    return len(errores) == 0, errores

def validar_coherencia_entradas(parametros):
    """
    Valida la coherencia entre todas las entradas
    
    Args:
        parametros: Diccionario con todos los parámetros
        
    Raises:
        ValueError: Si hay inconsistencias graves
    """
    errores = []
    
    # Validar parámetros básicos
    es_valido, errores_produccion = validar_parametros_produccion(
        parametros["raza"],
        parametros["edad_dias"], 
        parametros["peso_actual"],
        parametros["peso_objetivo"]
    )
    
    errores.extend(errores_produccion)
    
    # Validar ingredientes disponibles
    ingredientes_disponibles = parametros.get("ingredientes_disponibles", [])
    if ingredientes_disponibles:
        for i in ingredientes_disponibles:
            if i < 0 or i >= len(INGREDIENTES):
                errores.append(f"Índice de ingrediente inválido: {i}")
    
    # Validar restricciones
    restricciones = parametros.get("restricciones_usuario")
    if restricciones:
        if ingredientes_disponibles:
            # Verificar que no se excluyan todos los ingredientes disponibles
            disponibles_set = set(ingredientes_disponibles)
            excluidos_set = set(restricciones.ingredientes_excluidos)
            
            if disponibles_set.issubset(excluidos_set):
                errores.append("No se pueden excluir todos los ingredientes disponibles")
    
    # Validar volúmenes de producción
    cantidad_pollos = parametros.get("cantidad_pollos", 0)
    if cantidad_pollos > 10000:
        # Verificar capacidad de planta para grandes volúmenes
        if restricciones and restricciones.capacidad_planta:
            consumo_estimado_diario = cantidad_pollos * 0.15  # Estimación rough: 150g/día por pollo
            if consumo_estimado_diario > restricciones.capacidad_planta:
                errores.append(f"Capacidad de planta insuficiente: necesita {consumo_estimado_diario:.0f} kg/día, disponible {restricciones.capacidad_planta:.0f} kg/día")
    
    if errores:
        print("\n❌ Errores de validación encontrados:")
        for error in errores:
            print(f"   • {error}")
        raise ValueError(f"Se encontraron {len(errores)} errores de validación")

def cargar_parametros_desde_archivo(archivo):
    """
    Carga parámetros desde un archivo JSON
    
    Args:
        archivo: Ruta al archivo JSON
        
    Returns:
        Diccionario con parámetros cargados
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            parametros = json.load(f)
        
        # Recrear objeto de restricciones si existe
        if "restricciones_usuario" in parametros and parametros["restricciones_usuario"]:
            restricciones_data = parametros["restricciones_usuario"]
            restricciones = RestriccionesUsuario()
            
            # Cargar datos del objeto
            for attr in ["ingredientes_excluidos", "limites_personalizados", "capacidad_planta", "presupuesto_maximo"]:
                if attr in restricciones_data:
                    setattr(restricciones, attr, restricciones_data[attr])
            
            parametros["restricciones_usuario"] = restricciones
        
        print(f"✅ Parámetros cargados desde: {archivo}")
        return parametros
        
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {archivo}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error cargando archivo: {e}")
        return None

def guardar_parametros_en_archivo(parametros, archivo):
    """
    Guarda parámetros en un archivo JSON
    
    Args:
        parametros: Diccionario con parámetros
        archivo: Ruta donde guardar el archivo
    """
    try:
        # Preparar datos para serialización
        parametros_serializables = parametros.copy()
        
        # Convertir objeto de restricciones a diccionario
        if "restricciones_usuario" in parametros and parametros["restricciones_usuario"]:
            restricciones = parametros["restricciones_usuario"]
            parametros_serializables["restricciones_usuario"] = {
                "ingredientes_excluidos": restricciones.ingredientes_excluidos,
                "limites_personalizados": restricciones.limites_personalizados,
                "capacidad_planta": restricciones.capacidad_planta,
                "presupuesto_maximo": restricciones.presupuesto_maximo
            }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(parametros_serializables, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Parámetros guardados en: {archivo}")
        
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")

def mostrar_resumen_parametros(parametros):
    """
    Muestra un resumen de todos los parámetros capturados
    
    Args:
        parametros: Diccionario con parámetros del usuario
    """
    print(f"\n📋 RESUMEN DE PARÁMETROS")
    print("=" * 50)
    
    # Parámetros de producción
    print(f"Raza: {parametros['raza']}")
    print(f"Edad actual: {parametros['edad_dias']} días")
    print(f"Peso actual: {parametros['peso_actual']:.2f} kg")
    print(f"Peso objetivo: {parametros['peso_objetivo']:.2f} kg")
    print(f"Cantidad de pollos: {parametros['cantidad_pollos']:,}")
    
    # Ingredientes disponibles
    ingredientes_disponibles = parametros.get("ingredientes_disponibles", [])
    if ingredientes_disponibles:
        print(f"\nIngredientes disponibles ({len(ingredientes_disponibles)}):")
        for i in ingredientes_disponibles:
            print(f"  • {INGREDIENTES[i]['nombre']}")
    else:
        print(f"\nIngredientes: Todos disponibles")
    
    # Restricciones
    restricciones = parametros.get("restricciones_usuario")
    if restricciones:
        print(f"\nRestricciones especiales:")
        if restricciones.ingredientes_excluidos:
            print(f"  • Ingredientes excluidos: {len(restricciones.ingredientes_excluidos)}")
        if restricciones.limites_personalizados:
            print(f"  • Límites personalizados: {len(restricciones.limites_personalizados)}")
        if restricciones.presupuesto_maximo:
            print(f"  • Presupuesto máximo: ${restricciones.presupuesto_maximo:.2f}/kg")
        if restricciones.capacidad_planta:
            print(f"  • Capacidad de planta: {restricciones.capacidad_planta:,.0f} kg/día")
    else:
        print(f"\nRestricciones: Configuración estándar")
    
    print("=" * 50)