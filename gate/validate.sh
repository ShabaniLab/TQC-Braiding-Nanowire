#!/bin/sh

MSG_NO="Error: Please provide a valid"
RET_TRUE=1
RET_FALSE=0

###########################################################################
validate_circuit_config() {
    key_gate="gate"
    key_particles="particles"
    key_qubits="qubits"
    key_voltages="voltages"
    gate=""
    qubits=""
    particles=""
    voltages=""

    # Checks if the file exists
    if [ ! -f $2/$1 ];
    then
        return $RET_FALSE
    fi

    # Reads the config data from file
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
    done < $2/$1

    # Checks if there are all the required config data
    if [ -z $gate ] || [ -z $qubits ] || [ -z $particles ] || [ -z $voltages ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_nanowire_structure() {
    if [ ! -f $2/$1 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_nanowire_positions() {
    if [ ! -f $2/$1 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_initial_positions() {
    if [ ! -f $2/$1 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_braid_sequence() {
    if [ ! -f $2/$1 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_fusion_rules() {
    if [ ! -f $2/$1 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_fusion_channels() {
    if [ ! -f $2/$1 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

###########################################################################
validate_circuit_config $1 $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} ${1}\033[0m"
    exit $RET_FALSE
fi

validate_nanowire_structure $2 $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} ${2}\033[0m"
    exit $RET_FALSE
fi

validate_nanowire_positions $3 $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} ${3}\033[0m"
    exit $RET_FALSE
fi

validate_initial_positions $4 $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} ${4}\033[0m"
    exit $RET_FALSE
fi

validate_braid_sequence $5 $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} ${5}\033[0m"
    exit $RET_FALSE
fi

validate_fusion_rules $6 $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} ${6}\033[0m"
    exit $RET_FALSE
fi

validate_fusion_channels $7 $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} ${7}\033[0m"
    exit $RET_FALSE
fi

#
exit $RET_TRUE
