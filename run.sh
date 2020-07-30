#!/bin/sh

# Variables
file_nanowire="nanowire.csv"
file_position="position.csv"
file_sequence="sequence.csv"
file_movement="movements.csv"

python3 particle-movement.py $file_nanowire $file_position $file_sequence >> $file_movement
