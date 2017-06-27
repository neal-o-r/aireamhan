#!/bin/bash
if [ ! -z $1 ] 
then

	code=`cat $1`
	python -c "import eval; eval.run_block('$code')"

else
	python3 -c 'import eval; eval.repl()'
fi
