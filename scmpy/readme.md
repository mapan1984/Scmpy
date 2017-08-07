### overlook

program (str) --> [parse] --> abstract syntax tree (list) --> [eval] --> result (object)

### syntax

1. Scheme programs consist solely of expressions. There is no statement/expression distinction.
2. Numbers (e.g. 1) and symbols (e.g. A) are called atomic expressions; they cannot be broken into pieces. These are similar to their Java counterparts, except that in Scheme, operators such as + and > are symbols too, and are treated the same way as A and fn.
3. Everything else is a list expression: a "(", followed by zero or more expressions, followed by a ")". The first element of the list determines what it means:
    * A list starting with a keyword, e.g. (if ...), is a special form; the meaning depends on the keyword.
    * A list starting with a non-keyword, e.g. (fn ...), is a function call.

#### keywords

1. define
2. if
3. else
4. set!
5. lambda

### parse

#### lexical annalysis

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

#### syntactic analysis

### Built-In Datatypes

2. Booleans --> True, False

        input: #t, #f   -----------
         |                        |
         v                        V
        atom: True, False        eval: True, False
         |                        |
         v                        |
        to_stirng: #t, #f  <-------

1. Numbers --> int, float, complex
3. Strings --> str
4. Symbols --> Symbol
5. Pairs and List --> list

#### define lambda

1. isinstance(var, Symbol) and len(exp) == 1

        (define f 1)
        ['define', 'f', 1]
        var = 'f'; exp = [1]

        (define f (lambda (x) (+ 1 x)))
        ['define', 'f', ['lambda', ['x'], ['+', 1, 'x']]]
        var = 'f'; exp = [['lambda', ['x'], ['+', 1, 'x']]]

        (define f (lambda (x) (display "hello") (+ 1 x)))
        ['define', 'f', ['lambda', ['x'], ['display', 'hello'], ['+', 1, 'x']]]
        var = 'f'; exp = [['lambda', ['x'], ['display', 'hello'], ['+', 1, 'x']]]

2. isinstance(var, list) and len(exp) == 1

        (define (f x) (+ 1 x))
        ['define', ['f', 'x'], ['+', 1, 'x']]
        var = ['f', 'x']; exp = [['+', 1, 'x']]

3. len(var) > 1 and len(exp) > 1

        (define (f x) (display "hello") (+ 1 x))
        ['define', ['f', 'x'], ['display', 'hello'], ['+', 1, 'x']]
        var = ['f', 'x']; exp = [['display', 'hello'], ['+', 1, 'x']]

#### str-->list

"(* 1 2)" --> ["(", "*", 1, 2, ")"]

1. `split_exp_str`

2. `bulid_exp_list`


#### list-->Pair

["(", "*", 1, 2, ")"] --> Pair("*", Pair(1, Pair(2, None)))

buffer栈中存放表达式list，exp栈作为中间工具

1. 从buffer栈中取出val
2. 如果val是')'，则存入exp栈中
3. 如果val是'('，则：
    1. 从exp中取出栈顶元素car，
    2. 并弹出exp中的')'
        1. 如果exp已经empty，那么返回结果car
        2. 如果exp不是empty，那么从exp中弹出cdr，将Pair(car, cdr)存入exp栈中
4. 如果val不是'('，或者')'，则：
    1. 如果exp栈顶是')'，则将Pair(val, None)存入exp栈中
    2. 如果exp栈顶不是')'，则取出栈顶元素cdr，将Pair(val, cdr)存入栈中
