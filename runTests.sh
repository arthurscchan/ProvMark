#!/bin/bash

if [[ "$#" -ne 3 || ("$3" != "rb" && "$3" != "rg" && "$3" != "rh") ]] 
then
	echo "Usage: "$0" <Tools> <Tools_Path> <Result Type>"
	echo "Result Type:"
	echo "rb: benchmark only"
	echo "rg: benchmark and generalized foreground and background graph only"
	echo "rh: html page displaying benchmark and generalied foreground and background graph"
	exit 1
fi

sudo mkdir finalResult > /dev/null 2>&1
for i in `ls benchmarkProgram/baseSyscall`
do
	for j in `ls benchmarkProgram/baseSyscall/$i`
	do
		syscall=${j:3}
		syscall=${syscall,,}
		if [ -e finalResult/$syscall ]
		then
			sudo rm -f finalResult/$syscall/*
		else		
			sudo mkdir finalResult/$syscall > /dev/null 2>&1
		fi

		echo "Generating provenance benchmark for $syscall in group $i using $1 settings..."
		sudo ./fullAutomation.py $1 $2 benchmarkProgram/baseSyscall/$i/$j 
		sudo genClingoGraph/clingo2Dot.py result/result.clingo result.dot
		sudo dot -Tsvg -o "finalResult/$syscall/benchmark.svg" result.dot
		sudo rm -f result.dot

		if [ "$3" != "rb" ]
		then
			sudo genClingoGraph/clingo2Dot.py result/general.clingo-control control.dot
			sudo dot -Tsvg -o "finalResult/$syscall/background.svg" control.dot
			sudo rm -f control.dot

			sudo genClingoGraph/clingo2Dot.py result/general.clingo-program program.dot
			sudo dot -Tsvg -o "finalResult/$syscall/foreground.svg" program.dot
			sudo rm -f program.dot

			if [ "$3" = "rh" ]
			then
				row=$row$(cat template/row.html | sed "s/%%%SYSCALL%%%/${syscall}/g")				
			fi
		fi

		echo "Process complete for $syscall."
	done
done

if [ "$3" = "rh" ]
then
	cp template/base.html finalResult/index.html
	sed -i "s/%%%TABLEROW%%%/${row}/g" finalResult/index.html
fi

echo "Process done. Result in finalResult directory."
