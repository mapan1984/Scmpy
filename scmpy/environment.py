"""
Provides the definition of the environment and the initial global environment.
"""

import sys
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
                raise ValueError("{var} not is defined".format(var=var))
            else:
                return outer_env.find(var)
        else:
            return val

    def define(self, var, val):
        """Define var = val in the current environment."""
        self[var] = val

    def set(self, var, val):
        """Find the innermost Env where var appears, set var = val."""
        if var in self:
            self[var] = val
        else:
            if self.outer is not None:
                self.outer.set(var, val)
            else:
                raise ValueError("{var} is not defined".format(var=var))

def standard_env():
    """Rutern an environment with some Scheme standard procedures."""
    env = Env()
    env.update({k:v for k,v in vars(math).items() if not k.startswith('__')})
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, '%':op.mod,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'max':     max,
        'min':     min,
        'round':   round,
        'append':  op.add,
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:],
        'cons':    lambda x, y: [x, y],
        'eq?':     op.is_,
        'equal?':  op.eq,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x, list),
        'length':  len,
        'map':     map,
        'boolean?': lambda x: true if x is true or x is false else False,
        'symbol?': lambda x: isinstance(x, Symbol),
        'string?': lambda x: isinstance(x, str),
        'not':     op.not_,
        'display': print,
        'apply':   lambda fn, *args, **kwargs: fn(*args, **kwargs),
        'exit':    lambda: sys.exit(0),
    })
    return env

global_env = standard_env()
