import copy
import graph
import exception
import validation
import metrics

from itertools import permutations

TYPE_FINAL = 1
TYPE_INTER = 2
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
        perm0 = permutations(positions_single, 2)
        perm = []
        for p in perm0:
            pair = list(p)
            if pair in perm or list(reversed(pair)) in perm:
                continue
            perm.append(pair)

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
        if gate_flag is False:
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

################################################################################
## Braiding phase

# Braiding particles on the same branch
def get_1st_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions):
    par1 = pair[0]
    par2 = pair[1]
    pos1 = positions[par1-1]
    pos2 = positions[par2-1]
    inner = ["a'","b'","f'","c'","d'","e'"]

    if pos1 in inner:
        return list(pair)
    else:
        return list(reversed(list(pair)))

def get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions):
    # return list(reversed(list(pair)))
    return list(pair)

def braid_particles_same_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state):
    try:
        update_zero_modes(nanowire)

        ## Initial Validation Phase
        # Getting the expected final positions after the braiding operation and validating it before moving forward with the braiding operation
        final_positions = get_final_positions(positions,pair)
        f_nw = update_nanowire(nanowire,final_positions)
        msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,final_positions,','.join(voltages))
        validation.validate_nanowire_state(f_nw,final_positions,voltages,TYPE_FINAL,msg)

        # Once final position validity is confirmed, move the particles to their intermediate positions
        # 1st particle that moves gets the 1st empty branch (for now)
        # --Can later specify any rule/restriction to move particles to certain branches
        intermediate_positions = []
        pair = get_1st_pair_sequence(pair, nanowire, vertices, positions, positions, final_positions)
        for par in pair:
            pos_start = positions[par-1]
            pos_end = None
            f_nw = None
            positions_temp = copy.copy(positions)
            p_pos = None
            p_score = 0
            p_steps = 10

            inter_positions = get_intermediate_positions(nanowire,pos_start)
            if dir is 1:
                inter_positions = list(reversed(inter_positions))

            # getting the best intermediate positions
            for pos in inter_positions:
                positions_temp[par-1] = pos
                i_nw = update_nanowire(nanowire,positions_temp)
                msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,positions_temp,','.join(voltages))
                score = validation.validate_nanowire_state(i_nw,positions_temp,voltages,TYPE_INTER,msg)
                steps = get_steps(matrix,vertices,pos_start,pos)
                p_pos = comparator(p_pos,p_steps,pos,steps)

                if p_pos is not None:
                    pos_end = p_pos
                    intermediate_positions = inter_positions
                    if p_pos==pos:
                        p_score = score
                        p_steps = steps
                        f_nw = i_nw
                        positions = copy.copy(positions_temp)

            if pos_end is not None and f_nw is not None:
                # Dijkstra's algorithm gives the shortest path for a particle from its current position to its final position.
                path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
                block = validation.validate_path_particle(path,positions,vertices,par)
                if len(block)==0:
                    nanowire = copy.deepcopy(f_nw)
                    update_zero_modes(nanowire)
                    update_voltages(positions,cutoff_pairs)
                    if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                        metrics.update_particle_movements(file_mvmt,par,path,vertices,voltages)
                        metrics.update_nanowire_state(file_state,positions,path,vertices,par,voltages)

        # Now, move the particles from their intermediate positions to their respective final positions
        p_pair = get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions)
        for par in p_pair:
            pos_start = positions[par-1]
            pos_end = final_positions[par-1]

            path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
            block = validation.validate_path_particle(path,positions,vertices,par)
            if len(block)==0:
                positions[par-1] = pos_end
                f_nw = update_nanowire(nanowire,positions)
                nanowire = copy.deepcopy(f_nw)
                update_zero_modes(nanowire)
                update_voltages(positions,cutoff_pairs)
                if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                    metrics.update_particle_movements(file_mvmt,par,path,vertices,voltages)
                    metrics.update_nanowire_state(file_state,positions,path,vertices,par,voltages)

        return nanowire, positions

    except exception.NoEmptyPositionException as err:
        raise
    except exception.InvalidNanowireStateException as err:
        raise
    except exception.PathBlockedException as err:
        raise

# Braiding particles on the different branches
def get_particles_list(nanowire,pair,positions):
    particles = []
    inner = ["a'","b'","f'","c'","d'","e'"]
    if positions[pair[0]-1] in inner:
        particles.append(pair[0])
        inter = get_intersection(nanowire,positions[pair[1]-1])
        op = get_other_particle(pair[1],inter)
        particles.append(op)
        particles.append(pair[1])
    elif positions[pair[1]-1] in inner:
        particles.append(pair[1])
        inter = get_intersection(nanowire,positions[pair[0]-1])
        op = get_other_particle(pair[1],inter)
        particles.append(op)
        particles.append(pair[0])
    return particles

