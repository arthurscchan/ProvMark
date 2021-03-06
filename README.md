# ProvMark

ProvMark is a fully automated system that generates system level provenance benchmarks from provenance information collected by different provenance collection tools and systems, such as SPADE, OPUS and CamFlow.

# System Description

## Stage 1 Execute provenance collecting tools of choice on chosen syscall benchmark program (and control program)
In this step, the chosen syscall and control program will be prepared in a clean stage. Then the chosen provenance collecting tools will be started and record provenance of the execution of those programs with multiple trials. The provenance collecting tools will create one set of provenance results per trial per program. These results are collected from the provenance collecting tools and are further processed and analysed in our system to generate benchmarks. Currently, there are three types of output format supported: [Graphviz](https://www.graphviz.org/), [Neo4j Graph db (in full db or cypher dump of db)](https://neo4j.com/) and the [PROV-JSON](https://www.w3.org/Submission/2013/SUBM-prov-json-20130424/) format.

## Stage 2 Transform raw result to Clingo graph format
[Potassco Clingo](https://potassco.org/) is an Answer Set Programming tool that provides powerful modelling ability to solve combinatorial problems. We make use of it to solve the complicated graph comparison problems for matching vertices and edges in multiple trials of benchmark program execution for generalization of graphs and identification of additional elements (benchmarks of a syscall for certain provenance collecting tools). In this step, the system will run a different script to transform the raw result generated by the provenance collecting tools to clingo graph format for further processing. As this provenance information is supposed to describe the execution trace of the chosen syscall program, it is always possible to transform into a directed graph. Each trial result will be transformed into one clingo graph for the next stage.

## Stage 3 Generalize resulting graph for multiple trial
In this stage, multiple clingo graphs descirbing the multiple trials of the same program execution will be put together to be compared. The clingo graph will match the elements in the graph two by two and provide a matching list of nodes and edges with least edit distance. Then the properties in the graph will be compared one by one, and noise will be identified and removed. The result of this stage should be a generalized graph for the control program and another generalized graph for the chosen syscall program. They should contain the information which is truly related to the program execution with minimum noise.

## Stage 4 Generating benchmark of chosen syscall for chosen provenance collecting tool
This is the last stage of the benchmarking system execution. In this stage, the two generalized graphs will be compared to each other. As we assume that the chosen syscall is always a few steps or command more than the control program execution and they are both executed based on a same stage environment with the same language. So the additional elements in the generalized syscall graph shows the patterns that can be used as a benchmark to identify this syscall when we are using the chosen provenance collecting tools. All those addtional branches and properties will be identified and summarized in the result file in clingo format. Currently, this is the end of the full system. The clingo format graph can be transformed into Graphiz DOT format which allows further transformation to general displayable image.

## Extra Stage Benchmark Comparison and Evaluation
This is an extra stage provided by ProvMark. It is a standalone subsystem that takes the set of benchmark and a testing program and identify if the patterns described by the benchmark group exists in the testing program. Is it done by comparing the provenance graph of the testing program with the set of benchmark. If the benchmark patterns does exists in the provenance graph of the testing program. All elements in the benchmark should be reappearing in the provenance graph of the testing program. Thus the edit distance between the provenance graph of the testing program and the benchmark itself should be equal to the numbers of elements difference between them. We add in a threshold value to allow some errors from noise in the provenance generation process. This allow a slightly differece between the edit distance and elements difference between the two graph. Of course, the same provenance collecting tools is used in the testing stage. The result will be a simple yes or no answer. It can help to identify certain action in a testing program and together provide expressiveness evaluation of ProvMark and the provenance collecting tools itself. The false positive rate and false negative rate identify the correctness and completeness of the benchmark generation and collection respectively. It can help to identify bugs in the provenance collecting tools and ProvMark generation process. It can be further use as a pattern discovery of certain existing syscall patterns for security and forensics usage.

## Deterministic and Non-deterministic Input
It is worth mentioning that deterministic input will only result in one set of benchmark result. While ProvMark will generate multiple set of benchmark for non-deterministic input to cover patterns across different execution order affected by non-deterministism. The different is there are multiple background graph and foreground graph generated in the mid-process and they are grouped by their ftrace fingerprint separately. The graph with the same ftrace fingerprint are considered as the same execution branch and will be generalized together. Each generalized foreground graph will match will its closest generalized background graph to generate a separate benchmark and thus the output from stage 4 will be a set of benchmark. But currently we provide no guarantee that all of the branches will be executed, we are currently working on method to have full coverage of all possible branches.

# Folder Structure
- benchmarkProgram: Contains sample c program for the collection of provenance information on different syscall
- clingo: Contains the clingo code
- config: Contains the configuration profile of different tool choices for stage 1 and stage 2
- core: Contains the entrance for the training (benchmark generation) and testing (benchmark evaluation)
- documentation: Contains the documentation for ProvMark
- genClingoGraph: Contains code to transform graph format
- processGraph: Contains code to handle graph comparison and generalization
- sampleResult: Contains sample benchmark result on our trial
- startTool: Contains tools to handle provenance collecting tools currently supported and retrieve result from them
- template: Contains html template for result generation
- vagrant: Contains vagrant files for those provenance collecting tools currently supported

# Use of Clingo
The content inside the directory Clingo is an external work provided by University of Potsdam as part of the [Potassco system](https://potassco.org/). It is distributed under MIT License and the developer retains their right for the distribution of the binary and code. We provide a local copy of the compiled version 5.2.1 for convenience only. You should always search for the original code and binary of Clingo from the original developer. Here is a link to the original developer [http://potassco.sourceforge.net/]

# Documentation

- [Installation](./documentation/install.md)
- [Configuration](./documentation/config.md)
- [Usage](./documentation/usage.md)
