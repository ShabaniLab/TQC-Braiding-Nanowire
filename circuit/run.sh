#!/bin/sh

# --------------------------------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------------------------------
# inputs
file_circuit_config="circuit-config.yml"
file_nanowire_config="nanowire.yml"
file_fusion_config="fusion.yml"
file_gate_config="-config.yml"

# outputs
file_tqc_measurements="tqc-fusion.csv"
file_nanowire_vertex="nanowire-vertices.csv"
file_nanowire_matrix="nanowire-matrix.csv"
file_nanowire_states="nanowire-states.csv"
file_particle_movement="particle-movements.csv"
file_particle_position_braid="particle-positions-braid.csv"
file_particle_position_nanowire="particle-positions-nanowire.csv"

RET_FALSE=1
RET_TRUE=0

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;33m###########################################################################\033[0m"
echo "\033[1;33m#                 P R E P R O C E S S I N G    I N P U T S                #\033[0m"
echo "\033[0;33m###########################################################################\033[0m"

echo "Inputs preprocessing started..."
# --------------------------------------------------------------------------------------------------
# Checks for an inputs dir
# --------------------------------------------------------------------------------------------------
if [ -z $1 ];
then
    echo "\033[0;31mError:\033[0m Please provide \033[0;31minputs\033[0m and \033[0;31moutputs\033[0m directories of your choice as arguments"
    echo "\033[0;31mInputs preprocessing failed...\033[0m"
    exit $RET_FALSE
fi

# --------------------------------------------------------------------------------------------------
# Validates the inputs dir: circuit-config.yml and fusion.yml
# --------------------------------------------------------------------------------------------------
./validate.sh \
    $1/$file_circuit_config\
    $1/$file_nanowire_config\
    $1/$file_fusion_config

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mInputs preprocessing failed...\033[0m"
    exit $RET_FALSE
fi
line=$(head -n 1 $1/$file_circuit_config)
application=$(echo $line | cut -d ':' -f 2)

# --------------------------------------------------------------------------------------------------
# Create a new outputs dir
# --------------------------------------------------------------------------------------------------
OUTPUTS=./outputs
if [ ! -z $2 ];
then
    OUTPUTS=$2
fi
if [ -d $OUTPUTS ];
then
    rm -r $OUTPUTS
fi
mkdir $OUTPUTS
echo "All your outputs will be saved at \033[0;36m${OUTPUTS}\033[0m"

# --------------------------------------------------------------------------------------------------
# Generate headers for output files
# --------------------------------------------------------------------------------------------------
python tqc-preprocess-inputs.py \
    $1/$file_circuit_config\
    $1/$file_nanowire_config\
    $OUTPUTS/$file_particle_movement\
    $OUTPUTS/$file_nanowire_states\
    $OUTPUTS/$file_particle_position_braid\
    $OUTPUTS/$file_particle_position_nanowire

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mInputs preprocessing failed...\033[0m"
    exit $RET_FALSE
fi

echo "\033[0;32mInputs preprocessing completed...\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;33m###########################################################################\033[0m"
echo "\033[1;33m#               P R E P R O C E S S I N G    N A N O W I R E              #\033[0m"
echo "\033[0;33m###########################################################################\033[0m"

echo "Nanowire preprocessing started..."
: > $OUTPUTS/$file_nanowire_vertex
: > $OUTPUTS/$file_nanowire_matrix
python tqc-preprocess-nanowire.py\
    $1/$file_nanowire_config\
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
echo "\033[0;36m################################################################################################\033[0m"
echo "\033[1;36m    T O P O L O G I C A L  Q U A N T U M  C O M P U T I N G: \033[1;37m${application}\033[0m  \033[1;36mC I R C U I T    \033[0m"
echo "\033[0;36m################################################################################################\033[0m"

echo "Topological Quantum Computing started..."
python tqc-algorithm-compute.py\
    $1/$file_circuit_config\
    $1/$file_nanowire_config\
    $file_gate_config\
    $OUTPUTS/$file_nanowire_vertex\
    $OUTPUTS/$file_nanowire_matrix\
    $OUTPUTS/$file_particle_position_nanowire\
    $OUTPUTS/$file_particle_position_braid\
    $OUTPUTS/$file_particle_movement\
    $OUTPUTS/$file_nanowire_states

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mTopological Quantum Computing failed...\033[0m"
    exit $RET_FALSE
fi
echo "\033[0;32mTopological Quantum Computing completed...\033[0m"

# --------------------------------------------------------------------------------------------------

echo ""
echo "\033[0;36m###########################################################################\033[0m"
echo "\033[1;36m#                     M E A S U R I N G    A N Y O N S                    #\033[0m"
echo "\033[0;36m###########################################################################\033[0m"

echo "Measurement (Fusion) started..."
python tqc-algorithm-measure.py \
    $1/$file_circuit_config\
    $1/$file_fusion_config\
    $OUTPUTS/$file_particle_position_nanowire\
    $OUTPUTS/$file_nanowire_matrix\
    $OUTPUTS/$file_nanowire_vertex\
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
    $1/$file_circuit_config\
    $1/$file_nanowire_config\
    $OUTPUTS/$file_nanowire_matrix\
    $OUTPUTS/$file_nanowire_vertex\
    $OUTPUTS/$file_nanowire_states\
    $OUTPUTS/$file_particle_position_braid\
    $OUTPUTS

check=$?
if [ "$check" -eq $RET_FALSE ];
then
    echo "\033[0;31mAnimation operation failed...\033[0m"
    exit $RET_FALSE
fi
echo "\033[0;32mBraid and Nanowire animation completed...\033[0m"

rm $OUTPUTS/$file_nanowire_matrix
rm $OUTPUTS/$file_nanowire_vertex

exit $RET_TRUE

# --------------------------------------------------------------------------------------------------
