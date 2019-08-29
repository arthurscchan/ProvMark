# ProvMark Usage

## Single Execution

Usage:
~~~~
./fullAutomation.py <Tools> <Tools Base Directory> <Benchmark Directory> [<Trial>]
~~~~

Example for generating benchmark for syscall create using SPADE with Graphviz storage:
~~~~
./fullAutomation.py spg /path/to/spade/base/directory ./benchmarkProgram/baseSyscall/grpCreat/cmdCreat 2 
~~~~

Example for CamFlow (note that the "tool base directory" is unused and arbitrary in this case):
~~~~
./fullAutomation.py cam . ./benchmarkProgram/baseSyscall/grpCreat/cmdCreat 2 
~~~~

#### Currently Supported Tools:
- spg:    SPADE with Graphviz storage
- spn:    SPADE with Neo4j storage
- opu:    OPUS
- cam:    CamFlow

#### Tools Base Directory:
- Base directory of the chosen tool, it is assumed that if you want to execute this benchmarking system on certain provenance collecting tools, you should have installed that tools with all dependencies required by the tools. If you build ProvMark with the given Vagrant script, the default tools base directory is shown as follows; ignored for CamFlow
- SPADE: /home/vagrant/SPADE
- OPUS: You should have installed OPUS manually
- CamFlow: ./

#### Benchmark Directory:
- Base directory of the benchmark program
- Point the script to the syscall choice for the benchmarking process

#### Number of trials (Default: 2):
- Number of trials executed for each graph for generalization
- More trials will result in longer processing time, but provide a more accurate result as multiple trial can help to filter out uncertainty and unrelated elements and noise

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

#### Visualization of Clingo Graph

Usage:
~~~~
./genClingoGraph/clingo2Dot.py <Clingo Graph> <Output Graph>
~~~~

Example:
~~~~
./genClingoGraph/clingo2Dot.py result/result.clingo result/result.dot
~~~~

The command shown above is used to transfer clingo graph into DOT format. DOT is a graph description language. The default tool of DOT visualization is Graphviz DOT tool, which is shown as follows:

Usage:
~~~~
dot -T<Graph Type> -o <Output File> <DOT graph>
~~~~

Example for visualizing DOT graph as pdf format:
~~~~
dot -Tpdf -o result/result.pdf result/result.dot
~~~~

Example for visualizing DOT graph as svg format:
~~~~
dot -Tsvg -o result/result.pdf result/result.dot
~~~~

#### Sample Clingo Graph

~~~~
ng1(n1,"File").
pg1(n1,"Userid","1").
pg1(n1,"Name","text").

ng2(n1,"File").
ng2(n2,"Process").
pg2(n1,"Userid","1").
eg2(e1,n1,n2,"Used").
pg2(n1,"Name","text").
~~~~

![Visualized graph for the above Clingo code](img/sample.pdf)

## Batch Execution

Automatically execute ProvMark for all syscall currently supported. The runTests.sh script will search for all benchmark program recrusively in the default benchmarkProgarm folder and benchmark them one by one. It will also group the final result and post process them according to the given result type paramemter.

Usage:
~~~~
./runTests.sh <Tools> <Tools_Path> <Result Type>
~~~~

Example for batch execution of spade with Graphviz storage and generate html webpage to display all result
~~~~
./runTests.sh spg /home/vagrant/SPADE rh
~~~~

Example for batch execution of CamFlow (again, the base directory is ignored in this case):
~~~~
./runTests.sh cam . rh
~~~~

#### Currently Supported Tools:
- spg:    SPADE with Graphviz storage
- spn:    SPADE with Neo4j storage
- opu:    OPUS
- cam:    CamFlow

#### Tools Base Directory:
- Base directory of the chosen tool, it is assumed that if you want to execute this benchmarking system with a specific provenance collecting tool; ignored for CamFlow

#### Result Type:
- rb: benchmark only
- rg: benchmark and generalized foreground and background graph only
- rh: html page displaying benchmark and generalized foreground and background graph

#### Output:
- Result stored in finalResult directory
- Each syscall has a subdirectory under finalResult directory
- Graph in svg format
- Benchmark graph stored in each syscall subdirectory separately
- Generalized foreground and background graph stored in each syscall subdirectory separately (rg and rh only)
- An index.html file stored in finalResult directory to display all graph in html table (rh only)

#### Creation of sample output

For the generation of the sample output, we have used the provided Vagrant script to build up the environment for the three provenance systems and execute a batch execution in each of the built virtual machine. The following command is used in each virtual machine respectively.

##### SPADE
~~~~
./runTests.sh spg /home/vagrant/SPADE rh
~~~~

##### OPUS
~~~~
./runTests.sh opu /home/vagrant/opus rh
~~~~

##### CamFlow
~~~~
./runTests.sh cam . rh 11
~~~~
