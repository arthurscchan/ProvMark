% Match graphs that have key-value pairs on nodes and edges
% which can be ignored at a cost, and
% labels on nodes and edges which must match exactly

% Generate matches s.t. each node in n1 is matched to one node in n2.
{ match(X,Y) : n1(X,_), n2(Y,_)} = 1 :- n1(X,_).

% Generate edge matches s.t. each node in e1 is matched to one node in e2.
{ match(X,Y) : e1(X,_,_,_), e2(Y,_,_,_)} = 1 :- e1(X,_,_,_).

% distinct nodes/edges  map to distinct nodes/edges in both directions.
:- X <> Y, match(X,Z), match(Y,Z).
:- X <> Y, match(Z,Y), match(Z,X).

% node in g1 maps to node in g2 with same label
:- n1(X,L), match(X,Y), not n2(Y,L).

% edge in g1 maps to edge in e2 with same label
:- e1(E1,X1,X2,L), match(E1,E2), match(X1,Y1), match(X2,Y2), not e2(E2,Y1,Y2,L).


#minimize { C,X,K : cost(X,K,C)}.

cost(X,K,0) :- l1(X,K,V), match(X,Y), l2(X,K,V).
cost(X,K,1) :- l1(X,K,V1), match(X,Y), l2(X,K,V2), V1 <> V2.
cost(X,K,1) :- l1(X,K,V), match(X,Y), not l2(X,K,_).

% Display
#show match/2.
