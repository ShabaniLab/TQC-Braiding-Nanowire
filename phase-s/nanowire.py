#    Copyright (C) 2020
#    Arahant Ashok Kumar
#    All rights reserved.
#    BSD license.
#
# Author:  Arahant Ashok Kumar (aak700@nyu.edu)

import graph

# Base class for Nanowire structure
class Nanowire(object):

    def __init__(self,nanowire):
        ## Functions
        # File I/O
        self.position_vacancies = self.position_vacancies
        self.read_nanowire_structure = self.read_nanowire_structure
        self.read_nanowire_vertices = self.read_nanowire_vertices
        self.read_particle_positions = self.read_particle_positions

        # Initialising the Nanowire
        self.initiate_nanowire = self.initiate_nanowire
        self.initiate_cutoff_voltage_pairs_adj = self.initiate_cutoff_voltage_pairs_adj
        self.initiate_cutoff_voltage_pairs_opp = self.initiate_cutoff_voltage_pairs_opp
        self.get_cutoff_pairs_adj = self.get_cutoff_pairs_adj
        self.get_cutoff_pairs_opp = self.get_cutoff_pairs_opp

        # Utility functions
        self.update_nanowire = self.update_nanowire
        self.update_zero_modes = self.update_zero_modes

        ## Attributes
        self.nanowire = nanowire                   # a nested array

    ################################################################################
    # Reading Nanowire data from File I/O

    def position_vacancies(arr):
        nano = []
        for e in arr:
            json = { e.strip(): 0 }
            nano.append(json)
        return nano

    def read_nanowire_structure(file):
        data = []
        intersection = []
        try:
            file = open(file,'r')
            line = file.readline()
            if 'x' not in line:
                row = line.split(',')
                branch = position_vacancies(row)
                intersection.append(branch)
            while line:
                line = file.readline()
                if not line:
                    continue
                if 'x' not in line:
                    row = line.split(',')
                    branch = position_vacancies(row)
                    intersection.append(branch)
                else:
                    data.append(intersection)
                    intersection = []
            file.close()
            return data
        except IOError:
            raise

    def read_nanowire_vertices(file):
        data = []
        try:
            fr = open(file,'r')
            line = fr.readline()
            row = line.split(',')
            row = [e.strip() for e in row]
            data = row
            fr.close()
            return data
        except IOError:
            raise

    def read_particle_positions(file):
        try:
            fr = open(file,'r')
            line = fr.readline()
            positions = line.split(',')
            positions = [e.strip() for e in positions]
            fr.close()
            return positions
        except IOError:
            raise

    ################################################################################

    # Initiating nanowire with given particle positions
    def initiate_nanowire(nanowire,positions):
        for i in range(len(positions)):
            pos = positions[i]
            for intersection in nanowire:
                for branch in intersection:
                    for tup in branch:
                        if list(tup.keys())[0]==pos:
                            tup[pos] = (i+1)
        return nanowire

    # Initiating list of ADJACENT positions pair for voltage gates
    def initiate_cutoff_voltage_pairs_adj(nanowire):
        cutoff_pairs = []
        for intersection in nanowire:
            v11 = []
            v12 = []
            c1 = []
            c0 = []
            c = 0
            n = len(intersection)/2
            flag = 1

            # pairing opposite branches
            for branch in intersection:
                cb = []
                for tup in branch:
                    if type(tup) is not dict:
                        continue
                    pos = list(tup.keys())[0]
                    cb.append(pos)

                c += 1
                c = c%n
                if c==1:
                    c1.append(cb)
                elif c==0:
                    c0.append(cb)

            # pairing positions from adjacent cutoff branches
            flag = 1
            temp = get_adjacent_cutoff_pairs(c1,c0,flag)
            v11.extend(temp)
            flag = 2
            temp = get_adjacent_cutoff_pairs(c0,c1,flag)
            v12.extend(temp)

            cutoff_pairs.append(v11)
            cutoff_pairs.append(v12)

        return cutoff_pairs

    # Initiating list of OPPOSITE positions pair for voltage gates
    def initiate_cutoff_voltage_pairs_opp(nanowire):
        cutoff_pairs_opp = []
        for intersection in nanowire:
            o11 = []
            o12 = []
            c1 = []
            c0 = []
            c = 0
            n = len(intersection)/2
            flag = 1

            # pairing opposite branches
            for branch in intersection:
                cb = []
                for tup in branch:
                    if type(tup) is not dict:
                        continue
                    pos = list(tup.keys())[0]
                    cb.append(pos)

                c += 1
                c = c%n
                if c==1:
                    c1.append(cb)
                elif c==0:
                    c0.append(cb)

            # pairing positions from opposite cutoff branches
            opposite = []
            opposite.extend(get_opposite_cutoff_pairs(c1))
            opposite.extend(get_opposite_cutoff_pairs(c0))
            o11.extend(opposite)
            o12.extend(opposite)
            cutoff_pairs_opp.append(o11)
            cutoff_pairs_opp.append(o12)

        return cutoff_pairs_opp

    def get_cutoff_pairs_opp(c):
        opposite = []
        bi = c[0]
        bj = c[1]
        for ti in bi:
            for tj in bj:
                pair = [ti,tj]
                opposite.append(pair)
        return opposite

    def get_cutoff_pairs_adj(c1,c2,flag):
        adjacent = []

        bi = c1[0]
        if flag is 1:
            bj = c2[1]
        elif flag is 2:
            bj = c2[0]

        for ti in bi:
            for tj in bj:
                pair = [ti,tj]
                adjacent.append(pair)

        bi = c1[1]
        if flag is 1:
            bj = c2[0]
        elif flag is 2:
            bj = c2[1]

        for ti in bi:
            for tj in bj:
                pair = [ti,tj]
                adjacent.append(pair)

        return adjacent

    def initiate_attributes():
        self.intersections = self.intersections         # array of intersection id
        self.branches = self.branches                   # array of branc id
        self.positions = self.positions                 # array of position id
        self.particles = self.particles                 # array of particle id
        self.empty_branches = self.empty_branches       # array of empty branch id
        self.empty_positions = self.empty_positions     # array of position id

    ################################################################################
    # Utility functions

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

    # Retrieves the empty positions on adjacent empty branches
    def get_empty_positions(nanowire,intersection):
        positions = []
        temp = []
        for branch in nanowire[i]:
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
