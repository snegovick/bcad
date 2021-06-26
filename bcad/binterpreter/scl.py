from bcad.binterpreter.scadlike_parser import ScadLikeParser, ParserError

#from imcad import *
#from imcad.core.context import BaseContext, BaseElement, current

import os
import numpy as np
import json
import math
import traceback

from logging import debug, info, warning, error, critical
import logging


from bcad.binterpreter.events import EVEnum, EventProcessor, ee, ep
from bcad.binterpreter.singleton import Singleton
from bcad.binterpreter.scl_writer import SCLSTLWriter, SCLSTEPWriter, SCLDXFWriter
from bcad.binterpreter.scl_util import Noval, unstringify, sign
from bcad.binterpreter.scl_context import V2, V3, SCLContext, SCLProfile2, SCLExtrude, SCLUnion, SCLIntersection, SCLDifference, SCLProjection, SCLPart3, SCLLoft, get_inc_name
from bcad.binterpreter.args import parse_args

debug_parser=False
debug_expr_en = False

def debug_expr(msg):
    if (debug_expr_en):
        debug(msg)

class UnknownVariableError(Exception):
    def __init__(self, varname, line):
        self.message = "Unknown variable %s at line %i"%(varname, line)

class UnknownFunctionError(Exception):
    def __init__(self, fname, line):
        self.message = "Unknown function %s at line %i"%(fname, line)

class UnknownModuleError(Exception):
    def __init__(self, fname, line):
        self.message = "Unknown module %s at line %i"%(fname, line)

class UnhandledCaseError(Exception):
    def __init__(self, message):
        self.message = "Unhandled case encountered: %s"%(message)

class SyntaxError(Exception):
    def __init__(self, message, line):
        self.message = "Syntax error at line %i: %s"%(line, message)

rotate_module_definition = {'type': 'stat_module_definition', 'id': 'rotate', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'array_list', 'line': 0, 'val': [
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0}
    ]}}]}
polygon_module_definition = {'type': 'stat_module_definition', 'id': 'polygon', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'points', 'val': {'type': 'array_list', 'line': 0, 'val': []}},
    {'type': 'expr_assign', 'id': 'paths', 'val': {'type': 'array_list', 'line': 0, 'val': []}},
]}
translate_module_definition = {'type': 'stat_module_definition', 'id': 'translate', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'array_list', 'line': 0, 'val': [
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0}
    ]}}]}
color_module_definition = {'type': 'stat_module_definition', 'id': 'color', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'array_list', 'line': 0, 'val': [
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0}
    ]}}]}
profile_module_definition = {'type': 'stat_module_definition', 'id': 'profile', 'line': 0, 'args': []}
linear_extrude_module_definition = {'type': 'stat_module_definition', 'id': 'linear_extrude', 'line': 0, 'args': [{'type': 'expr_assign', 'id': 'height', 'val': {'type': 'expr_number', 'val': 1.0, 'line': 0}, 'line': 0}]}
union_module_definition = {'type': 'stat_module_definition', 'id': 'union', 'line': 0, 'args': []}
intersection_module_definition = {'type': 'stat_module_definition', 'id': 'intersection', 'line': 0, 'args': []}
difference_module_definition = {'type': 'stat_module_definition', 'id': 'difference', 'line': 0, 'args': []}
mirror_module_definition = {'type': 'stat_module_definition', 'id': 'mirror', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'array_list', 'line': 0, 'val': [
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0}
    ]}}]}
fillet_module_definition = {'type': 'stat_module_definition', 'id': 'fillet', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'r', 'val': {'type': 'expr_number', 'val': 1.0, 'line': 0}, 'line': 0}
]}
import_step_module_definition = {'type': 'stat_module_definition', 'id': 'fillet', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'filename', 'val': {'type': 'expr_string', 'val': "", 'line': 0}, 'line': 0}
]}
import_stl_module_definition = {'type': 'stat_module_definition', 'id': 'fillet', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'filename', 'val': {'type': 'expr_string', 'val': "", 'line': 0}, 'line': 0}
]}
line_module_definition = {'type': 'stat_module_definition', 'id': 'line', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'start', 'val': {'type': 'array_list', 'line': 0, 'val': [
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0}
    ]}},
    {'type': 'expr_assign', 'id': 'end', 'val': {'type': 'array_list', 'line': 0, 'val': [
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0},
        {'type': 'expr_number', 'val': 0.0, 'line': 0}
    ]}}
]}
cube_module_definition = {'type': 'stat_module_definition', 'id': 'cube', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'array_list', 'line': 0, 'val': [
        {'type': 'expr_number', 'val': 1.0, 'line': 0},
        {'type': 'expr_number', 'val': 1.0, 'line': 0},
        {'type': 'expr_number', 'val': 1.0, 'line': 0}
    ]}},
    {'type': 'expr_assign', 'id': 'center', 'line': 0, 'val': {'type': 'expr_bool', 'line': 0, 'val': False}}
]}
cylinder_module_definition = {'type': 'stat_module_definition', 'id': 'cylinder', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'r', 'val': {'type': 'expr_number', 'line': 0, 'val': Noval}},
    {'type': 'expr_assign', 'id': 'd', 'val': {'type': 'expr_number', 'line': 0, 'val': Noval}},
    {'type': 'expr_assign', 'id': 'r1', 'val': {'type': 'expr_number', 'line': 0, 'val': Noval}},
    {'type': 'expr_assign', 'id': 'd1', 'val': {'type': 'expr_number', 'line': 0, 'val': Noval}},
    {'type': 'expr_assign', 'id': 'r2', 'val': {'type': 'expr_number', 'line': 0, 'val': Noval}},
    {'type': 'expr_assign', 'id': 'd2', 'val': {'type': 'expr_number', 'line': 0, 'val': Noval}},
    {'type': 'expr_assign', 'id': 'h', 'val': {'type': 'expr_number', 'line': 0, 'val': 1.0}},
    {'type': 'expr_assign', 'id': 'center', 'line': 0, 'val': {'type': 'expr_bool', 'line': 0, 'val': False}}
]}

