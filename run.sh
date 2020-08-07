#!/bin/sh

# Variables
file_nanowire_str="nanowire-structure.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_matrix="nanowire-matrix.csv"
file_braid_sequence="braid-sequence.csv"
file_particle_position="particle-positions.csv"
file_particle_movement="particle-movements.csv"
file_particle_states="particle-states.csv"

# constructing the adjacency matrix using the nanowire structure.
: > $file_nanowire_matrix
python nanowire-graph.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix

# : > $file_particle_movement
# : > $file_particle_states
# python tqc-compiler.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix $file_braid_sequence $file_position $file_particle_movement $file_particle_states
