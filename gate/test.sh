#!/bin/sh

file_circuit_config="circuit-config.csv"
file_nanowire_str="nanowire-structure.csv"
file_nanowire_positions="nanowire-positions.csv"
file_initial_positions="initial-positions.csv"
file_braid_sequence="braid-sequence.csv"
file_tqc_fusion_rules="fusion-rules.csv"
file_tqc_fusion_channel="fusion-channel.csv"
RET_FALSE=0
MSG_NO_INPUT="Error: Please provide an inputs dir as an argument"

if [ -z $1 ];
then
    echo "\033[0;31m${MSG_NO_INPUT}\033[0m"
    exit
fi

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
    echo "validation error"
    exit
fi
