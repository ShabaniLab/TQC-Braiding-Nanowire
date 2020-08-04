import sys

# File I/O
def position_vacancies(arr):
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
        if 'x' not in line:
            row = line.split(',')
            data.append(position_vacancies(row))
        while line:
            line = file.readline()
            if not line:
                continue;
            if 'x' not in line:
                row = line.split(',')
                data.append(position_vacancies(row))
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

def print_op(pa,p1,p2,vg11,vg12,vg21,vg22):
    line = "{},{},{},{},{},{},{}".format(pa,p1,p2,vg11,vg12,vg21,vg22)
    print(line)

#
def initiate_nanowire(nanowire,positions):
    for i in range(len(positions)):
        pos = positions[i]
        for branch in nanowire:
            for tup in branch:
                if list(tup.keys())[0]==pos:
                    tup[pos] = i
    return nanowire

def move_particles(nanowire,sequence,positions):
    for tup in sequence:
        par1 = tup[0]-1
        par2 = tup[1]-1
        pos1 = positions[pa1]
        pos2 = positions[pa2]

#
def start():
    try:
        nanowire_str = read_nanowire_structure(sys.argv[1])
        positions = read_particle_positions(sys.argv[4])
        sequence = read_braid_sequence(sys.argv[5])

        nanowire = initiate_nanowire(nanowire_str,positions)
        print(nanowire)
        # move_particles(nanowire,sequence,positions)
    except IOError as err:
        print(err)

#
start()
