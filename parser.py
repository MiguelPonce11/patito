import ply.yacc as yacc
from scanner import tokens
from cubo_semantico import get_tipo_resultado, T_ENTERO, T_FLOTANTE, T_BOOL, T_ERROR
from directorio_funciones import (
    inicializar_dirfunc, agregar_variable, buscar_variable, agregar_funcion,
    imprimir_dirfunc, reportar_error, validar_variable_declarada,
    validar_funcion_existe, mostrar_resumen_errores,
    # Importar las pilas y funciones para generar cuádruplos
    PilaO, PTypes, POper, quads, get_next_temporal,
    # Importar funciones para direcciones virtuales
    get_direccion_variable, get_direccion_constante,
    # Importar para estatutos de control (saltos)
    PJumps, rellenar,
    # Importar para funciones
    agregar_parametro, finalizar_funcion, iniciar_llamada_funcion,
    agregar_argumento_llamada, finalizar_llamada_funcion
)

# Definición de la gramática
def p_programa(p):
    '''
    programa : PROGRAMA ID SEMICOLON np_programa_start vars_opc funcs_opc INICIO np_programa_label cuerpo FIN
    '''
    # PUNTO NEUROLOGICO 1: Inicializar el directorio al reconocer el programa
    from directorio_funciones import dir_func
    if not dir_func:
        inicializar_dirfunc(p[2])  # p[2] es el ID del programa
    print("Programa reconocido exitosamente!")
    # Generar cuádruplo END al finalizar el programa
    quads.append(('END', None, None, None))
    imprimir_dirfunc()  # Mostrar el contenido del directorio al final
    mostrar_resumen_errores()  # Mostrar errores encontrados

def p_np_programa_start(p):
    '''np_programa_start : empty'''
    # Generar un GOTO inicial para saltar la(s) funciones y brincar al INICIO
    # Guardamos su índice en PJumps para rellenarlo cuando encontremos INICIO
    quads.append(('GOTO', None, None, None))
    PJumps.append(len(quads) - 1)
    print(f"[NP_PROG_START] GOTO inicial generado en cuadruplo {len(quads) - 1}")

def p_np_programa_label(p):
    '''np_programa_label : empty'''
    # Al llegar a INICIO, rellenamos el GOTO inicial para que apunte aquí
    if PJumps:
        inicio_jump = PJumps.pop()
        rellenar(inicio_jump, len(quads))
        print(f"[NP_PROG_LABEL] INICIO del programa etiquetado en cuadruplo {len(quads)}")

def p_vars_opc(p):
    '''
    vars_opc : vars
             | empty
    '''
    print("Seccion de variables (opcional) reconocida.")

def p_funcs_opc(p):
    '''
    funcs_opc : funcs
              | empty
    '''
    print("Seccion de funciones (opcional) reconocida.")

def p_cuerpo(p):
    '''
    cuerpo : LBRACE estatutos_opc RBRACE
    '''
    print("Cuerpo del programa reconocido.")

def p_estatutos_opc(p):
    '''
    estatutos_opc : estatuto estatutos_opc
                  | empty
    '''
    print("Lista de estatutos (opcional) reconocida.")

def p_vars(p):
    '''
    vars : VARS vars_group
         | VARS vars_decl
    '''
    print("Bloque de declaracion de variables reconocido.")

def p_vars_group(p):
    '''
    vars_group : ID vars_coma COLON tipo SEMICOLON vars_final
    '''
    # p[1] es el primer ID, p[2] la lista de IDs extra, p[4] el tipo
    tipo = p[4]
    agregar_variable(p[1], tipo)
    ids_extra = p[2] if isinstance(p[2], list) else []
    for vid in ids_extra:
        agregar_variable(vid, tipo)
    print("Declaracion de variables (lista) reconocida.")

def p_vars_coma(p):
    '''
    vars_coma : empty
              | COMMA ID vars_coma
    '''
    if len(p) == 1:
        p[0] = []
    else:
        # Construir lista de IDs acumulados
        if len(p) < 3:
            p[0] = []
        else:
            resto = []
            if len(p) >= 4 and isinstance(p[3], list):
                resto = p[3]
            p[0] = [p[2]] + resto
    print("Lista de IDs con comas (opcional) reconocida.")

