"""
Resolves the input to a list structure that can be evaluated.
"""

import re
import io

from scmpy.data import *

class InPort(object):
    """An input port. Retains a line of chars.
    tokenizer: to match lisp's token
    """

#     tokenizer = re.compile(
#         r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*|\d/\d)(.*)''')

    tokenizer = re.compile(r'''
        \s*                     # Start with any whitespace
        (
         ,@                     # ,@
        |[('`,)]                # ( ' ` , )
        |"(?:[\\].|[^\\"])*"    # string
        |;.*                    # commentary
        |[^\s('"`,;)]*          # Symbols, Numbers
        |\d/\d                  # fraction
        )
        (.*)
        ''', re.VERBOSE)

    def __init__(self, file):
        if isinstance(file, str):
            self.file = io.StringIO(file)
        else:
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
            token, self.line = InPort.tokenizer.match(self.line).groups()
            if token != '' and not token.startswith(';'):
                return token

def atom(token):
    """
       Numbers become numbers; #t and #f are booleans;
       "..." become string; otherwise is Symbol.
    """
    if token == '#t':
        return True
    elif token == '#f':
        return False
    elif token[0] == '"':  # string
        return str(token[1:-1])
    elif re.match(r'\d/\d', token): # 分数
        member, denominator = re.match(r'(\d)/(\d)', token).groups()
        return float(int(member)/int(denominator))
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

quotes = {"'":quote_, "`":quasiquote_, ",":unquote_, ",@":unquotesplicing_}

def represent(x):
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
        return '('+' '.join(map(represent, x))+')'
    elif isinstance(x, complex):
        return str(x).replace('j', 'i')
    else:
        return str(x)

def parse(inport):
    """Read a Scheme expression from an input port and parse it."""
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
            return [quotes[token], parse(inport)]
        elif token is eof_object:
            raise SyntaxError('unexpected EOF in list')
        else:
            return atom(token)
    # body of read
    token1 = inport.next_token()
    return read_ahead(token1)
