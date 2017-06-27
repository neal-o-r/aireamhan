Symbol = str         
List   = list         
Number = (int, float)

def tokenize(chars):
	"Convert a string of characters into a list of tokens."
	return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program):
	"Read a expression from a string."
	return read_from_tokens(tokenize(program))

def read_from_tokens(tokens):
	"Read an expression from a sequence of tokens."
	if len(tokens) == 0:
		raise SyntaxError('unexpected EOF while reading')

	token = tokens.pop(0)
	if '(' == token:
		L = []
		while tokens[0] != ')':
			L.append(read_from_tokens(tokens))
        
		tokens.pop(0) # pop off ')'
		return L
	
	elif ')' == token:
		raise SyntaxError('unexpected )')
	else:
 		return atom(token)

def atom(token):
	"Numbers become numbers; every other token is a symbol."
	try: return int(token)
	except ValueError:

		try: return float(token)
		except ValueError:

			return Symbol(token)
