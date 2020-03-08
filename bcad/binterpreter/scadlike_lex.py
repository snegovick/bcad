import ply.lex as lex
from logging import debug, info, warning, error, critical

reserved = {
    'module': 'MODULE',
    'children': 'CHILDREN',
    'group': 'GROUP',
    'sphere': 'SPHERE',
    'cylinder': 'CYLINDER',
    'cube': 'CUBE',
    'multmatrix': 'MULTMATRIX',
    'intersection': 'INTERSECTION',
    'difference': 'DIFFERENCE',
    'union': 'UNION',
    'rotate_extrude': 'ROTATE_EXTRUDE',
    'linear_extrude': 'LINEAR_EXTRUDE',
    'true': 'TRUE',
    'false': 'FALSE',
    'circle': 'CIRCLE',
    'square': 'SQUARE',
    'text': 'TEXT',
    'polygon': 'POLYGON',
    'undef': 'UNDEF',
    'polyhedron': 'POLYHEDRON',
    'triangles': 'TRIANGLES',
    'faces': 'FACES',
    'render': 'RENDER',
    'surface': 'SURFACE',
    'subdiv': 'SUBDIV',
    'glide': 'GLIDE',
    'hull': 'HULL',
    'minkowski': 'MINKOWSKI',
    'projection': 'PROJECTION',
    'import': 'IMPORT',
    'color': 'COLOR',
    'offset': 'OFFSET',
    'resize': 'RESIZE',
    'scale': 'SCALE',
    'mirror': 'MIRROR',
    'rotate': 'ROTATE',
    'translate': 'TRANSLATE',
    'if': 'IF',
    'else': 'ELSE',
    'use': 'USE',
    'include': 'INCLUDE',
    'function': 'FUNCTION',
    'for': 'FOR'
}

bsuite_reserved = {
    'profile': 'PROFILE',
    'line': 'LINE',
    'move': 'MOVE',
    'fillet': 'FILLET',
    'import_step': 'IMPORT_STEP',
    'import_stl': 'IMPORT_STL',
}

reserved.update(bsuite_reserved)

class ScadLikeLex(object):
    precedence = ()
    tokens = [
        #    'NAME',
        'NUMBER',
        'COMMA',
        'SEMICOLON',
        'COLON',
        'QUESTION',
        'PLUS',
        'MOD',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'EQUALS',
        'LPAREN',
        'RPAREN',
        'OBRACE',
        'EBRACE',
        'OSQUARE',
        'ESQUARE',
        'ID',
        'DOT',
        'STRING',
        'USESTRING',
        'ISEQUAL',
        'ISNOTEQUAL',
        'GE',
        'LE',
        'GT',
        'LT',
        # 'MODIFIERBACK',
        # 'MODIFIERDEBUG',
        # 'MODIFIERROOT',
        # 'MODIFIERDISABLE'
    ] + list(reserved.values())

    #t_NAME          = r'[$]?[a-zA-Z_]+[0-9]*'
    t_NUMBER         = r'[0-9]*[\.]*[0-9]+([eE]-?[0-9]+)*'
    t_COMMA          = r','
    t_SEMICOLON      = r';'
    t_COLON          = r':'
    t_QUESTION       = r'\?'
    t_PLUS           = r'\+'
    t_MOD            = r'%'
    t_MINUS          = r'-'
    t_TIMES          = r'\*'
    t_DIVIDE         = r'/'
    t_EQUALS         = r'='
    t_LPAREN         = r'\('
    t_RPAREN         = r'\)'
    t_OBRACE         = r'{'
    t_EBRACE         = r'\}'
    t_OSQUARE        = r'\['
    t_ESQUARE        = r'\]'
    t_DOT            = r'\.'
    t_STRING         = r'"[^"]*"'
    t_USESTRING      = r'<[\w_\.]*>'
    t_ISEQUAL        = r'=='
    t_ISNOTEQUAL     = r'!='
    t_GE             = r'>='
    t_LE             = r'<='
    t_GT             = r'>'
    t_LT             = r'<'
    t_ignore_COMMENT = r'//.*'

    # t_MODIFIERBACK    = r'%'
    # t_MODIFIERDEBUG   = r'\#'
    # t_MODIFIERROOT    = r'!'
    # t_MODIFIERDISABLE = r'\*'


    t_ignore = " \t"

    def t_comment(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')

    def t_ID(self, t):
        r'[$]?[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value,'ID')    # Check for reserved words
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        error("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

#lexer = lex.lex()
if __name__ == "__main__":
    lex.runmain(lexer)
