"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Utility

Objectives:
    1. TQC Braiding Nanowire Algorithm - Utility functions

Class: Utility

Methods:
    @self
    1. reset_variables
    2. update_zero_modes
    3. refresh_zero_modes
    4. get_isolated_particles
    5. update_voltages
    6. check_particle_pair_zmode
    7. check_pair_zmode
    8. check_particle_zmode
    9. get_positions_from_braids

    @classmethod
    9. get_par_braid_pos
    10. update_par_braid_pos
    11. get_final_positions
    12. update_nanowire
    13. get_steps
    14. comparator
    15. get_intermediate_positions
    16. get_intersection
    17. get_empty_positions
    18. get_other_particle
    19. get_permutations
"""

from itertools import permutations
import copy
from . import graph
from . import exception

class Utility():
    """
    A class of Utility functions
    """

    VOLTAGE_OPEN = 'O'
    VOLTAGE_SHUT = 'S'
    gate_index = -1
    gate_flag = False
    gate_flag_ex = False

    def __init__(self):
        self.voltages = ['O', 'O', 'O', 'O']
        self.zmodes_old = []
        self.zmodes_new = []
        self.positions_old = []

    def reset_variables(self, positions_new):
        """
        Resets [positions_old, gate_flag] variables
        """
        self.positions_old = copy.copy(positions_new)
        if Utility.gate_flag:
            Utility.gate_index = -1
            Utility.gate_flag = False
            Utility.gate_flag_ex = False

    def update_zero_modes(self, nanowire):
        """
        A list of Zero mode pairs DURING a braiding op
        """
        zmodes = []
        # if the pair is on same branch
        for intersection in nanowire:
            for branch in intersection:
                pair = []
                for tup in branch:
                    if not isinstance(tup, dict):
                        continue
                    par = list(tup.values())[0]
                    if par is not 0:
                        pair.append(par)
                if len(pair)==2:
                    zmodes.append(pair)

        if len(self.zmodes_new) is 0:
            self.zmodes_new = zmodes

        for el in self.zmodes_new:
            if el not in self.zmodes_old:
                self.zmodes_old.append(el)
        self.zmodes_new = zmodes

    def refresh_zero_modes(self):
        """
        A list of Zero mode pairs AFTER a braiding op
        """
        self.zmodes_old = self.zmodes_new
        self.zmodes_new = []

    def get_isolated_particles(self, positions):
        """
        Get Isolated particles which are NOT part of any zero mode
        (in the middle of a braiding operation)
        """
        positions_paired = []
        particles_paired = []
        for zm in self.zmodes_new:
            particles_paired.extend(zm)
        positions_paired = [positions[par-1] for par in particles_paired]
        return list(set(positions)-set(positions_paired))

    def update_voltages(self, positions, cutoff_pairs):
        """
        Get Voltage Gate Changes if braiding involves particles from different zero modes.
        """
        positions_single = self.get_isolated_particles(positions)
        if len(positions_single)>1:
            perm = Utility.get_permutations(positions_single, 2)
            for i in range(len(cutoff_pairs)):
                pairs = cutoff_pairs[i]
                val = False
                for pair in perm:
                    if (pair in pairs or list(reversed(pair)) in pairs) and\
                        (not self.check_particle_pair_zmode(pair, positions, positions_single, i)):
                        val = True
                        break
                if val:
                    self.voltages[i] = Utility.VOLTAGE_SHUT
                else:
                    self.voltages[i] = Utility.VOLTAGE_OPEN

            if Utility.gate_flag is True and Utility.gate_flag_ex is False:
                inter = len(self.voltages)/2
                Utility.gate_index += 1
                offset = 0
                if Utility.gate_index>=inter:
                    offset = inter
                self.voltages[int(Utility.gate_index%inter+offset)] = Utility.VOLTAGE_SHUT
                Utility.gate_flag_ex = True

    def check_particle_pair_zmode(self, pair_pos, positions, positions_single, i):
        """
        Checks if the particle or pair is a zero mode
        """
        if self.check_pair_zmode(pair_pos, positions):
            return True
        return self.check_particle_zmode(pair_pos, positions, positions_single, i)

    def check_pair_zmode(self, pair_pos, positions):
        """
        Checks if the pair is a zero mode
        """
        p1 = positions.index(pair_pos[0])+1
        p2 = positions.index(pair_pos[1])+1
        pair = [p1, p2]
        val = False

        # Checks if the pair is a zero mode
        if pair in self.zmodes_old or list(reversed(pair)) in self.zmodes_old:
            val = True
        elif pair in self.zmodes_new or list(reversed(pair)) in self.zmodes_new:
            val = True
        return val

    def check_particle_zmode(self, pair_pos, positions, positions_single, i):
        """
        Checks if at least 1 particle in the pair is part of a zero mode
        """
        p1 = positions.index(pair_pos[0])+1
        p2 = positions.index(pair_pos[1])+1
        val1 = val2 = False

        for zmode in self.zmodes_new:
            if p1 in zmode:
                val1 = True
                break

        for zmode in self.zmodes_new:
            if p2 in zmode:
                val2 = True
                break

        if val1 is True or val2 is True:
            return True
        if val1 is False and val2 is False and len(positions_single) is 2:
            if Utility.gate_flag is False and i is not None:
                Utility.gate_index = i
                Utility.gate_flag = True
            return True
        return False

    def get_positions_from_braids(self, nanowire, braid_positions):
        """
        Returns the position on the nanowire from the braiding positions
        """
        positions = []
        for braid_par in braid_positions:
            for intersection in nanowire:
                for branch in intersection:
                    for tup in branch:
                        if not isinstance(tup, dict):
                            continue
                        par = list(tup.values())[0]
                        pos = list(tup.keys())[0]
                        if par == int(braid_par):
                            positions.append(pos)
        return positions

    @classmethod
    def get_par_braid_pos(cls, n):
        """
        Particle locations in the braiding pattern
        """
        line_pos = [(i+1) for i in range(n)]
        return line_pos

    @classmethod
    def update_par_braid_pos(cls, positions, pair):
        """
        Update Particle locations in the braiding pattern
        """
        pos1 = pair[0]-1
        pos2 = pair[1]-1
        positions[pos1], positions[pos2] = positions[pos2], positions[pos1]
        return positions

    @classmethod
    def get_final_positions(cls, positions, pair):
        """
        Retrieves the expected final (swapped) positions of the particles to be braided
        """
        final_positions = copy.copy(positions)
        p1 = pair[0]-1
        p2 = pair[1]-1
        temp = final_positions[p1]
        final_positions[p1] = final_positions[p2]
        final_positions[p2] = temp
        return final_positions

    @classmethod
    def update_nanowire(cls, nanowire, positions):
        """
        Update Nanowire with new Positions
        """
        i_nw = copy.deepcopy(nanowire)
        for intersection in i_nw:
            for branch in intersection:
                for tup in branch:
                    if not isinstance(tup, dict):
                        continue
                    pos = list(tup.keys())[0]
                    if pos in positions:
                        i = positions.index(pos)
                        tup[pos] = (i+1)
                    else:
                        tup[pos] = 0
        return i_nw

    @classmethod
    def get_steps(cls, matrix, vertex, pos1, pos2):
        """
        Returns # steps from initial to final position
        """
        p1 = vertex.index(pos1)
        p2 = vertex.index(pos2)
        path = graph.route(matrix, p1, p2)
        return len(path)-1

    @classmethod
    def comparator(cls, pos1, steps1, pos2, steps2):
        """
        Ranks the positions based on Validity Score and # steps
        """
        pos = pos1
        if steps2<steps1:
            pos = pos2
        return pos

    @classmethod
    def get_intermediate_positions(cls, nanowire, pos):
        """
        Retrieves the potential Intermediate positions of the particles to be braided
        """
        try:
            intersection = Utility.get_intersection(nanowire, pos)
            empty_positions = Utility.get_empty_positions(nanowire, intersection)
            return empty_positions
        except exception.NoEmptyPositionException:
            raise

    @classmethod
    def get_intersection(cls, nanowire, pos):
        """
        Retrieves the intersection of a position in the nanowire structure
        """
        res = None
        flag = 1
        if isinstance(pos, int):
            flag = 2
        for intersection in nanowire:
            for branch in intersection:
                for tup in branch:
                    if not isinstance(tup, dict):
                        continue
                    if flag is 1:
                        if pos in tup:
                            res = intersection
                            break
                    elif flag is 2:
                        if pos in tup.values():
                            res = intersection
                            break
        return res

    @classmethod
    def get_empty_positions(cls, nanowire, intersection):
        """
        Retrieves the empty positions on adjacent empty branches
        """
        positions = []
        temp = []
        for branch in intersection:
            val = True
            for tup in branch:
                if not isinstance(tup, dict):
                    continue
                if list(tup.values())[0] != 0:
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
            msg = "No Empty Branches on Intersection {} to continue this braiding"\
                    .format((nanowire.index(intersection)+1))
            raise exception.NoEmptyPositionException(msg)
        return positions

    @classmethod
    def get_other_particle(cls, par, intersection):
        """
        Get the other (3rd) particle in the intersection to be moved
        """
        res = None
        for branch in intersection:
            flag = False
            for tup in branch:
                if not isinstance(tup, dict):
                    continue
                val = list(tup.values())[0]
                if val is par:
                    flag = True
                if val is not par and flag:
                    res = val
                    break
        return res

    @classmethod
    def get_permutations(cls, array, n):
        """
        Returns list permutations of size n for an array
        """
        perm0 = permutations(array, n)
        perm = []
        for p in perm0:
            pair = list(p)
            if pair in perm or list(reversed(pair)) in perm:
                continue
            perm.append(pair)
        return perm
