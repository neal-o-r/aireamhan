#!/bin/bash
if [ ! -z $1 ] 
then

	python -c "import run; run.run_block('$1')"

else
	python3 -c 'import eval; eval.repl()'
fi
