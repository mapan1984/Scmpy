"""
Basic data and global quantities.
"""

class Symbol(str): # A Scheme Symbol is implemented as a Python str
    pass

def Sym(s, symbol_table={}):
    """Find or create unique Symbol entry for str s in symbol table."""
    if s not in symbol_table:
        symbol_table[s] = Symbol(s)
    return symbol_table[s]

Strings = str

List = list  # A Scheme List is implemented as a Python list

# A Scheme Number is implemented as a Python int or float
Number = (int, float, complex)

eof_object = Symbol('#<eof-object>')  # Note: uninterned; can't be read

quote_, if_, cond_, set_, define_, lambda_, begin_, definemacro, = \
    map(Sym, "quote if cond set! define lambda begin define-macro".split())

quasiquote_, unquote_, unquotesplicing_ = \
    map(Sym, "quasiquote unquote unquote-splicing".split())

class number():
    def __init__(self, value):
        if '.' in value:
            self.value = float(value)
        else:
            self.value = int(value)

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __add__(self, other):
        return self.value + other.value

    def __sub__(self, other):
        return self.value - other.value

    def __mul__(self, other):
        return self.value * other.value

    def __div__(self, other):
        return self.value / other.value

    def __floordiv__(self, other):
        return self.value // other.value

    def __mod__(self, other):
        return self.value // other.value

    def __divmod__(self, other):
        return self.value / other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
