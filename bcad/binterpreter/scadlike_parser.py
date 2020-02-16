import ply.lex as lex
import ply.yacc as yacc
from bcad.binterpreter import scadlike_lex
from bcad.binterpreter.scadlike_lex import ScadLikeLex
import logging

class ParserError(Exception):
    def __init__(self, lineno, message):
        self.message = "Parser error \"%s\": %i"%(message, lineno,)
        self.lineno = lineno
        self.message = message

class ScadLikeParser(ScadLikeLex):
    precedence = (
        ('nonassoc', 'LT', 'LE', 'GE', 'GT'),  # Nonassociative operators
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),
    )

    def load_from_file(self, filename):
        lex.lex(module=self)
        parser = yacc.yacc(module=self, debug=self.debug)
        logging.info("Loading %s"%(filename,))
        f = open(filename, 'r')
        logging.debug('Start Parser')
        result = parser.parse(f.read(),debug=self.debug)
        f.close()
        self.data = result

    def load_from_data(self, data):
        lex.lex(module=self)
        parser = yacc.yacc(module=self, debug=self.debug)
        logging.debug('Start Parser')
        result = parser.parse(data, debug=self.debug)
        self.data=result

    def __init__(self, data=None, path=None, debug=False):
        self.ids = {}
        self.debug = debug
        logging.debug ('data: %s, path: %s'%(data, path))
        if data!=None:
            self.load_from_data(data)
        elif path!=None:
            self.load_from_file(path)

    def p_block_list(self, p):
        '''
        block_list : statement
                   | block_list statement
        '''
        logging.debug("Block list len: %i"%(len(p),))
        if (len(p)<3):
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_statement_action(self, p):
        '''statement : builtin_actions
                     | function_definition
                     | module_definition
                     | for_loop
                     | if_cond
                     | use
                     | include'''
        p[0] = p[1]

    def p_statement_call(self, p):
        'statement : call SEMICOLON'
        p[1]['type'] = 'stat_call'
        p[0] = p[1]

    def p_statement_call_builtin_modules(self, p):
        'statement : call_builtin_modules SEMICOLON'
        p[0] = p[1]

    def p_statement_assign(self, p):
        'statement : assign SEMICOLON'
        p[0] = {'type': 'stat_assign', 'val': p[1], 'line': p.lineno(1)}

    def p_assign(self, p):
        'assign : ID EQUALS expression'
        p[0] = {'type': 'expr_assign', 'id': p[1], 'val': p[3], 'line': p.lineno(1)}

    def p_expression_assign(self, p):
        'expression : assign'
        p[0] = p[1]

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression TIMES expression
                   | expression DIVIDE expression
                   | expression ISEQUAL expression
                   | expression ISNOTEQUAL expression
                   | expression GT expression
                   | expression GE expression
                   | expression LT expression
                   | expression LE expression
        """
        # print [repr(p[i]) for i in range(0,4)]
        p[0] = {'type': 'expr_binop', 'val': [p[1], p[3], p[2]], 'line': p.lineno(1)}

    def p_expression_unop(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = {'type': 'expr_unop', 'val': [p[2], '-'], 'line': p.lineno(1)}

    def p_expression_terop(self, p):
        'expression : expression QUESTION expression COLON expression'
        p[0] = {'type': 'expr_terop', 'val': {'condition': p[1], 'true': p[3], 'false': p[5]}, 'line': p.lineno(1)}

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = {'type': 'expr_number', 'val': float(p[1]), 'line': p.lineno(1)}

    def p_expression_string(self, p):
        'expression : STRING'
        p[0] = {'type': 'expr_string', 'val': p[1], 'line': p.lineno(1)}

    def p_expression_bool(self, p):
        '''expression : TRUE
                      | FALSE'''
        p[0] = {'type': 'expr_bool', 'val': (True if p[1]=='true' else False), 'line': p.lineno(1)}

    def p_expression_name(self, p):
        'expression : ID'
        p[0] = {'type': 'expr_id', 'val': p[1], 'line': p.lineno(1)}

    # def p_moddef(p):
    #     "moddef : MODULE NAME parameters"
    #     #p[0] = ast.Function(None, p[2], tuple(p[3]), (), 0, None, p[5])

    def p_call(self, p):
        'call : ID parameters'
        p[0] = {'type': 'call', 'id': p[1], 'args': p[2], 'line': p.lineno(1)}

    def p_use(self, p):
        'use : USE USESTRING SEMICOLON'
        p[0] = {'type': 'use', 'path': p[2], 'line': p.lineno(1)}

    def p_include(self, p):
        'include : INCLUDE USESTRING SEMICOLON'
        p[0] = {'type': 'include', 'path': p[2], 'line': p.lineno(1)}

    def p_call_builtin_modules(self, p):
        '''call_builtin_modules : LINE parameters
                                | FILLET parameters
                                | CUBE parameters
                                | CYLINDER parameters
                                | IMPORT_STEP parameters
                                | IMPORT_STL parameters
                                | POLYGON parameters
        '''
        p[0] = {'type': 'stat_call_builtin_modules', 'id': p[1], 'args': p[2], 'line': p.lineno(1)}

    def p_expression_call(self, p):
        "expression : call"
        p[1]['type'] = 'expr_call'
        p[0] = p[1]

    def p_parameters(self, p):
        """parameters : LPAREN RPAREN
                      | LPAREN varargslist RPAREN"""
        if len(p) == 3:
            p[0] = []
        else:
            p[0] = p[2]

    def p_varargslist(self, p):
        """varargslist : varargslist COMMA expression
                       | expression"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_action_child_block(self, p):
        '''action_child_block : OBRACE block_list EBRACE
                              | statement
                              | OBRACE EBRACE'''
        if (len(p)==2):
            p[0] = [p[1]]
        elif (len(p)==3):
            p[0] = []
        else:
            p[0] = p[2]

    def p_builtin_actions(self, p):
        '''builtin_actions : PROFILE parameters action_child_block
                           | LINEAR_EXTRUDE parameters action_child_block
                           | MIRROR parameters action_child_block
                           | ROTATE parameters action_child_block
                           | UNION parameters action_child_block
                           | DIFFERENCE parameters action_child_block
                           | TRANSLATE parameters action_child_block
                           | PROJECTION parameters action_child_block
                           | COLOR parameters action_child_block'''
        p[0] = {'type': 'stat_builtin', 'id': p[1], 'args': p[2], 'block': p[3], 'line': p.lineno(1)}

    def p_function_definition(self, p):
        'function_definition : FUNCTION ID parameters EQUALS expression SEMICOLON'
        p[0] = {'type': 'stat_function_definition', 'id': p[2], 'args': p[3], 'expression': p[5], 'line': p.lineno(2)}

    def p_array_list(self, p):
        '''array_list : array_list COMMA expression
                      | expression'''
        if len(p) == 4:
            logging.debug('p1:',p[1])
            p[1]['val'] += [p[3]]
            p[0] = p[1]
        else:
            p[0] = {'type':'array_list', 'val': [p[1]], 'line': p.lineno(0)}

    def p_array_right(self, p):
        '''array_right : OSQUARE ESQUARE
                       | OSQUARE array_list ESQUARE'''
        if (len(p) == 3):
            p[0] = {'type':'array_list', 'val': [], 'line': p.lineno(0)}
        else:
            p[0] = p[2]

    def p_array_right_range(self, p):
        '''array_right : OSQUARE expression COLON expression ESQUARE
                       | OSQUARE expression COLON expression COLON expression ESQUARE'''
        if (len(p) == 5):
            p[0] = {'type':'array_range', 'val': {'start': p[2], 'end': p[4]}, 'line': p.lineno(0)}
        else:
            p[0] = {'type':'array_range', 'val': {'start': p[2], 'end': p[6], 'step': p[4]}, 'line': p.lineno(0)}

    def p_expression_array(self, p):
        'expression : array_right'
        p[0] = p[1]

    def p_expression_array_element(self, p):
        'expression : ID OSQUARE expression ESQUARE'
        p[0] = {'type': 'array_access', 'id': p[1], 'index': p[3], 'val': None, 'line': p.lineno(1)}

    def p_for_loop(self, p):
        'for_loop : FOR LPAREN ID EQUALS array_right RPAREN action_child_block'
        p[0] = {'type': 'stat_for', 'counter': p[3], 'counter_vals': p[5], 'block': p[7], 'line': p.lineno(1)}

    def p_if_cond(self, p):
        '''if_cond : IF LPAREN expression RPAREN action_child_block
                   | IF LPAREN expression RPAREN action_child_block ELSE action_child_block'''
        blocks = [p[5]]
        if len(p)>6:
            blocks.append(p[7])
        p[0] = {'type': 'stat_if', 'condition': p[3], 'blocks': blocks, 'line': p.lineno(1)}

    def p_module_definition(self, p):
        'module_definition : MODULE ID parameters action_child_block'
        p[0] = {'type': 'stat_module_definition', 'id': p[2], 'args': p[3], 'block': p[4], 'line': p.lineno(2)}

    def p_error(self, p):
        if p:
            raise ParserError(p.lineno, p.value)
        else:
            raise ParserError(p.lineno, p.value)
            
if __name__=="__main__":
    import sys
    import json
    p = ScadLikeParser(path=sys.argv[1], debug=True)
    logging.debug(json.dumps(p.data, indent=2))