def p_vars_final(p):
    '''
    vars_final : empty
               | vars_group
    '''
    print("Continuacion de declaracion de variables (opcional).")

# Regla alternativa para soportar formato sencillo por línea:
def p_vars_decl(p):
    '''
    vars_decl : ID COLON tipo SEMICOLON vars_decl_cont
    '''
    tipo = p[3]
    agregar_variable(p[1], tipo)
    p[0] = type('obj', (object,), {'tipo_usado': tipo})()
    print("Declaracion de variable (simple) reconocida.")

def p_vars_decl_cont(p):
    '''
    vars_decl_cont : vars_decl
                   | empty
    '''
    print("Continuacion de declaracion de variables (simple).")

def p_tipo(p):
    '''
    tipo : ENTERO
         | FLOTANTE
    '''
    p[0] = p[1]  # Propagamos el tipo hacia arriba
    print(f"Tipo '{p[1]}' reconocido.")

def p_funcs(p):
    '''
    funcs : func_decl funcs
          | func_decl
    '''
    print("Declaracion de funcion reconocida.")

# Variable temporal global para pasar datos de funciones
current_func_type = None
current_func_name = None

def p_func_decl(p):
    '''
    func_decl : tipo_func ID np_func_save_data np_func_inicio LPAREN params RPAREN vars_opc cuerpo np_func_fin SEMICOLON
    '''
    print(f"Funcion '{p[2]}' reconocida.")

def p_np_func_save_data(p):
    '''np_func_save_data : empty'''
    # Guardar datos de la función en variables globales
    global current_func_type, current_func_name
    current_func_type = p[-2]  # tipo_func
    current_func_name = p[-1]  # ID

def p_np_func_inicio(p):
    '''np_func_inicio : empty'''
    # PUNTO NEUROLOGICO: Agregar función al directorio
    import directorio_funciones
    global current_func_type, current_func_name
    
    # Solo agregar si NO existe ya
    if current_func_name not in directorio_funciones.dir_func:
        agregar_funcion(current_func_name, current_func_type)
        # Cambiar ámbito actual
        directorio_funciones.ambito_actual = current_func_name

def p_np_func_fin(p):
    '''np_func_fin : empty'''
    # PUNTO NEUROLOGICO: Finalizar función
    import directorio_funciones
    
    finalizar_funcion(directorio_funciones.ambito_actual)
    # Regresar a ámbito global
    directorio_funciones.ambito_actual = 'global'

def p_tipo_func(p):
    '''
    tipo_func : tipo
              | NULA
    '''
    p[0] = p[1]  # Propagamos el tipo hacia arriba
    print(f"Tipo de retorno '{p[1]}' reconocido.")

def p_params(p):
    '''
    params : ID COLON tipo params_cont
           | empty
    '''
    # PUNTO NEUROLOGICO: Agregar parámetro a función actual
    if len(p) == 5:  # Hay parámetro
        import directorio_funciones
        nombre_param = p[1]
        tipo_param = p[3]
        agregar_parametro(directorio_funciones.ambito_actual, nombre_param, tipo_param)
    
    print("Parametros de funcion reconocidos.")

def p_params_cont(p):
    '''
    params_cont : COMMA params
                | empty
    '''
    print("Continuacion de parametros.")
    
def p_estatuto(p):
    '''
    estatuto : asignacion
             | condicion
             | ciclo
             | llamada SEMICOLON
             | imprime
             | LBRACKET estatutos_opc RBRACKET
             | retorno
    '''
    print("Estatuto reconocido.")

