import copy
import graph
import exception
import validation
import metrics
import utility

from itertools import permutations

VOLTAGE_OPEN = 'O'
VOLTAGE_SHUT = 'S'
voltages = ['O','O','O','O']
zmodes_old = []
zmodes_new = []
positions_old = []
gate_index = -1
gate_flag = False
gate_flag_ex = False

################################################################################
## Utility functions

# Return voltages
def get_voltages():
    return voltages

# Retrieves the expected final positions of the particles to be braided (essentially the positions are swapped)
def get_final_positions(positions,pair):
    final_positions = copy.copy(positions)
    p1 = pair[0]-1
    p2 = pair[1]-1
    temp = final_positions[p1]
    final_positions[p1] = final_positions[p2]
    final_positions[p2] = temp
    return final_positions

# Update Nanowire with new Positions
def update_nanowire(nanowire,positions):
    i_nw = copy.deepcopy(nanowire)
    for intersection in i_nw:
        for branch in intersection:
            for tup in branch:
                if type(tup) is not dict:
                    continue
                pos = list(tup.keys())[0]
                if pos in positions:
                    i = positions.index(pos)
                    tup[pos] = (i+1)
                else:
                    tup[pos] = 0
    return i_nw

# A list of Zero mode pairs DURING a braiding op
def update_zero_modes(nanowire):
    global zmodes_old
    global zmodes_new
    zmodes = []

    # if the pair is on same branch
    for intersection in nanowire:
        for branch in intersection:
            pair = []
            for tup in branch:
                if type(tup) is not dict:
                    continue
                par = list(tup.values())[0]
                if par is not 0:
                    pair.append(par)
            if len(pair)==2:
                zmodes.append(pair)

    if len(zmodes_new) is 0:
        zmodes_new = zmodes

    for el in zmodes_new:
        if el not in zmodes_old:
            zmodes_old.append(el)
    zmodes_new = zmodes

# A list of Zero mode pairs AFTER a braiding op
def refresh_zero_modes():
    global zmodes_old
    global zmodes_new
    zmodes_old = zmodes_new
    zmodes_new = []

# Resets [positions_old, gate_flag] variables
def reset_variables(positions_new):
    global positions_old
    global gate_index
    global gate_flag
    global gate_flag_ex
    positions_old = copy.copy(positions_new)
    if gate_flag:
        gate_index = -1
        gate_flag = False
        gate_flag_ex = False

# Retrieves the potential Intermediate positions of the particles to be braided
def get_intermediate_positions(nanowire,pos):
    try:
        intersection = get_intersection(nanowire,pos)
        empty_positions = get_empty_positions(nanowire,intersection)
        return empty_positions
    except exception.NoEmptyPositionException:
        raise

# Retrieves the intersection of a position in the nanowire structure
def get_intersection(nanowire,pos):
    flag = 1
    if isinstance(pos, int):
        flag = 2

    for intersection in nanowire:
        for branch in intersection:
            for tup in branch:
                if type(tup) is not dict:
                    continue
                if flag is 1:
                    if list(tup.keys())[0]==pos:
                        return intersection
                elif flag is 2:
                    if list(tup.values())[0]==pos:
                        return intersection

# Retrieves the empty positions on adjacent empty branches
def get_empty_positions(nanowire,intersection):
    positions = []
    temp = []
    for branch in intersection:
        val = True
        for tup in branch:
            if type(tup) is not dict:
                continue
            if list(tup.values())[0] is not 0:
                val = False
            temp.append(list(tup.keys())[0])
        if val is False:
            temp = []
            val = True
        if len(temp)>0:
            positions.extend(temp)
            temp = []

    if len(temp)>0:
        positions.extend(temp)
    if len(positions)==0:
        msg = "No Empty Branches on Intersection {} to continue this braiding".format((nanowire.index(intersection)+1))
        raise exception.NoEmptyPositionException(msg)
    return positions

