#!/bin/sh

# Variables
file_nanowire_str="nanowire-structure.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_matrix="nanowire-matrix.csv"
file_nanowire_positions="nanowire-positions.csv"
file_braid_data="circuit-config.csv"
file_braid_sequence="braid-sequence.csv"
file_particle_position="particle-positions.csv"
file_particle_movement="particle-movements.csv"
file_particle_braid_pos="braid-particle-positions.csv"
file_nanowire_states="nanowire-states.csv"
file_tqc_metrics="tqc-metrics.csv"

# Preprocessing - Nanowire
# Constructing the Adjacency Matrix for the given Nanowire structure
: > $file_nanowire_vertex
: > $file_nanowire_matrix
python nanowire-graph.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix

# Preprocessing - Braid sequence
# python braid-generate.py $file_braid_data > $file_braid_sequence

# TQC - performing braiding on the Nanowire
echo "Par1,Par2,Particle,Path,X11,X12,X21,X22" > $file_particle_movement
echo "Par1,Par2,P1,P2,P3,P4,P5,P6,X11,X12,X21,X22" > $file_nanowire_states
echo "Par1,Par2,P1,P2,P3,P4,P5,P6" > $file_particle_braid_pos
echo "----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x -----"
python compiler.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix $file_braid_sequence $file_particle_position $file_particle_movement $file_nanowire_states $file_particle_braid_pos
echo "----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x -----"

# Nanowire movement and Braiding animation
echo "Creating CNOT Braid pattern..."
python animation.py $file_nanowire_matrix $file_nanowire_vertex $file_nanowire_positions $file_particle_braid_pos $file_nanowire_states
echo "----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x -----"