def p_asignacion(p):
    '''
    asignacion : ID ASSIGN expresion SEMICOLON
                | ID PLUS_ASSIGN expresion SEMICOLON
                | ID MINUS_ASSIGN expresion SEMICOLON
                | ID TIMES_ASSIGN expresion SEMICOLON
                | ID DIVIDE_ASSIGN expresion SEMICOLON
    '''
    # PUNTO NEUROLOGICO: Generar cuádruplo de asignación
    # Al final de la expresión, el resultado está en el tope de PilaO/PTypes
    
    if validar_variable_declarada(p[1], p.lineno(1)):
        tipo_variable = buscar_variable(p[1])
        direccion_variable = get_direccion_variable(p[1])  # Obtener dirección
        
        # Obtener el resultado de la expresión de las pilas
        if PilaO and PTypes:
            res_opnd = PilaO.pop()
            res_type = PTypes.pop()
            
            # Validar tipos con reglas de coerción
            if res_type != T_ERROR:
                # ¿Es asignación compuesta?
                op_token = p[2]
                if op_token == '=':
                    target_val = res_opnd
                else:
                    # Generar op compuesto: var = var op expr
                    op_map = {
                        '+=': '+',
                        '-=': '-',
                        '*=': '*',
                        '/=': '/',
                    }
                    # Determinar operador real por token type
                    tok_type = p.slice[2].type
                    real_op = {
                        'PLUS_ASSIGN': '+',
                        'MINUS_ASSIGN': '-',
                        'TIMES_ASSIGN': '*',
                        'DIVIDE_ASSIGN': '/',
                    }.get(tok_type, '+')
                    # Tipo resultante
                    res_t = get_tipo_resultado(tipo_variable, res_type, real_op)
                    if res_t == T_ERROR:
                        reportar_error(f"Error de tipos en asignacion compuesta: '{tipo_variable}' {real_op} '{res_type}'", p.lineno(1))
                    else:
                        tmp = get_next_temporal(res_t)
                        quads.append((real_op, direccion_variable, res_opnd, tmp))
                        target_val = tmp
                # Asignar al destino (con coerción implícita entero->flotante)
                if tipo_variable == res_type or (tipo_variable == T_FLOTANTE and res_type == T_ENTERO):
                    quads.append(('=', target_val, None, direccion_variable))
                else:
                    reportar_error(f"Error de tipos en asignacion: variable '{p[1]}' es '{tipo_variable}' pero se intenta asignar '{res_type}'", p.lineno(1))
        
    print(f"Asignacion a variable '{p[1]}' reconocida.")
    
def p_condicion(p):
    '''
    condicion : SI LPAREN expresion RPAREN np_if_1 cuerpo np_if_2 sino_opc np_if_3 SEMICOLON
    '''
    print("Condicion SI reconocida.")

def p_sino_opc(p):
    '''
    sino_opc : SINO cuerpo
             | SINO_SI LPAREN expresion RPAREN np_if_1 cuerpo np_if_2 sino_opc np_if_3
             | empty
    '''
    print("Bloque SINO (opcional) reconocido.")

# --- PUNTOS NEUROLOGICOS PARA IF (SI) ---

def p_np_if_1(p):
    '''np_if_1 : empty'''
    # PUNTO NEUROLOGICO 1: Después de evaluar expresión, generar GOTOF
    global PilaO, PTypes, quads, PJumps
    
    if PTypes:
        exp_type = PTypes.pop()
        
        if exp_type != T_BOOL:
            reportar_error("Type-mismatch: La expresión del SI debe ser booleana", p.lineno(0) if hasattr(p, 'lineno') else None)
            # Aún así generamos el cuadruplo para continuar
        
        if PilaO:
            result = PilaO.pop()
            # Generar GOTOF con destino pendiente (None)
            quads.append(('GOTOF', result, None, None))
            PJumps.append(len(quads) - 1)  # Guardar índice del GOTOF para rellenarlo después
            print(f"[NP_IF_1] GOTOF generado en cuadruplo {len(quads) - 1}")

def p_np_if_2(p):
    '''np_if_2 : empty'''
    # PUNTO NEUROLOGICO 2: Fin del bloque TRUE, generar GOTO y rellenar GOTOF
    global quads, PJumps
    
    # Generar GOTO incondicional (para saltar el bloque ELSE)
    quads.append(('GOTO', None, None, None))
    
    # Sacar el índice del GOTOF que está pendiente
    falso = PJumps.pop()
    
    # Meter el índice del GOTO para rellenarlo después
    PJumps.append(len(quads) - 1)
    
    # Rellenar el GOTOF con la dirección actual (inicio del ELSE o fin si no hay ELSE)
    rellenar(falso, len(quads))
    print(f"[NP_IF_2] GOTO generado en cuadruplo {len(quads) - 1}")

