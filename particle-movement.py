import sys

# File I/O
def nanowire_positions(arr):
    nano = []
    for e in arr:
        json = { e.strip(): 0 }
        nano.append(json)
    return nano

def read_nanowire_structure(file):
    data = []
    try:
        file = open(file,'r')
        line = file.readline()
        row = line.split(',')
        data.append(nanowire_positions(row))
        while line:
            line = file.readline()
            if not line:
                continue;
            row = line.split(',')
            data.append(nanowire_positions(row))
        file.close()
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
        row = [int(e) for e in row]
        data.append(row)
        while line:
            line = file.readline()
            if not line:
                continue;
            row = line.split(',')
            row = [int(e) for e in row]
            data.append(row)
        file.close()
        return data
    except IOError:
        raise

def print_op(pa,p1,p2,v1,v2):
    line = "{},{},{},{},{}".format(pa,p1,p2,v1,v2)
    print(line)

#
def initiate_nanowire(nanowire,positions):
    for pos in positions:
        for branch in nanowire:
            for tup in branch:
                if list(tup.keys())[0]==pos:
                    tup[pos] = 1
    return nanowire

def move_particles(nanowire,sequence,positions):
    ;

#
def start():
    try:
        nanowire = read_nanowire_structure(sys.argv[1])
        positions = read_particle_positions(sys.argv[2])
        sequence = read_braid_sequence(sys.argv[3])

        nanowire = initiate_nanowire(nanowire,positions)
        move_particles(nanowire,sequence,positions)
    except IOError as err:
        print(err)

#
start()
