from typing import Dict
# Importar el administrador de memoria virtual
from memoria import memoria

# Directorio de Funciones (DirFunc) - Estructura global
dir_func = {}

# Variable para rastrear el ámbito actual durante el análisis
ambito_actual = None

# Contador de errores semánticos
errores_semanticos = []

# TABLA DE CONSTANTES
# Diccionario: { valor_constante : direccion_memoria }
# ej: { 1: 8000, 3.14: 9000, "Hola": 10000 }
tabla_constantes = {}

# PILAS Y FILA PARA GENERACIÓN DE CUÁDRUPLOS 

# Pila de Operandos (PilaO)
# Guarda los operandos (IDs, constantes, temporales) ej: 'x', 5, 't1'
PilaO = []

# Pila de Tipos (PTypes)
# Guarda los tipos de los operandos, paralela a PilaO. ej: 'entero', 'flotante'
PTypes = []

# Pila de Operadores (POper)
# Guarda los operadores pendientes. ej: '+', '*', '('
POper = []

# PILA DE SALTOS (PJumps)
# Guarda los índices de los cuádruplos que tienen pendiente su destino de salto.
# Se usa para backpatching (rellenar) en estatutos de control (SI, MIENTRAS)
PJumps = []

# Fila/Lista de Cuádruplos (Quads)
# Lista de tuplas que representa el código intermedio
# ej: [('+', 'x', 5, 't1'), ('*', 't1', 2, 't2'), ('=', 't2', None, 'resultado')]
quads = []

# MANEJO DE TEMPORALES 
temp_counter = 1

# VARIABLES PARA FUNCIONES
# Contador de parámetros durante llamada a función
param_counter = 0
# Nombre de la función actual siendo llamada
current_function_call = None
# Tabla de parámetros de funciones: {nombre_func: [(tipo, nombre), ...]}
func_params = {}
# Saltos de retorno por función para backpatching de RETURN -> ENDFUNC
func_return_jumps: Dict[str, list] = {}


def inicializar_dirfunc(nombre_programa):
    global dir_func, ambito_actual
    dir_func = {
        'global': {
            'program_name': nombre_programa,
            'tipo_retorno': 'nula',
            'vars': {}
        }
    }
    ambito_actual = 'global'
    print(f"[DirFunc] Directorio inicializado para programa '{nombre_programa}'")


def agregar_variable(nombre_var, tipo_var, ambito=None):
    # PUNTO NEUROLOGICO: Agregar variable con validación de duplicados
    global dir_func, ambito_actual
    scope = ambito if ambito else ambito_actual
    
    if scope not in dir_func:
        reportar_error(f"El ámbito '{scope}' no existe en DirFunc")
        return False
    
    # VALIDACION: Variable doblemente declarada
    if nombre_var in dir_func[scope]['vars']:
        reportar_error(f"Variable '{nombre_var}' ya fue declarada en ámbito '{scope}'")
        return False
    
    # DETERMINAR SI ES GLOBAL O LOCAL
    tipo_memoria = 'global' if scope == 'global' else 'local'
    
    # SOLICITAR DIRECCION VIRTUAL
    direccion = memoria.get_direccion(tipo_memoria, tipo_var)
    
    # Guardar dirección junto con el tipo
    dir_func[scope]['vars'][nombre_var] = {
        'tipo': tipo_var,
        'direccion': direccion  # <--- NUEVO CAMPO
    }
    print(f"[DirFunc] Variable '{nombre_var}' de tipo '{tipo_var}' agregada a ámbito '{scope}' @ Dirección: {direccion}")
    return True


def buscar_variable(nombre_var, ambito=None):
    # Busca variable en ámbito actual y luego en global
    global dir_func, ambito_actual
    scope = ambito if ambito else ambito_actual
    
    # Primero buscar en el ámbito actual
    if scope in dir_func and nombre_var in dir_func[scope]['vars']:
        return dir_func[scope]['vars'][nombre_var]['tipo']
    
    # Si no está en el ámbito actual y no es global, buscar en global
    if scope != 'global' and nombre_var in dir_func['global']['vars']:
        return dir_func['global']['vars'][nombre_var]['tipo']
    
    return None


