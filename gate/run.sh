#!/bin/sh

file_circuit_config="circuit-config.csv"
file_nanowire_str="nanowire-structure.csv"
file_braid_sequence="braid-sequence.csv"
file_initial_positions="initial-positions.csv"
file_tqc_fusion_rules="fusion-rules.csv"
file_tqc_fusion_channel="fusion-channel.csv"
file_nanowire_positions="nanowire-positions.csv"
file_tqc_measurements="tqc-fusion.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_matrix="nanowire-matrix.csv"
file_particle_position_current="particle-positions-current.csv"
file_particle_movement="particle-movements.csv"
file_nanowire_states="nanowire-states.csv"
file_particle_position_braid="particle-positions-braid.csv"
file_particle_position_nanowire="particle-positions-nanowire.csv"

KEY_GATE="gate"
KEY_QUBITS="qubits"
KEY_PARTICLES="particles"
KEY_VOLTAGES="voltages"
KEY_BRANCHES="branches"
KEY_GROUP="group"
gate=""
qubits=""
particles=""
groups=""
voltages=""
branches=""
RET_FALSE=1
RET_TRUE=0
MSG_NO_IP_OP="\033[0;31mError:\033[0m Please provide \033[0;31minputs\033[0m and \033[0;31moutputs\033[0m directories of your choice as arguments"
MSG_EX_IP_OP="\033[0;33mLike so:\033[0m ./run.sh \033[0;33m./inputs/hadamard\033[0m \033[0;33m./outputs/hadamard\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "###########################################################################"
echo "#                    P R O C E S S I N G    I N P U T S                   #"
echo "###########################################################################"

# --------------------------------------------------------------------------------------------------
# Checks for an inputs and outputs dir
# --------------------------------------------------------------------------------------------------
if [ -z $1 ];
then
    echo $MSG_NO_IP_OP
    echo $MSG_EX_IP_OP
    exit
fi

# --------------------------------------------------------------------------------------------------
# Validates the contents of the files of the inputs dir
# --------------------------------------------------------------------------------------------------
./validate.sh \
    $file_circuit_config\
    $file_nanowire_str\
    $file_nanowire_positions\
    $file_initial_positions\
    $file_braid_sequence\
    $file_tqc_fusion_rules\
    $file_tqc_fusion_channel\
    $1
check=$?
if [ "$check" -eq $RET_FALSE ];
then
    exit $RET_FALSE
fi

# --------------------------------------------------------------------------------------------------
# Read the config data from file
# --------------------------------------------------------------------------------------------------
while IFS= read -r line
do
    value=$(echo $line| cut -d '=' -f 2)
    if [[ $line == *"$KEY_GATE"* ]];
    then
        gate=$value
    elif [[ $line == *"$KEY_PARTICLES"* ]];
    then
        particles=$value
    elif [[ $line == *"$KEY_QUBITS"* ]];
    then
        qubits=$value
    elif [[ $line == *"$KEY_VOLTAGES"* ]];
    then
        voltages=$value
    elif [[ $line == *"$KEY_BRANCHES"* ]];
    then
        branches=$value
    elif [[ $line == *"$KEY_GROUP"* ]];
    then
        group=$value
    fi
done < $1/$file_circuit_config

# --------------------------------------------------------------------------------------------------
# Create a new outputs dir
# --------------------------------------------------------------------------------------------------
OUTPUT=./outputs
OUTPUTS="${OUTPUT}/${gate}"
MSG_OP_ALT="All the outputs will be saved at \033[0;36m${OUTPUTS}\033[0m instead"
if [ -z $2 ];
then
    echo "No output dir provided..."
    echo $MSG_OP_ALT
    if [ -d $OUTPUT ];
    then
        rm -r -d $OUTPUT
    fi
    mkdir $OUTPUT
else
    OUTPUTS=$2
fi
if [ -d $OUTPUTS ];
then
    rm -r -d $OUTPUTS
fi
mkdir $OUTPUTS

# --------------------------------------------------------------------------------------------------
# Generate headers for output files
# --------------------------------------------------------------------------------------------------
cat $1/$file_initial_positions > $OUTPUTS/$file_particle_position_nanowire
tail -n 1 $OUTPUTS/$file_particle_position_nanowire > $OUTPUTS/$file_particle_position_current

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
echo $heading1 > $OUTPUTS/$file_particle_movement
echo $heading2 > $OUTPUTS/$file_nanowire_states
echo $heading3 > $OUTPUTS/$file_particle_position_braid

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;37m###########################################################################\033[0m"
echo "\033[0;37m    Constructing a \033[1;36m${qubits}\033[0m\033[0;37m-qubit(s) \033[1;36m${gate}\033[0m\033[0;37m gate by braiding \033[1;36m${particles}\033[0m\033[0;37m quasi-particles\033[0m"
echo "\033[0;37m###########################################################################\033[0m"

