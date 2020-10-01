import sys
import graph
import braid

################################################################################
# File I/O
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

def read_braid_sequence(file):
    data = []
    try:
        file = open(file,'r')
        line = file.readline()
        row = line.split(',')
        tup = (int(row[0].strip()),int(row[1].strip()))
        data.append(tup)
        while line:
            line = file.readline()
            if not line:
                continue;
            row = line.split(',')
            tup = (int(row[0].strip()),int(row[1].strip()))
            data.append(tup)
        file.close()
        return data
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

# Initiating list of opposite positions pair for voltage gates
def initiate_cutoff_voltage_pairs(nanowire):
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

        # pairing positions from opposite cutoff branches
        opposite = []
        temp = get_opposite_cutoff_pairs(c1)
        opposite.extend(temp)
        temp = get_opposite_cutoff_pairs(c0)
        opposite.extend(temp)
        # v11.extend(opposite)
        # v12.extend(opposite)

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

def get_opposite_cutoff_pairs(c):
    opposite = []
    bi = c[0]
    bj = c[1]
    for ti in bi:
        for tj in bj:
            pair = [ti,tj]
            opposite.append(pair)
    return opposite

def get_adjacent_cutoff_pairs(c1,c2,flag):
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

################################################################################
# TQC Nanowire Braiding algorithm
def start():
    try:
        # Preprocessing - Nanowire
        nanowire_structure = read_nanowire_structure(sys.argv[1])
        nanowire_vertex = read_nanowire_vertices(sys.argv[2])
        nanowire_matrix = graph.adjacency_matrix(sys.argv[3])
        graph.validate_matrix(nanowire_matrix)

        # Preprocessing - Braiding sequence
        sequence = read_braid_sequence(sys.argv[4])
        positions = read_particle_positions(sys.argv[5])

        # Braiding on Nanowire
        nanowire = initiate_nanowire(nanowire_structure,positions)
        cutoff_pairs = initiate_cutoff_voltage_pairs(nanowire_structure)
        braid.braid_particles(nanowire,nanowire_vertex,nanowire_matrix,sequence,positions,cutoff_pairs,sys.argv[6],sys.argv[7])
    except IOError as err:
        print(err)
    except SyntaxError as err:
        print(err)

#
start()
