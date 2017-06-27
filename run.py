from eval import *

def run_block(fname):
	
	with open(fname, 'r') as f:
		block = f.read()

	block = block.split('\n')[:-1]
	for line in block:
		run(line)