echo ""
echo "\033[0;33m###########################################################################\033[0m"
echo "\033[1;33m#               P R E P R O C E S S I N G    N A N O W I R E              #\033[0m"
echo "\033[0;33m###########################################################################\033[0m"

echo "Nanowire preprocessing started..."
: > $OUTPUTS/$file_nanowire_vertex
: > $OUTPUTS/$file_nanowire_matrix
python tqc-preprocess-nanowire.py\
    $1/$file_nanowire_str\
    $OUTPUTS/$file_nanowire_vertex\
    $OUTPUTS/$file_nanowire_matrix

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mNanowire preprocessing failed...\033[0m"
    exit $RET_FALSE
fi
echo "\033[0;32mNanowire preprocessing completed...\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;33m###########################################################################\033[0m"
echo "\033[1;33m#        P R E P R O C E S S I N G    B R A I D    S E Q U E N C E        #\033[0m"
echo "\033[0;33m###########################################################################\033[0m"

echo "Braid generation preprocessing started..."
# python tqc-preprocess-braid.py
echo "\033[0;32mBraid generation preprocessing completed...\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;33m###########################################################################\033[0m"
echo "\033[1;33m#              P R E P R O C E S S I N G    P O S I T I O N S             #\033[0m"
echo "\033[0;33m###########################################################################\033[0m"

echo "Positions preprocessing started..."
python tqc-preprocess-positions.py\
    $1/$file_nanowire_str\
    $OUTPUTS/$file_nanowire_vertex\
    $OUTPUTS/$file_nanowire_matrix\
    $OUTPUTS/$file_particle_position_current\
    $OUTPUTS/$file_particle_position_nanowire\
    $OUTPUTS/$file_particle_movement\
    $OUTPUTS/$file_nanowire_states\
    $branches\
    $group\
    $gate

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mPositions preprocessing failed...\033[0m"
    exit $RET_FALSE
fi
echo "\033[0;32mPositions preprocessing completed...\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;36m###########################################################################\033[0m"
echo "\033[1;36m#       S T A R T I N G     B R A I D I N G    O P E R A T I O N S        #\033[0m"
echo "\033[0;36m###########################################################################\033[0m"

echo "Braiding started..."
python tqc-algorithm-compile.py \
    $1/$file_nanowire_str\
    $OUTPUTS/$file_nanowire_vertex\
    $OUTPUTS/$file_nanowire_matrix\
    $1/$file_braid_sequence\
    $OUTPUTS/$file_particle_position_nanowire\
    $OUTPUTS/$file_particle_movement\
    $OUTPUTS/$file_nanowire_states\
    $OUTPUTS/$file_particle_position_braid\
    $gate

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mBraiding operation failed...\033[0m"
    exit $RET_FALSE
fi
echo "\033[0;32mBraiding completed...\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;36m###########################################################################\033[0m"
echo "\033[1;36m#                     M E A S U R I N G    A N Y O N S                    #\033[0m"
echo "\033[0;36m###########################################################################\033[0m"

echo "Measurement (Fusion) started..."
python tqc-algorithm-measure.py \
    $OUTPUTS/$file_particle_position_nanowire\
    $1/$file_tqc_fusion_rules\
    $1/$file_tqc_fusion_channel\
    $OUTPUTS/$file_nanowire_matrix\
    $OUTPUTS/$file_nanowire_vertex\
    $qubits\
    >> $OUTPUTS/$file_tqc_measurements

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mMeasurement operation failed...\033[0m"
    exit $RET_FALSE
fi
echo "\033[0;32mMeasurement (Fusion) completed...\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;34m###########################################################################\033[0m"
echo "\033[1;34m#        A N I M A T I N G    B R A I D    A N D    N A N O W I R E       #\033[0m"
echo "\033[0;34m###########################################################################\033[0m"

echo "Braid and Nanowire animation started..."
python tqc-animate.py \
    $OUTPUTS/$file_nanowire_matrix\
    $OUTPUTS/$file_nanowire_vertex\
    $1/$file_nanowire_positions\
    $OUTPUTS/$file_nanowire_states\
    $OUTPUTS/$file_particle_position_braid\
    $gate\
    $OUTPUTS

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mAnimation operation failed...\033[0m"
    exit $RET_FALSE
fi
echo "\033[0;32mBraid and Nanowire animation completed...\033[0m"
exit $RET_TRUE

# --------------------------------------------------------------------------------------------------
