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
            # Once final positions are validated, move the particles to their intermediate pos
            # 1st particle that moves gets the 1st empty branch (for now)
            # --Can later specify any rule/restriction to move particles to certain branches
            # intermediate_positions = []
            pair = self.get_1st_pair_sequence(pair)
            for par in pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = None
                f_nw = None
                positions_temp = copy.copy(self.compiler.positions)

                # getting the list of positions on free branches (intermediate positions)
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                f_nw, pos_end = self.code_block_inter_positions(inter_positions, positions_temp,
                    pair, par, voltages, utility, pos_start, pos_end)

                if pos_end is not None and f_nw is not None:
                    self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                        pair0, file_mvmt, file_state, False, f_nw)

            # 2.
            p_pair = self.get_2nd_pair_sequence(pair)
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]
                self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                    pair0, file_mvmt, file_state, True, None)

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
        # inner = ["a'", "b'", "f'", "c'", "d'", "e'"]
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
        voltages, utility, pos_start, pos_end):
        """getting the best (least # steps) intermediate position in the list"""
        p_pos = None
        # p_score = 0
        p_steps = 10
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
                    # intermediate_positions = inter_pos
                    if p_pos==pos:
                        # p_score = score
                        p_steps = steps
                        f_nw = i_nw
                        self.compiler.positions = copy.copy(positions_temp)

            return f_nw, pos_end
        except exception.InvalidNanowireStateException:
            raise

    def code_block_path(self, pos_start, pos_end, par, f_nw, utility, voltages, pair,
        file_mvmt, file_state, pos_update, f_nw_update):
        """Dijkstra's algorithm gives the shortest path for a particle
        from its current position to its final position."""
        path = graph.route(self.nanowire.matrix,
                self.nanowire.vertices.index(pos_start),
                self.nanowire.vertices.index(pos_end))
        block = validation.validate_path_particle(path,
                self.compiler.positions, self.nanowire.vertices, par)
        if len(block)==0:
            if pos_update:
                self.compiler.positions[par-1] = pos_end
            self.code_block_update_states(f_nw_update, utility)
            Braiding.code_block_save_path_output(self.nanowire, voltages,
                self.compiler.positions, pair, par, path, file_mvmt, file_state)

    def code_block_update_states(self, f_nw, utility):
        """Updates the necessary states after a braiding op"""
        if f_nw is None:
            f_nw = Utility.update_nanowire(self.nanowire.nanowire, self.compiler.positions)

        self.nanowire.nanowire = copy.deepcopy(f_nw)
        utility.update_zero_modes(f_nw)
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

    @classmethod
    def move_particles(cls, *args):
        """
        Particle position preprocessing
        1. If the zero modes are on different intersections
        2. If the zero modes have different branch config but on the same intersection

        Moving particles to respective positions:
        1. Preserving the order - outer to outer
        2. Reversing the order  - inner to outer
        """
        nanowire_obj  = args[0]
        positions     = args[1]
        intersections = args[2]
        branches      = args[3]
        particles     = args[4]
        file_pos      = args[5]
        file_mvmt     = args[6]
        file_state    = args[7]
        branch_cfg    = args[8]

        par1 = particles[0]
        par2 = particles[1]
        par3 = particles[2]
        par4 = particles[3]
        pair1 = [par1, par2]
        pair2 = [par3, par4]

        inter_initial  = 0
        inter_target   = 0
        branch_initial = 0
        branch_target  = 0
        n_branches = len(nanowire_obj.nanowire[0])

        if len(set(intersections)) == 1:
            inter_initial = intersections[0]
            inter_target  = intersections[0]
        else:
            inter_initial = intersections[0]
            inter_target  = intersections[2]

        paired_branch = branches[2]
        if "adjacent" and "clockwise" in branch_cfg:
            branch_target = paired_branch + 1
        elif "adjacent" and "counter clockwise" in branch_cfg:
            branch_target = paired_branch - 1
        elif "opposite" in branch_cfg:
            branch_target = paired_branch + n_branches/2
        branch_target = branch_target%n_branches

        ########################################################################################
        ## 1. Get target branch from intersection along with respective positions
        voltages = utility.voltages
        branch = inter_target[branch_target]
        tgt_pos_out = branch
        tgt_pos_in  = branch

        ## 2. Map start to end positions in reverse order
        tgt_pos_par1 = tgt_pos_in
        tgt_pos_par2 = tgt_pos_out

        ## 3. Check if the movement causes the nanowire state to be invalid
        pair = pair1
        final_positions = copy.copy(positions)
        final_positions[par1-1] = tgt_pos_par1
        final_positions[par2-1] = tgt_pos_par2
        f_nw = Utility.update_nanowire(self.nanowire.nanowire, final_positions)

        # getting the list of isolated particles
        positions_single = utility.get_isolated_particles(final_positions)

        # validating final positions before moving forward with the braiding operation
        msg = "Error while trying to move {}: {} is an invalid state"\
                .format(pair, final_positions)
        validation.validate_nanowire_state(f_nw, final_positions, utility,
                positions_single, voltages, self.nanowire, Braiding.TYPE_FINAL, msg)

        ########################################################################################
        # Reverse order:
        ########################################################################################
        ## 4. Extract the path and move them in reverse order
        path2 = graph.route(nanowire_obj.matrix, positions[par2-1], tgt_pos_par2)
        path1 = graph.route(nanowire_obj.matrix, positions[par1-1], tgt_pos_par1)

        # checking if the path is not blocked
        block2 = validation.validate_path_particle(path2, final_positions, nanowire_obj.vertices, par2)
        block1 = validation.validate_path_particle(path1, final_positions, nanowire_obj.vertices, par1)
        if len(block1) == 0 and len(block2) == 0:
            f_nw = Utility.update_nanowire(nanowire_obj.nanowire, self.compiler.positions)
            nanowire_obj.nanowire = copy.deepcopy(f_nw)

            # checks if the voltage gate changes doesn't block the movement path
            Braiding.save_path_output(nanowire_obj, voltages,
                positions, pair, par2, path2, file_mvmt, file_state)
            Braiding.save_path_output(nanowire_obj, voltages,
                positions, pair, par1, path1, file_mvmt, file_state)

        ########################################################################################
        # Same order
        ########################################################################################
        # 4. Move inner particle to temporary position on the middle branch
        # depending on the initial and finak intersections
        inter_positions = Utility.get_intermediate_positions(nanowire_obj.nanowire, positions[par1-1])
        pos = None
        middle = ['m']
        inner = ["a'", "b'", "f'", "c'", "d'", "e'"]

        for position in inter_positions:
            if inter_initial == inter_target and position in moddle:
                # if the intersection is the same then move the inner particle onto
                # the middle of the nanowire, which is (m) in this case
                pos = position
                break
            elif inter_initial != inter_target and\
                position not in moddle and position is inner:
                # else move it into the other branch, so this doesn't block the path
                # to the other intersection
                pos = position
                break

        if pos is None:
            msg = "The initial positions of particles are in an invalid state to commence braiding"
            raise exception.InvalidNanowireStateException(msg)

        path = graph.route(nanowire_obj.matrix, positions[par2-1], pos)
        block = validation.validate_path_particle(path, final_positions, nanowire_obj.vertices, par2)

        positions_temp = copy.copy(positions)
        positions_temp[par2-1] = pos
        i_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
        positions_single = utility.get_isolated_particles(positions_temp)

        # 5. Move outer particle to same position on target branch
        path1 = graph.route(nanowire_obj.matrix, positions[par1-1], tgt_pos_par1)
        block1 = validation.validate_path_particle(path1, final_positions, nanowire_obj.vertices, par1)

        # 6. Move particle from #2 to inner position on target branch
        path2 = graph.route(nanowire_obj.matrix, positions[par2-1], tgt_pos_par2)
        block2 = validation.validate_path_particle(path2, final_positions, nanowire_obj.vertices, par2)

        # updating all 3 movements
        if len(block) == 0 and len(block1) == 0 and len(block2) == 0:
            nanowire_obj.nanowire = copy.deepcopy(f_nw)

            Braiding.save_path_output(nanowire_obj, voltages,
                positions, pair, par2, path, file_mvmt, file_state)
            Braiding.save_path_output(nanowire_obj, voltages,
                positions, pair, par1, path1, file_mvmt, file_state)
            Braiding.save_path_output(nanowire_obj, voltages,
                positions, pair, par2, path2, file_mvmt, file_state)

        msg = "The initial positions of particles are in an invalid state to commence braiding"
        raise exception.InvalidNanowireStateException(msg)


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
            # intermediate_positions = []
            for par in pair:
                pos_start = self.compiler.positions[par-1]
                positions_temp = copy.copy(self.compiler.positions)
                pos_end = None
                f_nw = None

                # getting the list of positions on free branches
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                f_nw, pos_end = self.code_block_inter_positions(inter_positions, positions_temp,
                    pair, par, voltages, utility, pos_start, pos_end)

                if pos_end is not None and f_nw is not None:
                    self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                        pair, file_mvmt, file_state, False, f_nw)

            # 2.
            p_pair = pair
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]
                self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                    pair, file_mvmt, file_state, True, None)

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
            # intermediate_positions = []
            pair2 = particles[:2]
            for par in pair2:
                pos_start = self.compiler.positions[par-1]
                pos_end = None
                f_nw = None
                positions_temp = copy.copy(self.compiler.positions)

                # getting the list of positions on free branches
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                f_nw, pos_end = self.code_block_inter_positions(inter_positions, positions_temp,
                    pair, par, voltages, utility, pos_start, pos_end)

                if pos_end is not None and f_nw is not None:
                    self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                        pair0, file_mvmt, file_state, False, f_nw)

            # 2.
            par = particles[2]
            pos_start = self.compiler.positions[pair[1]-1]
            pos_end = final_positions[pair[1]-1]
            self.compiler.positions[par-1] = final_positions[par-1]
            self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                pair0, file_mvmt, file_state, False, None)

            # 3.
            p_pair = pair2
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]
                self.code_block_path(pos_start, pos_end, par, f_nw, utility, voltages,
                    pair0, file_mvmt, file_state, True, None)

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
        # inner = ["a'", "b'", "f'", "c'", "d'", "e'"]
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
