from representation import Pair
from split import bulid_exp_list

class Stack:
    def __init__(self, line=None):
        self.line = line or []
        self.index = len(self.line)

    def pop(self):
        self.index -= 1
        return self.line.pop()

    def top(self):
        return self.line[self.index-1]

    def stash(self, val):
        self.index += 1
        self.line.append(val)

    def not_empty(self):
        return self.index > 0

def parse(exp_stack):
    buffer = Stack()
    while exp_stack.not_empty():
        val = exp_stack.pop()
        if val == ')':
            buffer.stash(val)
        elif val == '(':
            car = buffer.pop()
            buffer.pop()
            if buffer.not_empty():
                if buffer.top() != ')':
                    cdr = buffer.pop()
                    val = Pair(car, cdr)
                    buffer.stash(val)
                else:
                    buffer.stash(car)
            else:
                return car
        else:
            if buffer.top() == ')':
                buffer.stash(Pair(val, None))
            else:
                cdr = buffer.pop()
                buffer.stash(Pair(val, cdr))

if __name__ == "__main__":
    #b1 = Stack(["(", "*", 1, 2, ")"])
    #b2 = Stack(["(", "*", "(", "+", 1, 2, ")", 3, ")"])
    #val1 = parse(b1)
    #val2 = parse(b2)
    #print(val1)
    #print(val2)
    exp = "(lambda (x) (+ 1 x))"
    print(exp)
    exp = bulid_exp_list(exp)
    print(exp)
    b3 = Stack(exp)
    print(parse(b3))
