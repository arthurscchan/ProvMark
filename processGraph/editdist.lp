% Match graphs that have key-value pairs on nodes and edges
% which can be ignored at a cost, and
% labels on nodes and edges which must match exactly

% Generate matches s.t. at most one matching relation betweek each pair of nodes in
% n1 and n2.
{ match(X,Y) } <= 1 :- n1(X,_), n2(Y,_).

% Generate edge matches s.t. each edge in e1 is matched to at most one edge in e2.
{ match(X,Y) } <= 1 :- e1(X,_,_,_), e2(Y,_,_,_).


% distinct nodes/edges  map to distinct nodes/edges in both directions.
:- X <> Y, match(X,Z), match(Y,Z).
:- X <> Y, match(Z,Y), match(Z,X).

% node in g1 maps to node in g2 with same label
:- n1(X,L), match(X,Y), not n2(Y,L).

% edge in g1 maps to edge in e2 with same label
:- e1(E1,_,_,L), match(E1,E2), not e2(E2,_,_,L).

% edge is mapped only if source and target are mapped
:- e1(E1,X1,_,_), match(E1,E2), e2(E2,Y1,_,_), not match(X1,Y1).
:- e1(E1,_,X2,_), match(E1,E2), e2(E2,_,Y2,_), not match(X2,Y2).

%edits to nodes and node costs
remove_node(X) :- n1(X,_), not match(X,_).
add_node(Y,L) :- n2(Y,L), not match(_,Y).

node_cost(X,0) :- n1(X,_), match(X,Y), n2(Y,_).
node_cost(Y,1) :- add_node(Y,_).
node_cost(X,1) :- remove_node(X).

% edits to edges and edge costs
remove_edge(X) :- e1(X,_,_,_), not match(X,_).
add_edge(Y,S,T,L) :- e2(Y,S,T,L), not match(_,Y).

edge_cost(X,0) :- e1(X,_,_,_), match(X,Y), e2(Y,_,_,_).
edge_cost(Y,1) :- add_edge(Y,_,_,_).
edge_cost(X,1) :- remove_edge(X).

% edits to labels and label costs
% note that we need to account for key-value pairs on added and deleted nodes

update_value(X,K,V1,V2) :- l1(X,K,V1), match(X,Y), l2(X,K,V2), V1 <> V2.
delete_key(X,K) :- l1(X,K,_), match(X,Y), not l2(Y,K,_).
delete_key(X,K) :- l1(X,K,_), remove_node(X).
delete_key(X,K) :- l1(X,K,_), remove_edge(X).
add_key(Y,K,V) :- l2(Y,K,V), match(X,Y), not l1(X,K,_).
add_key(Y,K,V) :- l2(Y,K,V), add_node(Y,_).
add_key(Y,K,V) :- l2(Y,K,V), add_edge(Y,_,_,_).

label_cost(X,K,0) :- l1(X,K,V), match(X,Y), l2(X,K,V).
label_cost(X,K,1) :- update_value(X,K,V1,V2).
label_cost(X,K,1) :- delete_key(X,K).
label_cost(Y,K,1) :- add_key(Y,K,V).

% minimize overall cost

#minimize { NC,X : node_cost(X,NC);
            EC,X : edge_cost(X,EC);
            LC,X,K : label_cost(X,K,LC)}.


% Display
#show match/2.
%#show add_node/2.
%#show remove_node/1.
%#show add_edge/4.
%#show remove_edge/1.
%#show update_value/4.
%#show delete_key/2.
%#show add_key/3.

