import copy
import graph
import exception
import validation

TYPE_FINAL = 1
TYPE_INTER = 2
v11 = v12 = v21 = v22 = 'O'

################################################################################
## Validation phase utility functions

# Retrieves the expected final positions of the particles to be braided (basially the positions are swapped)
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
    for intersection in nanowire:
        for branch in intersection:
            for tup in branch:
                if type(tup) is not dict:
                    continue
                if list(tup.keys())[0]==pos:
                    return intersection

# Retrieves the empty positions on adjacent empty branches
def get_empty_positions(nanowire,intersection):
    positions = []
    temp = []
    for branch in intersection:
        if len(temp)>1:
            positions.extend(temp)
            temp = []
        for tup in branch:
            if type(tup) is not dict:
                continue
            if list(tup.values())[0]!=0:
                temp = []
                break
            else:
                temp.append(list(tup.keys())[0])

    if len(temp)>0:
        positions.extend(temp)
    if len(positions)==0:
        msg = "No Empty Branches on Intersection {} to continue this braiding".format((nanowire.index(intersection)+1))
        raise exception.NoEmptyPositionException(msg)
    return positions

def get_other_particle(par,intersection):
    op = -1
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

################################################################################
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

# Update Particle positions by generating a similar sequence for the particles.
def update_particle_movements(par,path,vertices,v11,v12,v21,v22):
    # line = "{},{},{},{},{},{}".format(par,'-'.join(vertices[v] for v in path),v11,v12,v21,v22)
    line = "{},{}".format(par,'-'.join(vertices[v] for v in path))
    print(line)

################################################################################
## Braiding phase

# Get Voltage Gate Changes if braiding involves particles from different zero modes.
# def get_voltage_changes():

# Update the Adjacency Matrix as Gate variations may create a disconnected graph.
# def retrieve_isolated_branches():

################################################################################
## Braiding particles on the same branch

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

def braid_particles_same_branch(nanowire, vertices, matrix, pair, positions):
    try:
        ## Initial Validation Phase
        # Getting the expected final positions after the braiding operation and validating it
        # before moving forward with the braiding operation itself
        final_positions = get_final_positions(positions,pair)
        f_nw = update_nanowire(nanowire,final_positions)
        msg = "Error while trying to braid {}: {} is an invalid state".format(pair,final_positions)
        validation.validate_nanowire_state(f_nw,TYPE_FINAL,msg)

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

            # getting the best intermediate positions
            for pos in inter_positions:
                positions_temp[par-1] = pos
                i_nw = update_nanowire(nanowire,positions_temp)
                msg = "Error while braiding {}: {} is an invalid state".format(pair,positions_temp)
                score = validation.validate_nanowire_state(i_nw,TYPE_INTER,msg)
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
                block = validation.validate_path(path,positions,vertices,par)
                if len(block)==0:
                    nanowire = copy.deepcopy(f_nw)
                    update_particle_movements(par,path,vertices,v11,v12,v21,v22)

        # Now, move the particles from their intermediate positions to their respective final positions
        p_pair = get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions)
        for par in p_pair:
            pos_start = positions[par-1]
            pos_end = final_positions[par-1]

            path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
            block = validation.validate_path(path,positions,vertices,par)
            if len(block)==0:
                positions[par-1] = pos_end
                f_nw = update_nanowire(nanowire,positions)
                nanowire = copy.deepcopy(f_nw)
                update_particle_movements(par,path,vertices,v11,v12,v21,v22)

        return nanowire,positions

    except exception.NoEmptyPositionException as err:
        print(err)
    except exception.InvalidNanowireStateException as err:
        print(err)
    except exception.PathBlockedException as err:
        print(err)

################################################################################
## Braiding particles on the different branches

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

def braid_particles_diff_branch(nanowire, vertices, matrix, pair, positions):
    particles = get_particles_list(nanowire,pair,positions)

    ## Initial Validation Phase
    # Getting the expected final positions after the braiding operation and validating it
    # before moving forward with the braiding operation itself
    final_positions = get_final_positions(positions,pair)
    f_nw = update_nanowire(nanowire,final_positions)
    msg = "Error while trying to braid {}: {} is an invalid state".format(pair,final_positions)
    validation.validate_nanowire_state(f_nw,TYPE_FINAL,msg)

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

        # getting the best intermediate positions
        for pos in inter_positions:
            positions_temp[par-1] = pos
            i_nw = update_nanowire(nanowire,positions_temp)
            msg = "Error while braiding {}: {} is an invalid state".format(pair2,positions_temp)
            score = validation.validate_nanowire_state(i_nw,TYPE_INTER,msg)
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
            block = validation.validate_path(path,positions,vertices,par)
            if len(block)==0:
                nanowire = copy.deepcopy(f_nw)
                update_particle_movements(par,path,vertices,v11,v12,v21,v22)

    # moving 2nd particle in the given pair
    par = particles[2]
    pos_start = positions[pair[1]-1]
    pos_end = final_positions[pair[1]-1]
    positions[par-1] = final_positions[par-1]
    path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
    block = validation.validate_path(path,positions,vertices,par)
    if len(block)==0:
        f_nw = update_nanowire(nanowire,positions)
        nanowire = copy.deepcopy(f_nw)
        update_particle_movements(par,path,vertices,v11,v12,v21,v22)

    # moving the 2 particles back to their respective positions
    # p_pair = get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions)
    p_pair = pair2
    for par in p_pair:
        pos_start = positions[par-1]
        pos_end = final_positions[par-1]

        path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
        block = validation.validate_path(path,positions,vertices,par)
        if len(block)==0:
            positions[par-1] = pos_end
            f_nw = update_nanowire(nanowire,positions)
            nanowire = copy.deepcopy(f_nw)
            update_particle_movements(par,path,vertices,v11,v12,v21,v22)

    return nanowire, positions

################################################################################

def braid_particles(nanowire, vertices, matrix, sequence, positions):
    try:
        for pair in sequence:
            print("Braiding particles {}".format(pair))
            intersection = get_intersection(nanowire,positions[pair[0]-1])
            condition = validation.check_unibranch_validity(pair,positions,intersection)
            if condition:
                nanowire,positions = braid_particles_same_branch(nanowire, vertices, matrix, pair, positions)
            else:
                nanowire,positions = braid_particles_diff_branch(nanowire, vertices, matrix, pair, positions)

    except exception.NoEmptyPositionException as err:
        print(err)
    except exception.InvalidNanowireStateException as err:
        print(err)
    except exception.PathBlockedException as err:
        print(err)
