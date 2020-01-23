Noval = 'no val'

def unstringify(s):
    return s[1:-1]

def is_var_set(v):
    if (v!=None) and (v!=Noval):
        return True
    return False
