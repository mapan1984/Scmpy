import re
import sys


class Symbol(str): # A Scheme Symbol is implemented as a Python str
    pass

def Sym(s, symbol_table={}):
    """Find or create unique Symbol entry for str s in symbol table."""
    if s not in symbol_table:
        symbol_table[s] = Symbol(s)
    return symbol_table[s]

_quote, _if, _set, _define, _lambda, _begin, definemacro, = \
    map(Sym, "quote if set! define lambda begin define-macro".split())

_quasiquote, _unquote, _unquotesplicing = \
    map(Sym, "quasiquote unquote unquote-splicing".split())

Strings = str

List = list  # A Scheme List is implemented as a Python list

# A Scheme Number is implemented as a Python int or float
Number = (int, float, complex) 

Boolean = bool

eof_object = Symbol('#<eof-object>')  # Note: uninterned; can't be read

##### parse
class InPort(object):
    """An input port. Retains a line of chars.
    tokenizer:
        匹配句首任意空格\s*
        之后为,@
              ( ' ` , )

              以;开头的任意数量字符

    """
    tokenizer = \
        r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)'''

    def __init__(self, file):
        self.file = file
        self.line = ''

    def next_token(self):
        """Return the next token,
        reading new text into line buffer if needed."""
        while True:
            if self.line == '':
                self.line = self.file.readline()
            if self.line == '':
                return eof_object
            token, self.line = re.match(InPort.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token

quotes = {"'":_quote, "`":_quasiquote, ",":_unquote, ",@":_unquotesplicing}

def atom(token):
    """
       Numbers become numbers; #t and #f are booleans;
       "..." string; otherwise Symbol.
    """
    if token == '#t':
        return True
    elif token == '#f':
        return False
    elif token[0] == '"':
        return str(token[1:-1])
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            try:
                return complex(token.replace('i', 'j', 1))
            except ValueError:
                return Sym(token)

def read(inport):
    """Read a Scheme expression from an input port."""
    def read_ahead(token):
        """return expression tokenize"""
        if token == '(':
            L = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return L
                else:
                    L.append(read_ahead(token))
        elif token == ')':
            raise SyntaxError('unexpected )')
        elif token in quotes:
            return [quotes[token], read(inport)]
        elif token is eof_object:
            raise SyntaxError('unexpected EOF in list')
        else:
            return atom(token)
    # body of read
    token1 = inport.next_token()
    return eof_object if token1 is eof_object else read_ahead(token1)

def parse(inport):
    """Read a Scheme expression form a string."""
    return read(inport)

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
        val = self.get(var)
        if val is None:
            outer_env = self.outer
            if outer_env is None:
                raise ValueError("{var} not is bound".format(var))
            else:
                return outer_env.find(var)
        else:
            return val

    def set(self, var, val):
        """Find the innermost Env where var appears,
           set var = val
        """
        if var in self:
            self[var] = val
        else:
            if self.outer is not None:
                self.outer.set(var, val)
            else:
                raise ValueError("{var} is not bound")

def standard_env():
    """An environment with some Scheme standard procedures."""
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, '%':op.mod,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'display': print,
        'abs':     abs,
        'append':  op.add,
        'apply':   lambda fn, *args, **kwargs: fn(*args, **kwargs),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x, y: [x, y],
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x, list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
        'string?': lambda x: isinstance(x, str),
        'exit': lambda: sys.exit(0)
    })
    return env

global_env = standard_env()

##### eval
def eval(exp, env=global_env):
    """Evaluate an expression i an environment."""
    if isinstance(exp, Symbol):  # variable reference
        return env.find(exp)
    elif not isinstance(exp, List):  # constant literal
        return exp
    elif exp[0] is _quote:  # quotation (quote exp)
        (_, exp) = exp
        return exp
    elif exp[0] is _if:   # conditional (if test conseq alt)
        (_, test, conseq, alt) = exp
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif exp[0] is _define:  # definition (define var exp) 
        #(_, var, exp) = exp              #(define (<id> <id>*) (<expr>+))
        var = exp[1]
        exp = exp[2:]
        if isinstance(var, list): # Procedure
            name = var[0]
            parms = var[1:]
            body = exp
            env[name] = Procedure(name, parms, body, env)
        elif isinstance(var, Symbol):  # variable
            env[var] = eval(exp[0], env)
        else:
            print("DEFINE: no var")
    elif exp[0] is _set:  # assignment (set! var exp)
        (_, var, exp) = exp
        env.set(var, eval(exp, env))
    elif exp[0] is _lambda:  # procedure (lambda (<var>*) <expr>+)
        #(_, parms, body) = exp
        parms = exp[1]
        body = exp[2:]
        return Procedure("lambda", parms, body, env)
    else:  # procedure call (proc exp*)
        proc = eval(exp[0], env)
        args = [eval(arg, env) for arg in exp[1:]]
        return proc(*args)

class Procedure(object):
    """A user-defined Scheme procedure.
    args:
        name: the name of the procedure.
        parms: the parameter list of the procedure.
        body: a list of expressions that need to be executed 
              in the body of the procedure. [<exp>*]
        env: environment in which the definition of the process
    """
    def __init__(self, name, parms, body, env):
        self.name = name
        self.parms = parms
        self.body = body
        self.env = env

    def __call__(self, *args):
        if len(self.body) > 1:  # the function's body include multiple exprs
            return [eval(exp, Env(self.parms, args, self.env)) \
                                                    for exp in self.body][-1]
        else:  # the function's body include one expression
            return eval(self.body[0], Env(self.parms, args, self.env))

    def __repr__(self):
        return "#<procedure: {name}>".format(name=self.name)

#### main
def to_string(x):
    """Convert a Python object back into a Lisp-readable string."""
    if x is True:
        return "#t"
    elif x is False:
        return "#f"
    elif isinstance(x, Symbol):
        return x
    elif isinstance(x, str):
        return '"%s"' % x
    elif isinstance(x, list):
        return '('+' '.join(map(to_string, x))+')'
    elif isinstance(x, complex):
        return str(x).replace('j', 'i')
    else:
        return str(x)

def repl(prompt='lispy> ', inport=InPort(sys.stdin), out=sys.stdout):
    """A prompt-read-eval-print loop."""
    sys.stderr.write("Lispy version 2.0\n")
    while True:
        try:
            if prompt:
                #sys.stderr.write(prompt)
                print(prompt, end='', flush=True)
            exp = parse(inport)
            if exp is eof_object:
                return
            val = eval(exp)
            if val is not None and out:
                print(to_string(val), file=out)
        except Exception as e:
            print('%s: %s' % (type(e).__name__, e))

def load(filename):
    """Eval every expression from a file."""
    repl(None, InPort(open(filename)), None)

if __name__ == "__main__":
    repl()