def p_np_if_3(p):
    '''np_if_3 : empty'''
    # PUNTO NEUROLOGICO 3: Fin del estatuto SI completo, rellenar el GOTO
    global PJumps, quads
    
    if PJumps:
        end = PJumps.pop()
        rellenar(end, len(quads))
        print(f"[NP_IF_3] Fin del SI, cuadruplo {end} rellenado")

def p_ciclo(p):
    '''
    ciclo : MIENTRAS np_while_1 LPAREN expresion RPAREN np_while_2 HAZ cuerpo np_while_3 SEMICOLON
    '''
    print("Ciclo MIENTRAS reconocido.")

# --- PUNTOS NEUROLOGICOS PARA WHILE (MIENTRAS) ---

def p_np_while_1(p):
    '''np_while_1 : empty'''
    # PUNTO NEUROLOGICO 1: Marcar el inicio del ciclo para poder regresar
    global PJumps, quads
    PJumps.append(len(quads))  # Guardar la dirección actual (inicio de la evaluación)
    print(f"[NP_WHILE_1] Inicio de ciclo marcado en cuadruplo {len(quads)}")

def p_np_while_2(p):
    '''np_while_2 : empty'''
    # PUNTO NEUROLOGICO 2: Evaluar expresión y generar GOTOF (salida del ciclo)
    global PilaO, PTypes, quads, PJumps
    
    if PTypes:
        exp_type = PTypes.pop()
        
        if exp_type != T_BOOL:
            reportar_error("Type-mismatch: La expresión del MIENTRAS debe ser booleana", p.lineno(0) if hasattr(p, 'lineno') else None)
        
        if PilaO:
            result = PilaO.pop()
            # Generar GOTOF con destino pendiente (salida del ciclo)
            quads.append(('GOTOF', result, None, None))
            PJumps.append(len(quads) - 1)  # Guardar índice del GOTOF
            print(f"[NP_WHILE_2] GOTOF generado en cuadruplo {len(quads) - 1}")

def p_np_while_3(p):
    '''np_while_3 : empty'''
    # PUNTO NEUROLOGICO 3: Fin del cuerpo del ciclo. Generar GOTO al inicio y rellenar salida
    global PJumps, quads
    
    if len(PJumps) >= 2:
        end = PJumps.pop()      # Índice del GOTOF (salida)
        retorno = PJumps.pop()  # Índice del inicio del ciclo
        
        # Generar GOTO para regresar al inicio del ciclo
        quads.append(('GOTO', None, None, retorno))
        print(f"[NP_WHILE_3] GOTO generado en cuadruplo {len(quads) - 1} hacia {retorno}")
        
        # Rellenar el GOTOF con la dirección actual (fin del ciclo)
        rellenar(end, len(quads))

def p_imprime(p):
    '''
    imprime : ESCRIBE LPAREN imprime_args RPAREN SEMICOLON
    '''
    # Esta regla principal solo define la gramática.
    # Las acciones semánticas (NPs) están en 'imprime_args'.
    print("Estatuto ESCRIBE reconocido.")

def p_imprime_args(p):
    '''
    imprime_args : expresion np_gen_print_quad imprime_args_cont
                 | LETRERO np_gen_print_quad_letrero imprime_args_cont
    '''
    # NP se ejecuta después de procesar 'expresion' o 'LETRERO'.
    print("Argumento de escritura reconocido.")
    
def p_imprime_args_cont(p):
    '''
    imprime_args_cont : COMMA imprime_args
                      | empty
    '''
    # Maneja argumentos múltiples (ej. escribe(a, b, c))
    print("Continuacion de argumentos de escritura.")

# --- PUNTO NEUROLOGICO para IMPRIME (expresión) ---
def p_np_gen_print_quad(p):
    '''np_gen_print_quad : empty'''
    # Se activa después de una 'expresion' en 'escribe'.
    # El resultado de la expresión está en el tope de las pilas.
    if PilaO:
        res_opnd = PilaO.pop()
        if PTypes:
            PTypes.pop()  # Siempre sacar de ambas pilas
        
        # Generar el cuádruplo de impresión
        quads.append(('IMPRIME', None, None, res_opnd))
        print(f"[Quad] Generado: ('IMPRIME', None, None, {res_opnd})")

