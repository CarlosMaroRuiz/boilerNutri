"""
Punto de entrada principal del sistema de optimización de alimentos para pollos.

Este módulo coordina todo el proceso de optimización:
- Recibe parámetros del usuario
- Carga la base de conocimiento
- Ejecuta el algoritmo genético
- Genera reportes de resultados
"""

import sys
import traceback
from datetime import datetime
import argparse

# Importaciones del sistema
from config import (
    SISTEMA_INFO, 
    ALGORITMO_CONFIG, 
    mostrar_informacion_sistema,
    inicializar_directorios,
    validar_configuracion
)

from conocimiento import (
    INGREDIENTES, 
    REQUERIMIENTOS_NUTRICIONALES,
    RAZAS_POLLOS,
    PROVEEDORES,
    validar_consistencia_datos
)

from genetic import AlgoritmoGenetico, Individuo
from genetic.fitness import calcular_fitness_adaptativo

from utils import (
    procesar_entradas,
    validar_parametros_produccion,
    mostrar_resumen_parametros,
    generar_reporte_sistema_completo,
    cargar_parametros_desde_archivo,
    guardar_parametros_en_archivo
)

def main():
    """
    Función principal del sistema
    """
    try:
        # Mostrar información del sistema
        mostrar_informacion_sistema()
        
        # Validar configuración del sistema
        if not validar_sistema():
            return 1
        
        # Procesar argumentos de línea de comandos
        args = procesar_argumentos()
        
        # Obtener parámetros del usuario
        parametros_usuario = obtener_parametros_usuario(args)
        if not parametros_usuario:
            print("❌ No se pudieron obtener los parámetros del usuario")
            return 1
        
        # Mostrar resumen de parámetros
        mostrar_resumen_parametros(parametros_usuario)
        
        # Confirmar ejecución
        if not args.auto_confirmar and not confirmar_ejecucion():
            print("🚫 Ejecución cancelada por el usuario")
            return 0
        
        # Ejecutar optimización
        resultados = ejecutar_optimizacion(parametros_usuario)
        if not resultados or "error" in resultados:
            print(f"❌ Error en la optimización: {resultados.get('error', 'Error desconocido')}")
            return 1
        
        # Generar reportes
        generar_reportes_finales(resultados, parametros_usuario, args)
        
        print(f"\n🎉 ¡Optimización completada exitosamente!")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Proceso interrumpido por el usuario")
        return 130
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        if "--debug" in sys.argv:
            print(f"\nTraceback completo:")
            traceback.print_exc()
        return 1

def procesar_argumentos():
    """
    Procesa argumentos de línea de comandos
    
    Returns:
        Objeto args con argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description=f"{SISTEMA_INFO['nombre']} - {SISTEMA_INFO['descripcion']}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Ejemplos de uso:
  python {sys.argv[0]}                          # Modo interactivo
  python {sys.argv[0]} --config params.json    # Cargar parámetros desde archivo
  python {sys.argv[0]} --auto-confirmar        # Ejecutar sin confirmación
  python {sys.argv[0]} --solo-reportes         # Solo generar reportes
        """
    )
    
    parser.add_argument("--version", action="version", 
                       version=f"{SISTEMA_INFO['nombre']} v{SISTEMA_INFO['version']}")
    
    parser.add_argument("--config", metavar="ARCHIVO",
                       help="Cargar parámetros desde archivo JSON")
    
    parser.add_argument("--auto-confirmar", action="store_true",
                       help="Ejecutar sin solicitar confirmación")
    
    parser.add_argument("--solo-reportes", action="store_true",
                       help="Solo generar reportes (requiere --config)")
    
    parser.add_argument("--sin-graficas", action="store_true",
                       help="No generar gráficas en los reportes")
    
    parser.add_argument("--debug", action="store_true",
                       help="Mostrar información de depuración")
    
    parser.add_argument("--guardar-config", metavar="ARCHIVO",
                       help="Guardar parámetros capturados en archivo JSON")
    
    parser.add_argument("--tamaño-problema", choices=["pequeño", "mediano", "grande"],
                       help="Ajustar configuración según tamaño del problema")
    
    return parser.parse_args()

