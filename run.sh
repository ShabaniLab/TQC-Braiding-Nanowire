#!/bin/sh

# Variables
file_nanowire_str="nanowire-structure.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_graph="nanowire-graph.csv"
file_position="position.csv"
file_braid_sequence="braid-sequence.csv"
file_movement="movements.csv"

# constructing the adjacency matrix using the nanowire structure.
: > $file_nanowire_graph
python nanowire-graph.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_graph

# echo "\n" >> $file_movement
python particle-movement.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_graph $file_position $file_braid_sequence
