#!/bin/sh

file_config="./inputs/circuit-config.csv"
MSG_NO_CFG="Please provide a valid circuit-config.csv file in the following format:"
MSG_CFG_FORMAT="gate=hadamard\nparticles=4\nqubits=1\nvoltages=4"
gate=""
qubits=""
particles=""
voltages=""

# Checks if there is a valid circuit-config file
if [ ! -f $file_config ]
then
    echo $MSG_NO_CFG
    echo $MSG_CFG_FORMAT
    exit
fi

# Extracts the required circuit config data
key_gate="gate"
key_particles="particles"
key_qubits="qubits"
key_voltages="voltages"
while IFS= read -r line
do
    if [[ $line == *"$key_gate"* ]];
    then
        gate=$(echo $line| cut -d'=' -f 2)
    elif [[ $line == *"$key_particles"* ]];
    then
        particles=$(echo $line| cut -d'=' -f 2)
    elif [[ $line == *"$key_qubits"* ]];
    then
        qubits=$(echo $line| cut -d'=' -f 2)
    elif [[ $line == *"$key_voltages"* ]];
    then
        voltages=$(echo $line| cut -d'=' -f 2)
    fi
done < "$file_config"

# Checks if there are all the required config data
if [ -z $gate ] || [ -z $qubits ] || [ -z $particles ] || [ -z $voltages ];
then
    echo $MSG_NO_CFG
    echo $MSG_CFG_FORMAT
    exit
fi

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

key_pair="Par1,Par2"
key_par="Particle"
key_path="Path"
key_pars=""
key_volts=""
key_P="P"
key_V="Vg"

# Constructing key_pars
for ((i=1;i<$(( $particles ));i++))
do
    pi="${key_P}${i}"
    key_pars="${key_pars}${pi},"
done
key_pars="${key_pars}${key_P}${particles}"

# Constructing key_volts
for ((i=0;i<$(( $voltages ));i++))
do
    v1=$(($i/2 + 1))
    v2=$(($i%2 + 1))
    vi="${key_V}${v1}${v2}"
    if [[ $i == $(($voltages - 1)) ]];
    then
        key_volts="${key_volts}${vi}"
    else
        key_volts="${key_volts}${vi},"
    fi
done

heading1="${key_pair},${key_par},${key_path},${key_volts}"
heading2="${key_pair},${key_pars},${key_volts}"
heading3="${key_pair},${key_pars}"

echo "Braiding started..."

echo $heading1 > ./outputs/$file_particle_movement
echo $heading2 > ./outputs/$file_nanowire_states
echo $heading3 > ./outputs/$file_particle_position_braid

# echo "Par1,Par2,Particle,Path,Vg11,Vg12,Vg21,Vg22" > ./outputs/$file_particle_movement
# echo "Par1,Par2,P1,P2,P3,P4,Vg11,Vg12,Vg21,Vg22" > ./outputs/$file_nanowire_states
# echo "Par1,Par2,P1,P2,P3,P4" > ./outputs/$file_particle_position_braid
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

echo "Measurement (Fusion) started..."
python tqc-algorithm-measure.py ./outputs/$file_particle_position_nanowire ./inputs/$file_tqc_fusion_rules ./inputs/$file_tqc_fusion_channel ./outputs/$file_nanowire_matrix ./outputs/$file_nanowire_vertex $qubits >> ./outputs/$file_tqc_measurements
echo "Measurement (Fusion) completed..."

echo ""
echo "##########################################################################"
echo "#       A N I M A T I N G    B R A I D    A N D    N A N O W I R E       #"
echo "##########################################################################"
# Files
file_nanowire_positions="nanowire-positions.csv"

echo "Braid and Nanowire animation started..."
python tqc-animate.py ./outputs/$file_nanowire_matrix ./outputs/$file_nanowire_vertex ./inputs/$file_nanowire_positions ./outputs/$file_nanowire_states ./outputs/$file_particle_position_braid $gate
echo "Braid and Nanowire animation completed..."

echo ""
echo "##########################################################################"
