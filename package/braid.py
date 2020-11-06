"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Braiding

Objectives:
    1. TQC Braiding Nanowire Algorithm - Braiding phase
    2. Classes representing braiding sequences for different gates

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
"""

import copy
from . import graph
from . import exception
from . import validation
from . import metrics
from .utility import Utility

################################################################################
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

            ########################################################################
            ## Initial Validation Phase
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

            ########################################################################
            # 1.
            ########################################################################
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
                p_pos = None
                # p_score = 0
                p_steps = 10

                # getting the list of positions on free branches (intermediate positions)
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                # getting the best (with least #steps)intermediate position in the list
                for pos in inter_positions:
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
                        # intermediate_positions = inter_positions
                        if p_pos==pos:
                            # p_score = score
                            p_steps = steps
                            f_nw = i_nw
                            self.compiler.positions = copy.copy(positions_temp)

                if pos_end is not None and f_nw is not None:
                    # Dijkstra's algorithm gives the shortest path for a particle
                    # from its current position to its final position.
                    path = graph.route(self.nanowire.matrix,
                                        self.nanowire.vertices.index(pos_start),
                                        self.nanowire.vertices.index(pos_end))

                    # checking if the path is not blocked
                    block = validation.validate_path_particle(path, self.compiler.positions,
                                                                self.nanowire.vertices, par)
                    if len(block)==0:
                        self.nanowire.nanowire = copy.deepcopy(f_nw)

                        # update the zero modes according to the new Nanowire state
                        utility.update_zero_modes(self.nanowire.nanowire)
                        utility.update_voltages(self.compiler.positions,
                                                self.nanowire.cutoff_pairs_adj)

                        # checks if the voltage gate changes doesn't block the movement path
                        if validation.validate_path_gates(par, path, self.nanowire.vertices,
                                voltages, self.nanowire.cutoff_pairs_adj,
                                self.nanowire.cutoff_pairs_opp):
                            metrics.update_particle_movements(file_mvmt, pair0, par, path,
                                                            self.nanowire.vertices, voltages)
                            metrics.update_nanowire_state(file_state, pair0,
                                self.compiler.positions, path,
                                self.nanowire.vertices, par, voltages)

            ########################################################################
            # 2.
            ########################################################################
            p_pair = self.get_2nd_pair_sequence(pair)
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]

                path = graph.route(self.nanowire.matrix,
                                    self.nanowire.vertices.index(pos_start),
                                    self.nanowire.vertices.index(pos_end))

                # checking if the path is not blocked
                block = validation.validate_path_particle(path,
                        self.compiler.positions, self.nanowire.vertices, par)
                if len(block)==0:
                    self.compiler.positions[par-1] = pos_end
                    f_nw = Utility.update_nanowire(self.nanowire.nanowire, self.compiler.positions)
                    self.nanowire.nanowire = copy.deepcopy(f_nw)
                    utility.update_zero_modes(self.nanowire.nanowire)
                    utility.update_voltages(self.compiler.positions, self.nanowire.cutoff_pairs_adj)

                    # checks if the voltage gate changes doesn't block the movement path
                    if validation.validate_path_gates(par, path, self.nanowire.vertices,
                            voltages, self.nanowire.cutoff_pairs_adj,
                            self.nanowire.cutoff_pairs_opp):
                        metrics.update_particle_movements(file_mvmt, pair0, par, path,
                                self.nanowire.vertices, voltages)
                        metrics.update_nanowire_state(file_state, pair0,
                            self.compiler.positions, path, self.nanowire.vertices, par, voltages)

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

            ########################################################################
            ## Initial Validation Phase
            # Getting the expected final positions after the braiding operation and validating it
            # before moving forward with the braiding operation itself
            final_positions = Utility.get_final_positions(self.compiler.positions, pair)
            f_nw = Utility.update_nanowire(self.nanowire.nanowire, final_positions)

            # getting the list of isolated particles
            positions_single = utility.get_isolated_particles(final_positions)

            # validating final positions before moving forward with the braiding operation
            msg = "Error while trying to braid {}: {}, {} is an invalid state"\
                    .format(pair, final_positions, ','.join(voltages))
            validation.validate_nanowire_state(f_nw, final_positions, utility,
                    positions_single, voltages, self.nanowire, Braiding.TYPE_FINAL, msg)

            ########################################################################
            # 1.
            ########################################################################
            # intermediate_positions = []
            for par in pair:
                pos_start = self.compiler.positions[par-1]
                positions_temp = copy.copy(self.compiler.positions)
                pos_end = None
                f_nw = None
                p_pos = None
                # p_score = 0
                p_steps = 10

                # getting the list of self.compiler.positions on free branches
                # (intermediate positions)
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                # getting the best intermediate self.compiler.positions
                for pos in inter_positions:
                    positions_temp[par-1] = pos
                    i_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                    positions_single = utility.get_isolated_particles(positions_temp)

                    msg = "Error while trying to braid {}: {}, {} is an invalid state"\
                            .format(pair, positions_temp, ','.join(voltages))
                    score = validation.validate_nanowire_state(i_nw, positions_temp, utility,
                            positions_single, voltages, self.nanowire, Braiding.TYPE_INTER, msg)
                    steps = Utility.get_steps(self.nanowire.matrix,
                            self.nanowire.vertices, pos_start, pos)
                    p_pos = Utility.comparator(p_pos, p_steps, pos, steps)

                    if p_pos is not None:
                        pos_end = p_pos
                        # intermediate_positions = inter_positions
                        if p_pos==pos:
                            # p_score = score
                            p_steps = steps
                            f_nw = i_nw
                            self.compiler.positions = copy.copy(positions_temp)

                if pos_end is not None and f_nw is not None:
                    # Dijkstra's algorithm gives the shortest path for a particle
                    # from its current position to its final position.
                    path = graph.route(self.nanowire.matrix,
                            self.nanowire.vertices.index(pos_start),
                            self.nanowire.vertices.index(pos_end))
                    block = validation.validate_path_particle(path,
                            self.compiler.positions, self.nanowire.vertices, par)
                    if len(block)==0:
                        self.nanowire.nanowire = copy.deepcopy(f_nw)
                        utility.update_zero_modes(self.nanowire.nanowire)
                        utility.update_voltages(self.compiler.positions,
                                self.nanowire.cutoff_pairs_adj)
                        if validation.validate_path_gates(par, path, self.nanowire.vertices,
                            voltages, self.nanowire.cutoff_pairs_adj,
                            self.nanowire.cutoff_pairs_opp):
                            metrics.update_particle_movements(file_mvmt, pair, par, path,
                                    self.nanowire.vertices, voltages)
                            metrics.update_nanowire_state(file_state, pair,
                                self.compiler.positions, path,
                                self.nanowire.vertices, par, voltages)

            ########################################################################
            # 2.
            ########################################################################
            p_pair = pair
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]

                path = graph.route(self.nanowire.matrix, self.nanowire.vertices.index(pos_start),
                        self.nanowire.vertices.index(pos_end))
                block = validation.validate_path_particle(path, self.compiler.positions,
                        self.nanowire.vertices, par)
                if len(block)==0:
                    self.compiler.positions[par-1] = pos_end
                    f_nw = Utility.update_nanowire(self.nanowire.nanowire, self.compiler.positions)
                    self.nanowire.nanowire = copy.deepcopy(f_nw)
                    utility.update_zero_modes(self.nanowire.nanowire)
                    utility.update_voltages(self.compiler.positions, self.nanowire.cutoff_pairs_adj)
                    if validation.validate_path_gates(par, path, self.nanowire.vertices, voltages,
                            self.nanowire.cutoff_pairs_adj, self.nanowire.cutoff_pairs_opp):
                        metrics.update_particle_movements(file_mvmt, pair, par, path,
                            self.nanowire.vertices, voltages)
                        metrics.update_nanowire_state(file_state, pair,
                            self.compiler.positions, path, self.nanowire.vertices, par, voltages)

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

################################################################################
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

            ########################################################################
            ## Initial Validation Phase
            # Getting the expected final positions after the braiding operation and validating it
            # before moving forward with the braiding operation itself
            final_positions = Utility.get_final_positions(self.compiler.positions, pair)
            f_nw = Utility.update_nanowire(self.nanowire.nanowire, final_positions)

            # getting the list of isolated particles
            positions_single = utility.get_isolated_particles(final_positions)

            # validating final positions before moving forward with the braiding operation
            msg = "Error while trying to braid {}: {}, {} is an invalid state"\
                    .format(pair, final_positions, ','.join(voltages))
            validation.validate_nanowire_state(f_nw, final_positions, utility, positions_single,
                    voltages, self.nanowire, Braiding.TYPE_FINAL, msg)

            ########################################################################
            # 1.
            ########################################################################
            # intermediate_positions = []
            pair2 = particles[:2]
            for par in pair2:
                pos_start = self.compiler.positions[par-1]
                pos_end = None
                f_nw = None
                positions_temp = copy.copy(self.compiler.positions)
                p_pos = None
                # p_score = 0
                p_steps = 10

                # getting the list of self.compiler.positions on free branches
                # (intermediate positions)
                inter_positions = Utility.get_intermediate_positions(self.nanowire.nanowire, pos_start)
                if dir is 1:
                    inter_positions = list(reversed(inter_positions))

                # getting the best intermediate self.compiler.positions
                for pos in inter_positions:
                    positions_temp[par-1] = pos
                    i_nw = Utility.update_nanowire(self.nanowire.nanowire, positions_temp)
                    positions_single = utility.get_isolated_particles(positions_temp)

                    msg = "Error while trying to braid {}: {}, {} is an invalid state"\
                            .format(pair, positions_temp, ','.join(voltages))
                    score = validation.validate_nanowire_state(i_nw, positions_temp, utility,
                            positions_single, voltages, self.nanowire, Braiding.TYPE_INTER, msg)
                    steps = Utility.get_steps(self.nanowire.matrix, self.nanowire.vertices,
                            pos_start, pos)
                    p_pos = Utility.comparator(p_pos, p_steps, pos, steps)

                    if p_pos is not None:
                        pos_end = p_pos
                        # intermediate_positions = inter_positions
                        if p_pos==pos:
                            # p_score = score
                            p_steps = steps
                            f_nw = i_nw
                            self.compiler.positions = copy.copy(positions_temp)

                if pos_end is not None and f_nw is not None:
                    # Dijkstra's algorithm gives the shortest path for a particle
                    # from its current position to its final position.
                    path = graph.route(self.nanowire.matrix,
                        self.nanowire.vertices.index(pos_start),
                        self.nanowire.vertices.index(pos_end))
                    block = validation.validate_path_particle(path,
                        self.compiler.positions, self.nanowire.vertices, par)
                    if len(block)==0:
                        self.nanowire.nanowire = copy.deepcopy(f_nw)
                        utility.update_zero_modes(self.nanowire.nanowire)
                        utility.update_voltages(self.compiler.positions,
                            self.nanowire.cutoff_pairs_adj)
                        if validation.validate_path_gates(par, path, self.nanowire.vertices,
                            voltages, self.nanowire.cutoff_pairs_adj,
                            self.nanowire.cutoff_pairs_opp):
                            metrics.update_particle_movements(file_mvmt, pair0, par, path,
                                self.nanowire.vertices, voltages)
                            metrics.update_nanowire_state(file_state, pair0,
                                self.compiler.positions, path,
                                self.nanowire.vertices, par, voltages)

            ########################################################################
            # 2.
            ########################################################################
            par = particles[2]
            pos_start = self.compiler.positions[pair[1]-1]
            pos_end = final_positions[pair[1]-1]
            self.compiler.positions[par-1] = final_positions[par-1]
            path = graph.route(self.nanowire.matrix, self.nanowire.vertices.index(pos_start),
                    self.nanowire.vertices.index(pos_end))
            block = validation.validate_path_particle(path, self.compiler.positions,
                    self.nanowire.vertices, par)
            if len(block)==0:
                f_nw = Utility.update_nanowire(self.nanowire.nanowire, self.compiler.positions)
                self.nanowire.nanowire = copy.deepcopy(f_nw)
                utility.update_zero_modes(self.nanowire.nanowire)
                utility.update_voltages(self.compiler.positions, self.nanowire.cutoff_pairs_adj)
                if validation.validate_path_gates(par, path, self.nanowire.vertices, voltages,
                        self.nanowire.cutoff_pairs_adj, self.nanowire.cutoff_pairs_opp):
                    metrics.update_particle_movements(file_mvmt, pair0, par, path,
                            self.nanowire.vertices, voltages)
                    metrics.update_nanowire_state(file_state, pair0,
                        self.compiler.positions, path, self.nanowire.vertices, par, voltages)

            ########################################################################
            # 3.
            ########################################################################
            p_pair = pair2
            for par in p_pair:
                pos_start = self.compiler.positions[par-1]
                pos_end = final_positions[par-1]

                path = graph.route(self.nanowire.matrix,
                        self.nanowire.vertices.index(pos_start),
                        self.nanowire.vertices.index(pos_end))
                block = validation.validate_path_particle(path,
                        self.compiler.positions, self.nanowire.vertices, par)
                if len(block)==0:
                    self.compiler.positions[par-1] = pos_end
                    f_nw = Utility.update_nanowire(self.nanowire.nanowire, self.compiler.positions)
                    self.nanowire.nanowire = copy.deepcopy(f_nw)
                    utility.update_zero_modes(self.nanowire.nanowire)
                    utility.update_voltages(self.compiler.positions,
                        self.nanowire.cutoff_pairs_adj)
                    if validation.validate_path_gates(par, path,
                        self.nanowire.vertices, voltages,
                        self.nanowire.cutoff_pairs_adj, self.nanowire.cutoff_pairs_opp):
                        metrics.update_particle_movements(file_mvmt, pair0, par, path,
                            self.nanowire.vertices, voltages)
                        metrics.update_nanowire_state(file_state, pair0,
                            self.compiler.positions, path, self.nanowire.vertices, par, voltages)

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

################################################################################
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
