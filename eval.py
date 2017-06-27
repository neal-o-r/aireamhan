#!/usr/bin/python
# -*- coding: utf8 -*-

import math
import operator as op
from parse import *

Symbol = str         
List   = list         
Number = (int, float)

class Procedure(object):
	"A user-defined procedure."
	def __init__(self, parms, body, env):
		self.parms, self.body, self.env = parms, body, env
    
	def __call__(self, *args): 
		return eval(self.body, Env(self.parms, args, self.env))

class Env(dict):
	"An environment: a dict of {'var':val} pairs, with an outer Env."
	def __init__(self, parms=(), args=(), outer=None):
		self.update(zip(parms, args))
		self.outer = outer

	def find(self, var):
		"Find the innermost Env where var appears."
		return self if (var in self) else self.outer.find(var)


def standard_env():
	"An environment with some Scheme standard procedures."
	env = Env()
	env.update(vars(math))
	env.update({
        	'+':op.add, '-':op.sub, '*':op.mul, '/':op.itruediv, 
        	'>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        	'dearbhluach':     abs,
        	'cuir_le':  op.add,  
        	'tosaigh':   lambda *x: x[-1],
        	'tús':     lambda x: x[0],
        	'deireadh':     lambda x: x[1:], 
        	'ag_tús':    lambda x,y: [x] + y,
        	'ionann?':     op.is_, 
        	'cothrom_le?':  op.eq, 
        	'fad':  len, 
        	'liosta':    lambda *x: list(x), 
        	'liosta?':   lambda x: isinstance(x,list), 
        	'mapáil':     map,
        	'uas':     max,
        	'íos':     min,
        	'ní':     op.not_,
        	'nialasach?':   lambda x: x == [], 
        	'uimhir?': lambda x: isinstance(x, Number),   
        	'modh?': callable,
        	'slánaigh':   round,
        	'siombail?': lambda x: isinstance(x, Symbol),
    	})
	return env

global_env = standard_env()

def eval(x, env=global_env):
	"Evaluate an expression in an environment."
	if isinstance(x, Symbol):      # variable reference
		return env.find(x)[x]
	
	elif not isinstance(x, List):  # constant literal
		return x                

	elif x[0] == 'athfhriotal':          # quotation
		(_, exp) = x
		return exp

	elif x[0] == 'má':             # conditional
		(_, test, conseq, alt) = x
		exp = (conseq if eval(test, env) else alt)
		return eval(exp, env)

	elif x[0] == 'sainigh':         # definition
		(_, var, exp) = x
		env[var] = eval(exp, env)

	elif x[0] == 'go!':           # assignment
		(_, var, exp) = x
		env.find(var)[var] = eval(exp, env)

	elif x[0] == 'lambda':         # procedure
		(_, parms, body) = x
		return Procedure(parms, body, env)
	
	else:                          # procedure call
		proc = eval(x[0], env)
		args = [eval(arg, env) for arg in x[1:]]
		return proc(*args)


def repl(prompt='Áireamhán > '):
	"A prompt-read-eval-print loop."
	while True:
		val = input(prompt)
		status = run(val)
		if status == 0:
			break

def run_block(block):
	print(block)
	block = block.split(';')
	for line in block:
		run(line)

def run(code):
	if code == 'dún':
		print('Slán')
		return 0		
	code = eval(parse(code))
 
	if code is not None: 
		print(codestr(code))
		return 1

def codestr(exp):
	"Convert a Python object back into a code string."
	if isinstance(exp, List):
		return '(' + ' '.join(map(schemestr, exp)) + ')' 
	else:
		return str(exp)