# --- PUNTO NEUROLOGICO para IMPRIME (letrero/string) ---
def p_np_gen_print_quad_letrero(p):
    '''np_gen_print_quad_letrero : empty'''
    # Se activa después de un 'LETRERO' en 'escribe'.
    # p[-1] es el token LETRERO (el string) que acabamos de leer.
    res_letrero = p[-1]
    
    # CAMBIO: Obtener dirección constante para el string
    direccion_letrero = get_direccion_constante(res_letrero, 'letrero')
    
    # Generar el cuádruplo de impresión con dirección
    quads.append(('IMPRIME', None, None, direccion_letrero))
    print(f"[Quad] Generado: ('IMPRIME', None, None, {direccion_letrero}) [String: '{res_letrero}']")

def p_expresion(p):
    '''
    expresion : exp comp_opc
    '''
    # PUNTO NEUROLOGICO: Generar cuádruplo de comparación si hay operador
    if p[2] is not None:  # Hay operador de comparación
        operador = p[2]
        if POper and POper[-1] == operador:
            POper.pop()
            
            # Pop operandos y tipos
            if len(PilaO) >= 2 and len(PTypes) >= 2:
                right_opnd = PilaO.pop()
                right_type = PTypes.pop()
                left_opnd = PilaO.pop()
                left_type = PTypes.pop()
                
                # Validar tipos
                tipo_resultado = get_tipo_resultado(left_type, right_type, operador)
                if tipo_resultado == T_ERROR:
                    reportar_error(f"Error de tipos: no se puede comparar '{left_type}' {operador} '{right_type}'")
                    PilaO.append(None)
                    PTypes.append(T_ERROR)
                else:
                    # Generar cuádruplo de comparación (resultado siempre es bool)
                    result_temp = get_next_temporal(T_BOOL)  # <--- PASAR TIPO
                    quads.append((operador, left_opnd, right_opnd, result_temp))
                    
                    # Push resultado
                    PilaO.append(result_temp)
                    PTypes.append(tipo_resultado)
    
    print(f"Expresion relacional reconocida.")

def p_comp_opc(p):
    '''
    comp_opc : GT exp
             | LT exp
             | NE exp
             | EQ exp
             | LE exp
             | GE exp
             | empty
    '''
    # PUNTO NEUROLOGICO: Push operador de comparación
    if len(p) == 3:  # Hay comparación
        operador = p[1]  # '>', '<', '!=', '=='
        POper.append(operador)
        p[0] = operador
    else:
        p[0] = None
    print(f"Operador de comparacion (opcional) reconocido.")

def p_exp(p):
    '''
    exp : termino op_exp
    '''
    print(f"Expresion aritmetica reconocida.")

def p_op_exp(p):
    '''
    op_exp : PLUS np_push_oper termino np_gen_sum_sub op_exp
        | MINUS np_push_oper termino np_gen_sum_sub op_exp
        | empty
    '''
    print(f"Operador de suma/resta (opcional) reconocido.")

def p_np_gen_sum_sub(p):
    '''np_gen_sum_sub : empty'''
    if POper and POper[-1] in ('+', '-'):
        op = POper.pop()
        if len(PilaO) >= 2 and len(PTypes) >= 2:
            right_opnd = PilaO.pop()
            right_type = PTypes.pop()
            left_opnd = PilaO.pop()
            left_type = PTypes.pop()
            res_type = get_tipo_resultado(left_type, right_type, op)
            if res_type != T_ERROR:
                result_temp = get_next_temporal(res_type)
                quads.append((op, left_opnd, right_opnd, result_temp))
                PilaO.append(result_temp)
                PTypes.append(res_type)
            else:
                reportar_error(f"Error de tipos: no se puede realizar '{left_type}' {op} '{right_type}'")
                PilaO.append(None)
                PTypes.append(T_ERROR)

def p_np_push_oper(p):
    '''np_push_oper : empty'''
    # PUNTO NEUROLOGICO: Push operador a la pila
    # p[-1] es el operador que acabamos de leer
    if p[-1] in ('+', '-', '*', '/', '%'):
        POper.append(p[-1])

