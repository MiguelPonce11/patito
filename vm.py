from typing import List, Tuple, Dict, Any

class VirtualMachine:
    def __init__(self, quads: List[Tuple[Any, Any, Any, Any]], tabla_constantes: Dict[Any, int]):
        self.quads = quads
        self.ip = 0  # instruction pointer
        # Memoria global: direccion -> valor (1000-2999)
        self.global_mem: Dict[int, Any] = {}
        # Pila de marcos de activación (locals/temporals)
        self.frames: List[Dict[int, Any]] = []
        # Crear un marco base para código global (no se elimina)
        self.frames.append({})
        # Mapa inverso de constantes: direccion -> valor
        self.const_by_addr: Dict[int, Any] = {addr: val for val, addr in tabla_constantes.items()}
        # Pila de llamadas: lista de tuplas (return_ip, func_name)
        self.call_stack: List[Tuple[int, str]] = []
        # Tabla de valores de retorno persistentes por función
        self.return_values: Dict[str, Any] = {}
        # Parámetros pendientes antes de crear el marco (ERA/PARAMETER -> GOSUB)
        self.pending_params: List[Tuple[int, Any]] = []

    def _get_val(self, addr_or_val: Any) -> Any:
        """Obtiene el valor dado un operando.
        Si es una dirección (int), lee de memoria o constante. Si es literal/None, regresa directamente.
        """
        if addr_or_val is None:
            return None
        if isinstance(addr_or_val, int):
            # ¿Es constante?
            if addr_or_val in self.const_by_addr:
                return self.const_by_addr[addr_or_val]
            # Direcciones por rango (según memoria.py)
            if 1000 <= addr_or_val <= 2999:
                return self.global_mem.get(addr_or_val, 0)
            elif 3000 <= addr_or_val <= 7999:
                # locals (3000-4999) + temporals (5000-7999) en el marco superior
                if self.frames:
                    return self.frames[-1].get(addr_or_val, 0)
                else:
                    # Sin marco, fallback seguro
                    return 0
        # Si es nombre simbólico (ej. nombre de función usado como slot de retorno),
        # intentar leer de memoria
        if isinstance(addr_or_val, str):
            # Primero, si es un nombre de función y ya tenemos su último valor de retorno
            if addr_or_val in self.return_values:
                return self.return_values[addr_or_val]
            # Simular slot simbólico en marco actual
            if self.frames and addr_or_val in self.frames[-1]:
                return self.frames[-1].get(addr_or_val)
            if addr_or_val in self.global_mem:
                return self.global_mem.get(addr_or_val)
            return addr_or_val
        # Literal directo (raro en este diseño), devolver tal cual
        return addr_or_val

    def _write(self, addr: int, value: Any):
        if addr is None:
            return
        if isinstance(addr, int):
            if 1000 <= addr <= 2999:
                self.global_mem[addr] = value
            elif 3000 <= addr <= 7999:
                if self.frames:
                    self.frames[-1][addr] = value
                else:
                    # Sin marco, no escribir
                    pass
        elif isinstance(addr, str):
            # Slot simbólico en marco actual
            if self.frames:
                self.frames[-1][addr] = value

    def run(self):
        # Ejecuta hasta encontrar END o salir del rango
        while 0 <= self.ip < len(self.quads):
            op, a1, a2, res = self.quads[self.ip]
            # print(f"[VM] IP={self.ip} Quad={op, a1, a2, res}")  # debug opcional

            if op in ('+', '-', '*', '/', '%', '>', '<', '!=', '==', '>=', '<='):
                v1 = self._get_val(a1)
                v2 = self._get_val(a2)
                if op == '+': out = v1 + v2
                elif op == '-': out = v1 - v2
                elif op == '*': out = v1 * v2
                elif op == '/': out = v1 / v2
                elif op == '%': out = v1 % v2
                elif op == '>': out = v1 > v2
                elif op == '<': out = v1 < v2
                elif op == '!=': out = v1 != v2
                elif op == '==': out = v1 == v2
                elif op == '>=': out = v1 >= v2
                elif op == '<=': out = v1 <= v2
                else: out = None
                self._write(res, out)
                self.ip += 1

            elif op == '=':
                v1 = self._get_val(a1)
                self._write(res, v1)
                self.ip += 1

            elif op == 'IMPRIME':
                v = self._get_val(res)
                print(v)
                self.ip += 1

            elif op == 'GOTOF':
                cond_val = self._get_val(a1)
                if not cond_val:
                    self.ip = int(res) if res is not None else self.ip + 1
                else:
                    self.ip += 1

            elif op == 'GOTO':
                self.ip = int(res) if res is not None else self.ip + 1

            elif op == 'ENDFUNC':
                # Terminar ejecución de función actual
                if self.call_stack:
                    return_ip, func_name = self.call_stack.pop()
                    # Antes de eliminar el marco, capturar valor de retorno si existe
                    if len(self.frames) > 1:  # Mantener el marco base
                        frame = self.frames[-1]
                        if func_name in frame:
                            self.return_values[func_name] = frame[func_name]
                        # Destruir solo el marco de la función
                        self.frames.pop()
                    self.ip = return_ip
                else:
                    # ENDFUNC sin contexto de llamada (no debería ocurrir)
                    self.ip += 1

            elif op == 'RETURN':
                # Capturar valor de retorno y saltar al ENDFUNC (res)
                ret_val = self._get_val(a1)
                func_name = a2 if isinstance(a2, str) else None
                if func_name:
                    # Guardar en marco actual para que ENDFUNC lo pueda persistir
                    self._write(func_name, ret_val)
                    # También actualizar el mapa de retorno inmediato
                    self.return_values[func_name] = ret_val
                # Saltar al ENDFUNC de la función actual (backpatched destino)
                self.ip = int(res) if res is not None else self.ip + 1

            elif op == 'ERA':
                # Preparación de activación; sin efecto en este VM simple
                self.ip += 1
            
            elif op == 'PARAMETER':
                # Asignar argumento a dirección destino del parámetro
                val = self._get_val(a1)
                # Guardar para escritura cuando se cree el marco en GOSUB
                if isinstance(res, int):
                    self.pending_params.append((res, val))
                self.ip += 1
            
            elif op == 'GOSUB':
                # Saltar al inicio de la función y guardar retorno
                func_name = a1 if isinstance(a1, str) else ''
                self.call_stack.append((self.ip + 1, func_name))
                # Crear nuevo marco para la llamada
                self.frames.append({})
                # Escribir parámetros pendientes en el nuevo marco
                if self.pending_params:
                    for addr, val in self.pending_params:
                        self._write(addr, val)
                    self.pending_params.clear()
                self.ip = int(res) if res is not None else self.ip + 1

            elif op == 'END':
                break

            else:
                # Operador desconocido: continuar para no bloquear
                self.ip += 1

        # Retornar snapshot de memorias
        return {
            'global': dict(self.global_mem),
            'top_frame': dict(self.frames[-1]) if self.frames else {}
        }
