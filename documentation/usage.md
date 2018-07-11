# ProvMark Usage

## Single Execution

Usage:
~~~~
./fullAutomation <Tools> <Tools Base Directory> <Benchmark Directory> [<Trial>]
~~~~

Example for generating benchmark for syscall create using SPADE with Graphviz storage:
~~~~
./fullAutomation.py spg /path/to/spade/base/directory ./benchmarkProgram/baseSyscall/grpCreat/cmdCreat 2 
~~~~

#### Currently Supported Tools:
- spg:    SPADE with Graphviz storage
- spn:    SPADE with Neo4j storage
- opu:    OPUS
- cam:    CamFlow

#### Tools Base Directory:
- Base directory of the chosen tool, it is assumed that if you want to execute this benchmarking system on certain provenance collecting tools, you should have installed that tools with all dependencies required by the tools.

#### Benchmark Directory:
- Base directory of the benchmark program
- Point the script to the syscall choice for the benchmarking process

#### Trial (Default: 2):
- Number of trial executed for each graph for generalization
- More trial will result in longer processing time, but provide a more accurate result as multiple trial can help to filter out uncertainty and unrelated elements and noise

#### Output:
- Three clingo graphs stored in result folder
- general.clingo-program: generalized foreground graph
- general.clingo-control: generalized background graph
- result.clingo: final benchmark graph

#### Output Clingo File Format

- Node

~~~~
n<graph identifier>(<node identifier>,<type>)
~~~~

- Edge (Directed edge)

~~~~
e<graph identifier>(<edge identifier>, <start node identifier>, <end node identifier>, <type>)
~~~~

- Properties

~~~~
l<graph identifier>(<node / edge identifier>, <key>, <value>)
~~~~


## Batch Execution

Auto execute ProvMark for all syscall currently supported

Usage:
~~~~
./runTests.sh <Tools> <Tools_Path> <Result Type>
~~~~

Example for batch execution of spade with Graphviz storage and generate html webpage to display all result
~~~~
./runTests.sh spg /path/to/spade/base/directory rh
~~~~

#### Currently Supported Tools:
- spg:    SPADE with Graphviz storage
- spn:    SPADE with Neo4j storage
- opu:    OPUS
- cam:    CamFlow

#### Tools Base Directory:
- Base directory of the chosen tool, it is assumed that if you want to execute this benchmarking system on certain provenance collecting to$

#### Result Type:
- rb: benchmark only
- rg: benchmark and generalized foreground and background graph only
- rh: html page displaying benchmark and generalied foreground and background graph

#### Output:
- Result stored in finalResult directory
- Each syscall has a subdirectory under finalResult directory
- Graph in svg format
- Benchmark graph stored in each syscall subdirectory separately
- Generalized foreground and background graph stored in each syscall subdirectory separately (rg and rh only)
- An index.html file stored in finalResult directory to display all graph in html table (rh only)
