"""
Evaluate the expression.
"""

from scmpy.data import *
from scmpy.environment import Env, global_env

def cond_to_if(expr):
    """"Convert the cond structure to an if construct."""
    def expand_clauses(clauses):
        if len(clauses) == 0:
            raise SyntaxError("empty cond")
        first, rest = clauses[0], clauses[1:]
        if first[0] == "else":
            if rest == []:
                return first[1]
            else:
                raise SyntaxError("ELSE clause isn't last")
        else:
            return [Sym('if'), first[0], first[1], expand_clauses(rest)]
    return expand_clauses(expr[1:])

def evaluate(exp, env=global_env):
    """Evaluate an expression in an environment."""
    if isinstance(exp, Symbol):  # variable reference
        return env.find(exp)
    elif not isinstance(exp, List):  # constant literal
        return exp
    elif exp[0] is quote_:  # quotation (quote exp)
        (_, exp) = exp
        return exp
    elif exp[0] is cond_:  # (cond (<test> <conseq>)*)
        return evaluate(cond_to_if(exp), env)
    elif exp[0] is if_:   # conditional (if test conseq alt)
        (_, test, conseq, alt) = exp
        exp = (conseq if evaluate(test, env) else alt)
        return evaluate(exp, env)
    elif exp[0] is define_:  # definition (define var exp)
        #(_, var, exp) = exp              #(define (<id> <id>*) (<expr>+))
        var = exp[1]
        exp = exp[2:]
        if isinstance(var, list): # Procedure
            name = var[0]
            parms = var[1:]
            body = exp
            env[name] = Procedure(name, parms, body, env)
        elif isinstance(var, Symbol):  # variable
            env[var] = evaluate(exp[0], env)
        else:
            print("DEFINE: no var")
    elif exp[0] is set_:  # assignment (set! var exp)
        (_, var, exp) = exp
        env.set(var, evaluate(exp, env))
    elif exp[0] is lambda_:  # procedure (lambda (<var>*) <expr>+)
        #(, parms, body) = exp
        parms = exp[1]
        body = exp[2:]
        return Procedure("lambda", parms, body, env)
    else:  # procedure call (proc exp*)
        proc = evaluate(exp[0], env)
        args = [evaluate(arg, env) for arg in exp[1:]]
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
            return [evaluate(exp, Env(self.parms, args, self.env)) \
                                                    for exp in self.body][-1]
        else:  # the function's body include one expression
            return evaluate(self.body[0], Env(self.parms, args, self.env))

    def __repr__(self):
        return "#<procedure: {name}>".format(name=self.name)
