"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Measurement

Objectives:
    1. TQC Braiding Nanowire Algorithm - Measurement phase

Functions:
    1. read_positions
    2. read_fusion_rules
    3. read_fusion_channels
    4. extract_pairs
    5. measure_particles
    6. save_measurements
"""

import random
from . import graph
from . import nanowire

def read_positions(file):
    """
    Read Final and Initial positions
    """
    positions_initial = []
    positions_final = []
    try:
        fr = open(file,'r')
        line = fr.readline().strip()
        positions_initial = line.split(',')

        line = fr.readline().strip()
        positions_final = line.split(',')
        return positions_initial, positions_final
    except IOError as err:
        print(err)

def read_fusion_rules(file):
    """
    Read Fusion Rules
    """
    rules = {}
    try:
        fr = open(file,'r')
        line = fr.readline().strip()
        while line:
            line = fr.readline().strip()
            row = line.split(',')
            if len(row) < 3:
                continue
            key = "{}-{}".format(row[0],row[1])
            val = row[2]
            if key in rules.keys():
                rules[key].append(val)
            else:
                rules[key] = [val]
        fr.close()
        return rules
    except IOError:
        raise

def read_fusion_channels(file):
    """Read Fusion Channels"""
    channels = {}
    try:
        fr = open(file,'r')
        line = fr.readline().strip()
        while line:
            line = fr.readline().strip()
            row = line.split(',')
            if len(row) < 5:
                continue
            key = "{}-{}-{}".format(row[2], row[3], row[4])
            val = (row[0], row[1])
            channels[key] = val
        fr.close()
        return channels
    except IOError:
        raise

def extract_pairs(positions, file1, file2):
    """Extract zero mode pairs from the given matrix, vertices list and final positions"""
    matrix = graph.adjacency_matrix(file1)
    vertices = nanowire.read_nanowire_vertices(file2)
    pairs = {}
    for pos1 in positions:
        id1 = positions.index(pos1)+1
        if id1 in pairs:
            continue
        p1 = vertices.index(pos1)
        for pos2 in positions:
            id2 = positions.index(pos2)+1
            if id2 in pairs:
                continue
            p2 = vertices.index(pos2)
            if pos1 != pos2 and (matrix[p1][p2] == 1 or matrix[p2][p1] == 1):
                pairs[id1] = id2
    return pairs

def measure_particles(pairs,rules,channel):
    """Perform Measurement"""
    channels = []
    par_pair = 'o-o'
    outcomes = rules[par_pair]
    for _ in pairs.keys():
        n = round(random.random()*(len(outcomes)-1))
        channels.append(outcomes[n])
    chl = "-".join(channels)
    qb = ()
    if chl in channel:
        qb = channel[chl]
    return tuple(channels), qb

def save_measurements(chl, qb):
    """Print it into a file"""
    if qb:
        line = "{},{},{},{},{}".format(chl[0],chl[1],chl[2],qb[0],qb[1])
        print(line)
