class Pair:
    """Pair: has car and cdr"""

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
    
    def __repr__(self):
        return "<Pair: {car} {cdr}>".format(car=repr(self.car), 
                                            cdr=repr(self.cdr))

    def __str__(self):
        s = "(" + str(self.car)
        cdr = self.cdr
        while isinstance(cdr, Pair):
            s += " " + str(cdr.car)
            cdr = cdr.cdr
        if cdr is not None:
            s += " . " + str(cdr)
        return s + ")"

    def __len__(self):
        n, cdr = 1, self.cdr
        while isinstance(cdr, Pair):
            n += 1
            cdr = cdr.cdr
        if cdr is not None:
            raise TypeError("length attempted on improper list")
        return n
