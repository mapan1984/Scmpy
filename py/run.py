#!/usr/bin/env python3

"""
Run the interpreter.
"""

import os
import sys

from data import *
from parse import InPort, parse
from evaluater import evaluate

def to_string(x):
    """Convert a Python object back into a Lisp-readable string."""
    if x is True:
        return "#t"
    elif x is False:
        return "#f"
    elif isinstance(x, Symbol):
        return x
    elif isinstance(x, Strings):
        return '"%s"' % x
    elif isinstance(x, List):
        return '('+' '.join(map(to_string, x))+')'
    elif isinstance(x, complex):
        return str(x).replace('j', 'i')
    else:
        return str(x)

def repl(prompt=None, inport=InPort(sys.stdin), out=sys.stdout):
    """A prompt-read-eval-print loop."""
    while True:
        try:
            if prompt:
                #sys.stderr.write(prompt)
                print(prompt, end='', flush=True)
            exp = parse(inport)
            if exp is eof_object:
                return
            val = evaluate(exp)
            if val is not None and out:
                print(to_string(val), file=out)
        except Exception as e:
            print('%s: %s' % (type(e).__name__, e))

def load(filename):
    """Load the lisp program."""
    repl(None, InPort(open(filename)), None)

def interpreter(prompt='Lispy> '):
    """Interactive interpreted lisp program."""
    sys.stderr.write("Lispy version 2.0\n")
    repl(prompt=prompt)

def interpret(filename):
    """Eval every expression from a file."""
    repl(inport=InPort(open(filename)))

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            print("{name} is not a file".format(name=filename))
        else:
            interpret(sys.argv[1])
    else:
        interpreter()
