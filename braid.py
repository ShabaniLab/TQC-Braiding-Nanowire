"""
TQC Braiding Nanowire Algorithm - Braiding phase

A. Braiding particles on the same branch
    1. The braiding sequence movements of particles from initial positions to intermediate positions
    2. The braiding sequence movements of particles from intermediate positions to respective final positions

B. Braiding particles on different branches
    1. Moving the outermost (blocking) particle and 1st particle in the given pair
    2. Moving 2nd particle in the given pair
    3. Moving the 2 particles back to their respective positions
"""

import copy
import graph
import exception
import validation
import metrics
import utility

################################################################################
# A.
################################################################################
def braid_particles_same_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state):
    try:
        utility.update_zero_modes(nanowire)
        voltages = utility.get_voltages()
        pair0 = copy.copy(pair)
        TYPE_FINAL = 1
        TYPE_INTER = 2

        ########################################################################
        ## Initial Validation Phase
        # Getting the expected final positions after the braiding operation
        final_positions = utility.get_final_positions(positions,pair)
        f_nw = utility.update_nanowire(nanowire,final_positions)

        # getting the list of isolated particles
        positions_single = utility.get_isolated_particles(final_positions)

        # validating final positions before moving forward with the braiding operation
        msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,final_positions,','.join(voltages))
        validation.validate_nanowire_state(f_nw,final_positions,positions_single,voltages,cutoff_pairs,cutoff_pairs_opp,TYPE_FINAL,msg)

        ########################################################################
        # 1.
        ########################################################################
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

            # getting the list of positions on free branches (intermediate positions)
            inter_positions = utility.get_intermediate_positions(nanowire,pos_start)
            if dir is 1:
                inter_positions = list(reversed(inter_positions))

            # getting the best (with least #steps)intermediate position in the list
            for pos in inter_positions:
                positions_temp[par-1] = pos
                i_nw = utility.update_nanowire(nanowire,positions_temp)
                positions_single = utility.get_isolated_particles(positions_temp)
                msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,positions_temp,','.join(voltages))

                # validating the change in nanowire state because of an intermediate position
                score = validation.validate_nanowire_state(i_nw,positions_temp,positions_single,voltages,cutoff_pairs,cutoff_pairs_opp,TYPE_INTER,msg)
                steps = utility.get_steps(matrix,vertices,pos_start,pos)
                p_pos = utility.comparator(p_pos,p_steps,pos,steps)

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

                # checking if the path is not blocked
                block = validation.validate_path_particle(path,positions,vertices,par)
                if len(block)==0:
                    nanowire = copy.deepcopy(f_nw)

                    # update the zero modes according to the new Nanowire state
                    utility.update_zero_modes(nanowire)
                    voltages = utility.update_voltages(positions,cutoff_pairs)

                    # checks if the voltage gate changes doesn't block the movement path
                    if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                        metrics.update_particle_movements(file_mvmt,pair0,par,path,vertices,voltages)
                        metrics.update_nanowire_state(file_state,pair0,positions,path,vertices,par,voltages)

        ########################################################################
        # 2.
        ########################################################################
        p_pair = get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions)
        for par in p_pair:
            pos_start = positions[par-1]
            pos_end = final_positions[par-1]

            path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))

            # checking if the path is not blocked
            block = validation.validate_path_particle(path,positions,vertices,par)
            if len(block)==0:
                positions[par-1] = pos_end
                f_nw = utility.update_nanowire(nanowire,positions)
                nanowire = copy.deepcopy(f_nw)
                utility.update_zero_modes(nanowire)
                voltages = utility.update_voltages(positions,cutoff_pairs)

                # checks if the voltage gate changes doesn't block the movement path
                if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                    metrics.update_particle_movements(file_mvmt,pair0,par,path,vertices,voltages)
                    metrics.update_nanowire_state(file_state,pair0,positions,path,vertices,par,voltages)

        return nanowire, positions

    except exception.NoEmptyPositionException as err:
        raise
    except exception.InvalidNanowireStateException as err:
        raise
    except exception.PathBlockedException as err:
        raise

# 1.
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

# 2.
def get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions):
    # return list(reversed(list(pair)))
    return list(pair)

