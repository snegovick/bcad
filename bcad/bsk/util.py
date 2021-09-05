from __future__ import absolute_import, division, print_function

from logging import debug, info, warning, error, critical
import traceback
import argparse
import sys

# from stackoverflow:: http://stackoverflow.com/questions/251464/how-to-get-the-function-name-as-string-in-python

def who_am_i(depth):
    stack = traceback.extract_stack()
    filename, codeline, funcName, text = stack[-depth]
    return filename, codeline, funcName

def dbgfname():
    fn, cl, func = who_am_i(3)
    debug("In "+fn+":"+str(cl)+" "+func)

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='file to read', required=False, type=str)
    parser.add_argument('--verbose', help='Verbose level, when set to 0: print only critical errors, 4+: print all debug messages, 3: default', required=False, type=int, default=3)
    args = parser.parse_args(argv)
    return args
