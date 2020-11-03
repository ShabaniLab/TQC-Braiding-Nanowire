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

#
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
echo $heading1
echo $heading2
echo $heading3
