#!/bin/sh

# Variables
file_nanowire_str="nanowire-structure.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_matrix="nanowire-matrix.csv"
file_braid_sequence="braid-sequence.csv"
file_particle_position="particle-positions.csv"
file_particle_movement="particle-movements.csv"
file_nanowire_states="nanowire-states.csv"
file_tqc_metrics="tqc-metrics.csv"

# Constructing the Adjacency Matrix for the given Nanowire structure
# : > $file_nanowire_vertex
# : > $file_nanowire_matrix
# python nanowire-graph.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix

# TQC - performing braiding on the Nanowire
echo "Particle,Path,V11,V12,V21,V22" > $file_particle_movement
python tqc-compiler.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix $file_braid_sequence $file_particle_position

# Calculating metrics
# : > $file_nanowire_states
# : > $file_tqc_metrics
# python tqc-compiler-metrics.py $file_particle_movement $file_nanowire_states $file_tqc_metrics
