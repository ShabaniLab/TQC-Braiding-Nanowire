"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Braiding

Objectives:
    1. TQC Braiding Nanowire Algorithm - Braiding phase
    2. Classes representing braiding sequences for different gates
    3. Particle position preprocessing

Class:
    1. Braiding
    2. Braiding1Qubit
    3. Braiding2Qubits
    4. BraidingCNOT
    5. BraidingHadamard
    6. BraidingPauliX
    7. BraidingPhaseS

Methods:
    1. braid_particles_same_branch
    2. braid_particles_diff_branch
    3. move_particles

    4. code_block_validation
    5. code_block_inter_positions
    6. code_block_path
    7. code_block_update_states
    8. code_block_save_path_output
    9. code_block_target_branch_config
    10. code_block_target_position_config
"""

import copy
from . import exception, graph, validation, metrics
from .utility import Utility

################################################################################################
class Braiding:
    """
    The super class for all gates' braiding
    """

    TYPE_FINAL = 1
    TYPE_INTER = 2
    TYPE_MOVE  = 0

    def __init__(self, nanowire, compiler):
        self.nanowire = nanowire
        self.compiler = compiler

    def braid_particles_same_branch(self, *args):
        """
        Method for braiding between particles on same branch - a generic implementation
        """
        pair = args[0]
        utility = args[1]
        file_mvmt = args[2]
        file_state = args[3]
        try:
            utility.update_zero_modes(self.nanowire.nanowire)
            voltages = utility.voltages
            pair0 = copy.copy(pair)
            f_nw, final_positions, positions_single = self.code_block_validation(pair, voltages, utility)

            # 1.
            pair = self.get_1st_pair_sequence(pair)
            for par in pair:
                pos_start = self.compiler.positions[par-1]
                positions_temp = copy.copy(self.compiler.positions)

                # getting the list of positions on free branches (intermediate positions)
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                f_nw, pos_end = self.code_block_inter_positions(inter_positions, positions_temp,
                    pair, par, voltages, utility, pos_start)

                if pos_end is not None and f_nw is not None:
                    self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                        pair0, file_mvmt, file_state, False, f_nw, True, True)

            # 2.
            p_pair = self.get_2nd_pair_sequence(pair)
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]
                self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                    pair0, file_mvmt, file_state, True, None, True, True)

        except exception.NoEmptyPositionException:
            raise
        except exception.InvalidNanowireStateException:
            raise
        except exception.PathBlockedException:
            raise

    def get_1st_pair_sequence(self, pair):
        """
        The braiding sequence of particles from initial positions to intermediate positions
        """
        par1 = pair[0]
        # par2 = pair[1]
        pos1 = self.compiler.positions[par1-1]
        # pos2 = self.compiler.positions[par2-1]
        if pos1 in self.nanowire.inner:
            return list(pair)
        return list(reversed(list(pair)))

    def get_2nd_pair_sequence(self, pair):
        """
        The braiding sequence of particles from intermediate to respective final positions
        """
        return list(pair)

    def braid_particles_diff_branch(self, *args):
        """
        Method for braiding between particles on different branches
        """

    def code_block_validation(self, pair, voltages, utility):
        """Initial Validation Phase"""
        try:
            # Getting the expected final positions after the braiding operation
            final_positions = Utility.get_final_positions(self.compiler.positions, pair)
            f_nw = Utility.update_nanowire(self.nanowire.nanowire, final_positions)

            # getting the list of isolated particles
            positions_single = utility.get_isolated_particles(final_positions)

            # validating final positions before moving forward with the braiding operation
            msg = "Error while trying to braid {}: {}, {} is an invalid state"\
                    .format(pair, final_positions, ','.join(voltages))
            validation.validate_nanowire_state(f_nw, final_positions, utility,
                    positions_single, voltages, self.nanowire, Braiding.TYPE_FINAL, msg)
            return f_nw, final_positions, positions_single
        except exception.InvalidNanowireStateException:
            raise

    def code_block_inter_positions(self, inter_pos, positions_temp, pair, par,
            voltages, utility, pos_start):
        """getting the best (least # steps) intermediate position in the list"""
        p_pos = None
        # p_score = 0
        p_steps = 10
        pos_end = None
        f_nw = None
        try:
            for pos in inter_pos:
                positions_temp[par-1] = pos
                i_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                positions_single = utility.get_isolated_particles(positions_temp)
                msg = "Error while trying to braid {}: {}, {} is an invalid state"\
                        .format(pair, positions_temp, ','.join(voltages))

                # validating the change in nanowire state because of an intermediate position
                score = validation.validate_nanowire_state(i_nw, positions_temp, utility,
                        positions_single, voltages, self.nanowire, Braiding.TYPE_INTER, msg)
                steps = Utility.get_steps(self.nanowire.matrix, self.nanowire.vertices,
                        pos_start, pos)
                p_pos = Utility.comparator(p_pos, p_steps, pos, steps)

                if p_pos is not None:
                    pos_end = p_pos
                    if p_pos==pos:
                        # p_score = score
                        p_steps = steps
                        f_nw = i_nw
                        self.compiler.positions = copy.copy(positions_temp)

            return f_nw, pos_end
        except exception.InvalidNanowireStateException:
            raise

    def code_block_path(self, pos_start, pos_end, par, f_nw, utility, voltages, pair,
            file_mvmt, file_state, pos_update, f_nw_update, update_zm, update_volt):
        """Dijkstra's algorithm gives the shortest path for a particle"""
        path = graph.route(self.nanowire.matrix,
                self.nanowire.vertices.index(pos_start),
                self.nanowire.vertices.index(pos_end))
        block = validation.validate_path_particle(path,
                self.compiler.positions, self.nanowire.vertices, par)
        if len(block)==0:
            if pos_update:
                self.compiler.positions[par-1] = pos_end
            self.code_block_update_states(f_nw_update, utility, update_zm, update_volt)
            Braiding.code_block_save_path_output(self.nanowire, voltages,
                self.compiler.positions, pair, par, path, file_mvmt, file_state)

    def code_block_update_states(self, f_nw, utility, update_zm, update_volt):
        """Updates the necessary states after a braiding op"""
        if f_nw is None:
            f_nw = Utility.update_nanowire(self.nanowire.nanowire, self.compiler.positions)
        self.nanowire.nanowire = copy.deepcopy(f_nw)
        if update_zm:
            utility.update_zero_modes(f_nw)
        if update_volt:
            utility.update_voltages(self.compiler.positions, self.nanowire.cutoff_pairs_adj)

    @classmethod
    def code_block_save_path_output(cls, nanowire_obj, voltages, positions,
            pair, par, path, file_mvmt, file_state):
        """Function calls to metrics """
        if validation.validate_path_gates(par, path, nanowire_obj.vertices,
                voltages, nanowire_obj.cutoff_pairs_adj, nanowire_obj.cutoff_pairs_opp):
            metrics.update_particle_movements(file_mvmt, pair, par, path,
                nanowire_obj.vertices, voltages)
            metrics.update_nanowire_state(file_state, pair,
                positions, path, nanowire_obj.vertices, par, voltages)

    def move_particles(self, *args):
        """
        Particle position preprocessing
        1. If the zero modes are on different intersections
        2. If the zero modes have different branch config but on the same intersection

        Moving particles to respective positions:
        1. Preserving the order - outer to outer
        2. Reversing the order  - inner to outer
        """
        try:
            utility       = args[0]
            intersections = args[1]
            branches      = args[2]
            particles     = args[3]
            branch_cfg    = args[4]
            file_mvmt     = args[5]
            file_state    = args[6]
            gate          = args[7]

            inter_initial, inter_target, branch_initial, branch_target = \
                self.code_block_target_branch_config(intersections, branches, branch_cfg)
            # print(inter_initial, inter_target, branch_initial, branch_target)

            final_positions, dir, par_inner, par_outer = \
                self.code_block_target_position_config(gate, utility,
                particles, branches, inter_initial, inter_target, branch_initial, branch_target)
            # print(self.compiler.positions, final_positions, dir, par_inner, par_outer)
            pair = (par_inner, par_outer)
            pair_ret = ()

            # Reverse order
            if dir == 0:
                print("\033[0;33m----- Moving particles {} -----\033[0m".format(pair))
                pair = (0,0)
                # 1. Move initial inner to target outer position
                positions_temp = copy.copy(self.compiler.positions)
                positions_temp[par_inner-1] = final_positions[par_inner-1]
                f_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                self.code_block_path(self.compiler.positions[par_inner-1], final_positions[par_inner-1], par_inner,
                    f_nw, utility, utility.voltages, pair, file_mvmt, file_state, True, f_nw, False, False)

                # 2. Move initial outer to target inner position
                positions_temp = copy.copy(self.compiler.positions)
                positions_temp[par_outer-1] = final_positions[par_outer-1]
                f_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                self.code_block_path(self.compiler.positions[par_outer-1], final_positions[par_outer-1], par_outer,
                    f_nw, utility, utility.voltages, pair, file_mvmt, file_state, True, f_nw, True, True)

            # Same order
            if dir == 1:
                print("\033[0;33m----- Moving particles {} -----\033[0m".format(pair))
                pair_ret = pair
                pair = (0,0)
                # a. getting the intermediate positions for par_inner
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, self.compiler.positions[par_inner-1])
                middle = ['m']
                pos_mid2 = None
                for position in inter_positions:
                    if inter_initial == inter_target and position in middle:
                        # if the intersection is the same then move the inner particle onto
                        # the middle branch, which is (m) in this case
                        pos_mid2 = position
                        break
                    elif inter_initial != inter_target and position in self.nanowire.inner:
                        # else move it into the other branch, so this doesn't block the path
                        # to the other intersection
                        pos_mid2 = position
                        break

                if pos_mid2 is None:
                    msg = "The initial positions of particles are in an invalid state to move them"
                    raise exception.InvalidMovementException(msg)

                # 1. Move par_inner to pos_mid2
                positions_temp = copy.copy(self.compiler.positions)
                positions_temp[par_inner-1] = pos_mid2
                f_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                self.code_block_path(self.compiler.positions[par_inner-1], pos_mid2, par_inner,
                    f_nw, utility, utility.voltages, pair, file_mvmt, file_state, True, f_nw, False, False)

                # 2. Move the par_outer to outer position on target branch
                positions_temp = copy.copy(self.compiler.positions)
                positions_temp[par_outer-1] = final_positions[par_outer-1]
                f_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                self.code_block_path(self.compiler.positions[par_outer-1], final_positions[par_outer-1], par_outer,
                    f_nw, utility, utility.voltages, pair, file_mvmt, file_state, True, f_nw, False, False)

                # 3. Move par_inner from pos_mid2 to inner position on target branch
                positions_temp = copy.copy(self.compiler.positions)
                positions_temp[par_inner-1] = final_positions[par_inner-1]
                f_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                self.code_block_path(pos_mid2, final_positions[par_inner-1], par_inner, f_nw,
                    utility, utility.voltages, pair, file_mvmt, file_state, True, f_nw, True, True)

            if self.compiler.positions == final_positions:
                return final_positions, pair_ret
            msg = "There was an error in movement: {}".format(self.compiler.positions)
            raise exception.InvalidMovementException(msg)
        except exception.NoEmptyPositionException:
            raise
        except exception.InvalidNanowireStateException:
            raise
        except exception.InvalidMovementException:
            raise
        except exception.PathBlockedException:
            raise

    def code_block_target_branch_config(self, intersections, branches, branch_cfg):
        """returns the initial and final intersections and branches"""
        inter_initial  = 0
        inter_target   = 0
        branch_initial = 0
        branch_target  = 0
        n_branches = len(self.nanowire.nanowire[0])
        opp_allowed = [(0,0), (0,2), (1,0), (1,2)]
        adj_clk_allowed = [(0,1), (0,2), (1,0), (1,3)]
        adj_clk_2_allowed = [(0,0), (0,1), (1,3), (1,2)]
        adj_ctr_clk_allowed = [(0,0), (0,1), (1,2), (1,3)]
        adj_ctr_clk_2_allowed = [(0,1), (0,2), (1,3), (1,0)]

        # getting the initial and target intersections
        si = list(set(intersections))
        if len(si) == 1:
            inter_initial = si[0]
            inter_target  = si[0]
        elif len(si) == 2:
            inter_initial = si[0]
            inter_target  = si[1]

        if len(branches) > 4:
            msg = "With the given positions, {}, it isn't possible to move the particles into a valid gate branch config"\
                .format(branches)
            raise exception.InvalidMovementException(msg)

        bi = list(set(branches))
        if len(bi) > 2:
            msg = "With the given positions, {}, it isn't possible to move the particles into a valid gate branch config"\
                .format(bi)
            raise exception.InvalidMovementException(msg)

        # getting the initial and target branches
        b1 = bi[0]
        b2 = bi[1]
        ib1 = (inter_initial, b1%n_branches)
        ib2 = (inter_target, b2%n_branches)
        msg = "With the current positions of ({}, {}) it isn't possible to move them into a valid gate branch config"\
            .format(b1, b2)

        try:
            tup_cur1 = self.nanowire.nanowire[inter_initial][b1%n_branches][-1]
            pos_cur1 = list(tup_cur1.keys())[0]
            free_positions1 = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_cur1)
            free_branches1 = int(len(free_positions1)/2)+1

            tup_cur2 = self.nanowire.nanowire[inter_target][b2%n_branches][-1]
            pos_cur2 = list(tup_cur2.keys())[0]
            free_positions2 = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_cur2)
            free_branches2 = int(len(free_positions2)/2)+1

            if "opposite" in branch_cfg:
                min_free_branch = 3
                if inter_initial == inter_target:
                    min_free_branch = 2
                if ib1 in opp_allowed and free_branches1 >= min_free_branch:
                    branch_initial = b2
                    branch_target = (b1 + n_branches/2)%n_branches
                    if inter_target != inter_initial:
                        inter_target, inter_initial = inter_initial, inter_target
                elif ib2 in opp_allowed and free_branches2 >= min_free_branch:
                    branch_initial = b1
                    branch_target = (b2 + n_branches/2)%n_branches
                    # if inter_target != inter_initial:
                    #     inter_target, inter_initial = inter_initial, inter_target
                else:
                    raise exception.InvalidMovementException(msg)
            elif "adjacent" and "clockwise" in branch_cfg:
                min_free_branch = 3
                if inter_initial == inter_target:
                    min_free_branch = 2
                if free_branches1 >= min_free_branch and ib1 in adj_clk_allowed:
                    branch_initial = b2
                    if ib1 in adj_clk_allowed:
                        branch_target = (b1 - 1)%n_branches
                    if inter_target != inter_initial:
                        inter_target, inter_initial = inter_initial, inter_target
                elif free_branches2 >= min_free_branch and ib2 in adj_clk_2_allowed:
                    branch_initial = b1
                    if ib2 in adj_clk_2_allowed:
                        branch_target = (b2 + 1)%n_branches
                    # if inter_target != inter_initial:
                    #     inter_target, inter_initial = inter_initial, inter_target
                else:
                    raise exception.InvalidMovementException(msg)
            elif "adjacent" and "counter clockwise" in branch_cfg:
                min_free_branch = 3
                if inter_initial == inter_target:
                    min_free_branch = 2
                if free_branches1 >= min_free_branch and\
                    (ib1 in adj_ctr_clk_allowed or ib1 in adj_ctr_clk_2_allowed):
                    branch_initial = b2
                    if ib1 in adj_ctr_clk_allowed:
                        branch_target = (b1 + 1)%n_branches
                    elif ib1 in adj_ctr_clk_2_allowed:
                        branch_target = (b1 - 1)%n_branches
                    if inter_target != inter_initial:
                        inter_target, inter_initial = inter_initial, inter_target
                elif free_branches2 >= min_free_branch and\
                    (ib2 in adj_ctr_clk_allowed or ib2 in adj_ctr_clk_2_allowed):
                    branch_initial = b1
                    if ib2 in adj_ctr_clk_2_allowed:
                        branch_target = (b2 - 1)%n_branches
                    elif ib2 in adj_ctr_clk_allowed:
                        branch_target = (b2 + 1)%n_branches
                    # if inter_target != inter_initial:
                    #     inter_target, inter_initial = inter_initial, inter_target
                else:
                    raise exception.InvalidMovementException(msg)
        except exception.NoEmptyPositionException:
            raise
        return inter_initial, inter_target, branch_initial, int(branch_target)

    def code_block_target_position_config(self, gate, utility, particles, branches,
            inter_initial, inter_target, branch_initial, branch_target):
        """get particles to be moved, final positions, zero mode order"""
        try:
            # i. getting the particles to be moved
            pars = []
            branch_idx = [i for i in range(len(branches)) if branches[i] == branch_initial]
            pars = [particles[i] for i in branch_idx]
            if len(pars) != 2:
                msg = "Invalid number of particles for the movement"
                raise exception.InvalidMovementException(msg)
            par1 = pars[0]
            par2 = pars[1]

            # ii. getting the positions on target branch
            target_branch = self.nanowire.nanowire[inter_target][branch_target]
            pos_end_inner = None
            pos_end_outer = None
            for tup in target_branch:
                if not isinstance(tup, dict):
                    continue
                pos = list(tup.keys())[0]
                if pos in self.nanowire.inner:
                    pos_end_inner = pos
                elif pos in self.nanowire.outer:
                    pos_end_outer = pos

            if pos_end_outer is None or pos_end_inner is None:
                msg = "Invalid final positions ({}, {}) of particles for the movement"\
                    .format(pos_end_outer, pos_end_inner)
                raise exception.InvalidMovementException(msg)

            # 1. getting the order of the final zero mode positions
            dir = None
            dir_rev_gates  = ["hadamard", "pauli-x"]
            dir_same_gates = ["cnot", "phase-s"]
            if gate in dir_rev_gates:
                dir = 0
            elif gate in dir_same_gates:
                dir = 1
            else:
                msg = "There is not zero mode alignment for {} gate".format(gate)
                raise exception.InvalidMovementException(msg)

            final_positions = copy.copy(self.compiler.positions)
            if dir == 1:
                final_positions[par1-1] = pos_end_outer
                final_positions[par2-1] = pos_end_inner
            else:
                final_positions[par1-1] = pos_end_inner
                final_positions[par2-1] = pos_end_outer

            # 1a. validating final positions before moving forward with the braiding operation
            msg = "Error while trying to move {}: {} is an invalid state"\
                .format((par1, par2), final_positions)
            f_nw = Utility.update_nanowire(self.nanowire.nanowire, final_positions)
            positions_single = utility.get_isolated_particles(final_positions)
            validation.validate_nanowire_state(f_nw, final_positions, utility,
                positions_single, utility.voltages, self.nanowire, Braiding.TYPE_FINAL, msg)

            # 2. getting order (dir) of movement
            pos_start1 = self.compiler.positions[par1-1]
            pos_start2 = self.compiler.positions[par2-1]
            pos_end1 = final_positions[par1-1]
            pos_end2 = final_positions[par2-1]
            dir = None
            if (pos_start1 in self.nanowire.outer and pos_end1 in self.nanowire.outer) or\
                (pos_start2 in self.nanowire.outer and pos_end2 in self.nanowire.outer) or\
                (pos_start1 in self.nanowire.inner and pos_end1 in self.nanowire.inner) or\
                (pos_start2 in self.nanowire.inner and pos_end2 in self.nanowire.inner):
                dir = 1
            elif (pos_start1 in self.nanowire.outer and pos_end1 in self.nanowire.inner) or\
                (pos_start1 in self.nanowire.inner and pos_end1 in self.nanowire.outer) or\
                (pos_start2 in self.nanowire.outer and pos_end2 in self.nanowire.inner) or\
                (pos_start2 in self.nanowire.inner and pos_end2 in self.nanowire.outer):
                dir = 0

            # 3. getting the par_inner, par_outer
            par_inner = None
            par_outer = None
            if self.compiler.positions[par1-1] in self.nanowire.inner:
                par_inner = par1
            elif self.compiler.positions[par1-1] in self.nanowire.outer:
                par_outer = par1

            if self.compiler.positions[par2-1] in self.nanowire.inner:
                par_inner = par2
            elif self.compiler.positions[par2-1] in self.nanowire.outer:
                par_outer = par2

            if par_inner is None or par_outer is None or par_inner == par_outer:
                msg = "Error in position of the particles' to be moved: ({}, {})"\
                    .format(par_inner, par_outer)
                raise exception.InvalidMovementException(msg)

            return final_positions, dir, par_inner, par_outer
        except exception.InvalidNanowireStateException:
            raise

