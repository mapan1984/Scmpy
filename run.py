#!/usr/bin/env python3

"""
Run the interpreter.
"""

import os
import sys

from scmpy import InPort, parse, represent, evaluate

def repl(prompt=None, inport=InPort(sys.stdin), out=sys.stdout):
    """A prompt-read-eval-print loop."""
    while True:
        try:
            if prompt:
                #sys.stderr.write(prompt)
                print(prompt, end='', flush=True)
            exp = parse(inport)
            val = evaluate(exp)
            if val is not None and out:
                print(represent(val), file=out)
        except Exception as e:
            print('%s: %s' % (type(e).__name__, e))

def load(filename):
    """Load the lisp program."""
    repl(None, InPort(open(filename)), None)

def interpreter(prompt='Lispy> '):
    """Interactive interpreted lisp program."""
    sys.stderr.write("Scmpy version 2.0\n")
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
