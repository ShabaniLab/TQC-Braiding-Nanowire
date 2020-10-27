import sys
import graph
import random

################################################################################
# 1. Read Final and Initial positions
def read_positions(file):
    positions_initial = []
    positions_final = []
    try:
        fr = open(file,'r')
        line = fr.readline().strip()
        positions_initial = line.split(',')

        line = fr.readline().strip()
        positions_final = line.split(',')
        return positions_initial, positions_final
    except IOError as err:
        print(err)

# 2. Read Fusion Rules
def read_fusion_rules(file):
    rules = {}
    try:
        fr = open(file,'r')
        line = fr.readline().strip()
        while line:
            line = fr.readline().strip()
            row = line.split(',')
            if len(row) < 3:
                continue
            key = "{}-{}".format(row[0],row[1])
            val = row[2]
            if key in rules.keys():
                rules[key].append(val)
            else:
                rules[key] = [val]
        fr.close()
        return rules
    except IOError as err:
        raise

# 3. Read Fusion Channels
def read_fusion_channels(file):
    channels = {}
    try:
        fr = open(file,'r')
        line = fr.readline().strip()
        while line:
            line = fr.readline().strip()
            row = line.split(',')
            if len(row) < 3:
                continue
            key = "{}-{}".format(row[1], row[2])
            val = row[0]
            channels[key] = val
        fr.close()
        return channels
    except IOError as err:
        raise

# 4. Read vertices
def read_nanowire_vertices(file):
    data = []
    try:
        fr = open(file,'r')
        line = fr.readline().strip()
        row = line.split(',')
        row = [e.strip() for e in row]
        data = row
        fr.close()
        return data
    except IOError:
        raise

# 5. Extract zero mode pairs from the given matrix, vertices list and final positions
def extract_pairs(positions, file1, file2):
    matrix = graph.adjacency_matrix(file1)
    vertices = read_nanowire_vertices(file2)
    pairs = {}
    for pos1 in positions:
        id1 = positions.index(pos1)+1
        if id1 in pairs:
            continue
        p1 = vertices.index(pos1)
        for pos2 in positions:
            id2 = positions.index(pos2)+1
            if id2 in pairs:
                continue
            p2 = vertices.index(pos2)
            if pos1 != pos2 and (matrix[p1][p2] == 1 or matrix[p2][p1] == 1):
                pairs[id1] = id2
    return pairs

# 6. Perform Measurement
def measure_particles(pairs,rules,channel):
    channels = []
    par_pair = 'o-o'
    outcomes = rules[par_pair]
    for key in pairs.keys():
        n = round(random.random()*(len(outcomes)-1))
        channels.append(outcomes[n])
    chl = "-".join(channels)
    qb = None
    if chl in channel:
        qb = channel[chl]
    return tuple(channels), qb

# 7. Print it into a file
def save_measurements(chl, qb):
    if qb:
        line = "{},{},{}".format(chl[0],chl[1],qb)
        print(line)

# 8. Start
def start():
    try:
        positions_initial, positions_final = read_positions(sys.argv[1])
        rules = read_fusion_rules(sys.argv[2])
        channels = read_fusion_channels(sys.argv[3])
        pairs = extract_pairs(positions_final, sys.argv[4], sys.argv[5])

        chl, qb = measure_particles(pairs,rules,channels)
        save_measurements(chl, qb)
    except IOError as err:
        print(err)

start()
