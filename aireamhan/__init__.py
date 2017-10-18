#!/usr/bin/python
# -*- coding: utf8 -*-

import re, sys 
from io import StringIO

class Fadhb(Exception):
    pass


isa = isinstance

class Symbol(str): 
    pass

def Sym(s, symbol_table={}):
    "Find or create unique Symbol entry for str s in symbol table."
    if s not in symbol_table: 
        symbol_table[s] = Symbol(s)
    
    return symbol_table[s]

_quote, _if, _define, _lambda, _begin, _set, = map(Sym, 
"athfhriotal   má   sainigh   lambda   tosaigh  cuir!".split())
eof_object = Symbol('#<eof-object>')


class Procedure(object):
    "Class for user defined lambdas" 
    def __init__(self, parms, exp, env):
        self.parms, self.exp, self.env = parms, exp, env
    
    def __call__(self, *args): 
        return evaluate(self.exp, Env(self.parms, args, self.env))


def parse(inport):
    
    if isinstance(inport, str): 
        inport = InPort(StringIO(inport))
    
    return expand(read(inport), toplevel=True)


class InPort(object):
    
    tokenizer = r"""\s*([(')]|"(?:[\\].|[^\\"])*"|;.*|[^\s('";)]*)(.*)"""
    
    def __init__(self, file):
        self.file = file; self.line = ''
    
    def next_token(self):
        while True:
            if self.line == '': 
                self.line = self.file.readline()
            if self.line == '': 
                return eof_object

            token, self.line = re.match(InPort.tokenizer, self.line).groups()

            if token != '' and not token.startswith(';'):
                return token


def readchar(inport):
    "Read the next character from an input port."

    if inport.line != '':
        ch, inport.line = inport.line[0], inport.line[1:]
        return ch
 
    else:
        return inport.file.read(1) or eof_object


def read(inport):
    " get next token, atomise it. "
    def read_ahead(token):
        if '(' == token: 
            L = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return L
                else: 
                    L.append(read_ahead(token))
        
        elif ')' == token: 
            raise Fadhb(' ) gan súil leis')
        
        elif token is eof_object: 
            raise Fadhb('EOF gan súil leis')
        
        else: 
            return atom(token)
    
    token1 = inport.next_token()
    return eof_object if token1 is eof_object else read_ahead(token1)

def atom(token):
    'Numbers become numbers; #t and #n are booleans; "..." string; otherwise Symbol.'
    if token == '#tá': 
        return True
    elif token == '#níl': 
        return False
    elif token[0] == '"': 
        return str(token[1:-1])
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

def to_string(x):
    "reverse the atomisation"
    if x is True: 
        return "#tá"
    elif x is False: 
        return "#níl"
    elif isa(x, Symbol): 
         return x
    elif isa(x, str): 
        return '{0}'.format(str(x).replace('"',r'\"'))
    elif isa(x, list): 
        return '('+' '.join(map(to_string, x))+')'
    elif isa(x, complex): 
        return str(x).replace('j', 'i')
    else: 
        return str(x)


def load(filename):
    "evaluate every expression from a file."
    repl(None, InPort(open(filename)), None)


def repl(prompt='áireamhán > ', inport=InPort(sys.stdin), out=sys.stdout):
    "A prompt-read-evaluate-print loop."

    if prompt != None: sys.stderr.write("\nFáilte\n" + 5*'-' + '\n')

    while True:
        try:
            if prompt: print(prompt, file=sys.stderr)
            x = parse(inport)
            if x is eof_object: return
            if x == 'dún': 
                print('-'*5 + '\nSlán\n')
                return

            val = evaluate(x)

            if val is not None and out: 
                print(to_string(val))
        except Fadhb as e:
            print('{0}: {1}'.format(type(e).__name__, e))


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        # Bind parm list to corresponding args, or single parm to list of args
        self.outer = outer
        if isa(parms, Symbol): 
            self.update({parms:list(args)})

        else: 
            if len(args) != len(parms):
                raise Fadhb('ag súil le {0}, fuair {1}, '.format(to_string(parms), to_string(args)))

            self.update(zip(parms,args))

    def find(self, var):
        "Find the innermost Env where var appears."
        if var in self:
            return self
        elif self.outer is None: 
            raise Fadhb("Earráid Cuardach: {}".format(var))
        else: 
            return self.outer.find(var)


def cons(x, y): return [x]+y

