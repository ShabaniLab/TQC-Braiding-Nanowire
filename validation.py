import exception

################################################################################
## Validation phase

# Nanowire Validation Algorithm which returns a score
def validate_nanowire_state(nanowire,positions,voltages,type,msg):
    try:
        min_free_branch = 0
        if type==2:
            min_free_branch = 1
        elif type==1:
            min_free_branch = 2

        score = validate_empty_branches(nanowire,min_free_branch,msg)
        validate_multi_modal_crossing(nanowire,voltages,msg)
        return score
    except exception.InvalidNanowireStateException:
        raise

# Checks if there are at least 2 empty branches in every intersection
def validate_empty_branches(nanowire,min_free_branch,msg):
    score = 0
    valid = False

    for intersection in nanowire:
        free_b = 0
        for branch in intersection:
            min_free_pos = len(branch)
            free_p = 0
            for tup in branch:
                if type(tup) is not dict:
                    continue
                if list(tup.values())[0]==0:
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

# *Check if resulting nanowire violates Rule 3 - Particle-Zero mode isolation
def validate_multi_modal_crossing(nanowire,voltages,msg):
    score = 1
    if score==0:
        raise exception.MultiModalCrossingException(msg)

# if the pair is on different branches
# def get_adjacent_zmode(nanowire):
#     for intersection in nanowire:
#     b1 = b2 = 0
#     for i in range(len(intersection)):
#         branch = intersection[i]
#         for tup in branch:
#             if list(tup.values())[0]==pair[0]:
#                 b1 = i
#
#     for i in range(len(intersection)):
#         branch = intersection[i]
#         for tup in branch:
#             if list(tup.values())[0]==pair[1]:
#                 b2 = i
#
#     if abs(b1-b2)<=1 or abs(b1-b2)==3:
#         return True
#     return False

# Checks if any other particle blocks the path
def validate_path_particle(path,positions,vertices,par):
    block = []
    for el in path:
        pos = vertices[el]
        if pos in positions:
            block.append(pos)
    block.pop()

    if len(block)>1 and flag:
        route = [vertices[e] for e in path]
        msg = "The Particle ({}) with Path [{}] is blocked in [{}]".format(par,','.join(route),','.join(block))
        raise exception.PathBlockedException(msg)
    return block

# Checks if a shut voltage gate blocks the path
def validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
    p1 = vertices[path[0]]
    pn = vertices[path[len(path)-1]]
    pair = [p1,pn]
    gates = []

    flag1 = verify_cutoff_pair(cutoff_pairs,pair,voltages)
    gate1 = get_voltage_gate_values(flag1)
    if gate1 is not None:
        gates.append(gate1)
    else:
        flag2 = verify_cutoff_pair(cutoff_pairs_opp,pair,voltages)
        gate2 = get_voltage_gate_values(flag2)
        if gate2 is not None:
            gates.append(gate2)

    if flag1>=0 or flag2>=0:
        route = [vertices[e] for e in path]
        msg = "The Particle ({}) with Path [{}] is blocked by Voltage Gate {}".format(par,','.join(route),gates)
        raise exception.PathBlockedException(msg)
    return True

def verify_cutoff_pair(cutoff,pair,voltages):
    flag = -1
    for i in range(len(cutoff)):
        pairs = cutoff[i]
        if pair in pairs or list(reversed(pair)) in pairs:
            if voltages[i] is 'S':
                flag = i
                return flag
    return flag

def get_voltage_gate_values(flag):
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

# Check if the pair is in the same branch
def check_unibranch_validity(pair,positions,intersection):
    check = []
    for par in pair:
        b = 0
        pos = positions[par-1]
        for branch in intersection:
            b +=1
            for tup in branch:
                if type(tup) is not dict:
                    continue
                if list(tup.keys())[0] == pos:
                    check.append(b)
    if check[0]==check[1]:
        return True
    return False

# def validate_multi_modal_adjcacency():
