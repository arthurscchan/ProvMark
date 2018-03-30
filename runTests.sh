#!/bin/sh
sudo ./fullAutomation.py $1 . ./benchmarkProgram/control ./benchmarkProgram/grpRename/cmdRename 2 ./cmdRename.clingo
sudo ./fullAutomation.py $1 . ./benchmarkProgram/control ./benchmarkProgram/grpOpenClose/cmdOpen 2 ./cmdOpen.clingo
sudo ./fullAutomation.py $1 . ./benchmarkProgram/control ./benchmarkProgram/grpDup/cmdDup 2 ./cmdDup.clingo
sudo ./fullAutomation.py $1 . ./benchmarkProgram/control ./benchmarkProgram/grpSetuid/cmdSetuid 2 ./cmdSetuid.clingo
sudo ./fullAutomation.py $1 . ./benchmarkProgram/control ./benchmarkProgram/grpSetgid/cmdSetgid 2 ./cmdSetgid.clingo

genClingoGraph/clingo2Dot.py cmdRename.clingo cmdRename.dot
genClingoGraph/clingo2Dot.py cmdOpen.clingo cmdOpen.dot
genClingoGraph/clingo2Dot.py cmdDup.clingo cmdDup.dot
genClingoGraph/clingo2Dot.py cmdSetuid.clingo cmdSetuid.dot
genClingoGraph/clingo2Dot.py cmdSetgid.clingo cmdSetgid.dot