sqrt_function_definition = {'type': 'stat_function_definition', 'id': 'sqrt', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'expr_number', 'val': 0.0, 'line': 0}, 'line': 0}
]}

sin_function_definition = {'type': 'stat_function_definition', 'id': 'sin', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'expr_number', 'val': 0.0, 'line': 0}, 'line': 0}
]}

cos_function_definition = {'type': 'stat_function_definition', 'id': 'cos', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'expr_number', 'val': 0.0, 'line': 0}, 'line': 0}
]}

tan_function_definition = {'type': 'stat_function_definition', 'id': 'tan', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'val': {'type': 'expr_number', 'val': 0.0, 'line': 0}, 'line': 0}
]}

reverse_function_definition = {'type': 'stat_function_definition', 'id': 'reverse', 'line': 0, 'args': [
    {'type': 'expr_assign', 'id': 'v', 'line': 0, 'val': {'type': 'array_list', 'val': [], 'line': 0}}
]}

concat_function_definition = {'type': 'stat_function_definition', 'id': 'concat', 'line': 0, 'args': [
]}
loft_module_definition = {'type': 'stat_module_definition', 'id': 'loft', 'line': 0, 'args': [{'type': 'expr_assign', 'id': 'solid', 'val': {'type': 'expr_bool', 'val': True, 'line': 0}, 'line': 0},
                                                                                              {'type': 'expr_assign', 'id': 'ruled', 'val': {'type': 'expr_bool', 'val': True, 'line': 0}, 'line': 0},
                                                                                              {'type': 'expr_assign', 'id': 'precision', 'val': {'type': 'expr_number', 'val': 0.000001, 'line': 0}, 'line': 0}]}

class SCLFrame:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.modules = {}

    def get_variable_value(self, varname, line):
        if varname in self.variables:
            return self.variables[varname]
        raise UnknownVariableError(varname, line)

    def has_variable(self, varname, line):
        if varname in self.variables:
            return True
        return False

    def set_variable(self, varname, value, line):
        self.variables[varname] = value

    def get_function(self, fname, line):
        if fname in self.functions:
            return self.functions[fname]
        raise UnknownFunctionError(fname, line)

    def has_function(self, fname, line):
        if fname in self.functions:
            return True
        return False

    def set_function(self, fname, value, line):
        self.functions[fname] = value

    def get_module(self, mname, line):
        if mname in self.modules:
            return self.modules[mname]
        raise UnknownModuleError(mname, line)

    def has_module(self, mname, line):
        debug('SCLFrame:%i:Check module %s existance'%(line, mname))
        if mname in self.modules:
            return True
        return False

    def set_module(self, mname, value, line):
        debug('SCLFrame:%i:Setting module %s'%(line, mname))
        self.modules[mname] = value

