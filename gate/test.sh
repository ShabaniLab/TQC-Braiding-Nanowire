#!/bin/sh

file_circuit_config="circuit-config.csv"
file_nanowire_str="nanowire-structure.csv"
file_nanowire_positions="nanowire-positions.csv"
file_initial_positions="initial-positions.csv"
file_braid_sequence="braid-sequence.csv"
file_tqc_fusion_rules="fusion-rules.csv"
file_tqc_fusion_channel="fusion-channel.csv"

KEY_GATE="gate"
KEY_PARTICLES="particles"
KEY_QUBITS="qubits"
KEY_VOLTAGES="voltages"
gate=""
qubits=""
particles=""
voltages=""
RET_FALSE=0
RET_TRUE=1
OUTPUTS=./outputs
MSG_NO_IP_OP="\033[0;31mError:\033[0m Please provide \033[0;31minputs\033[0m and \033[0;31moutputs\033[0m directories of your choice as arguments"
MSG_EX_IP_OP="\033[0;33mLike so:\033[0m ./run.sh \033[0;33m./inputs-hadamard\033[0m \033[0;33m./outputs-hadamard\033[0m"
MSG_OP_ALT="All your outputs will be saved at \033[0;36m${OUTPUTS}\033[0m instead"

# Checks for an inputs and outputs dir
if [ -z $1 ];
then
    echo $MSG_NO_IP_OP
    echo $MSG_EX_IP_OP
    exit
fi
if [ -z $2 ];
then
    echo $MSG_NO_IP_OP
    echo $MSG_EX_IP_OP
    echo $MSG_OP_ALT
else
    OUTPUTS=$2
fi

# Validates the contents of the files of the inputs dir
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
exit $RET_TRUE
