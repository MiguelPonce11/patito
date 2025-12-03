import ply.lex as lex

# Palabras Reservadas del lenguaje Patito
palabras_reservadas = {
    'programa': 'PROGRAMA',
    'inicio': 'INICIO',
    'fin': 'FIN',
    'vars': 'VARS',
    'entero': 'ENTERO',
    'flotante': 'FLOTANTE',
    'escribe': 'ESCRIBE',
    'mientras': 'MIENTRAS',
    'haz': 'HAZ',
    'si': 'SI',
    'sino': 'SINO',
    'sino_si': 'SINO_SI',
    'nula': 'NULA',
    'return': 'RETURN',
}

# Lista de tokens
tokens = [
    'ID', 'CTE_ENT', 'CTE_FLOT', 'LETRERO',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN', 'SEMICOLON', 'COLON', 'COMMA',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',  
    'LBRACKET', 'RBRACKET',                  
    'GT', 'LT', 'NE', 'EQ', 'LE', 'GE'
] + list(palabras_reservadas.values())

# Expresiones regulares para tokens simples
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_MOD       = r'%'
t_ASSIGN    = r'='
t_PLUS_ASSIGN  = r'\+=' 
t_MINUS_ASSIGN = r'-='
t_TIMES_ASSIGN = r'\*='
t_DIVIDE_ASSIGN= r'/='
t_SEMICOLON = r';'
t_COLON     = r':'
t_COMMA     = r','
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_GT        = r'>'
t_LT        = r'<'
t_NE        = r'!='
t_EQ        = r'=='
t_LE        = r'<='
t_GE        = r'>='
t_ignore    = ' \t'

# Comentarios: línea y bloque
def t_comment_single(t):
    r'//.*'
    pass

def t_comment_block(t):
    r'/\*([^*]|\*+[^/])*\*/'
    # Ignorar contenido de comentarios tipo C
    t.lexer.lineno += t.value.count('\n')
    pass

# Reglas para tokens complejos
def t_ID(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    t.type = palabras_reservadas.get(t.value, 'ID') # Revisa si es palabra reservada
    return t

def t_CTE_FLOT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_CTE_ENT(t):
    r'\d+'
    t.value = int(t.value)
    return t
    
def t_LETRERO(t):
    r'\"([^\\\"]|\\.)*\"'
    t.value = t.value[1:-1] # Quita las comillas
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' en linea {t.lexer.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()
