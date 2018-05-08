#!/bin/bash

if [ "$#" -ne 2 ]
then
	echo "Usage: "$0" <Tools> <Tools_Path>"
	exit 1
fi

mkdir result > /dev/null 2>&1

for i in `ls benchmarkProgram/baseSyscall`
do
	for j in `ls benchmarkProgram/baseSyscall/$i`
	do
		syscall=${j:3}
		if [ -e result/${syscall,,}.svg ]
		then
			continue
		fi
		echo "Generating provenance benchmark for $syscall in group $i using $1 settings..."
		sudo ./fullAutomation.py $1 $2 benchmarkProgram/baseSyscall/$i/$j 
		genClingoGraph/clingo2Dot.py result.clingo result.dot
		dot -Tsvg -o "result/${syscall,,}.svg" result.dot
		rm -f result.clingo
		rm -f result.dot

		genClingoGraph/clingo2Dot.py working/general.clingo-control control.dot
		dot -Tsvg -o "result/${syscall,,}-control.svg" control.dot
		rm -f control.dot

		genClingoGraph/clingo2Dot.py working/general.clingo-program program.dot
		dot -Tsvg -o "result/${syscall,,}-program.svg" program.dot
		rm -f program.dot

		echo "Process complete for $syscall. Result stored in result/${syscall,,}.svg"
	done
done
