import argparse

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='file to read', required=True, type=str)
    parser.add_argument('--output', help='file to write', required=False, type=str)
    parser.add_argument('--linear-deflection', help='Linear deflection parameter of SCL writer', required=False, type=float, default=1.0)
    parser.add_argument('--angular-deflection', help='Angular deflection parameter of SCL writer', required=False, type=float, default=1.0)
    parser.add_argument('--verbose', help='Verbose level, when set to 0: print only critical errors, 4+: print all debug messages, 3: default', required=False, type=int, default=3)
    args = parser.parse_args(argv)
    return args
