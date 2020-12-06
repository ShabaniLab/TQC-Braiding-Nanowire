"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Nanowire

Objectives:
    1. This is the Nanowire Preprocessing stage
    2. Constructs the Graph Adjacency matrix from the given Nanowire structure
    3. Constructs the list of vertices in the graph
    4. Generates the Nanowire data structure

Class: Nanowire

Methods:
    1. initiate_nanowire
    2. initiate_positions_inner_outer
    3. initiate_cutoff_voltage_pairs_adj
    4. get_adjacent_cutoff_pairs
    5. initiate_cutoff_voltage_pairs_opp
    6. get_opposite_cutoff_pairs

Functions:
    1. read_nanowire_structure_as_branches
    2. read_nanowire_structure_as_intersections
    3. position_vacancies
    4. read_nanowire_vertices
    5. extract_nanowire_vertices
    6. print_nanowire_vertices
    7. initialise_matrix
    8. construct_links
    9. update_matrix
    10. construct_adj_matrix
    11. print_adj_matrix
    12. nanowire_yaml_to_structure_branches
    13. nanowire_yaml_to_structure_intersections
"""

class Nanowire:
    """
    A class to represent the Nanowire
    """
    def __init__(self, matrix, vertex, nanowire):
        self.matrix = matrix
        self.vertices = vertex
        self.nanowire = nanowire
        self.inner = []
        self.outer = []
        self.cutoff_pairs_adj = []
        self.cutoff_pairs_opp = []

    def initiate_nanowire(self, positions):
        """
        Initialize the Nanowire data structure
        """
        for i in range(len(positions)):
            pos = positions[i]
            for intersection in self.nanowire:
                for branch in intersection:
                    for tup in branch:
                        if pos in tup:
                            tup[pos] = (i+1)

    def initiate_positions_inner_outer(self):
        """
        Extracting the list of inner and outer positions
        """
        for intersection in self.nanowire:
            for branch in intersection:
                i = 0
                for tup in branch:
                    if i == 0:
                        po = list(tup.keys())[0]
                        self.outer.append(po)
                        i = 1
                    elif i == 1:
                        pi = list(tup.keys())[0]
                        self.inner.append(pi)
                        i = 0

    def initiate_cutoff_voltage_pairs_adj(self):
        """
        Extract the list of ADJACENT position pairs for every intersection
        when the corresponding voltage gate is shut
        """
        for intersection in self.nanowire:
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
                    if not isinstance(tup, dict):
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

            self.cutoff_pairs_adj.append(v11)
            self.cutoff_pairs_adj.append(v12)

    def initiate_cutoff_voltage_pairs_opp(self):
        """
        Extract the list of OPPOSITE position pairs for every intersection
        when the corresponding voltage gate is shut
        """
        for intersection in self.nanowire:
            o11 = []
            o12 = []
            c1 = []
            c0 = []
            c = 0
            n = len(intersection)/2

            # pairing opposite branches
            for branch in intersection:
                cb = []
                for tup in branch:
                    if not isinstance(tup, dict):
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
            self.cutoff_pairs_opp.append(o11)
            self.cutoff_pairs_opp.append(o12)

#
def read_nanowire_structure_as_branches(file):
    """
    Read the Nanowire config from the given file
    as a list of branches
    """
    data = []
    try:
        file = open(file, 'r')
        line = file.readline()
        if 'x' not in line:
            row = line.split(',')
            row = [e.strip() for e in row]
            data.append(row)
        while line:
            line = file.readline()
            if not line:
                continue
            if 'x' not in line:
                row = line.split(',')
                row = [e.strip() for e in row]
                data.append(row)
        file.close()
        return data
    except IOError:
        raise

def read_nanowire_structure_as_intersections(file):
    """
    Read the Nanowire config from the given file
    as a list of intersections
    """
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

def position_vacancies(arr):
    """
    read_nanowire_structure_as_intersections helper
    """
    nano = []
    for e in arr:
        json = { e.strip(): 0 }
        nano.append(json)
    return nano

#
def read_nanowire_vertices(file):
    """
    Read the list Nanowire vertices from the given input file
    """
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

def extract_nanowire_vertices(structure):
    """
    Extract the list of vertices in the Nanowire (including the intersections)
    """
    it = 1
    vertices = []
    junction = []
    for i in range(len(structure)):
        branch = structure[i]
        junction.extend(branch)
        if len(branch)==1:
            x1 = "{}{}".format('x', it)
            junction.extend([x1])
            vertices.extend(junction)
            junction = []
            it += 1
        elif i == (len(structure)-1):
            vertices.extend(junction)
            junction = []
    return set(vertices)

def print_nanowire_vertices(file, vertices):
    """
    Print the vertices list of vertices
    """
    try:
        fw = open(file, 'w')
        data = list(vertices)
        line = ",".join(data)
        fw.write(line)
        fw.close()
    except IOError:
        raise

#
def initialise_matrix(vertices):
    """
    Initialize the adjacency matrix
    """
    n = len(vertices)
    matrix = []
    for _ in range(n):
        row = [0 for _ in range(n)]
        matrix.append(row)
    return matrix

def construct_links(structure):
    """
    Construct links according to the given structure
    """
    links = []
    danglers = []
    it = 1
    for branch in structure:
        if len(branch)>1:
            links.append(branch)
            danglers.extend([branch[1]])
        else:
            danglers.extend(branch[0])
            intermediate = "{}{}".format('x', it)
            it += 1
            for el in danglers:
                links.append([el, intermediate])
            danglers = []
    if len(danglers)>0:
        for el in danglers:
            links.append([el, intermediate])
    return links

def update_matrix(matrix, vertices, state, node1, node2):
    """
    construct_adj_matrix helper function
    """
    vertices = list(vertices)
    n1 = vertices.index(node1)
    n2 = vertices.index(node2)
    matrix[n1][n2] = state

def construct_adj_matrix(vertices, structure):
    """
    Construct the Nanowire graph adjacency matrix
    """
    state_1 = 1
    matrix = initialise_matrix(vertices)
    links = construct_links(structure)
    for branch in links:
        b1 = branch[0]
        b2 = branch[1]
        update_matrix(matrix, vertices, state_1, b1, b1)
        update_matrix(matrix, vertices, state_1, b1, b2)
        update_matrix(matrix, vertices, state_1, b2, b2)
        update_matrix(matrix, vertices, state_1, b2, b1)
    return matrix

def print_adj_matrix(file, matrix):
    """
    Print the adjacency matrix into the given file
    """
    try:
        fw = open(file, 'a')
        for row in matrix:
            row = [str(e) for e in row]
            line = ",".join(row)
            line += '\n'
            fw.write(line)
        fw.close()
    except IOError:
        raise

#
def get_adjacent_cutoff_pairs(c1, c2, flag):
    """
    initiate_cutoff_voltage_pairs_adj helper
    """
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

def get_opposite_cutoff_pairs(c):
    """
    initiate_cutoff_voltage_pairs_opp helper
    """
    opposite = []
    bi = c[0]
    bj = c[1]
    for ti in bi:
        for tj in bj:
            pair = [ti,tj]
            opposite.append(pair)
    return opposite

def nanowire_yaml_to_structure_branches(structure):
    """convert the yaml object to the acceptable structure"""
    x1 = structure.get('x1')
    x2 = structure.get('x2')
    x1.extend(x2)
    nanowire_structure = []
    for b in x1:
        nanowire_structure.append(b.split(','))
    return nanowire_structure

def nanowire_yaml_to_structure_intersections(structure):
    """convert the yaml object to the acceptable structure"""
    nanowire_structure = []
    x1 = structure.get('x1')
    inter = []
    for b in x1:
        bl = []
        for t in b.split(','):
            g = {}
            g[t] = 0
            bl.append(g)
        inter.append(bl)
    nanowire_structure.append(inter)

    x2 = structure.get('x2')
    inter = []
    for b in x2:
        bl = []
        for t in b.split(','):
            g = {}
            g[t] = 0
            bl.append(g)
        inter.append(bl)
    nanowire_structure.append(inter)

    return nanowire_structure
