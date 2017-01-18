##### parse
def tokenize(chars):
    """Convert a string of characters into a list of tokens."""
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
    """Read a Scheme expression form a string."""
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
    """Read an expression from a sequence of tokens."""
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop of ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token):
    """Numbers become numbers; every other token is a symbol."""
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

Symbol = str  # A Scheme Symbol is implemented as a Python str
List = list  # A Scheme List is implemented as a Python list
Number = (int, float) # A Scheme Number is implemented as a Python int or float

##### Environments
import math
import operator as op


class Env(dict):
    """An environment: a dict of {'var':val} pairs, with an outer Env."""
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        """Find the innermost Env where var appears."""
        return self if (var in self) else self.outer.find(var)

def standard_env():
    """An environment with some Scheme standard procedures."""
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, '%':op.mod,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   lambda fn, *args, **kwargs: fn(*args, **kwargs),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x, list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

global_env = standard_env()

##### eval
def eval(exp, env=global_env):
    """Evaluate an expression i an environment."""
    if isinstance(exp, Symbol):  # variable reference
        return env.find(exp)[exp]
    elif not isinstance(exp, List):  # constant literal
        return exp
    elif exp[0] == 'quote':  # quotation
        (_, exp) = exp
        return exp
    elif exp[0] == 'if':   # conditional
        (_, test, conseq, alt) = exp
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif exp[0] == 'define':  # definition
        (_, var, exp) = exp
        env[var] = eval(exp, env)
    elif exp[0] == 'set!':  # assignment
        (_, var, exp) = exp
        env.find(var)[var] = eval(exp, env)
    elif exp[0] == 'lambda':  # procedure
        (_, parms, body) = exp
        return Procedure(parms, body, env)
    else:  # procedure call
        proc = eval(exp[0], env)
        args = [eval(arg, env) for arg in exp[1:]]
        return proc(*args)

class Procedure(object):
    """A user-defined Scheme procedure."""
    def __init__(self, parms, body, env):
        self.parms = parms
        self.body = body
        self.env = env

    def __call__(self, *args):
        return eval(self.body, Env(self.parms, args, self.env))

#### main
def repl(prompt='lis.py> '):
    """A prompt-read-eval-print loop."""
    exp = parse(input(prompt))
    while exp is not None:
        print("    {result}".format(result=eval(exp)))
        exp = parse(input(prompt))

def schemestr(exp):
    """Convert a Python object back into a Scheme-readable string."""
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')' 
    else:
        return str(exp)

if __name__ == "__main__":
    repl()
