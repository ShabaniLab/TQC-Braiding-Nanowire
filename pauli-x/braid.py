"""
TQC Braiding Nanowire Algorithm - Braiding phase

A. Braiding particles on the different branches
    1. The braiding sequence movements of particles from initial positions to intermediate positions
    2. The braiding sequence movements of particles from intermediate positions to respective final positions
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
def braid_particles_diff_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state):
    try:
        utility.update_zero_modes(nanowire)
        voltages = utility.get_voltages()
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
        for par in pair:
            pos_start = positions[par-1]
            positions_temp = copy.copy(positions)
            pos_end = None
            f_nw = None
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
                        metrics.update_particle_movements(file_mvmt,pair,par,path,vertices,voltages)
                        metrics.update_nanowire_state(file_state,pair,positions,path,vertices,par,voltages)

        ########################################################################
        # 2.
        ########################################################################
        p_pair = pair
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
                    metrics.update_particle_movements(file_mvmt,pair,par,path,vertices,voltages)
                    metrics.update_nanowire_state(file_state,pair,positions,path,vertices,par,voltages)

        return nanowire, positions

    except exception.NoEmptyPositionException as err:
        raise
    except exception.InvalidNanowireStateException as err:
        raise
    except exception.PathBlockedException as err:
        raise

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
            nanowire, positions = braid_particles_diff_branch(nanowire, vertices, matrix, pair, dir, positions, cutoff_pairs, cutoff_pairs_opp, file_mvmt, file_state)
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