class Braiding1Qubit(Braiding):
    """
    The Braiding class for 1 Qubit gate
    """

    def braid_particles_diff_branch(self, *args):
        pair = args[0]
        utility = args[1]
        file_mvmt = args[2]
        file_state = args[3]
        try:
            utility.update_zero_modes(self.nanowire.nanowire)
            voltages = utility.voltages
            f_nw, final_positions, positions_single = self.code_block_validation(pair, voltages, utility)

            # 1.
            for par in pair:
                pos_start = self.compiler.positions[par-1]
                positions_temp = copy.copy(self.compiler.positions)

                # getting the list of positions on free branches
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                f_nw, pos_end = self.code_block_inter_positions(inter_positions, positions_temp,
                    pair, par, voltages, utility, pos_start)

                if pos_end is not None and f_nw is not None:
                    self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                        pair, file_mvmt, file_state, False, f_nw, True, True)

            # 2.
            p_pair = pair
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]
                self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                    pair, file_mvmt, file_state, True, None, True, True)

        except exception.NoEmptyPositionException:
            raise
        except exception.InvalidNanowireStateException:
            raise
        except exception.PathBlockedException:
            raise


class Braiding2Qubits(Braiding):
    """
    The Braiding class for 2 Qubit gates
    """

################################################################################################
# 2 Qubit gates
class BraidingCNOT(Braiding2Qubits):
    """
    The Braiding class for CNOT gate
    """

    def braid_particles_diff_branch(self, *args):
        pair = args[0]
        utility = args[1]
        file_mvmt = args[2]
        file_state = args[3]
        try:
            particles = self.get_particles_list(pair)
            utility.update_zero_modes(self.nanowire.nanowire)
            voltages = utility.voltages
            pair0 = copy.copy(pair)
            f_nw, final_positions, positions_single = self.code_block_validation(pair, voltages, utility)

            # 1.
            pair2 = particles[:2]
            for par in pair2:
                pos_start = self.compiler.positions[par-1]
                positions_temp = copy.copy(self.compiler.positions)

                # getting the list of positions on free branches
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                f_nw, pos_end = self.code_block_inter_positions(inter_positions, positions_temp,
                    pair, par, voltages, utility, pos_start)

                if pos_end is not None and f_nw is not None:
                    self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                        pair0, file_mvmt, file_state, False, f_nw, True, True)

            # 2.
            par = particles[2]
            pos_start = self.compiler.positions[pair[1]-1]
            pos_end = final_positions[pair[1]-1]
            self.compiler.positions[par-1] = final_positions[par-1]
            self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                pair0, file_mvmt, file_state, False, None, True, True)

            # 3.
            p_pair = pair2
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]
                self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                    pair0, file_mvmt, file_state, True, None, True, True)

        except exception.NoEmptyPositionException:
            raise
        except exception.InvalidNanowireStateException:
            raise
        except exception.PathBlockedException:
            raise

    def get_particles_list(self, pair):
        """
        Returning a list of:
        1. the outermost (blocking) particle and 1st particle in the given pair
        2. the 2nd particle in the given pair
        3. the 2 particles back to their respective positions
        """
        particles = []
        if self.compiler.positions[pair[0]-1] in self.nanowire.inner:
            particles.append(pair[0])
            inter = Utility.get_intersection(self.nanowire.nanowire, self.compiler.positions[pair[1]-1])
            op = Utility.get_other_particle(pair[1], inter)
            particles.append(op)
            particles.append(pair[1])
        elif self.compiler.positions[pair[1]-1] in self.nanowire.inner:
            particles.append(pair[1])
            inter = Utility.get_intersection(self.nanowire.nanowire, self.compiler.positions[pair[0]-1])
            op = Utility.get_other_particle(pair[1], inter)
            particles.append(op)
            particles.append(pair[0])
        return particles


################################################################################################
# 1 Qubit gates
class BraidingHadamard(Braiding1Qubit):
    """
    The Braiding class for Hadamard gate
    """


class BraidingPauliX(Braiding1Qubit):
    """
    The Braiding class for Pauli-X gate
    """


class BraidingPhaseS(Braiding1Qubit):
    """
    The Braiding class for Phase-S gate
    """