################################################################################
# B.
################################################################################
def braid_particles_diff_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state):
    try:
        particles = get_particles_list(nanowire,pair,positions)
        utility.update_zero_modes(nanowire)
        voltages = utility.get_voltages()
        pair0 = copy.copy(pair)
        TYPE_FINAL = 1
        TYPE_INTER = 2

        ########################################################################
        ## Initial Validation Phase
        # Getting the expected final positions after the braiding operation and validating it
        # before moving forward with the braiding operation itself
        final_positions = utility.get_final_positions(positions,pair)
        f_nw = utility.update_nanowire(nanowire,final_positions)

        # getting the list of isolated particles
        positions_single = utility.get_isolated_particles(final_positions)

        # validating final positions before moving forward with the braiding operation
        msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,final_positions,','.join(voltages))
        validation.validate_nanowire_state(f_nw,final_positions,positions_single,voltages,cutoff_pairs,cutoff_pairs_opp,TYPE_FINAL,msg)

        ########################################################################
        # 1.
        ########################################################################
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

            # getting the list of positions on free branches (intermediate positions)
            inter_positions = utility.get_intermediate_positions(nanowire,pos_start)
            if dir is 1:
                inter_positions = list(reversed(inter_positions))

            # getting the best intermediate positions
            for pos in inter_positions:
                positions_temp[par-1] = pos
                i_nw = utility.update_nanowire(nanowire,positions_temp)
                positions_single = utility.get_isolated_particles(positions_temp)

                msg = "Error while trying to braid {}: {},{} is an invalid state".format(pair,positions_temp,','.join(voltages))
                score = validation.validate_nanowire_state(i_nw,positions_temp,positions_single,voltages,cutoff_pairs,cutoff_pairs_opp,TYPE_INTER,msg)
                steps = utility.get_steps(matrix,vertices,pos_start,pos)
                p_pos = utility.comparator(p_pos,p_steps,pos,steps)

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
                    utility.update_zero_modes(nanowire)
                    voltages = utility.update_voltages(positions,cutoff_pairs)
                    if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                        metrics.update_particle_movements(file_mvmt,pair0,par,path,vertices,voltages)
                        metrics.update_nanowire_state(file_state,pair0,positions,path,vertices,par,voltages)

        ########################################################################
        # 2.
        ########################################################################
        par = particles[2]
        pos_start = positions[pair[1]-1]
        pos_end = final_positions[pair[1]-1]
        positions[par-1] = final_positions[par-1]
        path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
        block = validation.validate_path_particle(path,positions,vertices,par)
        if len(block)==0:
            f_nw = utility.update_nanowire(nanowire,positions)
            nanowire = copy.deepcopy(f_nw)
            utility.update_zero_modes(nanowire)
            voltages = utility.update_voltages(positions,cutoff_pairs)
            if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                metrics.update_particle_movements(file_mvmt,pair0,par,path,vertices,voltages)
                metrics.update_nanowire_state(file_state,pair0,positions,path,vertices,par,voltages)

        ########################################################################
        # 3.
        ########################################################################
        # p_pair = get_2nd_pair_sequence(pair,nanowire,vertices,positions,intermediate_positions,final_positions)
        p_pair = pair2
        for par in p_pair:
            pos_start = positions[par-1]
            pos_end = final_positions[par-1]

            path = graph.route(matrix,vertices.index(pos_start),vertices.index(pos_end))
            block = validation.validate_path_particle(path,positions,vertices,par)
            if len(block)==0:
                positions[par-1] = pos_end
                f_nw = utility.update_nanowire(nanowire,positions)
                nanowire = copy.deepcopy(f_nw)
                utility.update_zero_modes(nanowire)
                voltages = utility.update_voltages(positions,cutoff_pairs)
                if validation.validate_path_gates(par,path,vertices,voltages,cutoff_pairs,cutoff_pairs_opp):
                    metrics.update_particle_movements(file_mvmt,pair0,par,path,vertices,voltages)
                    metrics.update_nanowire_state(file_state,pair0,positions,path,vertices,par,voltages)

        return nanowire, positions

    except exception.NoEmptyPositionException as err:
        raise
    except exception.InvalidNanowireStateException as err:
        raise
    except exception.PathBlockedException as err:
        raise

# list of particles in the order that they should be moved
# in case the brading operation is of category 2
def get_particles_list(nanowire,pair,positions):
    particles = []
    inner = ["a'","b'","f'","c'","d'","e'"]
    if positions[pair[0]-1] in inner:
        particles.append(pair[0])
        inter = utility.get_intersection(nanowire,positions[pair[1]-1])
        op = utility.get_other_particle(pair[1],inter)
        particles.append(op)
        particles.append(pair[1])
    elif positions[pair[1]-1] in inner:
        particles.append(pair[1])
        inter = utility.get_intersection(nanowire,positions[pair[0]-1])
        op = utility.get_other_particle(pair[1],inter)
        particles.append(op)
        particles.append(pair[0])
    return particles

################################################################################
# Performing braiding on each sequence
def braid_particles(nanowire, vertices, matrix, sequence, direction, positions, cutoff_pairs, cutoff_pairs_opp, file_pos, file_mvmt, file_state, file_line):
    try:
        msg = "----- Braiding completed -----"
        n = len(positions)
        line_pos = utility.get_par_braid_pos(n)
        metrics.update_particle_line_positions(file_line,sequence[0],line_pos)
        for i in range(len(sequence)):
            pair = sequence[i]
            dir = direction[i]
            print("----- Braiding particles {} -----".format(pair))
            utility.reset_variables(positions)
            utility.refresh_zero_modes()
            intersection = utility.get_intersection(nanowire,positions[pair[0]-1])
            condition = validation.check_unibranch_validity(pair,positions,intersection)
            if condition:
                nanowire,positions = braid_particles_same_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state)
            else:
                nanowire,positions = braid_particles_diff_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state)
            line_pos = utility.update_par_braid_pos(line_pos,pair)
            metrics.update_particle_line_positions(file_line,pair,line_pos)
        metrics.update_final_particle_positions(file_pos,positions)

    except exception.NoEmptyPositionException as err:
        print(err)
        msg = "----- Braiding interrupted -----"
    except exception.InvalidNanowireStateException as err:
        print(err)
        msg = "----- Braiding interrupted -----"
    except exception.PathBlockedException as err:
        print(err)
        msg = "----- Braiding interrupted -----"
    finally:
        print(msg)