def add_globals(self):
    "Add some Scheme standard procedures."
    import math, cmath, operator as op
    from functools import reduce
    self.update(vars(math))
    self.update(vars(cmath))
    self.update({
     '+':op.add, '-':op.sub, '*':op.mul, '/':op.itruediv, 'níl':op.not_, 'agus':op.and_,
     '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 'mod':op.mod, 
     'frmh':cmath.sqrt, 'dearbhluach':abs, 'uas':max, 'íos':min,
     'cothrom_le?':op.eq, 'ionann?':op.is_, 'fad':len, 'cons':cons,
     'ceann':lambda x:x[0], 'tóin':lambda x:x[1:], 'iarcheangail':op.add,  
     'liosta':lambda *x:list(x), 'liosta?': lambda x:isa(x,list),
     'folamh?':lambda x: x == [], 'adamh?':lambda x: not((isa(x, list)) or (x == None)),
     'boole?':lambda x: isa(x, bool), 'scag':lambda f, x: list(filter(f, x)),
     'cuir_le':lambda proc,l: proc(*l), 'mapáil':lambda p, x: list(map(p, x)), 
     'lódáil':lambda fn: load(fn), 'léigh':lambda f: f.read(),
     'oscail_comhad_ionchuir':open,'dún_comhad_ionchuir':lambda p: p.file.close(), 
     'oscail_comhad_aschur':lambda f:open(f,'w'), 'dún_comhad_aschur':lambda p: p.close(),
     'dac?':lambda x:x is eof_object, 'luacháil':lambda x: evaluate(x),
     'scríobh':lambda x,port=sys.stdout:port.write(to_string(x) + '\n'),
     'éirigh_as':exit})
    return self

global_env = add_globals(Env())


def evaluate(x, env=global_env):
    "evaluateuate an expression in an environment."
    while True:
        if isa(x, Symbol):       # variable reference
            return env.find(x)[x]

        elif not isa(x, list):   # constant literal
            return x                

        elif x[0] is _quote:     # (quote exp)
            (_, exp) = x
            return exp

        elif x[0] is _if:        # (if test conseq alt)
            (_, test, conseq, alt) = x
            x = (conseq if evaluate(test, env) else alt)

        elif x[0] is _set:       # (set! var exp)
            (_, var, exp) = x
            env.find(var)[var] = evaluate(exp, env)
            return None

        elif x[0] is _define:    # (define var exp)
            (_, var, exp) = x
            env[var] = evaluate(exp, env)
            return None

        elif x[0] is _lambda:    # (lambda (var*) exp)
            (_, vars, exp) = x
            return Procedure(vars, exp, env)

        elif x[0] is _begin:     # (begin exp+)
            for exp in x[1:-1]:
                evaluate(exp, env)
            x = x[-1]

        else:                    # (proc exp*)
            exps = [evaluate(exp, env) for exp in x]
            proc = exps.pop(0)

            if isa(proc, Procedure):
                x = proc.exp
                env = Env(proc.parms, exps, proc.env)

            else:
                return proc(*exps)


def expand(x, toplevel=False):
    "Walk tree of x, making optimizations/fixes, and signaling SyntaxError."
    require(x, x!=[])                    # () => Error
    if not isa(x, list):                 # constant => unchanged
        return x

    elif x[0] is _quote:                 # (quote exp)
        require(x, len(x)==2)
        return x

    elif x[0] is _if:                    
        if len(x)==3: x = x + [None]     # (if t c) => (if t c None)
        require(x, len(x)==4)
        return list(map(expand, x))

    elif x[0] is _set:                   
        require(x, len(x)==3); 
        var = x[1]                       # (set! non-var exp) => Error
        require(x, isa(var, Symbol), "is féidir leat cuir! siombail amháin")
        return [_set, var, expand(x[2])]

    elif x[0] is _begin:
        if len(x)==1: return None        # (begin) => None
        else: return [expand(xi, toplevel) for xi in x]

    elif x[0] is _lambda:                # (lambda (x) e1 e2) 
        require(x, len(x)>=3)            #  => (lambda (x) (begin e1 e2))
        vars, body = x[1], x[2:]
        require(x, (isa(vars, list) and all(isa(v, Symbol) for v in vars))
                or isa(vars, Symbol), "argóint mícheart don lambda")
        exp = body[0] if len(body) == 1 else [_begin] + body
        return [_lambda, vars, expand(exp)]   

    else:                                #        => macroexpand if m isa macro
        return list(map(expand, x))           # (f arg...) => expand each


def require(x, predicate, msg="fad mícheart"):
    "Signal a syntax error if predicate is false."
    if not predicate: 
        raise Fadhb(to_string(x)+': '+msg)


if __name__ == '__main__':
    repl()
