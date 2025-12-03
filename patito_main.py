from parser import parser
from directorio_funciones import (
    inicializar_dirfunc, limpiar_estado_global, quads, tabla_constantes
)
from vm import VirtualMachine

# Archivo de entrada a ejecutar (cambia esta ruta para correr otro .txt)
#input_file = "tests/factorial_iterativo.txt"
#input_file = "tests/exp.txt"
#input_file = "tests/valido.txt"
#input_file = "tests/retorno.txt"
#input_file = "tests/condicionales.txt"
#input_file = "tests/factorial_recursivo.txt"
#input_file = "tests/sumatoria.txt"
#input_file = "tests/funcion.txt"
#input_file = "tests/asignacion.txt"
input_file = "tests/fibonacci.txt"
#input_file = "tests/condicionales_anidados.txt"

def compilar():
    """Compila el programa y muestra solo el resultado final"""
    # Limpiar estado global
    limpiar_estado_global()
    
    # Inicializar el directorio
    inicializar_dirfunc('test_fibonacci')
    
    # Parsear código (mostrando errores)
    import sys
    import io
    
    # Leer código fuente desde archivo
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except Exception as e:
        print(f"No se pudo leer el archivo '{input_file}': {e}")
        return

    try:
        parser.parse(codigo)
        
        print("\n--- COMPILACIÓN EXITOSA ---\n")
        
        # Mostrar tabla de constantes
        print("--- TABLA DE CONSTANTES (VALOR -> DIRECCIÓN) ---")
        if tabla_constantes:
            for valor, direccion in sorted(tabla_constantes.items(), key=lambda x: x[1]):
                if isinstance(valor, str):
                    print(f"  {valor} : {direccion}")
                else:
                    print(f"  {valor} : {direccion}")
        
        print("\n--- LISTA DE CUÁDRUPLOS (DIRECCIONES) ---")
        if quads:
            for i, quad in enumerate(quads):
                op, op1, op2, res = quad
                op1_str = str(op1) if op1 is not None else 'None'
                op2_str = str(op2) if op2 is not None else 'None'
                res_str = str(res) if res is not None else 'None'
                print(f"  {i}: ({op}, {op1_str}, {op2_str}, {res_str})")
        
        print("-" * 42)
        print("\n--- EJECUCIÓN (Maquina Virtual) ---")
        # Ejecutar la Máquina Virtual sobre los cuádruplos generados
        vm = VirtualMachine(quads, tabla_constantes)
        vm.run()
    except Exception as e:
        import traceback
        print(f"\n--- ERROR DE COMPILACIÓN ---")
        print(f"Error: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    compilar()