def agregar_funcion(nombre_func, tipo_retorno):
    # PUNTO NEUROLOGICO: Agregar función con validación de duplicados
    global dir_func, quads, func_params
    
    # VALIDACION: Función doblemente declarada
    if nombre_func in dir_func:
        reportar_error(f"Función '{nombre_func}' ya fue declarada")
        return False
    
    # IMPORTANTE: Al crear una nueva función, REINICIAMOS los contadores locales
    memoria.reset_contadores_locales()
    
    # Guardar la dirección inicial de la función (número de cuádruplo actual)
    dir_inicio = len(quads)
    
    dir_func[nombre_func] = {
        'tipo_retorno': tipo_retorno,
        'vars': {},
        'params': [],  # Lista de parámetros
        'num_params': 0,
        'num_vars_locales': 0,
        'num_temps': 0,
        'dir_inicio': dir_inicio  # Dirección donde inicia la función
    }
    
    # Inicializar tabla de parámetros para esta función
    func_params[nombre_func] = []
    func_return_jumps[nombre_func] = []
    
    print(f"[DirFunc] Función '{nombre_func}' agregada @ Cuádruplo: {dir_inicio}")
    return True


def agregar_parametro(nombre_func, nombre_param, tipo_param):
    """
    Agregar parámetro a una función durante su declaración
    """
    global dir_func, func_params, ambito_actual
    
    if nombre_func not in dir_func:
        reportar_error(f"Función '{nombre_func}' no existe")
        return False
    
    # Agregar como variable local
    direccion = memoria.get_direccion('local', tipo_param)
    
    dir_func[nombre_func]['vars'][nombre_param] = {
        'tipo': tipo_param,
        'direccion': direccion
    }
    
    # Agregar a lista de parámetros
    dir_func[nombre_func]['params'].append({
        'nombre': nombre_param,
        'tipo': tipo_param,
        'direccion': direccion
    })
    
    # Agregar a tabla de parámetros (para validación en llamadas)
    func_params[nombre_func].append((tipo_param, nombre_param))
    
    dir_func[nombre_func]['num_params'] += 1
    
    print(f"[DirFunc] Parámetro '{nombre_param}' ({tipo_param}) agregado a '{nombre_func}' @ Dir: {direccion}")
    return True


def finalizar_funcion(nombre_func):
    """
    Generar cuádruplo ENDFUNC al finalizar declaración de función
    """
    global quads, dir_func
    
    # Actualizar contadores en DirFunc
    if nombre_func in dir_func:
        # Contar variables locales (excluyendo parámetros)
        num_params = dir_func[nombre_func]['num_params']
        total_vars = len(dir_func[nombre_func]['vars'])
        dir_func[nombre_func]['num_vars_locales'] = total_vars - num_params
    
    # Generar cuádruplo ENDFUNC
    quads.append(('ENDFUNC', None, None, None))
    end_index = len(quads) - 1
    # Backpatch de RETURNs a ENDFUNC
    if nombre_func in func_return_jumps:
        for ret_idx in func_return_jumps[nombre_func]:
            rellenar(ret_idx, end_index)
        func_return_jumps[nombre_func] = []
    print(f"[Quad] ENDFUNC generado para '{nombre_func}'")


def iniciar_llamada_funcion(nombre_func, linea=None):
    """
    Iniciar proceso de llamada a función
    """
    global current_function_call, param_counter, quads, dir_func
    
    # Validar que la función existe
    if nombre_func not in dir_func:
        reportar_error(f"Función '{nombre_func}' no ha sido declarada", linea)
        return False
    
    current_function_call = nombre_func
    param_counter = 0
    
    # Generar cuádruplo ERA
    # El tamaño se calculará en tiempo de ejecución
    quads.append(('ERA', None, None, nombre_func))
    print(f"[Quad] ERA generado para llamada a '{nombre_func}'")
    return True


def agregar_argumento_llamada():
    """
    Agregar argumento durante llamada a función (genera PARAMETER)
    """
    global PilaO, PTypes, quads, param_counter, current_function_call, func_params
    
    if not current_function_call:
        reportar_error("No hay función actual en proceso de llamada")
        return
    
    if not PilaO or not PTypes:
        reportar_error("No hay argumento disponible en las pilas")
        return
    
    # Obtener argumento de las pilas
    arg_direccion = PilaO.pop()
    arg_tipo = PTypes.pop()
    
    # Validar tipo con parámetro esperado
    if current_function_call in func_params:
        params_esperados = func_params[current_function_call]
        
        if param_counter >= len(params_esperados):
            reportar_error(f"Demasiados argumentos para función '{current_function_call}'")
            return
        
        tipo_esperado, nombre_param = params_esperados[param_counter]
        
        if arg_tipo != tipo_esperado:
            reportar_error(f"Tipo de argumento incorrecto: se esperaba '{tipo_esperado}' pero se recibió '{arg_tipo}'")
    
    # Determinar dirección objetivo del parámetro en la función llamada
    direccion_dest = None
    if current_function_call in dir_func:
        params_list = dir_func[current_function_call].get('params', [])
        if param_counter < len(params_list):
            direccion_dest = params_list[param_counter].get('direccion')
    # Generar cuádruplo PARAMETER con dirección destino
    quads.append(('PARAMETER', arg_direccion, None, direccion_dest))
    print(f"[Quad] PARAMETER generado: arg={arg_direccion}, dest={direccion_dest}")
    
    param_counter += 1


