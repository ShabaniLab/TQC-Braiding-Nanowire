#!/bin/sh

################################################################################
# Preprocessing - Nanowire
################################################################################
# Files
file_nanowire_str="nanowire-structure.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_matrix="nanowire-matrix.csv"

# Constructing the Adjacency Matrix for the given Nanowire structure
: > $file_nanowire_vertex
: > $file_nanowire_matrix
python nanowire-graph.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix

################################################################################
# Preprocessing - Braid sequence and Initial positions
################################################################################
# Files
file_braid_data="circuit-config.csv"
file_braid_sequence="braid-sequence.csv"
file_initial_positions="initial-positions.csv"
file_particle_position="particle-positions.csv"

# Generating the braid sequence for the given gate
# python braid-generate.py $file_braid_data > $file_braid_sequence
cat $file_initial_positions > $file_particle_position

################################################################################
# TQC Braiding Nanowire Algorithm
################################################################################
# Files
file_particle_movement="particle-movements.csv"
file_nanowire_states="nanowire-states.csv"
file_particle_braid_pos="braid-particle-positions.csv"

# TQC - Performing Braiding on the Nanowire
echo "Par1,Par2,Particle,Path,Vg11,Vg12,Vg21,Vg22" > $file_particle_movement
echo "Par1,Par2,P1,P2,P3,P4,Vg11,Vg12,Vg21,Vg22" > $file_nanowire_states
echo "Par1,Par2,P1,P2,P3,P4" > $file_particle_braid_pos
echo "----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x -----"
echo "Starting Braid operations..."
python compiler.py $file_nanowire_str $file_nanowire_vertex $file_nanowire_matrix $file_braid_sequence $file_particle_position $file_particle_movement $file_nanowire_states $file_particle_braid_pos

################################################################################
# Measurement - Fusion
################################################################################
# Files
file_tqc_fusion_rules="fusion-rules.csv"
file_tqc_fusion_channel="fusion-channel.csv"
file_tqc_measurements="tqc-phase-s-fusion.csv"

# Performing measurements
echo "Measuring Anyons..."
python measure.py $file_particle_position $file_tqc_fusion_rules $file_tqc_fusion_channel $file_nanowire_matrix $file_nanowire_vertex >> $file_tqc_measurements

################################################################################
# Animation - Braiding and Nanowire movement
################################################################################
# Files
file_nanowire_positions="nanowire-positions.csv"

# Nanowire movement and Braiding animation
# echo "Performing Phase-S Braid pattern and Nanowire movement animations..."
# python animation.py $file_nanowire_matrix $file_nanowire_vertex $file_nanowire_positions $file_particle_braid_pos $file_nanowire_states

echo "----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x ----- x -----"