# Get the other (3rd) particle in the intersection to be moved
def get_other_particle(par,intersection):
    for branch in intersection:
        flag = False
        for tup in branch:
            if type(tup) is not dict:
                continue
            val = list(tup.values())[0]
            if val is par:
                flag = True
            if val is not par and flag:
                return val

# Get Isolated particles which are NOT part of any zero mode (in the middle of a braiding operation)
def get_isolated_particles(positions):
    positions_paired = []
    particles_paired = []
    zmodes_diff = []
    for zm in zmodes_new:
        particles_paired.extend(zm)
    positions_paired = [positions[par-1] for par in particles_paired]
    return list(set(positions)-set(positions_paired))

# Get Voltage Gate Changes if braiding involves particles from different zero modes.
def update_voltages(positions,cutoff_pairs):
    global positions_old
    global gate_index
    global gate_flag
    global gate_flag_ex
    positions_single = get_isolated_particles(positions)

    if len(positions_single)>1:
        perm = get_permutations(positions_single,2)
        for i in range(len(cutoff_pairs)):
            pairs = cutoff_pairs[i]
            val = False
            for pair in perm:
                if (pair in pairs or list(reversed(pair)) in pairs) and (not check_particle_pair_zmode(pair,positions,positions_single,i)):
                    val = True
                    break
            if val:
                voltages[i] = VOLTAGE_SHUT
            else:
                voltages[i] = VOLTAGE_OPEN

        if gate_flag is True and gate_flag_ex is False:
            inter = len(voltages)/2
            gate_index += 1
            offset = 0
            if gate_index>=inter:
                offset = inter
            voltages[int(gate_index%inter+offset)] = VOLTAGE_SHUT
            gate_flag_ex = True

    # print(zmodes_old,zmodes_new)
    # print(positions,positions_single)
    # print(voltages)
    return voltages

# Returns list permutations of size n for an array
def get_permutations(array,n):
    perm0 = permutations(array, n)
    perm = []
    for p in perm0:
        pair = list(p)
        if pair in perm or list(reversed(pair)) in perm:
            continue
        perm.append(pair)
    return perm

def check_particle_pair_zmode(pair_pos,positions,positions_single,i):
    if check_pair_zmode(pair_pos,positions):
        return True
    else:
        return check_particle_zmode(pair_pos,positions,positions_single,i)

# Checks if the pair is a zero mode
def check_pair_zmode(pair_pos,positions):
    global zmodes_old
    global zmodes_new
    p1 = positions.index(pair_pos[0])+1
    p2 = positions.index(pair_pos[1])+1
    pair = [p1,p2]
    val = False

    # Checks if the pair is a zero mode
    if pair in zmodes_old or list(reversed(pair)) in zmodes_old:
        val = True
    elif pair in zmodes_new or list(reversed(pair)) in zmodes_new:
        val = True
    return val

# Checks if at least 1 particle in the pair is part of a zero mode
def check_particle_zmode(pair_pos,positions,positions_single,i):
    global zmodes_new
    global gate_index
    global gate_flag
    p1 = positions.index(pair_pos[0])+1
    p2 = positions.index(pair_pos[1])+1
    val1 = val2 = False

    for zmode in zmodes_new:
        if p1 in zmode:
            val1 = True
            break

    for zmode in zmodes_new:
        if p2 in zmode:
            val2 = True
            break

    if val1 is True or val2 is True:
        return True
    elif val1 is False and val2 is False and len(positions_single) is 2:
        if gate_flag is False and i is not None:
            gate_index = i
            gate_flag = True
        return True
    return False

# Returns # steps from initial to final position
def get_steps(matrix,vertex,pos1,pos2):
    p1 = vertex.index(pos1)
    p2 = vertex.index(pos2)
    path = graph.route(matrix,p1,p2)
    return (len(path)-1)

# Ranks the positions based on Validity Score and # steps
def comparator(pos1,steps1,pos2,steps2):
    pos = pos1
    if steps2<steps1:
        pos = pos2
    return pos
