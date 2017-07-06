#!/bin/bash
if [ ! -z $1 ] 
then
	python3 -c "import aireamhan; aireamhan.load('$1')"
else
	python3 aireamhan/aireamhan.py
fi
