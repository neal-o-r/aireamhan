#!/bin/bash
if [ ! -z $1 ] 
then
	python3 -c "import air; air.load('$1')"
else
	python3 air.py
fi