def braid_particles_diff_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state):
    try:
        particles = get_particles_list(nanowire,pair,positions)
        update_zero_modes(nanowire)

        ## Initial Validation Phase
        # Getting the expected final positions after the braiding operation and validating it
        # before moving forward with the braiding operation itself
        final_positions = get_final_positions(positions,pair)
        f_nw = update_nanowire(nanowire,final_positions)
        msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,final_positions,','.join(voltages))
        validation.validate_nanowire_state(f_nw,final_positions,voltages,TYPE_FINAL,msg)

        # moving the 1st particle in the given pair
        # moving the blocking particle
        intermediate_positions = []
        pair2 = particles[:2]
        for par in pair2:
            pos_start = positions[par-1]
            pos_end = None
            f_nw = None
            positions_temp = copy.copy(positions)
            p_pos = None
            p_score = 0
            p_steps = 10

            inter_positions = get_intermediate_positions(nanowire,pos_start)
            if dir is 1:
                inter_positions = list(reversed(inter_positions))

            # getting the best intermediate positions
            for pos in inter_positions:
                positions_temp[par-1] = pos
                i_nw = update_nanowire(nanowire,positions_temp)
                msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,positions_temp,','.join(voltages))
                score = validation.validate_nanowire_state(i_nw,positions_temp,voltages,TYPE_INTER,msg)
                steps = get_steps(matrix,vertices,pos_start,pos)
                p_pos = comparator(p_pos,p_steps,pos,steps)

                if p_pos is not None:
                    pos_end = p_pos
                    intermediate_positions = inter_positions
                    if p_pos==pos:
                        p_score = score
                        p_steps = steps
                        f_nw = i_nw
                        positions = copy.copy(positions_temp)

            if pos_end is not None and f_nw is not None:
                # Dijkstra's algorithm gives the shortest path for a particle from its current position to its final position.
                path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
                block = validation.validate_path_particle(path,positions,vertices,par)
                if len(block)==0:
                    nanowire = copy.deepcopy(f_nw)
                    update_zero_modes(nanowire)
                    update_voltages(positions,cutoff_pairs)
                    if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                        metrics.update_particle_movements(file_mvmt,par,path,vertices,voltages)
                        metrics.update_nanowire_state(file_state,positions,path,vertices,par,voltages)

        # moving 2nd particle in the given pair
        par = particles[2]
        pos_start = positions[pair[1]-1]
        pos_end = final_positions[pair[1]-1]
        positions[par-1] = final_positions[par-1]
        path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
        block = validation.validate_path_particle(path,positions,vertices,par)
        if len(block)==0:
            f_nw = update_nanowire(nanowire,positions)
            nanowire = copy.deepcopy(f_nw)
            update_zero_modes(nanowire)
            update_voltages(positions,cutoff_pairs)
            if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                metrics.update_particle_movements(file_mvmt,par,path,vertices,voltages)
                metrics.update_nanowire_state(file_state,positions,path,vertices,par,voltages)

        # moving the 2 particles back to their respective positions
        # p_pair = get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions)
        p_pair = pair2
        for par in p_pair:
            pos_start = positions[par-1]
            pos_end = final_positions[par-1]

            path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
            block = validation.validate_path_particle(path,positions,vertices,par)
            if len(block)==0:
                positions[par-1] = pos_end
                f_nw = update_nanowire(nanowire,positions)
                nanowire = copy.deepcopy(f_nw)
                update_zero_modes(nanowire)
                update_voltages(positions,cutoff_pairs)
                if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                    metrics.update_particle_movements(file_mvmt,par,path,vertices,voltages)
                    metrics.update_nanowire_state(file_state,positions,path,vertices,par,voltages)

        return nanowire, positions

    except exception.NoEmptyPositionException as err:
        raise
    except exception.InvalidNanowireStateException as err:
        raise
    except exception.PathBlockedException as err:
        raise

################################################################################

def braid_particles(nanowire, vertices, matrix, sequence, direction, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state):
    try:
        for i in range(len(sequence)):
            pair = sequence[i]
            dir = direction[i]
            print("----- Braiding particles {} -----".format(pair))
            reset_variables(positions)
            refresh_zero_modes()
            intersection = get_intersection(nanowire,positions[pair[0]-1])
            condition = validation.check_unibranch_validity(pair,positions,intersection)
            if condition:
                nanowire,positions = braid_particles_same_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state)
            else:
                nanowire,positions = braid_particles_diff_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state)

    except exception.NoEmptyPositionException as err:
        print(err)
    except exception.InvalidNanowireStateException as err:
        print(err)
    except exception.PathBlockedException as err:
        print(err)
