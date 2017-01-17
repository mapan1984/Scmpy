import string

_NUMERAL_STARTS = set(string.digits) | set('+-.')
_SYMBOL_CHARS = (set('!$%&*/:<=>?@^_~') | set(string.ascii_lowercase) |
                 set(string.ascii_uppercase) | _NUMERAL_STARTS)
_STRING_DELIMS = set('"')
_WHITESPACE = set(' \t\n\r')
_SINGLE_CHAR_TOKENS = set("()'`")
_TOKEN_END = _WHITESPACE | _SINGLE_CHAR_TOKENS | _STRING_DELIMS | {',', ',@'}
DELIMITERS = _SINGLE_CHAR_TOKENS | {'.', ',', ',@'}

def split_exp_str(line, index=0):
    """返回分割得到的字符串"""
    var = []
    while index < len(line):
        var.clear()
        char = line[index]
        if char in _WHITESPACE:
            index += 1
        elif char in _STRING_DELIMS:
            index += 1 # 跳过"
            char = line[index]
            while char not in _STRING_DELIMS:
                var.append(char)
                index += 1
                char = line[index]
            index += 1 # 跳过"
            yield "".join(var)
        elif char in _SINGLE_CHAR_TOKENS:
            index += 1
            yield char
        elif char in _SYMBOL_CHARS:
            while char not in _WHITESPACE | _SINGLE_CHAR_TOKENS:
                var.append(char)
                index += 1
                char = line[index]
            yield "".join(var)

def bulid_exp_list(line):
    exp = []
    for var in split_exp_str(line):
        exp.append(var)
    return exp

if __name__ == "__main__":
    print(bulid_exp_list('(define "asd" (+ 1 2) (* 3 4) "adf")'))
