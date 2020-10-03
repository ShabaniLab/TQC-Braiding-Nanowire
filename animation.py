import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as anima

################################################################################
# File I/O

# Reading the Nanowire graph matrix
def read_nanowire_matrix(file):
    matrix = []
    try:
        fr = open(file,'r')
        line = fr.readline()
        line = line.strip()
        row = line.split(',')
        values = [int(i) for i in row]
        matrix.append(values)
        while line:
            line = fr.readline()
            if line:
                line = line.strip()
                row = line.split(',')
                values = [int(i) for i in row]
                matrix.append(values)
        fr.close()
        return matrix
    except IOError as err:
        raise

# Reading the Nnaowire graph vertices
def read_nanowire_vertices(file):
    vertices = []
    try:
        fr = open(file,'r')
        line = fr.readline()
        line = line.strip()
        vertices = line.split(',')
        fr.close()
        return vertices
    except IOError as err:
        raise

# Reading Nanowire Node positions
def read_nanowire_positions(file):
    positions = dict()
    try:
        fr = open(file,'r')
        line = fr.readline()
        line = line.strip()
        heading = line.split(',')
        # states.append(heading)
        while line:
            line = fr.readline()
            if line:
                line = line.strip()
                row = line.split(',')

                node = row[0]
                x = int(row[1])
                y = int(row[2])

                positions[node] = np.array([x,y])
        fr.close()
        return positions
    except IOError as err:
        raise

# Reading the Nanowire states
def read_nanowire_state(file):
    states = []
    try:
        fr = open(file,'r')
        line = fr.readline()
        line = line.strip()
        heading = line.split(',')
        # states.append(heading)
        while line:
            line = fr.readline()
            if line:
                line = line.strip()
                row = line.split(',')
                states.append(row)
        fr.close()
        return states
    except IOError as err:
        raise

################################################################################
# Nanowire Graph Network

# Creating Nanowire network graph
def create_network_graph(attributes,matrix):
    G = nx.from_numpy_matrix(matrix)
    G = nx.relabel_nodes(G, lambda x: attributes[x])
    G.edges(data=True)
    return G

# Nanowire network animation
def nanowire_network_graph(G, positions, states):
    H = G.copy()
    BASE_WEIGHT = 1
    index = 0

    for node1, node2, weight in list(G.edges(data=True)):
        if weight["weight"]<BASE_WEIGHT:
            H.remove_edge(node1, node2)
    edges,weights = zip(*nx.get_edge_attributes(H,'weight').items())
    weights = tuple([(1+abs(x))**2 for x in weights])
    nds = list(H.nodes())

    def update(index):
        index += 1
        index = index%len(states)
        particles = states[index][:6]
        empty = list(set(nds)-set(particles))

        # Static nodes
        nx.draw_networkx_nodes(H, positions, node_color='#A2D290', nodelist=empty, node_size=500, alpha=0.8)
        nx.draw_networkx_labels(H, positions, font_size=10, font_family='sans-serif')
        nx.draw_networkx_edges(H, positions, edge_list=edges, style='solid',
                              width=weights, edge_color=weights, edge_cmap=plt.cm.GnBu)

        # Dynamic nodes
        nx.draw_networkx_nodes(H, positions, node_color='#FF8787', nodelist=particles, node_size=500, alpha=0.8)

        title = "Braiding particles"
        ax.set_title(title, fontweight="bold")

    fig, ax = plt.subplots()
    ani = anima.FuncAnimation(fig, update, frames=len(states), interval=1000, fargs=(index))
    ani.save('tqc-cnot.html', writer='imagemagick')
    plt.show()

################################################################################
def start():
    try:
        matrix = read_nanowire_matrix(sys.argv[1])
        vertices = read_nanowire_vertices(sys.argv[2])
        positions = read_nanowire_positions(sys.argv[3])

        states = read_nanowire_state(sys.argv[4])
        graph = create_network_graph(vertices,np.array(matrix))
        nanowire_network_graph(graph,positions,states)
    except IOError as err:
        print(err)

#
start()
