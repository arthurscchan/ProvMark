# Clingo: A grounder and solver for logic programs

Clingo is part of the [Potassco](https://potassco.org) project for *Answer Set
Programming* (ASP).  ASP offers a simple and powerful modeling language to
describe combinatorial problems as *logic programs*.  The *clingo* system then
takes such a logic program and computes *answer sets* representing solutions to
the given problem.  To get an idea, check our [Getting
Started](https://potassco.org/doc/start/) page and the [online
version](https://potassco.org/clingo/run/) of clingo.

Please consult the following resources for further information:

  - [**Downloading source and binary releases**](https://github.com/potassco/clingo/releases)
  - [Changes between releases](CHANGES.md)
  - [Documentation](http://sourceforge.net/projects/potassco/files/guide/)
  - [Potassco clingo page](https://potassco.org/clingo/)


## Contents of Linux Binary Release

The `clingo` and `gringo` binaries are compiled statically and include Lua 5.3
but no Python support. For Python support please get a source release and
compile clingo yourself.

- `clingo`: solver for non-ground programs
- `gringo`: grounder
- `clasp`: solver for ground programs
- `reify`: reifier for ground programs
- `lpconvert`: translator for ground formats
