# Constantes para los tipos
T_ENTERO = 'entero'
T_FLOTANTE = 'flotante'
T_BOOL = 'bool'
T_ERROR = 'error'

# El cubo semántico se implementa como un diccionario anidado.
# La estructura es: cubo[tipo_izq][tipo_der][operador] -> tipo_resultado

cubo_semantico = {
    T_ENTERO: {
        T_ENTERO: {
            '+': T_ENTERO,
            '-': T_ENTERO,
            '*': T_ENTERO,
            '/': T_FLOTANTE,
            '%': T_ENTERO,
            '>=': T_BOOL,
            '<=': T_BOOL,
            '>': T_BOOL,
            '<': T_BOOL,
            '!=': T_BOOL,
            '==': T_BOOL
        },
        T_FLOTANTE: {
            '+': T_FLOTANTE,
            '-': T_FLOTANTE,
            '*': T_FLOTANTE,
            '/': T_FLOTANTE,
            # Modulo entre flotantes no soportado
            '>=': T_BOOL,
            '<=': T_BOOL,
            '>': T_BOOL,
            '<': T_BOOL,
            '!=': T_BOOL,
            '==': T_BOOL
        }
    },
    T_FLOTANTE: {
        T_ENTERO: {
            '+': T_FLOTANTE,
            '-': T_FLOTANTE,
            '*': T_FLOTANTE,
            '/': T_FLOTANTE,
            # Modulo con flotante no soportado
            '>=': T_BOOL,
            '<=': T_BOOL,
            '>': T_BOOL,
            '<': T_BOOL,
            '!=': T_BOOL,
            '==': T_BOOL
        },
        T_FLOTANTE: {
            '+': T_FLOTANTE,
            '-': T_FLOTANTE,
            '*': T_FLOTANTE,
            '/': T_FLOTANTE,
            # Modulo entre flotantes no soportado
            '>=': T_BOOL,
            '<=': T_BOOL,
            '>': T_BOOL,
            '<': T_BOOL,
            '!=': T_BOOL,
            '==': T_BOOL
        }
    }
}

# Función auxiliar para consultar el cubo semántico
# Consulta el cubo semántico para obtener el tipo de resultado.
# Regresa T_ERROR si la operación no es válida.
def get_tipo_resultado(tipo_izq, tipo_der, op):
    try:
        return cubo_semantico[tipo_izq][tipo_der][op]
    except KeyError:
        return T_ERROR

# Función para probar todas las operaciones del cubo semántico
def probar_cubo_semantico():
    
    print("\n" + "="*60)
    print("PRUEBA DEL CUBO SEMANTICO")
    print("="*60)
    
    # Pruebas de operaciones aritméticas
    print("\n--- OPERACIONES ARITMETICAS ---")
    pruebas_aritmeticas = [
        ('entero', 'entero', '+'),
        ('entero', 'entero', '-'),
        ('entero', 'entero', '*'),
        ('entero', 'entero', '/'),
        ('entero', 'flotante', '+'),
        ('flotante', 'entero', '*'),
        ('flotante', 'flotante', '/'),
    ]
    
    for tipo_izq, tipo_der, op in pruebas_aritmeticas:
        resultado = get_tipo_resultado(tipo_izq, tipo_der, op)
        print(f"{tipo_izq:10} {op} {tipo_der:10} = {resultado}")
    
    # Pruebas de operaciones de comparación
    print("\n--- OPERACIONES DE COMPARACION ---")
    pruebas_comparacion = [
        ('entero', 'entero', '>'),
        ('entero', 'entero', '<'),
        ('entero', 'flotante', '=='),
        ('flotante', 'entero', '!='),
        ('flotante', 'flotante', '>'),
    ]
    
    for tipo_izq, tipo_der, op in pruebas_comparacion:
        resultado = get_tipo_resultado(tipo_izq, tipo_der, op)
        print(f"{tipo_izq:10} {op:2} {tipo_der:10} = {resultado}")
    
    # Pruebas de operaciones inválidas
    print("\n--- OPERACIONES INVALIDAS (deben dar error) ---")
    pruebas_error = [
        ('entero', 'bool', '+'),
        ('string', 'entero', '*'),
        ('flotante', 'entero', '&&'),
    ]
    
    for tipo_izq, tipo_der, op in pruebas_error:
        resultado = get_tipo_resultado(tipo_izq, tipo_der, op)
        print(f"{tipo_izq:10} {op:2} {tipo_der:10} = {resultado}")
    
    print("\n" + "="*60)
    print("FIN DE PRUEBA DEL CUBO SEMANTICO")
    print("="*60 + "\n")
