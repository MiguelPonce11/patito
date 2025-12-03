# Administrador de Memoria Virtual para el Compilador Patito
# Asigna direcciones virtuales a variables, temporales y constantes

class MemoriaVirtual:
    def __init__(self):
        #  RANGOS DE MEMORIA 
        
        # Globales
        self.glob_int_min = 1000
        self.glob_int_max = 1999
        self.glob_float_min = 2000
        self.glob_float_max = 2999
        
        # Locales 
        self.loc_int_min = 3000
        self.loc_int_max = 3999
        self.loc_float_min = 4000
        self.loc_float_max = 4999
        
        # Temporales 
        self.temp_int_min = 5000
        self.temp_int_max = 5999
        self.temp_float_min = 6000
        self.temp_float_max = 6999
        self.temp_bool_min = 7000  # Para resultados de comparaciones
        self.temp_bool_max = 7999
        
        # Constantes (Globales, no se reinician)
        self.cte_int_min = 8000
        self.cte_int_max = 8999
        self.cte_float_min = 9000
        self.cte_float_max = 9999
        self.cte_string_min = 10000
        self.cte_string_max = 10999

        # CONTADORES ACTUALES 
        self.reset_contadores_locales()
        self.reset_contadores_globales()
        self.reset_contadores_constantes()

    def reset_contadores_locales(self):
        """Reinicia los contadores para una nueva función (Locales y Temporales)"""
        self.cont_loc_int = self.loc_int_min
        self.cont_loc_float = self.loc_float_min
        self.cont_temp_int = self.temp_int_min
        self.cont_temp_float = self.temp_float_min
        self.cont_temp_bool = self.temp_bool_min

    def reset_contadores_globales(self):
        """Reinicia los contadores para variables globales"""
        self.cont_glob_int = self.glob_int_min
        self.cont_glob_float = self.glob_float_min

    def reset_contadores_constantes(self):
        """Reinicia los contadores para constantes"""
        self.cont_cte_int = self.cte_int_min
        self.cont_cte_float = self.cte_float_min
        self.cont_cte_string = self.cte_string_min

    def get_direccion(self, scope, tipo):
        """
        Asigna una dirección de memoria según el scope y tipo, 
        y avanza el contador.
        
        Args:
            scope: 'global', 'local', 'temporal', 'constante'
            tipo: 'entero', 'flotante', 'bool', 'letrero'
        
        Returns:
            int: Dirección de memoria virtual asignada
        """
        mem_dir = -1
        
        if scope == 'global':
            if tipo == 'entero':
                if self.cont_glob_int > self.glob_int_max:
                    raise MemoryError(f"Desbordamiento de memoria global entera (max: {self.glob_int_max})")
                mem_dir = self.cont_glob_int
                self.cont_glob_int += 1
            elif tipo == 'flotante':
                if self.cont_glob_float > self.glob_float_max:
                    raise MemoryError(f"Desbordamiento de memoria global flotante (max: {self.glob_float_max})")
                mem_dir = self.cont_glob_float
                self.cont_glob_float += 1
                
        elif scope == 'local':
            if tipo == 'entero':
                if self.cont_loc_int > self.loc_int_max:
                    raise MemoryError(f"Desbordamiento de memoria local entera (max: {self.loc_int_max})")
                mem_dir = self.cont_loc_int
                self.cont_loc_int += 1
            elif tipo == 'flotante':
                if self.cont_loc_float > self.loc_float_max:
                    raise MemoryError(f"Desbordamiento de memoria local flotante (max: {self.loc_float_max})")
                mem_dir = self.cont_loc_float
                self.cont_loc_float += 1
                
        elif scope == 'temporal':
            if tipo == 'entero':
                if self.cont_temp_int > self.temp_int_max:
                    raise MemoryError(f"Desbordamiento de memoria temporal entera (max: {self.temp_int_max})")
                mem_dir = self.cont_temp_int
                self.cont_temp_int += 1
            elif tipo == 'flotante':
                if self.cont_temp_float > self.temp_float_max:
                    raise MemoryError(f"Desbordamiento de memoria temporal flotante (max: {self.temp_float_max})")
                mem_dir = self.cont_temp_float
                self.cont_temp_float += 1
            elif tipo == 'bool':
                if self.cont_temp_bool > self.temp_bool_max:
                    raise MemoryError(f"Desbordamiento de memoria temporal bool (max: {self.temp_bool_max})")
                mem_dir = self.cont_temp_bool
                self.cont_temp_bool += 1
        
        elif scope == 'constante':
            if tipo == 'entero':
                if self.cont_cte_int > self.cte_int_max:
                    raise MemoryError(f"Desbordamiento de memoria constante entera (max: {self.cte_int_max})")
                mem_dir = self.cont_cte_int
                self.cont_cte_int += 1
            elif tipo == 'flotante':
                if self.cont_cte_float > self.cte_float_max:
                    raise MemoryError(f"Desbordamiento de memoria constante flotante (max: {self.cte_float_max})")
                mem_dir = self.cont_cte_float
                self.cont_cte_float += 1
            elif tipo == 'letrero':  # Strings
                if self.cont_cte_string > self.cte_string_max:
                    raise MemoryError(f"Desbordamiento de memoria constante string (max: {self.cte_string_max})")
                mem_dir = self.cont_cte_string
                self.cont_cte_string += 1

        return mem_dir
    
    def imprimir_mapa_memoria(self):
        """Imprime el mapa de memoria con los rangos definidos"""
        print("\n" + "="*70)
        print("MAPA DE MEMORIA VIRTUAL")
        print("="*70)
        print(f"\n{'Ámbito':<15} {'Tipo':<12} {'Rango Inicio':<15} {'Rango Fin':<15}")
        print("-" * 70)
        
        print(f"{'Global':<15} {'Entero':<12} {self.glob_int_min:<15} {self.glob_int_max:<15}")
        print(f"{'':15} {'Flotante':<12} {self.glob_float_min:<15} {self.glob_float_max:<15}")
        
        print(f"{'Local':<15} {'Entero':<12} {self.loc_int_min:<15} {self.loc_int_max:<15}")
        print(f"{'':15} {'Flotante':<12} {self.loc_float_min:<15} {self.loc_float_max:<15}")
        
        print(f"{'Temporal':<15} {'Entero':<12} {self.temp_int_min:<15} {self.temp_int_max:<15}")
        print(f"{'':15} {'Flotante':<12} {self.temp_float_min:<15} {self.temp_float_max:<15}")
        print(f"{'':15} {'Bool':<12} {self.temp_bool_min:<15} {self.temp_bool_max:<15}")
        
        print(f"{'Constante':<15} {'Entero':<12} {self.cte_int_min:<15} {self.cte_int_max:<15}")
        print(f"{'':15} {'Flotante':<12} {self.cte_float_min:<15} {self.cte_float_max:<15}")
        print(f"{'':15} {'String':<12} {self.cte_string_min:<15} {self.cte_string_max:<15}")
        
        print("="*70 + "\n")

# Instancia global del administrador de memoria
memoria = MemoriaVirtual()
