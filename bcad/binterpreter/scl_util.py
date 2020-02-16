Noval = 'no val'

def unstringify(s):
    return s[1:-1]

def is_var_set(v):
    if (v!=None) and (v!=Noval):
        return True
    return False

def sign(a):
    return (1 if a>0 else -1 if a<0 else 0)