def validar_sistema():
    """
    Valida que el sistema esté correctamente configurado
    
    Returns:
        True si el sistema es válido
    """
    print("🔍 Validando configuración del sistema...")
    
    # Validar configuración
    config_valida, errores_config = validar_configuracion()
    if not config_valida:
        print("❌ Errores en configuración:")
        for error in errores_config:
            print(f"   • {error}")
        return False
    
    # Validar base de conocimiento
    datos_validos, errores_datos = validar_consistencia_datos()
    if not datos_validos:
        print("❌ Errores en base de conocimiento:")
        for error in errores_datos:
            print(f"   • {error}")
        return False
    
    # Crear directorios necesarios
    inicializar_directorios()
    
    print("✅ Sistema validado correctamente")
    return True

def obtener_parametros_usuario(args):
    """
    Obtiene parámetros del usuario según los argumentos
    
    Args:
        args: Argumentos de línea de comandos
        
    Returns:
        Diccionario con parámetros del usuario
    """
    if args.config:
        # Cargar desde archivo
        print(f"📂 Cargando parámetros desde: {args.config}")
        parametros = cargar_parametros_desde_archivo(args.config)
        
        if parametros is None:
            return None
        
        # Validar parámetros cargados
        try:
            validar_parametros_produccion(
                parametros["raza"],
                parametros["edad_dias"],
                parametros["peso_actual"],
                parametros["peso_objetivo"]
            )
        except KeyError as e:
            print(f"❌ Parámetro faltante en archivo: {e}")
            return None
        except Exception as e:
            print(f"❌ Error validando parámetros: {e}")
            return None
        
        return parametros
    
    else:
        # Modo interactivo
        print("🎯 Iniciando captura interactiva de parámetros...")
        parametros = procesar_entradas()
        
        # Guardar parámetros si se solicita
        if parametros and args.guardar_config:
            guardar_parametros_en_archivo(parametros, args.guardar_config)
        
        return parametros

def confirmar_ejecucion():
    """
    Solicita confirmación al usuario para ejecutar la optimización
    
    Returns:
        True si el usuario confirma
    """
    print(f"\n❓ ¿Desea ejecutar la optimización con estos parámetros?")
    respuesta = input("Escriba 'si' para continuar o cualquier otra cosa para cancelar: ").strip().lower()
    return respuesta in ['si', 'sí', 's', 'yes', 'y']

def ejecutar_optimizacion(parametros_usuario):
    """
    Ejecuta el algoritmo de optimización
    
    Args:
        parametros_usuario: Parámetros del usuario
        
    Returns:
        Resultados del algoritmo genético
    """
    print(f"\n🚀 Iniciando optimización...")
    print("=" * 60)
    
    try:
        # Preparar configuración del algoritmo
        config_algoritmo = preparar_configuracion_algoritmo(parametros_usuario)
        
        # Crear y ejecutar algoritmo genético
        algoritmo = AlgoritmoGenetico(config_algoritmo)
        resultados = algoritmo.ejecutar()
        
        return resultados
        
    except Exception as e:
        print(f"❌ Error durante la optimización: {e}")
        return {"error": str(e)}

def preparar_configuracion_algoritmo(parametros_usuario):
    """
    Prepara la configuración para el algoritmo genético
    
    Args:
        parametros_usuario: Parámetros del usuario
        
    Returns:
        Diccionario con configuración del algoritmo
    """
    config = ALGORITMO_CONFIG.copy()
    
    # Configuración de evaluación
    config["config_evaluacion"] = {
        "raza": parametros_usuario["raza"],
        "edad_dias": parametros_usuario["edad_dias"],
        "peso_actual": parametros_usuario["peso_actual"],
        "peso_objetivo": parametros_usuario["peso_objetivo"],
        "cantidad_pollos": parametros_usuario["cantidad_pollos"]
    }
    
    # Datos del problema
    config["ingredientes_data"] = INGREDIENTES
    config["restricciones_usuario"] = parametros_usuario.get("restricciones_usuario")
    
    # Filtrar ingredientes disponibles si se especificaron
    ingredientes_disponibles = parametros_usuario.get("ingredientes_disponibles")
    if ingredientes_disponibles:
        # Aplicar filtro a las restricciones del usuario
        if not config["restricciones_usuario"]:
            from conocimiento.restricciones_usuario import RestriccionesUsuario
            config["restricciones_usuario"] = RestriccionesUsuario()
        
        # Establecer ingredientes disponibles
        config["restricciones_usuario"].ingredientes_disponibles = ingredientes_disponibles
    
    return config

