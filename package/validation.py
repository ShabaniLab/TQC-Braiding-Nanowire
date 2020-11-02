"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Validation

Objectives:
    1. TQC Braiding Nanowire Algorithm - Validation phase

Functions:
    1. validate_nanowire_state
    2. validate_empty_branches
    3. validate_multi_modal_crossing
    4. validate_path_particle
    5. validate_path_gates
    6. verify_cutoff_pair
    7. get_voltage_gate_values
    8. check_unibranch_validity
"""

from . import exception
from .utility import Utility

def validate_nanowire_state(nw, positions, utility, positions_single, voltages, nanowire,type,msg):
    """
    Nanowire Validation Algorithm which returns a score
    """
    try:
        min_free_branch = 0
        if type==2:
            min_free_branch = 1
        elif type==1:
            min_free_branch = 2
        score = validate_empty_branches(nw, min_free_branch, msg)
        validate_multi_modal_crossing(positions, positions_single, voltages, utility, nanowire,msg)
        return score
    except exception.InvalidNanowireStateException:
        raise

def validate_empty_branches(nanowire, min_free_branch, msg):
    """
    Checks if there are at least 2 empty branches in every intersection
    """
    score = 0
    valid = False

    for intersection in nanowire:
        free_b = 0
        for branch in intersection:
            min_free_pos = len(branch)
            free_p = 0
            for tup in branch:
                if not isinstance(tup, dict):
                    continue
                if list(tup.values())[0] == 0:
                    free_p += 1
                else:
                    free_p = 0
            if free_p>=min_free_pos:
                free_b += 1
        if free_b>=min_free_branch:
            valid = True

    if valid:
        score += 1
    if score==0:
        raise exception.NoEmptyBranchException(msg)
    return score

def validate_multi_modal_crossing(positions, positions_single, voltages, utility, nanowire, msg):
    """
    *Check if resulting nanowire violates Rule 3 - Particle-Zero mode isolation
    """
    perm = Utility.get_permutations(positions_single, 2)
    for pair in perm:
        flag1 = utility.check_particle_pair_zmode(pair, positions, positions_single, None)
        flag2 = verify_cutoff_pair(nanowire.cutoff_pairs_adj, pair, voltages)
        flag3 = verify_cutoff_pair(nanowire.cutoff_pairs_opp, pair, voltages)
        if flag1 is False and (flag2 is True or flag3 is True):
            raise exception.MultiModalCrossingException(msg)

def validate_path_particle(path, positions, vertices, par):
    """
    Checks if any other particle blocks the path
    """
    block = []
    for el in path:
        pos = vertices[el]
        if pos in positions:
            block.append(pos)
    block.pop()

    if len(block)>1:
        route = [vertices[e] for e in path]
        msg = "The Particle ({}) with Path [{}] is blocked in [{}]"\
                .format(par, ', '.join(route), ', '.join(block))
        raise exception.PathBlockedException(msg)
    return block

def validate_path_gates(par, path, vertices, voltages, cutoff_pairs, cutoff_pairs_opp):
    """
    Checks if a shut voltage gate blocks the path
    """
    p1 = vertices[path[0]]
    pn = vertices[path[len(path)-1]]
    pair = [p1, pn]
    gates = []

    flag1 = verify_cutoff_pair(cutoff_pairs, pair, voltages)
    gate1 = get_voltage_gate_values(flag1)
    if gate1 is not None:
        gates.append(gate1)
    else:
        flag2 = verify_cutoff_pair(cutoff_pairs_opp, pair, voltages)
        gate2 = get_voltage_gate_values(flag2)
        if gate2 is not None:
            gates.append(gate2)

    if flag1>=0 or flag2>=0:
        route = [vertices[e] for e in path]
        msg = "The Particle ({}) with Path [{}] is blocked by Voltage Gate {}"\
                .format(par, ', '.join(route), gates)
        raise exception.PathBlockedException(msg)
    return True

def verify_cutoff_pair(cutoff, pair, voltages):
    """
    Returns [0-4] if the pair is in the cutoff_pair
    """
    flag = -1
    for i in range(len(cutoff)):
        pairs = cutoff[i]
        if pair in pairs or list(reversed(pair)) in pairs:
            if voltages[i] is 'S':
                flag = i
                return flag
    return flag

def get_voltage_gate_values(flag):
    """
    For output format
    """
    gate = None
    if flag is 0:
        gate = 'x11'
    elif flag is 1:
        gate = 'x12'
    elif flag is 2:
        gate = 'x21'
    elif flag is 3:
        gate = 'x22'
    return gate

def check_unibranch_validity(pair, positions, intersection):
    """
    Check if the pair is in the same branch
    """
    assert(intersection!=None)
    check = []
    for par in pair:
        b = 0
        pos = positions[par-1]
        for branch in intersection:
            b +=1
            for tup in branch:
                if not isinstance(tup, dict):
                    continue
                if pos in tup:
                    check.append(b)
    if check[0] == check[1]:
        return True
    return False
