# Patito — Cómo ejecutar

Este proyecto implementa el lenguaje Patito con un analizador léxico y sintáctico (PLY) que genera cuádruplos y una máquina virtual para ejecutarlos. A continuación se indican los requisitos y los pasos para correrlo en Windows.

## Requisitos
- Python 3.11 (probado). También debería funcionar con Python 3.8+.
- Paquete `ply` (Python Lex-Yacc).

## Instalación
1) Verifica la versión de Python:
```
python --version
```

2) Instala la librería requerida:
```
pip install ply
```

Si tu entorno usa `python3`/`pip3`, ajusta los comandos:
```
python3 --version
pip3 install ply
```

## Estructura relevante
- `patito_main.py`: punto de entrada para compilar y ejecutar.
- `scanner.py`: lexer (PLY).
- `parser.py`: parser (PLY) y generación de cuádruplos.
- `vm.py`: máquina virtual que ejecuta los cuádruplos.
- `tests/`: programas de ejemplo en Patito.
- `parsetab.py`: tabla generada automáticamente por PLY (no editar).

## Cómo correr
1) Abre una terminal en la carpeta del proyecto `patito`.

2) Opcional: elige el archivo de prueba. En `patito_main.py` hay varias líneas comentadas que apuntan a archivos dentro de `tests/`. Cambia `input_file` a la que quieras ejecutar, por ejemplo:
```
input_file = "tests/fibonacci.txt"
```

3) Ejecuta el programa:
```
python patito_main.py
```

Esto compila el código Patito, imprime la tabla de constantes, los cuádruplos y ejecuta la máquina virtual mostrando la salida del programa.

## Notas
- La primera vez que ejecutes, PLY puede generar/actualizar `parsetab.py`.
- Si ves errores de importación de PLY, asegúrate de que la instalación se hizo en el mismo entorno de Python con el que ejecutas.
- Para cambiar de prueba, solo modifica `input_file` en `patito_main.py` y vuelve a correr.

## Ejemplos rápidos
- Ejecutar Fibonacci de ejemplo:
```
python patito_main.py
```

- Probar otro archivo (por ejemplo, `tests/factorial_iterativo.txt`): edita `patito_main.py` para usar ese `input_file` y vuelve a ejecutar el comando anterior.
