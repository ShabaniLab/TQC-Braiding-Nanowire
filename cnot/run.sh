#!/bin/sh

echo ""
echo "##########################################################################"
echo "#              P R E P R O C E S S I N G    N A N O W I R E              #"
echo "##########################################################################"
# Files
file_nanowire_str="nanowire-structure.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_matrix="nanowire-matrix.csv"

# Constructing the Adjacency Matrix for the given Nanowire structure
echo "Nanowire preprocessing started..."
: > ./outputs/$file_nanowire_vertex
: > ./outputs/$file_nanowire_matrix
python tqc-preprocess-nanowire.py ./inputs/$file_nanowire_str ./outputs/$file_nanowire_vertex ./outputs/$file_nanowire_matrix
echo "Nanowire preprocessing completed..."

echo ""
echo "##########################################################################"
echo "#        P R E P R O C E S S I N G    B R A I D    S E Q U E N C E       #"
echo "##########################################################################"
# Files
file_circuit_config="circuit-config.csv"
file_braid_sequence="braid-sequence.csv"
file_initial_positions="initial-positions.csv"
file_particle_position_nanowire="particle-positions-nanowire.csv"

echo "Braid generation preprocessing started..."
# python tqc-preprocess-braid.py $file_circuit_config
cat ./inputs/$file_initial_positions > ./outputs/$file_particle_position_nanowire
echo "Braid generation preprocessing completed..."

echo ""
echo "##########################################################################"
echo "#       S T A R T I N G     B R A I D I N G    O P E R A T I O N S       #"
echo "##########################################################################"
# Files
file_particle_movement="particle-movements.csv"
file_nanowire_states="nanowire-states.csv"
file_particle_position_braid="particle-positions-braid.csv"

echo "Braiding started..."
echo "Par1,Par2,Particle,Path,Vg11,Vg12,Vg21,Vg22" > ./outputs/$file_particle_movement
echo "Par1,Par2,P1,P2,P3,P4,P5,P6,Vg11,Vg12,Vg21,Vg22" > ./outputs/$file_nanowire_states
echo "Par1,Par2,P1,P2,P3,P4,P5,P6" > ./outputs/$file_particle_position_braid
python tqc-algorithm-compile.py ./inputs/$file_nanowire_str ./outputs/$file_nanowire_vertex ./outputs/$file_nanowire_matrix ./inputs/$file_braid_sequence ./outputs/$file_particle_position_nanowire ./outputs/$file_particle_movement ./outputs/$file_nanowire_states ./outputs/$file_particle_position_braid
echo "Braiding completed..."

echo ""
echo "##########################################################################"
echo "#                    M E A S U R I N G    A N Y O N S                    #"
echo "##########################################################################"
# Files
file_tqc_fusion_rules="fusion-rules.csv"
file_tqc_fusion_channel="fusion-channel.csv"
file_tqc_measurements="tqc-fusion.csv"
qubits="2"

echo "Measurement (Fusion) started..."
python tqc-algorithm-measure.py ./outputs/$file_particle_position_nanowire ./inputs/$file_tqc_fusion_rules ./inputs/$file_tqc_fusion_channel ./outputs/$file_nanowire_matrix ./outputs/$file_nanowire_vertex $qubits  >> ./outputs/$file_tqc_measurements
echo "Measurement (Fusion) completed..."

echo ""
echo "##########################################################################"
echo "#       A N I M A T I N G    B R A I D    A N D    N A N O W I R E       #"
echo "##########################################################################"
# Files
file_nanowire_positions="nanowire-positions.csv"
gate="cnot"

echo "Braid and Nanowire animation started..."
python tqc-animate.py ./outputs/$file_nanowire_matrix ./outputs/$file_nanowire_vertex ./inputs/$file_nanowire_positions ./outputs/$file_nanowire_states ./outputs/$file_particle_position_braid $gate
echo "Braid and Nanowire animation completed..."

echo ""
echo "##########################################################################"
