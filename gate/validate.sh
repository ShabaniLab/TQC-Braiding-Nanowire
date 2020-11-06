#!/bin/sh

MSG_NO="Error: Please provide valid"
RET_TRUE=1
RET_FALSE=0

###########################################################################
validate_inputs_dir() {
    if [ ! -d $1 ]
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_circuit_config() {
    KEY_GATE="gate"
    KEY_PARTICLES="particles"
    KEY_QUBITS="qubits"
    KEY_VOLTAGES="voltages"
    gate=""
    qubits=""
    particles=""
    voltages=""

    # Checks if the file exists
    if [ ! -f $1/$2 ];
    then
        return $RET_FALSE
    fi

    # Reads the config data from file
    while IFS= read -r line
    do
        if [[ $line == *"$KEY_GATE"* ]];
        then
            gate=$(echo $line| cut -d'=' -f 2)
        elif [[ $line == *"$KEY_PARTICLES"* ]];
        then
            particles=$(echo $line| cut -d'=' -f 2)
        elif [[ $line == *"$KEY_QUBITS"* ]];
        then
            qubits=$(echo $line| cut -d'=' -f 2)
        elif [[ $line == *"$KEY_VOLTAGES"* ]];
        then
            voltages=$(echo $line| cut -d'=' -f 2)
        fi
    done < $1/$2

    # Checks if there are all the required config data
    if [ -z $gate ] || [ -z $qubits ] || [ -z $particles ] || [ -z $voltages ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_nanowire_structure() {
    if [ ! -f $1/$2 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_nanowire_positions() {
    if [ ! -f $1/$2 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_initial_positions() {
    if [ ! -f $1/$2 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_braid_sequence() {
    if [ ! -f $1/$2 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_fusion_rules() {
    if [ ! -f $1/$2 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

validate_fusion_channels() {
    if [ ! -f $1/$2 ];
    then
        return $RET_FALSE
    fi
    return $RET_TRUE
}

###########################################################################
validate_inputs_dir $8
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${8}\033[0m"
    exit $RET_FALSE
fi

validate_circuit_config $8 $1
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${1}\033[0m"
    exit $RET_FALSE
fi

validate_nanowire_structure $8 $2
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${2}\033[0m"
    exit $RET_FALSE
fi

validate_nanowire_positions $8 $3
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${3}\033[0m"
    exit $RET_FALSE
fi

validate_initial_positions $8 $4
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${4}\033[0m"
    exit $RET_FALSE
fi

validate_braid_sequence $8 $5
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${5}\033[0m"
    exit $RET_FALSE
fi

validate_fusion_rules $8 $6
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${6}\033[0m"
    exit $RET_FALSE
fi

validate_fusion_channels $8 $7
ret=$?
if [ "$ret" -eq $RET_FALSE ];
then
    echo "\033[0;31m${MSG_NO} \033[0;33m${7}\033[0m"
    exit $RET_FALSE
fi

#
exit $RET_TRUE