def p_termino(p):
    '''
    termino : factor op_termino
    '''
    print(f"Termino reconocido.")

def p_op_termino(p):
    '''
    op_termino : TIMES np_push_oper termino np_gen_mult_div
               | DIVIDE np_push_oper termino np_gen_mult_div
               | MOD np_push_oper termino np_gen_mult_div
               | empty
    '''
    print(f"Operador de multiplicacion/division (opcional) reconocido.")

def p_np_gen_mult_div(p):
    '''np_gen_mult_div : empty'''
    if POper and POper[-1] in ('*', '/', '%'):
        op = POper.pop()
        if len(PilaO) >= 2 and len(PTypes) >= 2:
            right_opnd = PilaO.pop()
            right_type = PTypes.pop()
            left_opnd = PilaO.pop()
            left_type = PTypes.pop()
            res_type = get_tipo_resultado(left_type, right_type, op)
            if res_type != T_ERROR:
                result_temp = get_next_temporal(res_type)
                quads.append((op, left_opnd, right_opnd, result_temp))
                PilaO.append(result_temp)
                PTypes.append(res_type)
            else:
                reportar_error(f"Error de tipos: no se puede realizar '{left_type}' {op} '{right_type}'")
                PilaO.append(None)
                PTypes.append(T_ERROR)

def p_factor(p):
    '''
    factor : np_push_fondo_falso LPAREN expresion RPAREN np_pop_fondo_falso
        | sign_opc factor_val np_apply_unary
        | MINUS factor_val np_unary_neg
        | PLUS factor_val np_unary_pos
    '''
    # Ya no se propaga tipo
    print(f"Factor reconocido.")

def p_np_push_fondo_falso(p):
    '''np_push_fondo_falso : empty'''
    # PUNTO NEUROLOGICO: Push fondo falso para paréntesis
    POper.append('(')

def p_np_pop_fondo_falso(p):
    '''np_pop_fondo_falso : empty'''
    # PUNTO NEUROLOGICO: Pop fondo falso al cerrar paréntesis
    if POper and POper[-1] == '(':
        POper.pop()

