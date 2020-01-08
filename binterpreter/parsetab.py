
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftPLUSMINUSleftTIMESDIVIDErightUMINUSCHILDREN CIRCLE COLOR COMMA CUBE CYLINDER DIFFERENCE DIVIDE DOT EBRACE ECHO ELSE EQUALS ESQUARE FACES FALSE FILLET FOR FUNCTION GE GLIDE GROUP GT HULL ID IF IMPORT INCLUDE INTERSECTION ISEQUAL ISNOTEQUAL LE LINE LINEAR_EXTRUDE LPAREN LT MINKOWSKI MINUS MIRROR MODULE MOVE MULTMATRIX NUMBER OBRACE OFFSET OSQUARE PATHS PLUS POINTS POLYGON POLYHEDRON PROFILE PROJECTION RENDER RESIZE ROTATE ROTATE_EXTRUDE RPAREN SCALE SEMICOLON SPHERE SQUARE STRING SUBDIV SURFACE TEXT TIMES TRANSLATE TRIANGLES TRUE UNDEF UNION USE USESTRING\n        block_list : statement\n                   | block_list statement\n        statement : builtin_actions\n                     | function_definition\n                     | module_definition\n                     | for_loop\n                     | if_cond\n                     | use\n                     | includestatement : call SEMICOLONstatement : call_builtin_modules SEMICOLONstatement : assign SEMICOLONassign : ID EQUALS expressionexpression : assign\n        expression : expression PLUS expression\n                   | expression MINUS expression\n                   | expression TIMES expression\n                   | expression DIVIDE expression\n                   | expression ISEQUAL expression\n                   | expression ISNOTEQUAL expression\n                   | expression GT expression\n                   | expression GE expression\n                   | expression LT expression\n                   | expression LE expression\n        expression : MINUS expression %prec UMINUSexpression : LPAREN expression RPARENexpression : NUMBERexpression : TRUE\n                      | FALSEexpression : IDcall : ID parametersuse : USE USESTRING SEMICOLONinclude : INCLUDE USESTRING SEMICOLONcall_builtin_modules : LINE parameters\n                                | FILLET parameters\n                                | CUBE parameters\n        expression : callparameters : LPAREN RPAREN\n                      | LPAREN varargslist RPARENvarargslist : varargslist COMMA expression\n                       | expressionaction_child_block : OBRACE block_list EBRACE\n                              | statement\n                              | OBRACE EBRACEbuiltin_actions : PROFILE parameters action_child_block\n                           | LINEAR_EXTRUDE parameters action_child_block\n                           | MIRROR parameters action_child_block\n                           | ROTATE parameters action_child_block\n                           | TRANSLATE parameters action_child_blockfunction_definition : FUNCTION ID parameters EQUALS expression SEMICOLONarray_list : array_list COMMA expression\n                      | expressionarray_right : OSQUARE ESQUARE\n                       | OSQUARE array_list ESQUAREexpression : array_rightexpression : ID OSQUARE expression ESQUAREfor_loop : FOR LPAREN ID EQUALS array_right RPAREN action_child_blockif_cond : IF LPAREN expression RPAREN action_child_block\n                   | IF LPAREN expression RPAREN action_child_block ELSE action_child_blockmodule_definition : MODULE ID parameters action_child_block'
    