def generar_reportes_finales(resultados, parametros_usuario, args):
    """
    Genera todos los reportes finales del sistema
    
    Args:
        resultados: Resultados del algoritmo genético
        parametros_usuario: Parámetros del usuario
        args: Argumentos de línea de comandos
    """
    print(f"\n📊 Generando reportes finales...")
    
    try:
        # Preparar configuración de evaluación
        config_evaluacion = {
            "raza": parametros_usuario["raza"],
            "edad_dias": parametros_usuario["edad_dias"],
            "peso_actual": parametros_usuario["peso_actual"],
            "peso_objetivo": parametros_usuario["peso_objetivo"],
            "cantidad_pollos": parametros_usuario["cantidad_pollos"]
        }
        
        # Generar reporte completo
        incluir_graficas = not args.sin_graficas
        reporte_completo = generar_reporte_sistema_completo(
            resultados,
            INGREDIENTES,
            config_evaluacion,
            parametros_usuario.get("restricciones_usuario"),
            incluir_graficas=incluir_graficas,
            exportar_archivos=True
        )
        
        if "error" in reporte_completo:
            print(f"⚠️  Error generando reportes: {reporte_completo['error']}")
        else:
            print(f"✅ Reportes generados exitosamente")
            if reporte_completo.get("archivos_generados"):
                print(f"📁 Archivos creados:")
                for archivo in reporte_completo["archivos_generados"]:
                    print(f"   • {archivo}")
        
        # Mostrar resumen de las mejores soluciones
        mostrar_resumen_soluciones(resultados)
        
    except Exception as e:
        print(f"❌ Error generando reportes: {e}")

def mostrar_resumen_soluciones(resultados):
    """
    Muestra un resumen de las mejores soluciones encontradas
    
    Args:
        resultados: Resultados del algoritmo genético
    """
    mejores_individuos = resultados.get("mejores_individuos", [])
    
    if not mejores_individuos:
        print("⚠️  No se encontraron soluciones válidas")
        return
    
    print(f"\n🏆 RESUMEN DE MEJORES SOLUCIONES")
    print("=" * 50)
    
    for i, individuo in enumerate(mejores_individuos[:3]):
        print(f"\n🥇 Solución #{i+1}:")
        print(f"   💰 Costo: ${individuo.costo_total:.3f}/kg")
        print(f"   📊 Fitness: {individuo.fitness:.4f}")
        
        if hasattr(individuo, 'conversion_alimenticia'):
            print(f"   ⚡ Conversión alimenticia: {individuo.conversion_alimenticia:.2f}")
        
        if hasattr(individuo, 'dias_peso_objetivo'):
            print(f"   ⏱️  Días hasta peso objetivo: {individuo.dias_peso_objetivo:.0f}")
        
        # Mostrar ingredientes principales
        ingredientes_principales = []
        for j, porcentaje in enumerate(individuo.porcentajes):
            if porcentaje > 0.05 and j < len(INGREDIENTES):  # Más del 5%
                ingredientes_principales.append((INGREDIENTES[j]["nombre"], porcentaje * 100))
        
        if ingredientes_principales:
            print(f"   🥜 Ingredientes principales:")
            for nombre, porcentaje in sorted(ingredientes_principales, key=lambda x: x[1], reverse=True)[:3]:
                print(f"      • {nombre}: {porcentaje:.1f}%")
    
    print("=" * 50)

def mostrar_ayuda_usuario():
    """
    Muestra ayuda adicional al usuario
    """
    print(f"""
📖 AYUDA ADICIONAL

Archivos de configuración:
  Los parámetros se pueden guardar en archivos JSON para reutilización.
  Use --config para cargar y --guardar-config para guardar.

Interpretación de resultados:
  • Fitness: Menor es mejor (representa calidad global)
  • Costo: Precio por kilogramo de alimento
  • Conversión alimenticia: kg alimento / kg ganancia (menor es mejor)
  
Archivos generados:
  • reporte_optimizacion.txt: Reporte legible
  • reporte_optimizacion.json: Datos estructurados
  • graficas/: Visualizaciones del proceso y resultados

Para más información, consulte la documentación del sistema.
    """)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        sys.exit(1)