def p_sign_opc(p):
    '''
    sign_opc : PLUS
             | MINUS
             | empty
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None
    print("Signo (opcional) reconocido.")

def p_np_apply_unary(p):
    '''np_apply_unary : empty'''
    # Si hubo signo '-', aplicar negación al último operando
    # p[-3] es el signo capturado por sign_opc
    sign = p[-3]
    if sign == '-':
        if PilaO and PTypes:
            val = PilaO.pop()
            t = PTypes.pop()
            # Determinar constante cero según tipo
            if t == T_ENTERO:
                zero = get_direccion_constante(0, 'entero')
            elif t == T_FLOTANTE:
                zero = get_direccion_constante(0.0, 'flotante')
            else:
                reportar_error("No se puede aplicar '-' unario a tipo no numérico")
                PilaO.append(None)
                PTypes.append(T_ERROR)
                return
            tmp_t = get_tipo_resultado(t, t, '-')  # result type equals operand for unary minus
            if tmp_t == T_ERROR:
                reportar_error("Error de tipos en '-' unario")
                PilaO.append(None)
                PTypes.append(T_ERROR)
                return
            tmp = get_next_temporal(t)
            quads.append(('-', zero, val, tmp))
            PilaO.append(tmp)
            PTypes.append(t)

def p_np_unary_neg(p):
    '''np_unary_neg : empty'''
    if PilaO and PTypes:
        val = PilaO.pop()
        t = PTypes.pop()
        if t == T_ENTERO:
            zero = get_direccion_constante(0, 'entero')
        elif t == T_FLOTANTE:
            zero = get_direccion_constante(0.0, 'flotante')
        else:
            reportar_error("No se puede aplicar '-' unario a tipo no numérico")
            PilaO.append(None)
            PTypes.append(T_ERROR)
            return
        tmp = get_next_temporal(t)
        quads.append(('-', zero, val, tmp))
        PilaO.append(tmp)
        PTypes.append(t)

def p_np_unary_pos(p):
    '''np_unary_pos : empty'''
    # '+' unario no cambia el valor; no-op
    pass

def p_factor_val(p):
    '''
    factor_val : ID
               | CTE_ENT
               | CTE_FLOT
               | llamada
    '''
    # PUNTO NEUROLOGICO: Push operando y tipo a las pilas (AHORA CON DIRECCIONES VIRTUALES)
    if p.slice[1].type == 'ID':
        if validar_variable_declarada(p[1], p.lineno(1)):
            tipo = buscar_variable(p[1])
            # CAMBIO: Obtener la dirección virtual de la variable
            direccion = get_direccion_variable(p[1])
            
            # Push Dirección (no nombre)
            PilaO.append(direccion)
            PTypes.append(tipo)
        else:
            # Push error
            PilaO.append(None)
            PTypes.append(T_ERROR)
            
    elif p.slice[1].type == 'CTE_ENT':
        # CAMBIO: Obtener dirección constante entera
        direccion = get_direccion_constante(p[1], 'entero')
        
        # Push Dirección de constante (ej. 8000)
        PilaO.append(direccion)
        PTypes.append(T_ENTERO)
        
    elif p.slice[1].type == 'CTE_FLOT':
        # CAMBIO: Obtener dirección constante flotante
        direccion = get_direccion_constante(p[1], 'flotante')
        
        # Push Dirección de constante (ej. 9000)
        PilaO.append(direccion)
        PTypes.append(T_FLOTANTE)
    else:  # llamada a función
        # La regla 'llamada' (np_llamada_fin) ya empuja a las pilas
        # el temporal con el valor y su tipo de retorno.
        # No empujar nada aquí para evitar insertar None/Tipo incorrecto.
        pass
    
    print(f"Valor de factor '{p[1]}' reconocido.")
    
def p_llamada(p):
    '''
    llamada : ID np_llamada_inicio LPAREN llamada_args RPAREN np_llamada_fin
    '''
    print(f"Llamada a funcion '{p[1]}' reconocida.")

def p_np_llamada_inicio(p):
    '''np_llamada_inicio : empty'''
    # PUNTO NEUROLOGICO: Iniciar llamada a función (genera ERA)
    nombre_func = p[-1]
    iniciar_llamada_funcion(nombre_func, p.lineno(0) if hasattr(p, 'lineno') else None)

def p_np_llamada_fin(p):
    '''np_llamada_fin : empty'''
    # PUNTO NEUROLOGICO: Finalizar llamada a función (genera GOSUB)
    finalizar_llamada_funcion()
    
def p_llamada_args(p):
    '''
    llamada_args : expresion np_agregar_arg llamada_args_cont
                 | empty
    '''
    print("Argumentos de llamada reconocidos.")

def p_np_agregar_arg(p):
    '''np_agregar_arg : empty'''
    # PUNTO NEUROLOGICO: Agregar argumento (genera PARAMETER)
    agregar_argumento_llamada()

def p_llamada_args_cont(p):
    '''
    llamada_args_cont : COMMA llamada_args
                      | empty
    '''
    print("Continuacion de argumentos de llamada.")

def p_retorno(p):
    '''
    retorno : RETURN expresion SEMICOLON
    '''
    # Generar cuadruplo RETURN explícito con backpatch a ENDFUNC
    import directorio_funciones
    nombre_func = directorio_funciones.ambito_actual
    if PilaO and PTypes:
        valor = PilaO.pop()
        PTypes.pop()
        # RETURN: op1=valor, op2=nombre_func, res=destino (a rellenar con ENDFUNC)
        quads.append(('RETURN', valor, nombre_func, None))
        # Registrar el índice de este RETURN para backpatch al ENDFUNC
        directorio_funciones.func_return_jumps.setdefault(nombre_func, []).append(len(quads) - 1)
        print(f"[Quad] RETURN generado: valor={valor}, func={nombre_func}")
    else:
        reportar_error("RETURN sin valor evaluado")

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Error de sintaxis en el token '{p.value}' (tipo: {p.type}) en la linea {p.lineno}")
    else:
        print("Error de sintaxis al final del archivo.")

# Construir el parser
parser = yacc.yacc()