def finalizar_llamada_funcion():
    """
    Finalizar llamada a función (genera GOSUB)
    """
    global quads, param_counter, current_function_call, dir_func, PilaO, PTypes, func_params
    
    if not current_function_call:
        reportar_error("No hay función actual en proceso de llamada")
        return None
    
    # Validar número de parámetros
    if current_function_call in func_params:
        num_params_esperados = len(func_params[current_function_call])
        if param_counter != num_params_esperados:
            reportar_error(f"Número incorrecto de argumentos: se esperaban {num_params_esperados} pero se recibieron {param_counter}")
    
    # Obtener dirección inicial de la función
    dir_inicio = dir_func[current_function_call].get('dir_inicio', 0)
    
    # Generar cuádruplo GOSUB
    quads.append(('GOSUB', current_function_call, None, dir_inicio))
    print(f"[Quad] GOSUB generado: '{current_function_call}' @ {dir_inicio}")
    
    # Si la función retorna algo, crear temporal para el resultado
    tipo_retorno = dir_func[current_function_call]['tipo_retorno']
    resultado = None
    
    if tipo_retorno != 'nula':
        resultado = get_next_temporal(tipo_retorno)
        # Asignar resultado de la función al temporal
        quads.append(('=', current_function_call, None, resultado))
        # Guardar en pilas para usar en expresiones
        PilaO.append(resultado)
        PTypes.append(tipo_retorno)
        print(f"[Quad] Asignación de retorno: {current_function_call} -> {resultado}")
    
    # Reset
    current_function_call = None
    param_counter = 0
    
    return resultado


def imprimir_dirfunc():
    print("\n" + "="*70)
    print("DIRECTORIO DE FUNCIONES (DirFunc)")
    print("="*70)
    
    for ambito, info in dir_func.items():
        print(f"\n[Ámbito: {ambito}]")
        if 'program_name' in info:
            print(f"  Nombre del programa: {info['program_name']}")
        if 'tipo_retorno' in info:
            print(f"  Tipo de retorno: {info['tipo_retorno']}")
        
        print(f"  Variables:")
        if info['vars']:
            for var_name, var_info in info['vars'].items():
                direccion = var_info.get('direccion', 'N/A')
                print(f"    - {var_name}: {var_info['tipo']:<10} @ Dir: {direccion}")
        else:
            print(f"    (ninguna)")
    
    print("\n" + "="*70 + "\n")


def reportar_error(mensaje, linea=None):
    if linea:
        error_msg = f"[ERROR SEMANTICO - Linea {linea}] {mensaje}"
    else:
        error_msg = f"[ERROR SEMANTICO] {mensaje}"
    print(error_msg)
    errores_semanticos.append(error_msg)


def validar_variable_declarada(nombre_var, linea=None):
    # PUNTO NEUROLOGICO: Validar que variable esté declarada
    tipo = buscar_variable(nombre_var)
    if tipo is None:
        reportar_error(f"Variable '{nombre_var}' no ha sido declarada", linea)
        return False
    return True


def validar_funcion_existe(nombre_func, linea=None):
    # PUNTO NEUROLOGICO: Validar que función exista antes de llamarla
    if nombre_func not in dir_func:
        reportar_error(f"Funcion '{nombre_func}' no ha sido declarada", linea)
        return False
    return True


def mostrar_resumen_errores():
    if errores_semanticos:
        print("\n" + "="*70)
        print("RESUMEN DE ERRORES SEMANTICOS")
        print("="*70)
        for i, error in enumerate(errores_semanticos, 1):
            print(f"{i}. {error}")
        print(f"\nTotal de errores: {len(errores_semanticos)}")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("[OK] NO SE ENCONTRARON ERRORES SEMANTICOS")
        print("="*70 + "\n")


def get_next_temporal(tipo_temp):
    """
    Genera una dirección temporal según el tipo resultante de la operación.
    
    Args:
        tipo_temp: 'entero', 'flotante', 'bool'
    
    Returns:
        int: Dirección de memoria virtual para el temporal
    """
    direccion = memoria.get_direccion('temporal', tipo_temp)
    print(f"[Temporal] Generado: Tipo={tipo_temp} @ Dir: {direccion}")
    return direccion


