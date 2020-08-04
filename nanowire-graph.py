import sys

intersection = 'x'
state_1 = 1

# Reading the Nanowire Structure
def read_nanowire_structure(file):
    data = []
    try:
        file = open(file,'r')
        line = file.readline()
        if 'x' not in line:
            row = line.split(',')
            row = [e.strip() for e in row]
            data.append(row)
        while line:
            line = file.readline()
            if not line:
                continue;
            if 'x' not in line:
                row = line.split(',')
                row = [e.strip() for e in row]
                data.append(row)
        file.close()
        return data
    except IOError:
        raise

# Nanowire Graph Vertices
def extract_nanowire_vertices(structure):
    it = 1
    vertices = []
    junction = []
    for i in range(len(structure)):
        branch = structure[i]
        junction.extend(branch)
        if len(branch)==1:
            x1 = "{}{}".format(intersection,it)
            junction.extend([x1])
            vertices.extend(junction)
            junction = []
            it += 1
        elif i==(len(structure)-1):
            vertices.extend(junction)
            junction = []
    return set(vertices)

def print_nanowire_vertices(file,vertices):
    try:
        fw = open(file,'w')
        data = list(vertices)
        line = ",".join(data)
        fw.write(line)
        fw.close()
    except IOError:
        raise

# Nanowire Graph Adjacency matrix
def initialise_matrix(vertices):
    n = len(vertices)
    matrix = []
    for i in range(n):
        row = [0 for j in range(n)]
        matrix.append(row)
    return matrix

def construct_links(vertices,structure):
    links = []
    danglers = []
    it = 1
    for branch in structure:
        if len(branch)>1:
            links.append(branch)
            danglers.extend([branch[1]])
        else:
            danglers.extend(branch[0])
            intermediate = "{}{}".format(intersection,it)
            it += 1
            for el in danglers:
                links.append([el,intermediate])
            danglers = []
    if len(danglers)>0:
        for el in danglers:
            links.append([el,intermediate])
    return links

def update_matrix(matrix,vertices,state,node1,node2):
    vertices = list(vertices)
    n1 = vertices.index(node1)
    n2 = vertices.index(node2)
    matrix[n1][n2] = state

def construct_adj_matrix(vertices,structure):
    matrix = initialise_matrix(vertices)
    links = construct_links(vertices,structure)
    for branch in links:
        b1 = branch[0]
        b2 = branch[1]
        update_matrix(matrix,vertices,state_1,b1,b1)
        update_matrix(matrix,vertices,state_1,b1,b2)
        update_matrix(matrix,vertices,state_1,b2,b2)
        update_matrix(matrix,vertices,state_1,b2,b1)
    return matrix

def print_adj_matrix(file,matrix):
    try:
        fw = open(file,'a')
        for row in matrix:
            row = [str(e) for e in row]
            line = ",".join(row)
            line += '\n'
            fw.write(line)
        fw.close()
    except IOError:
        raise

#
def start():
    try:
        nanowire_structure = read_nanowire_structure(sys.argv[1])
        nanowire_vertices = extract_nanowire_vertices(nanowire_structure)
        print_nanowire_vertices(sys.argv[2],nanowire_vertices)
        nanowire_adj_matrix = construct_adj_matrix(nanowire_vertices,nanowire_structure)
        print_adj_matrix(sys.argv[3],nanowire_adj_matrix)
    except IOError as err:
        print(err)

#
start()
