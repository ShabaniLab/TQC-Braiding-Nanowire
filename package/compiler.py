"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Compiler

Objectives:
    1. Stores initial particle positions
    2. Stores Braid sequence for the given gate

Class: Compiler

Functions:
    1. read_particle_positions
    2. read_braid_sequence
    3. read_braid_positions
    4. yaml_to_structure_sequence
"""

class Compiler:
    """
    A class to represent Compiler class
    """

    def __init__(self, sequence, direction, positions):
        self.sequence = sequence
        self.direction = direction
        self.positions = positions

def read_particle_positions(file):
    """
    Read initial particle positions
    """
    try:
        fr = open(file, 'r')
        line = fr.readlines()[-1]
        positions = line.split(',')
        positions = [e.strip() for e in positions]
        fr.close()
        return positions
    except IOError:
        raise

def read_braid_sequence(file):
    """
    Read the given braid sequence
    """
    data = []
    dir = []
    try:
        file = open(file, 'r')
        line = file.readline()
        row = line.split(',')
        tup = (int(row[0].strip()), int(row[1].strip()))
        data.append(tup)
        dir.append(int(row[2].strip()))
        while line:
            line = file.readline()
            if not line:
                continue
            row = line.split(',')
            tup = (int(row[0].strip()), int(row[1].strip()))
            data.append(tup)
            dir.append(int(row[2].strip()))
        file.close()
        return data, dir
    except IOError:
        raise

def read_braid_positions(file):
    """
    Read initial particle positions
    """
    try:
        fr = open(file, 'r')
        line = fr.readlines()[-1]
        positions = line.strip().split(',')
        positions = positions[2:]
        positions = [int(e) for e in positions]
        fr.close()
        return positions
    except IOError:
        raise

def yaml_to_structure_sequence(gate):
    sequence = []
    direction = []
    braid_sequence = gate.get('braid_sequence')
    for seq in braid_sequence:
        slist = seq.split(',')
        s = (int(slist[0]), int(slist[1]))
        sequence.append(s)
        d = int(slist[2])
        direction.append(d)
    return sequence, direction
