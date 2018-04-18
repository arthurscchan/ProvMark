#!/bin/bash

if [ "$#" -ne 2 ]
then
	echo "Usage: "$0" <Tools> <Tools_Path>"
	exit 1
fi

mkdir result

for i in `ls benchmarkProgram/baseSyscall`
do
	for j in `ls benchmarkProgram/baseSyscall/$i`
	do
		syscall=${j:3}
		echo "Generating provenance benchmark for $syscall in group $i using $1 settings..."
		sudo ./fullAutomation.py $1 $2 benchmarkProgram/baseSyscall/$i/$j 
		genClingoGraph/clingo2Dot.py result.clingo result.dot
		dot -Tsvg -o "${syscall,,}.svg" result.dot
		rm -f result.clingo
		rm -f  result.dot
		mv "${syscall,,}.svg" result/
		echo "Process complete for $syscall. Result stored in result/${syscall,,}.svg"
	done
done
