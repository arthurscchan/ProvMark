% Match two graphs and check whether they are isomorphic, ignoring label structure.
% Generate matches s.t. each node in n1 is matched to one node in n2.
{ match(X,Y) : n2(Y,_)} = 1 :- n1(X,_).
% and vice versa
{ match(X,Y) : n1(X,_)} = 1 :- n2(Y,_).

% Generate edge matches s.t. each node in e1 is matched to one node in e2.
{ match(X,Y) : e2(Y,_,_,_)} = 1 :- e1(X,_,_,_).
% and vice versa
{ match(X,Y) : e1(X,_,_,_)} = 1 :- e2(Y,_,_,_).

% distinct nodes/edges  map to distinct nodes/edges in both directions.
:- X <> Y, match(X,Z), match(Y,Z).
:- X <> Y, match(Z,Y), match(Z,X).

% node in g1 maps to node in g2 with same label
:- n1(X,L), match(X,Y), not n2(Y,L).

% node in g2 maps to node in g1 with same label
:- n2(Y,L), match(X,Y), not n1(X,L).

% edge in g1 maps to edge in g2 with same label
:- e1(E1,_,_,L), match(E1,E2), not e2(E2,_,_,L).

% edge in g2 maps to edge in g1 with same label
:- e2(E2,_,_,L), match(E1,E2), not e1(E1,_,_,L).

% edge is mapped only if source and target are mapped
:- e1(E1,X1,_,_), match(E1,E2), e2(E2,Y1,_,_), not match(X1,Y1).
:- e1(E1,_,X2,_), match(E1,E2), e2(E2,_,Y2,_), not match(X2,Y2).

% properties on one side exist on the other
:- l1(X,K,_), match(X,Y), not l2(Y,K,_).
:- l2(Y,K,_), match(X,Y), not l1(X,K,_).


% Display
#show match/2.