class SCL:
    def __init__(self, data=None, path=None, output_path=None, verbose=3, extra={}):
        debug('SCL data: %s, path: %s'%(data, path))
        self.extra = extra
        self.output_path = output_path
        self.data = data
        if self.output_path == None:
            ep.push_event(ee.init_display, None)
            ep.process()
        self.stack = [SCLFrame()]
        self.verbose = verbose
        if verbose == 0:
            logging.getLogger("").setLevel(logging.CRITICAL)
        elif verbose == 1:
            logging.getLogger("").setLevel(logging.ERROR)
        elif verbose == 2:
            logging.getLogger("").setLevel(logging.WARNING)
        elif verbose == 3:
            logging.getLogger("").setLevel(logging.INFO)
        elif verbose >= 4:
            logging.getLogger("").setLevel(logging.DEBUG)

        self.debug=False

        self.path = path

    def reload_file(self):
        self.stack = [SCLFrame()]
        self.load_file()

    def load_file(self):
        filename, ext = os.path.splitext(self.path)
        run_parser = True
        if (ext == '.sck'):
            self.root = SCLProfile2(None)
        elif ((ext == '.scp') or (ext == '.scad')):
            self.root = SCLPart3(None)
        elif ((ext == '.stp') or (ext == '.step') or (ext == '.STP') or (ext == '.STEP')):
            self.root = SCLPart3(None)
            self.root.import_step(self.path)
            run_parser = False
        else:
            warning("Unknown file type %s"%(ext,))

        writer = None
        if self.output_path != None:
            filename, ext = os.path.splitext(self.output_path)
            if (ext == '.step'):
                writer = SCLSTEPWriter()
            elif (ext == '.stl'):
                writer = SCLSTLWriter()
                if (("linear-deflection" in self.extra) and
                    ("angular-deflection" in self.extra)):
                    writer.set_resolution(self.extra["linear-deflection"], self.extra["angular-deflection"])
            elif (ext == '.dxf'):
                writer = SCLDXFWriter()
            
        self.root.set_name("root")

        self.context = self.root
        self.active_context = self.context

        if run_parser:
            slp = None
            try:
                slp = ScadLikeParser(data=self.data, path=self.path, debug=self.debug)
                ep.push_event(ee.parse_file, self.path)
            except ParserError as pe:
                critical("%s:%i Unknown expression: %s"%(self.path, pe.lineno, pe.message))
                if (self.verbose>=4):
                    traceback.print_exc()
            else:
                debug(json.dumps(slp.data, indent=2))
                for s in slp.data:
                    self.parse_statement(s)

        debug("Display context")
        self.context.display(writer)
        
        if self.output_path != None:
            writer.Write(self.output_path)

    def push_context(self, ctx, name):
        n = ctx(self.active_context)
        n.set_name(name)
        self.active_context.add_child_context(n)
        self.active_context = n

    def pop_context(self):
        self.active_context = self.active_context.parent

    def find_variable_value(self, varname, line, print_function=debug):
        val = None
        print_function('SCL:%i:Looking for variable %s'%(line, varname,))

        for f in reversed(self.stack):
            try:
                val = f.get_variable_value(varname, line)
            except:
                pass
            else:
                print_function("Found value %s"%(val,))
                return val
        raise UnknownVariableError(varname, line)

    def set_variable(self, varname, value, line):
        debug('SCL:%i:Setting variable %s: %s'%(line, varname, value))
        top = self.stack[-1]
        top.set_variable(varname, value, line)

    def find_function(self, fname, line):
        val = None
        debug('SCL:%i:Looking for function %s'%(line, fname,))

        for f in reversed(self.stack):
            try:
                val = f.get_function(fname, line)
            except:
                pass
            else:
                debug("Found function %s"%(fname,))
                return val
        raise UnknownFunctionError(fname, line)

    def set_function(self, fname, value, line):
        debug('SCL:%i:Setting function %s'%(line, fname))
        top = self.stack[-1]
        top.set_function(fname, value, line)

    def find_module(self, mname, line):
        val = None
        debug('SCL:%i:Looking for module %s'%(line, mname,))

        for f in reversed(self.stack):
            try:
                val = f.get_module(mname, line)
            except:
                pass
            else:
                debug("Found module %s"%(mname,))
                return val
        raise UnknownModuleError(mname, line)

    def set_module(self, mname, value, line):
        debug('SCL:%i:Setting module %s'%(line, mname))
        top = self.stack[-1]
        top.set_module(mname, value, line)

    def find_callable(self, callable_name, line):
        cbl = None
        try:
            cbl = self.find_module(callable_name, line)
        except:
            try:
                cbl = self.find_function(callable_name, line)
            except:
                raise RuntimeError("No callable with name %s"%(callable_name), line)
        return cbl

    def push_stack(self):
        self.stack.append(SCLFrame())

    def pop_stack(self):
        self.stack.pop()

    def parse_expr(self, e):
        debug_expr('Parse expr %s'%(e,))
        if 'type' not in e:
            raise UnhandledCaseError('type is not set: %s'%(e,))
        t = e['type']
        debug_expr("%i:%s"%(e['line'],t))
        if t=='expr_number':
            return e['val']
        if t=='expr_string':
            return e['val']
        elif t=='expr_bool':
            return e['val']
        elif t=='expr_assign':
            val = self.parse_expr(e['val'])
            self.set_variable(e['id'], val, e['line'])
            return val
        elif t=='expr_binop':
            e1 = e['val'][0]
            e2 = e['val'][1]
            op = e['val'][2]
            e1num=self.parse_expr(e1)
            e2num=self.parse_expr(e2)
            debug_expr('%s %s %s'%(e1num, op, e2num))
            if op == '+':
                return e1num+e2num
            elif op == '-':
                return e1num-e2num
            elif op == '*':
                return e1num*e2num
            elif op == '/':
                return e1num/e2num
            elif op == '%':
                return e1num%e2num
            elif op == '==':
                debug("Compare %s == %s -> %s"%((e1num), str(e2num), str(e1num==e2num)))
                return e1num==e2num
            elif op == '!=':
                return e1num!=e2num
            elif op == '<':
                return e1num<e2num
            elif op == '>':
                return e1num>e2num
            elif op == '>=':
                return e1num>=e2num
            elif op == '<=':
                return e1num<=e2num
            else:
                raise UnhandledCaseError('unknown operation %s at line %i'%(op,e['line']))
        elif e['type']=='expr_unop':
            ev=e['val'][0]
            en=self.parse_expr(ev)
            if (isinstance(en, list)):
                return [-v for v in en]
            return -en
        elif t=='expr_terop':
            condition = e['val']['condition']
            true_branch = e['val']['true']
            false_branch = e['val']['false']
            condition=self.parse_expr(condition)
            result = None
            if (condition):
                result=self.parse_expr(true_branch)
            else:
                result=self.parse_expr(false_branch)
            return result
        elif e['type']=='expr_id':
            ev = e['val']
            return self.find_variable_value(ev, e['line'], debug_expr)
        elif e['type']=='array_list':
            arr = []
            for ev in e['val']:
                arr.append(self.parse_expr(ev))
            return arr
        elif e['type']=='array_range':
            step = 1.0
            if 'step' in e['val']:
                step = self.parse_expr(e['val']['step'])
            start = self.parse_expr(e['val']['start'])
            end = self.parse_expr(e['val']['end'])
            if ((end>=start) and (step>0)) or ((end<=start) and (step<0)):
                v = start
                arr = [v]
                diff = v-end
                pdiff = diff
                while (True):
                    v+=step
                    diff = v-end
                    if (diff!=0) and (sign(diff)!=sign(pdiff)):
                        break
                    arr.append(v)
                    pdiff = diff
            else:
                arr = []
                
            debug("arr: %s"%(str(arr),))
            return arr
        elif e['type']=='expr_call':
            self.push_stack()
            if e['id'] == 'sqrt':
                self.parse_kwargs(e['id'], e['line'], sqrt_function_definition['args'], e['args'], debug_expr)
                top = self.stack[-1]
                v = 0
                if (top.has_variable('v', e['line'])):
                    v = self.find_variable_value('v', e['line'], debug_expr)
                debug_expr("Call builtin sqrt(%f)"%(v,))
                ret = math.sqrt(v)
            elif e['id'] == 'reverse':
                self.parse_kwargs(e['id'], e['line'], reverse_function_definition['args'], e['args'], debug_expr)
                top = self.stack[-1]
                v = 0
                if (top.has_variable('v', e['line'])):
                    v = self.find_variable_value('v', e['line'], debug_expr)
                rv = v[:]
                rv.reverse()
                ret = rv
                debug_expr("Call builtin reverse(%s)->(%s)"%(str(v),str(ret)))
            elif e['id'] == 'concat':
                top = self.stack[-1]
                ov = []
                for i, a in enumerate(s['args']):
                    val = str(self.parse_expr(a))
                    ov+=val
                debug_expr("Call builtin concat %s"%(str(ov),))
                ret = ov
            elif e['id'] == 'sin':
                self.parse_kwargs(e['id'], e['line'], sin_function_definition['args'], e['args'], debug_expr)
                top = self.stack[-1]
                v = 0
                if (top.has_variable('v', e['line'])):
                    v = self.find_variable_value('v', e['line'], debug_expr)
                debug_expr("Call builtin sin(%f)"%(v,))
                ret = math.sin(math.radians(v))
            elif e['id'] == 'cos':
                self.parse_kwargs(e['id'], e['line'], cos_function_definition['args'], e['args'], debug_expr)
                top = self.stack[-1]
                v = 0
                if (top.has_variable('v', e['line'])):
                    v = self.find_variable_value('v', e['line'], debug_expr)
                debug_expr("Call builtin cos(%f)"%(v,))
                ret = math.cos(math.radians(v))
            elif e['id'] == 'tan':
                self.parse_kwargs(e['id'], e['line'], tan_function_definition['args'], e['args'], debug_expr)
                top = self.stack[-1]
                v = 0
                if (top.has_variable('v', e['line'])):
                    v = self.find_variable_value('v', e['line'], debug_expr)
                debug_expr("Call builtin tan(%f)"%(v,))
                ret = math.tan(math.radians(v))
            else:
                cbl = self.find_function(e['id'], e['line'])
                debug_expr('Found function %s'%(e['id'],))
                self.parse_kwargs(e['id'], e['line'], cbl['args'], e['args'], debug_expr)
                ret = self.parse_expr(cbl['expression'])
                debug_expr('Function %s done'%(e['id']))
            self.pop_stack()
            return ret
        elif e['type']=='array_access':
            val=self.find_variable_value(e['id'], e['line'], debug_expr)
            idx=self.parse_expr(e['index'])
            return val[int(idx)]
        else:
            raise UnhandledCaseError('unknown expression type \'%s\''%(t,))
        raise UnhandledCaseError('unknown error')

    def check_kwargs(self, args):
        prev_arg = None
        debug('args: %s'%(str(args),))
        for a in args:
            if prev_arg!=None:
                if (prev_arg['type'] == 'expr_assign') and (a['type'] != 'expr_assign'):
                    raise SyntaxError("positional argument after keyword argument", a['line'])
            prev_arg = a
    
    def check_kwargs_definition(self, args_definition):
        prev_arg = None
        debug("args definition: %s"%(str(args_definition), ))
        for a in args_definition:
            debug("Checking argument %s"%(a,))
            if prev_arg!=None:
                if (prev_arg['type'] == 'expr_assign') and (a['type'] == 'expr_name'):
                    raise SyntaxError("positional argument after keyword argument", a['line'])
                prev_arg = a
            if (a['type'] != 'expr_assign') and (a['type'] != 'expr_id'):
                raise SyntaxError("illegal argument", a['line'])
        self.check_kwargs(args_definition)

    def get_args_list(self, args_definition):
        def_vals = {}
        arg_list = []
        positional = 0
        debug('args_deginition: %s'%(str(args_definition),))
        for a in args_definition:
            defval = None
            argid = None
            if (a['type']!='expr_id'):
                defval = self.parse_expr(a['val'])
                argid = a['id']
            else:
                positional += 1
                argid = a['val']
            def_vals[argid] = defval
            arg_list.append(argid)
        return def_vals, arg_list, positional

    def parse_kwargs(self, name, line, args_definition, args, print_function=debug):
        print_function('kwargs args: %s'%(str(args),))
        self.check_kwargs_definition(args_definition)
        self.check_kwargs(args)
        def_vals, arg_list, positional = self.get_args_list(args_definition)
        print_function('defvals: %s, arglist: %s, positional: %i'%(def_vals, arg_list, positional))
        if (positional > len(args)):
            raise SyntaxError("%s takes %i positional arguments, but %i arguments supplied"%(name, positional, len(args)), line)
        if (len(args)>len(args_definition)):
            raise SyntaxError("%s takes %i arguments, but %i arguments supplied"%(name, len(args_definition), len(args)), line)   
        top = self.stack[-1]
        position = 0
        for a in args:
            if a['type'] != 'expr_assign':
                print_function('assign: %s'%(str(a),))
                self.set_variable(arg_list[position], self.parse_expr(a), a['line'])
            else:
                self.set_variable(a['id'], self.parse_expr(a['val']), a['line'])
            position+=1
        print_function('kwargs args: %s'%(args,))
        if (def_vals!=None):
            for k,v in def_vals.items():
                if (not top.has_variable(k, line)):
                    self.set_variable(k, v, line)

    def parse_block(self, block):
        for statement in block:
            self.parse_statement(statement)

    def parse_statement(self, s, use=False):
        debug("Parse statement %s"%(s,))
        if 'type' not in s:
            raise UnhandledCaseError('Statement type unknown: %s'%(s,))
        t = s['type']
        debug("%i:%s"%(s['line'],s['type']))
        if t=='stat_assign':
            self.parse_expr(s['val'])
        elif t=='stat_builtin':
            if use:
                debug("Skip builtin because \"use\" is set")
            else:
                if s['id'] == 'linear_extrude':
                    self.push_stack()
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.push_context(SCLExtrude, get_inc_name("linear_extrude"))
                        self.parse_block(s['block'])
                        self.push_stack()
                        self.parse_kwargs(s['id'], s['line'], linear_extrude_module_definition['args'], s['args'])
                        l = 1
                        top = self.stack[-1]
                        if (top.has_variable('height', s['line'])):
                            l = self.find_variable_value('height', s['line'])
                            
                        debug("Call builtin extrude(%f)"%(l,))
                        self.active_context.linear_extrude(l)
                        self.pop_stack()
                        self.pop_context()
                    debug("Leave linear extrude")
                    self.pop_stack()
                elif s['id'] == 'loft':
                    self.push_stack()
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.push_context(SCLLoft, get_inc_name("loft"))
                        self.parse_block(s['block'])
                        self.push_stack()
                        self.parse_kwargs(s['id'], s['line'], loft_module_definition['args'], s['args'])
                        solid = True
                        ruled = True
                        precision = 0.000001
                        top = self.stack[-1]
                        if (top.has_variable('solid', s['line'])):
                            solid = self.find_variable_value('solid', s['line'])
                        if (top.has_variable('ruled', s['line'])):
                            ruled = self.find_variable_value('ruled', s['line'])
                        if (top.has_variable('precision', s['line'])):
                            precision = self.find_variable_value('precision', s['line'])
                        debug("Call builtin loft(%s, %s, %f)"%(str(solid), str(ruled), precision))
                        self.active_context.loft(solid, ruled, precision)
                        self.pop_stack()
                        self.pop_context()
                    debug("Leave loft")
                    self.pop_stack()
                elif s['id']=='profile':
                    debug("Profile")
                    self.push_stack()

                    debug("Call builtin profile()")
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.push_context(SCLProfile2, get_inc_name("profile2"))
                        self.parse_block(s['block'])
                        self.pop_context()
                    debug("Leave profile")
                    self.pop_stack()
                elif s['id'] == 'union':
                    self.push_stack()
                    top = self.stack[-1]

                    debug("Call union()")
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.push_context(SCLUnion, get_inc_name("union"))
                        self.parse_block(s['block'])
                        self.active_context.union()
                        self.pop_context()
                    debug("Leave union")
                    self.pop_stack()
                elif s['id'] == 'intersection':
                    self.push_stack()
                    top = self.stack[-1]

                    debug("Call intersection()")
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.push_context(SCLIntersection, get_inc_name("intersection"))
                        self.parse_block(s['block'])
                        self.active_context.intersection()
                        self.pop_context()
                    debug("Leave intersection")
                    self.pop_stack()
                elif s['id'] == 'difference':
                    self.push_stack()
                    top = self.stack[-1]
                    debug("Call difference()")
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.push_context(SCLDifference, get_inc_name("difference"))
                        self.parse_block(s['block'])
                        self.active_context.difference()
                        self.pop_context()
                    debug("Leave difference")
                    self.pop_stack()
                elif s['id'] == 'projection':
                    self.push_stack()
                    top = self.stack[-1]
                    debug("Call projection()")
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.push_context(SCLProjection, get_inc_name("projection"))
                        self.parse_block(s['block'])
                        self.active_context.projection()
                        self.pop_context()
                    debug("Leave projection")
                    self.pop_stack()

                elif s['id']=='rotate':
                    debug("Rotate")
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], rotate_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    v = [0,0,0]
                    if (top.has_variable('v', s['line'])):
                        v_ = self.find_variable_value('v', s['line'])
                        l = (len(v) if (len(v)<len(v_)) else (len(v_)))
                        for i in range(l):
                            v[i] = v_[i]
                    self.push_context(SCLPart3, get_inc_name("rotate"))
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.parse_block(s['block'])
                        debug("Call builtin rotate(%f,%f,%f)"%(v[0],v[1],v[2]))
                        self.active_context.rotate(v[0],v[1],v[2])
                    debug("Leave rotate [%s]"%(self.active_context.name))
                    self.pop_context()
                    self.pop_stack()

                elif s['id']=='display_wireframe':
                    debug("Display wireframe")
                    self.push_stack()
                    self.push_context(SCLPart3, get_inc_name("display_wireframe"))
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.parse_block(s['block'])
                        debug("Call builtin display_wireframe()")
                        self.active_context.display_wireframe()
                    debug("Leave display_wireframe [%s]"%(self.active_context.name))
                    self.pop_context()
                    self.pop_stack()
                elif s['id']=='translate':
                    debug("translate")
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], translate_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    v = [0,0,0]
                    if (top.has_variable('v', s['line'])):
                        v_ = self.find_variable_value('v', s['line'])
                        l = (len(v) if (len(v)<len(v_)) else (len(v_)))
                        for i in range(l):
                            v[i] = v_[i]
                    self.push_context(SCLPart3, get_inc_name("translate"))
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.parse_block(s['block'])
                        debug("Call builtin translate(%f,%f,%f) line: %i [%s]"%(v[0],v[1],v[2], s['line'], self.active_context.name))
                        self.active_context.translate(v[0],v[1],v[2])
                    debug("Leave translate [%s]"%(self.active_context.name))
                    self.pop_context()
                    self.pop_stack()
                elif s['id']=='color':
                    debug("color")
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], color_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    v = [0,0,0]
                    if (top.has_variable('v', s['line'])):
                        v_ = self.find_variable_value('v', s['line'])
                        l = (len(v) if (len(v)<len(v_)) else (len(v_)))
                        if type(v_) == list:
                            for i in range(l):
                                v[i] = v_[i]
                        else:
                            v = v_
                    self.push_context(SCLPart3, get_inc_name("color"))
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        self.parse_block(s['block'])
                        debug("Call builtin color(%s) line: %i [%s]"%(str(v), s['line'], self.active_context.name))
                        self.active_context.color(v)
                    debug("Leave color [%s]"%(self.active_context.name))
                    self.pop_context()
                    self.pop_stack()
                elif s['id']=='mirror':
                    debug("Mirror")
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], mirror_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    v = [0,0,0]
                    if (top.has_variable('v', s['line'])):
                        v_ = self.find_variable_value('v', s['line'])
                        l = (len(v) if (len(v)<len(v_)) else (len(v_)))
                        for i in range(l):
                            v[i] = v_[i]
                    self.push_context(SCLPart3, get_inc_name("mirror"))
                    if debug_parser:
                        self.parse_block(s['block'])
                    else:
                        debug("Call builtin mirror(%f, %f, %f)"%(v[0],v[1], v[2]))
                        self.parse_block(s['block'])
                        self.active_context.mirror(v[0], v[1], v[2])
                    debug("Leave mirror")
                    self.pop_context()
                    self.pop_stack()
                else:
                    raise UnhandledCaseError('unknown builtin statement \"%s\"'%(s['id'],))
        elif t=='stat_call':
            if use:
                debug("Skip call because \"use\" is set")
            else:
                if (s['id'] == 'print') or (s['id'] == 'echo'):
                    top = self.stack[-1]
                    out = "PRINT[@"+str(s['line'])+']: '
                    for i, a in enumerate(s['args']):
                        val = str(self.parse_expr(a))
                        out+=val
                        if i<(len(s['args'])-1):
                            out+=', '
                    print(out)
                else:
                    self.push_stack()
                    cbl = self.find_module(s['id'], s['line'])
                    debug('Found module %s'%(s['id'],))
                    self.parse_kwargs(s['id'], s['line'], cbl['args'], s['args'])
                    for statement in cbl['block']:
                        debug('Parse statement %s'%(statement,))
                        self.parse_statement(statement)
                    debug('Module %s done'%(s['id']))
                    self.pop_stack()
        elif t=='stat_call_builtin_modules':
            if use:
                debug("Skip call builtin modules because \"use\" is set")
            else:
                mid = s['id']
                args = s['args']
                if mid=='line':
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], line_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    st = [0,0,0]
                    e = [0,0,0]
                    if (top.has_variable('start', s['line'])):
                        st_ = self.find_variable_value('start', s['line'])
                        l = (len(st) if (len(st)<len(st_)) else (len(st_)))
                        for i in range(l):
                            st[i] = st_[i]
                    if (top.has_variable('end', s['line'])):
                        e_ = self.find_variable_value('end', s['line'])
                        l = (len(e) if (len(e)<len(e_)) else (len(e_)))
                        for i in range(l):
                            e[i] = e_[i]
                    debug("Call builtin line(%s->%s)"%(st, e))
                    if not debug_parser:
                        self.active_context.line(V3(st[0],st[1],st[2]), V3(e[0],e[1],e[2]))
                    else:
                        pass
                    self.pop_stack()
                elif mid=='fillet':
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], fillet_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    r = 1.0
                    if (top.has_variable('r', s['line'])):
                        r = self.find_variable_value('r', s['line'])

                    debug("Call builtin fillet(%f)"%(r,))
                    if not debug_parser:
                        self.active_context.fillet(r)
                    else:
                        pass
                    self.pop_stack()
                elif mid=='polygon':
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], polygon_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    points = Noval
                    paths = Noval
                    if (top.has_variable('points', s['line'])):
                        points = self.find_variable_value('points', s['line'])
                    if (top.has_variable('paths', s['line'])):
                        paths = self.find_variable_value('paths', s['line'])
                    debug("Call builtin polygon(%s, %s) line: %i"%(str(points), str(paths), s['line']))
                    if not debug_parser:
                        self.push_context(SCLPart3, get_inc_name("part"))
                        try:
                            self.active_context.polygon(points, paths, s['id'], s['line'])
                        except BaseException as e:
                            warning(str(e))
                        self.pop_context()
                    else:
                        pass
                    self.pop_stack()
                elif mid=='cube':
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], cube_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    v = [1.0, 1.0, 1.0]
                    center = False
                    if (top.has_variable('v', s['line'])):
                        v_ = self.find_variable_value('v', s['line'])
                        l = (len(v) if (len(v)<len(v_)) else (len(v_)))
                        for i in range(l):
                            v[i] = v_[i]
                    if (top.has_variable('center', s['line'])):
                        center = self.find_variable_value('center', s['line'])
                    debug("Call builtin cube(%s, %s) line: %i"%(str(v), str(center), s['line']))
                    if not debug_parser:
                        self.active_context.cube(V3(v[0], v[1], v[2]), center)
                    else:
                        pass
                    self.pop_stack()
                elif mid=='cylinder':
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], cylinder_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    r = Noval
                    d = Noval
                    h = Noval
                    r1 = Noval
                    r2 = Noval
                    d1 = Noval
                    d2 = Noval
                    center = False
                    if (top.has_variable('center', s['line'])):
                        center = self.find_variable_value('center', s['line'])
                    if (top.has_variable('r', s['line'])):
                        r = self.find_variable_value('r', s['line'])
                    if (top.has_variable('r1', s['line'])):
                        r1 = self.find_variable_value('r1', s['line'])
                    if (top.has_variable('r2', s['line'])):
                        r2 = self.find_variable_value('r2', s['line'])
                    if (top.has_variable('d', s['line'])):
                        d = self.find_variable_value('d', s['line'])
                    if (top.has_variable('d1', s['line'])):
                        d1 = self.find_variable_value('d1', s['line'])
                    if (top.has_variable('d2', s['line'])):
                        d2 = self.find_variable_value('d2', s['line'])
                    if (top.has_variable('h', s['line'])):
                        h = self.find_variable_value('h', s['line'])

                    debug("args: %s"%(s['args'],))
                    debug("Call builtin cylinder(r=%s, d=%s, h=%s, center=%s) line: %i"%(str(r), str(d), str(h), str(center), s['line']))
                    if not debug_parser:
                        self.active_context.cylinder(r, r1, r2, d, d1, d2, h, center)
                    else:
                        pass
                    self.pop_stack()
                elif mid=='import_step':
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], import_step_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    path = ""
                    center = False
                    if (top.has_variable('filename', s['line'])):
                        path = self.find_variable_value('filename', s['line'])
                        path = unstringify(path)
                    debug("Call builtin import_step(%s) line: %i"%(str(path), s['line']))
                    if not debug_parser:
                        base_paths = [os.getcwd(), os.path.dirname(os.path.abspath(self.path))]
                        paths = [os.path.join(bp, path) for bp in base_paths]
                        file_path = None
                        for p in paths:
                            if os.path.isfile(p):
                                debug("Using path %s"%(p,))
                                file_path = p
                                break
                        if (file_path != None):
                            self.active_context.import_step(file_path)
                        else:
                            warning("Failed to load file %s: file not found"%(fname,))
                    else:
                        pass
                    self.pop_stack()
                elif mid=='import_stl':
                    self.push_stack()
                    self.parse_kwargs(s['id'], s['line'], import_stl_module_definition['args'], s['args'])
                    top = self.stack[-1]
                    path = ""
                    center = False
                    if (top.has_variable('filename', s['line'])):
                        path = self.find_variable_value('filename', s['line'])
                        path = unstringify(path)
                    debug("Call builtin import_stl(%s) line: %i"%(str(path), s['line']))
                    if not debug_parser:
                        base_paths = [os.getcwd(), os.path.dirname(os.path.abspath(self.path))]
                        paths = [os.path.join(bp, path) for bp in base_paths]
                        file_path = None
                        for p in paths:
                            if os.path.isfile(p):
                                debug("Using path %s"%(p,))
                                file_path = p
                                break
                        if (file_path != None):
                            self.active_context.import_stl(file_path)
                        else:
                            warning("Failed to load file %s: file not found"%(fname,))
                    else:
                        pass
                    self.pop_stack()
                else:
                    warning("%s:%i Built-in module \"%s\" is not implemented"%(self.path, s['line'], mid))
        elif t=='stat_function_definition':
            fid = s['id']
            l = s['line']
            self.set_function(fid, s, l)
        elif t=='stat_module_definition':
            mid = s['id']
            l = s['line']
            self.set_module(mid, s, l)
        elif t=='stat_for':
            if use:
                debug("Skip for because \"use\" is set")
            else:
                ctr_name = s['counter']
                self.push_stack()
                counter_vals = self.parse_expr(s['counter_vals'])
                debug("counter_vals: %s"%(counter_vals,))
                block = s['block']
                l = s['line']
                top = self.stack[-1]
                for c in counter_vals:
                    top.set_variable(ctr_name, c, l)
                    debug("Set loop counter %s to %s (%s)"%(ctr_name, str(c), counter_vals))
                    for statement in block:
                        self.parse_statement(statement)
                self.pop_stack()
        elif t=='stat_if':
            if use:
                debug("Skip for because \"use\" is set")
            else:
                cond = self.parse_expr(s['condition'])
                if_block = s['blocks'][0]
                else_block = None
                if len(s['blocks'])>1:
                    else_block = s['blocks'][1]
                debug("Cond: %s"%(str(cond),))
                if (cond):
                    self.push_stack()
                    for statement in if_block:
                        self.parse_statement(statement)
                    self.pop_stack()
                elif (else_block!=None):
                    self.push_stack()
                    for statement in else_block:
                        self.parse_statement(statement)
                    self.pop_stack()
        elif t=='use':
            path = unstringify(s['path'])
            filename, ext = os.path.splitext(path)
            base_paths = [os.getcwd(), os.path.dirname(os.path.abspath(self.path))]
            paths = [os.path.join(bp, path) for bp in base_paths]
            debug('paths: %s'%(repr(paths),))
            file_found = False
            for p in paths:
                if os.path.isfile(p):
                    debug("Using path %s"%(p,))
                    parser = None
                    old_path = self.path
                    self.path = p
                    if ext == '.sck':
                        self.push_context(SCLProfile2, get_inc_name("profile2"))
                    elif (ext == '.scp') or (ext == '.scad'):
                        self.push_context(SCLPart3, get_inc_name("part"))
                    else:
                        critical("%s:%i Unknown file type %s"%(self.path, s['line'], path,))

                    try:
                        parser = ScadLikeParser(data=None, path=p, debug=self.debug)
                        ep.push_event(ee.parse_file, p)
                    except ParserError as pe:
                        warning("%s:%i Use: unknown expression %s in file used at %s:%i"%(p, pe.lineno, pe.message, self.path, s['line']))
                        if (self.verbose>=4):
                            traceback.print_exc()
                    debug(json.dumps(parser.data, indent=2))
                    for s in parser.data:
                        self.parse_statement(s, use=True)
                    self.pop_context()
                    self.path=old_path
                    file_found = True
                    break
            if (not file_found):
                critical("%s:%i File %s not found"%(self.path, s['line'], path,))
        elif t=='include':
            path = unstringify(s['path'])
            base_paths = [os.getcwd(), os.path.dirname(os.path.abspath(self.path))]
            paths = [os.path.join(bp, path) for bp in base_paths]
            file_found = False
            for p in paths:
                if os.path.isfile(p):
                    debug("Including path %s"%(path,))
                    parser = None
                    old_path = self.path
                    self.path = p
                    try:
                        parser = ScadLikeParser(data=None, path=p, debug=self.debug)
                        ep.push_event(ee.parse_file, p)
                    except ParserError as pe:
                        warning("%s:%i Include: unknown expression %s in file included at %s:%i"%(p, pe.lineno, pe.message, self.path, s['line']))
                        if (self.verbose>=4):
                            traceback.print_exc()
                    debug(json.dumps(parser.data, indent=2))
                    for s in parser.data:
                        self.parse_statement(s)
                    self.path=old_path
                    file_found = True
                    break
            if (not file_found):
                critical("%s:%i File %s not found"%(self.path, s['line'], path,))
        else:
            raise UnhandledCaseError('unknown statement \"%s\"'%(t,))
                
if __name__=="__main__":
    import sys
    import signal

    from bcad.binterpreter.glfw_display import RunGLFWDisplay
    
    def occt_proc(pipe, img, cmdline):
        args = parse_args(cmdline)
        
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        Singleton.pipe = pipe
        Singleton.img = img
        Singleton.scl = SCL(path=args.file, output_path=args.output,
                            verbose=args.verbose, extra={"linear-deflection": args.linear_deflection,
                                                         "angular-deflection": args.angular_deflection})

        ep.push_event(ee.main_start, args)
        ep.process()
        if args.output == None:
            win.mainloop()
    RunGLFWDisplay(occt_proc, sys.argv[1:])