def rellenar(quad_index, destino):
    """
    Función FILL (Backpatching): Rellena el destino de un cuádruplo pendiente.
    Se usa para completar saltos (GOTOF, GOTO) en estatutos de control.
    
    Args:
        quad_index: Índice del cuádruplo a rellenar
        destino: Dirección/índice destino del salto
    """
    global quads
    # Como las tuplas son inmutables, convertimos a lista, editamos y reconvertimos
    temp_quad = list(quads[quad_index])
    temp_quad[3] = destino  # El índice 3 es el resultado/destino
    quads[quad_index] = tuple(temp_quad)
    print(f"[FILL] Cuádruplo {quad_index} rellenado con destino: {destino}")


def imprimir_cuadruplos():
    print("\n" + "="*70)
    print("CUADRUPLOS GENERADOS")
    print("="*70)
    
    if quads:
        print(f"\n{'#':<5} {'Operador':<10} {'Op1':<15} {'Op2':<15} {'Resultado':<15}")
        print("-" * 70)
        for i, quad in enumerate(quads):
            op, op1, op2, res = quad
            op1_str = str(op1) if op1 is not None else ''
            op2_str = str(op2) if op2 is not None else ''
            res_str = str(res) if res is not None else ''
            print(f"{i:<5} {op:<10} {op1_str:<15} {op2_str:<15} {res_str:<15}")
    else:
        print("  (no se generaron cuádruplos)")
    
    print("\n" + "="*70 + "\n")


def limpiar_errores():
    global errores_semanticos
    errores_semanticos.clear()


def limpiar_pilas_quads():
    # Limpia pilas, quads y reinicia contador de temporales
    global PilaO, PTypes, POper, quads, temp_counter, PJumps, param_counter, current_function_call
    PilaO.clear()
    PTypes.clear()
    POper.clear()
    PJumps.clear()  # <--- Limpiar también la pila de saltos
    quads.clear()
    temp_counter = 1
    param_counter = 0
    current_function_call = None


def get_direccion_variable(nombre_var, ambito=None):
    """
    Obtiene la dirección virtual de una variable.
    Busca primero en el ámbito actual, luego en global.
    
    Args:
        nombre_var: Nombre de la variable
        ambito: Ámbito donde buscar (opcional)
    
    Returns:
        int: Dirección virtual de la variable o None si no existe
    """
    global dir_func, ambito_actual
    scope = ambito if ambito else ambito_actual
    
    # Buscar en local
    if scope in dir_func and nombre_var in dir_func[scope]['vars']:
        return dir_func[scope]['vars'][nombre_var]['direccion']
    
    # Buscar en global
    if scope != 'global' and 'global' in dir_func and nombre_var in dir_func['global']['vars']:
        return dir_func['global']['vars'][nombre_var]['direccion']
    
    return None


def get_direccion_constante(valor, tipo):
    """
    Obtiene o asigna una dirección virtual para una constante.
    Si la constante ya existe, devuelve su dirección previa (ahorro de memoria).
    
    Args:
        valor: Valor de la constante (int, float, o string)
        tipo: 'entero', 'flotante', 'letrero'
    
    Returns:
        int: Dirección virtual de la constante
    """
    global tabla_constantes
    
    # Si la constante ya existe, devolvemos su dirección previa (ahorro de memoria)
    if valor in tabla_constantes:
        return tabla_constantes[valor]
    
    # Si no, pedimos nueva dirección
    direccion = memoria.get_direccion('constante', tipo)
    tabla_constantes[valor] = direccion
    print(f"[Constante] Nueva: Valor={valor} Tipo={tipo} @ Dir: {direccion}")
    return direccion


def imprimir_tabla_constantes():
    """
    Imprime la tabla de constantes con sus valores y direcciones.
    """
    print("\n" + "="*70)
    print("TABLA DE CONSTANTES")
    print("="*70)
    
    if tabla_constantes:
        print(f"\n{'Valor':<30} {'Dirección':<15}")
        print("-" * 70)
        for valor, direccion in sorted(tabla_constantes.items(), key=lambda x: x[1]):
            # Formatear el valor dependiendo de su tipo
            if isinstance(valor, str):
                valor_str = f'"{valor}"' if len(valor) <= 25 else f'"{valor[:25]}..."'
            else:
                valor_str = str(valor)
            print(f"{valor_str:<30} {direccion:<15}")
    else:
        print("  (no hay constantes)")
    
    print("\n" + "="*70 + "\n")


def limpiar_dirfunc():
    global dir_func, ambito_actual, tabla_constantes, func_params
    dir_func.clear()
    tabla_constantes.clear()
    func_params.clear()
    memoria.reset_contadores_globales()
    memoria.reset_contadores_locales()
    memoria.reset_contadores_constantes()
    ambito_actual = None


def limpiar_estado_global():
    # Limpia todo el estado global para nuevas pruebas
    limpiar_dirfunc()
    limpiar_errores()
    limpiar_pilas_quads()
