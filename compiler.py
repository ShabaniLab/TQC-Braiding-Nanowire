import sys
import graph
import braid

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

def print_particle_movements(par,pos,vg11,vg12,vg21,vg22):
    line = "{},{},{},{},{},{}".format(par,pos,vg11,vg12,vg21,vg22)
    print(line)

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
        braid.braid_particles(nanowire,nanowire_vertex,nanowire_matrix,sequence,positions,sys.argv[6],sys.argv[7])
    except IOError as err:
        print(err)
    except SyntaxError as err:
        print(err)

#
start()