_lr_action_items = {'PROFILE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[13,13,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,13,13,13,13,13,-45,13,-43,-38,-46,-47,-48,-49,13,-32,-33,13,-44,-39,-60,13,-42,-58,-50,13,13,-57,-59,]),'LINEAR_EXTRUDE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[14,14,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,14,14,14,14,14,-45,14,-43,-38,-46,-47,-48,-49,14,-32,-33,14,-44,-39,-60,14,-42,-58,-50,14,14,-57,-59,]),'MIRROR':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[15,15,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,15,15,15,15,15,-45,15,-43,-38,-46,-47,-48,-49,15,-32,-33,15,-44,-39,-60,15,-42,-58,-50,15,15,-57,-59,]),'ROTATE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[16,16,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,16,16,16,16,16,-45,16,-43,-38,-46,-47,-48,-49,16,-32,-33,16,-44,-39,-60,16,-42,-58,-50,16,16,-57,-59,]),'TRANSLATE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[17,17,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,17,17,17,17,17,-45,17,-43,-38,-46,-47,-48,-49,17,-32,-33,17,-44,-39,-60,17,-42,-58,-50,17,17,-57,-59,]),'FUNCTION':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[18,18,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,18,18,18,18,18,-45,18,-43,-38,-46,-47,-48,-49,18,-32,-33,18,-44,-39,-60,18,-42,-58,-50,18,18,-57,-59,]),'MODULE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[20,20,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,20,20,20,20,20,-45,20,-43,-38,-46,-47,-48,-49,20,-32,-33,20,-44,-39,-60,20,-42,-58,-50,20,20,-57,-59,]),'FOR':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[21,21,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,21,21,21,21,21,-45,21,-43,-38,-46,-47,-48,-49,21,-32,-33,21,-44,-39,-60,21,-42,-58,-50,21,21,-57,-59,]),'IF':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[22,22,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,22,22,22,22,22,-45,22,-43,-38,-46,-47,-48,-49,22,-32,-33,22,-44,-39,-60,22,-42,-58,-50,22,22,-57,-59,]),'USE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[23,23,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,23,23,23,23,23,-45,23,-43,-38,-46,-47,-48,-49,23,-32,-33,23,-44,-39,-60,23,-42,-58,-50,23,23,-57,-59,]),'INCLUDE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[24,24,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,24,24,24,24,24,-45,24,-43,-38,-46,-47,-48,-49,24,-32,-33,24,-44,-39,-60,24,-42,-58,-50,24,24,-57,-59,]),'ID':([0,1,2,3,4,5,6,7,8,9,18,20,28,29,30,31,32,33,34,35,36,37,40,42,43,49,50,51,52,53,57,64,65,66,67,68,71,74,75,76,77,79,80,81,82,83,84,85,86,87,88,89,90,92,96,97,99,100,115,118,121,122,123,124,125,],[19,19,-1,-3,-4,-5,-6,-7,-8,-9,38,41,-2,-10,-11,-12,19,61,19,19,19,19,61,72,61,-45,19,-43,61,-38,61,61,-46,-47,-48,-49,19,-32,-33,19,-44,-39,61,61,61,61,61,61,61,61,61,61,61,61,61,-60,19,-42,61,-58,-50,19,19,-57,-59,]),'LINE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[25,25,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,25,25,25,25,25,-45,25,-43,-38,-46,-47,-48,-49,25,-32,-33,25,-44,-39,-60,25,-42,-58,-50,25,25,-57,-59,]),'FILLET':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[26,26,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,26,26,26,26,26,-45,26,-43,-38,-46,-47,-48,-49,26,-32,-33,26,-44,-39,-60,26,-42,-58,-50,26,26,-57,-59,]),'CUBE':([0,1,2,3,4,5,6,7,8,9,28,29,30,31,32,34,35,36,37,49,50,51,53,65,66,67,68,71,74,75,76,77,79,97,99,100,118,121,122,123,124,125,],[27,27,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,27,27,27,27,27,-45,27,-43,-38,-46,-47,-48,-49,27,-32,-33,27,-44,-39,-60,27,-42,-58,-50,27,27,-57,-59,]),'$end':([1,2,3,4,5,6,7,8,9,28,29,30,31,49,51,65,66,67,68,74,75,77,97,100,118,121,124,125,],[0,-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,-45,-43,-46,-47,-48,-49,-32,-33,-44,-60,-42,-58,-50,-57,-59,]),'EBRACE':([2,3,4,5,6,7,8,9,28,29,30,31,49,50,51,65,66,67,68,74,75,76,77,97,100,118,121,124,125,],[-1,-3,-4,-5,-6,-7,-8,-9,-2,-10,-11,-12,-45,77,-43,-46,-47,-48,-49,-32,-33,100,-44,-60,-42,-58,-50,-57,-59,]),'ELSE':([3,4,5,6,7,8,9,29,30,31,49,51,65,66,67,68,74,75,77,97,100,118,121,124,125,],[-3,-4,-5,-6,-7,-8,-9,-10,-11,-12,-45,-43,-46,-47,-48,-49,-32,-33,-44,-60,-42,123,-50,-57,-59,]),'SEMICOLON':([10,11,12,39,44,45,46,47,48,53,56,58,59,60,61,62,63,70,79,91,93,101,103,104,105,106,107,108,109,110,111,112,114,116,119,],[29,30,31,-31,74,75,-34,-35,-36,-38,-14,-27,-28,-29,-30,-37,-55,-13,-39,-25,-53,-26,-15,-16,-17,-18,-19,-20,-21,-22,-23,-24,-54,121,-56,]),'LPAREN':([13,14,15,16,17,19,21,22,25,26,27,33,38,40,41,43,52,57,61,64,80,81,82,83,84,85,86,87,88,89,90,92,96,115,],[33,33,33,33,33,33,42,43,33,33,33,52,33,52,33,52,52,52,33,52,52,52,52,52,52,52,52,52,52,52,52,52,52,52,]),'EQUALS':([19,53,61,69,72,79,],[40,-38,40,96,98,-39,]),'USESTRING':([23,24,],[44,45,]),'OBRACE':([32,34,35,36,37,53,71,79,99,122,123,],[50,50,50,50,50,-38,50,-39,50,50,50,]),'RPAREN':([33,39,53,54,55,56,58,59,60,61,62,63,70,73,78,79,91,93,101,102,103,104,105,106,107,108,109,110,111,112,114,117,119,],[53,-31,-38,79,-41,-14,-27,-28,-29,-30,-37,-55,-13,99,101,-39,-25,-53,-26,-40,-15,-16,-17,-18,-19,-20,-21,-22,-23,-24,-54,122,-56,]),'MINUS':([33,39,40,43,52,53,55,56,57,58,59,60,61,62,63,64,70,73,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,95,96,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,119,120,],[57,-31,57,57,57,-38,82,-14,57,-27,-28,-29,-30,-37,-55,57,82,82,82,-39,57,57,57,57,57,57,57,57,57,57,57,-25,57,-53,82,57,-26,82,-15,-16,-17,-18,82,82,82,82,82,82,82,-54,57,82,-56,82,]),'NUMBER':([33,40,43,52,57,64,80,81,82,83,84,85,86,87,88,89,90,92,96,115,],[58,58,58,58,58,58,58,58,58,58,58,58,58,58,58,58,58,58,58,58,]),'TRUE':([33,40,43,52,57,64,80,81,82,83,84,85,86,87,88,89,90,92,96,115,],[59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,59,]),'FALSE':([33,40,43,52,57,64,80,81,82,83,84,85,86,87,88,89,90,92,96,115,],[60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,60,]),'OSQUARE':([33,40,43,52,57,61,64,80,81,82,83,84,85,86,87,88,89,90,92,96,98,115,],[64,64,64,64,64,92,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,64,]),'PLUS':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,81,-14,-27,-28,-29,-30,-37,-55,81,81,81,-39,-25,-53,81,-26,81,-15,-16,-17,-18,81,81,81,81,81,81,81,-54,81,-56,81,]),'TIMES':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,83,-14,-27,-28,-29,-30,-37,-55,83,83,83,-39,-25,-53,83,-26,83,83,83,-17,-18,83,83,83,83,83,83,83,-54,83,-56,83,]),'DIVIDE':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,84,-14,-27,-28,-29,-30,-37,-55,84,84,84,-39,-25,-53,84,-26,84,84,84,-17,-18,84,84,84,84,84,84,84,-54,84,-56,84,]),'ISEQUAL':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,85,-14,-27,-28,-29,-30,-37,-55,85,85,85,-39,-25,-53,85,-26,85,-15,-16,-17,-18,85,85,85,85,85,85,85,-54,85,-56,85,]),'ISNOTEQUAL':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,86,-14,-27,-28,-29,-30,-37,-55,86,86,86,-39,-25,-53,86,-26,86,-15,-16,-17,-18,86,86,86,86,86,86,86,-54,86,-56,86,]),'GT':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,87,-14,-27,-28,-29,-30,-37,-55,87,87,87,-39,-25,-53,87,-26,87,-15,-16,-17,-18,87,87,87,87,87,87,87,-54,87,-56,87,]),'GE':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,88,-14,-27,-28,-29,-30,-37,-55,88,88,88,-39,-25,-53,88,-26,88,-15,-16,-17,-18,88,88,88,88,88,88,88,-54,88,-56,88,]),'LT':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,89,-14,-27,-28,-29,-30,-37,-55,89,89,89,-39,-25,-53,89,-26,89,-15,-16,-17,-18,89,89,89,89,89,89,89,-54,89,-56,89,]),'LE':([39,53,55,56,58,59,60,61,62,63,70,73,78,79,91,93,95,101,102,103,104,105,106,107,108,109,110,111,112,113,114,116,119,120,],[-31,-38,90,-14,-27,-28,-29,-30,-37,-55,90,90,90,-39,-25,-53,90,-26,90,-15,-16,-17,-18,90,90,90,90,90,90,90,-54,90,-56,90,]),'COMMA':([39,53,54,55,56,58,59,60,61,62,63,70,79,91,93,94,95,101,102,103,104,105,106,107,108,109,110,111,112,114,119,120,],[-31,-38,80,-41,-14,-27,-28,-29,-30,-37,-55,-13,-39,-25,-53,115,-52,-26,-40,-15,-16,-17,-18,-19,-20,-21,-22,-23,-24,-54,-56,-51,]),'ESQUARE':([39,53,56,58,59,60,61,62,63,64,70,79,91,93,94,95,101,103,104,105,106,107,108,109,110,111,112,113,114,119,120,],[-31,-38,-14,-27,-28,-29,-30,-37,-55,93,-13,-39,-25,-53,114,-52,-26,-15,-16,-17,-18,-19,-20,-21,-22,-23,-24,119,-54,-56,-51,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'block_list':([0,50,],[1,76,]),'statement':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[2,28,51,51,51,51,51,2,51,28,51,51,51,]),'builtin_actions':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[3,3,3,3,3,3,3,3,3,3,3,3,3,]),'function_definition':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[4,4,4,4,4,4,4,4,4,4,4,4,4,]),'module_definition':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[5,5,5,5,5,5,5,5,5,5,5,5,5,]),'for_loop':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[6,6,6,6,6,6,6,6,6,6,6,6,6,]),'if_cond':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[7,7,7,7,7,7,7,7,7,7,7,7,7,]),'use':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[8,8,8,8,8,8,8,8,8,8,8,8,8,]),'include':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[9,9,9,9,9,9,9,9,9,9,9,9,9,]),'call':([0,1,32,33,34,35,36,37,40,43,50,52,57,64,71,76,80,81,82,83,84,85,86,87,88,89,90,92,96,99,115,122,123,],[10,10,10,62,10,10,10,10,62,62,10,62,62,62,10,10,62,62,62,62,62,62,62,62,62,62,62,62,62,10,62,10,10,]),'call_builtin_modules':([0,1,32,34,35,36,37,50,71,76,99,122,123,],[11,11,11,11,11,11,11,11,11,11,11,11,11,]),'assign':([0,1,32,33,34,35,36,37,40,43,50,52,57,64,71,76,80,81,82,83,84,85,86,87,88,89,90,92,96,99,115,122,123,],[12,12,12,56,12,12,12,12,56,56,12,56,56,56,12,12,56,56,56,56,56,56,56,56,56,56,56,56,56,12,56,12,12,]),'parameters':([13,14,15,16,17,19,25,26,27,38,41,61,],[32,34,35,36,37,39,46,47,48,69,71,39,]),'action_child_block':([32,34,35,36,37,71,99,122,123,],[49,65,66,67,68,97,118,124,125,]),'varargslist':([33,],[54,]),'expression':([33,40,43,52,57,64,80,81,82,83,84,85,86,87,88,89,90,92,96,115,],[55,70,73,78,91,95,102,103,104,105,106,107,108,109,110,111,112,113,116,120,]),'array_right':([33,40,43,52,57,64,80,81,82,83,84,85,86,87,88,89,90,92,96,98,115,],[63,63,63,63,63,63,63,63,63,63,63,63,63,63,63,63,63,63,63,117,63,]),'array_list':([64,],[94,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> block_list","S'",1,None,None,None),
  ('block_list -> statement','block_list',1,'p_block_list','scadlike_parser.py',48),
  ('block_list -> block_list statement','block_list',2,'p_block_list','scadlike_parser.py',49),
  ('statement -> builtin_actions','statement',1,'p_statement_action','scadlike_parser.py',58),
  ('statement -> function_definition','statement',1,'p_statement_action','scadlike_parser.py',59),
  ('statement -> module_definition','statement',1,'p_statement_action','scadlike_parser.py',60),
  ('statement -> for_loop','statement',1,'p_statement_action','scadlike_parser.py',61),
  ('statement -> if_cond','statement',1,'p_statement_action','scadlike_parser.py',62),
  ('statement -> use','statement',1,'p_statement_action','scadlike_parser.py',63),
  ('statement -> include','statement',1,'p_statement_action','scadlike_parser.py',64),
  ('statement -> call SEMICOLON','statement',2,'p_statement_call','scadlike_parser.py',68),
  ('statement -> call_builtin_modules SEMICOLON','statement',2,'p_statement_call_builtin_modules','scadlike_parser.py',73),
  ('statement -> assign SEMICOLON','statement',2,'p_statement_assign','scadlike_parser.py',77),
  ('assign -> ID EQUALS expression','assign',3,'p_assign','scadlike_parser.py',81),
  ('expression -> assign','expression',1,'p_expression_assign','scadlike_parser.py',85),
  ('expression -> expression PLUS expression','expression',3,'p_expression_binop','scadlike_parser.py',90),
  ('expression -> expression MINUS expression','expression',3,'p_expression_binop','scadlike_parser.py',91),
  ('expression -> expression TIMES expression','expression',3,'p_expression_binop','scadlike_parser.py',92),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_binop','scadlike_parser.py',93),
  ('expression -> expression ISEQUAL expression','expression',3,'p_expression_binop','scadlike_parser.py',94),
  ('expression -> expression ISNOTEQUAL expression','expression',3,'p_expression_binop','scadlike_parser.py',95),
  ('expression -> expression GT expression','expression',3,'p_expression_binop','scadlike_parser.py',96),
  ('expression -> expression GE expression','expression',3,'p_expression_binop','scadlike_parser.py',97),
  ('expression -> expression LT expression','expression',3,'p_expression_binop','scadlike_parser.py',98),
  ('expression -> expression LE expression','expression',3,'p_expression_binop','scadlike_parser.py',99),
  ('expression -> MINUS expression','expression',2,'p_expression_unop','scadlike_parser.py',105),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_group','scadlike_parser.py',109),
  ('expression -> NUMBER','expression',1,'p_expression_number','scadlike_parser.py',113),
  ('expression -> TRUE','expression',1,'p_expression_bool','scadlike_parser.py',117),
  ('expression -> FALSE','expression',1,'p_expression_bool','scadlike_parser.py',118),
  ('expression -> ID','expression',1,'p_expression_name','scadlike_parser.py',122),
  ('call -> ID parameters','call',2,'p_call','scadlike_parser.py',130),
  ('use -> USE USESTRING SEMICOLON','use',3,'p_use','scadlike_parser.py',134),
  ('include -> INCLUDE USESTRING SEMICOLON','include',3,'p_include','scadlike_parser.py',138),
  ('call_builtin_modules -> LINE parameters','call_builtin_modules',2,'p_call_builtin_modules','scadlike_parser.py',142),
  ('call_builtin_modules -> FILLET parameters','call_builtin_modules',2,'p_call_builtin_modules','scadlike_parser.py',143),
  ('call_builtin_modules -> CUBE parameters','call_builtin_modules',2,'p_call_builtin_modules','scadlike_parser.py',144),
  ('expression -> call','expression',1,'p_expression_call','scadlike_parser.py',150),
  ('parameters -> LPAREN RPAREN','parameters',2,'p_parameters','scadlike_parser.py',155),
  ('parameters -> LPAREN varargslist RPAREN','parameters',3,'p_parameters','scadlike_parser.py',156),
  ('varargslist -> varargslist COMMA expression','varargslist',3,'p_varargslist','scadlike_parser.py',163),
  ('varargslist -> expression','varargslist',1,'p_varargslist','scadlike_parser.py',164),
  ('action_child_block -> OBRACE block_list EBRACE','action_child_block',3,'p_action_child_block','scadlike_parser.py',171),
  ('action_child_block -> statement','action_child_block',1,'p_action_child_block','scadlike_parser.py',172),
  ('action_child_block -> OBRACE EBRACE','action_child_block',2,'p_action_child_block','scadlike_parser.py',173),
  ('builtin_actions -> PROFILE parameters action_child_block','builtin_actions',3,'p_builtin_actions','scadlike_parser.py',182),
  ('builtin_actions -> LINEAR_EXTRUDE parameters action_child_block','builtin_actions',3,'p_builtin_actions','scadlike_parser.py',183),
  ('builtin_actions -> MIRROR parameters action_child_block','builtin_actions',3,'p_builtin_actions','scadlike_parser.py',184),
  ('builtin_actions -> ROTATE parameters action_child_block','builtin_actions',3,'p_builtin_actions','scadlike_parser.py',185),
  ('builtin_actions -> TRANSLATE parameters action_child_block','builtin_actions',3,'p_builtin_actions','scadlike_parser.py',186),
  ('function_definition -> FUNCTION ID parameters EQUALS expression SEMICOLON','function_definition',6,'p_function_definition','scadlike_parser.py',190),
  ('array_list -> array_list COMMA expression','array_list',3,'p_array_list','scadlike_parser.py',194),
  ('array_list -> expression','array_list',1,'p_array_list','scadlike_parser.py',195),
  ('array_right -> OSQUARE ESQUARE','array_right',2,'p_array_right','scadlike_parser.py',204),
  ('array_right -> OSQUARE array_list ESQUARE','array_right',3,'p_array_right','scadlike_parser.py',205),
  ('expression -> array_right','expression',1,'p_expression_array','scadlike_parser.py',212),
  ('expression -> ID OSQUARE expression ESQUARE','expression',4,'p_expression_array_element','scadlike_parser.py',216),
  ('for_loop -> FOR LPAREN ID EQUALS array_right RPAREN action_child_block','for_loop',7,'p_for_loop','scadlike_parser.py',220),
  ('if_cond -> IF LPAREN expression RPAREN action_child_block','if_cond',5,'p_if_cond','scadlike_parser.py',224),
  ('if_cond -> IF LPAREN expression RPAREN action_child_block ELSE action_child_block','if_cond',7,'p_if_cond','scadlike_parser.py',225),
  ('module_definition -> MODULE ID parameters action_child_block','module_definition',4,'p_module_definition','scadlike_parser.py',232),
]