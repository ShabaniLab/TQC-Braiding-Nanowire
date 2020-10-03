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
    pos_par = dict()
    pos_volt = dict()
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

                if len(node) is 3 and 'x' in node:
                    x = float(row[1])
                    y = float(row[2])
                    pos_volt[node] = np.array([x,y])
                else:
                    x = int(row[1])
                    y = int(row[2])
                    pos_par[node] = np.array([x,y])
        fr.close()
        return pos_par, pos_volt
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
def nanowire_network_graph(G, pos_par, pos_volt, states):
    BASE_WEIGHT = 1
    index = 0

    # Nanowire network graph - positions
    for node1, node2, weight in list(G.edges(data=True)):
        if (weight["weight"]<BASE_WEIGHT) or (node1==node2):
            G.remove_edge(node1, node2)
    edges_par,weights_par = zip(*nx.get_edge_attributes(G,'weight').items())
    weights_par = [float((1+abs(x))**2) for x in weights_par]
    nds = list(G.nodes())

    # Nanowire network graph - voltage gates
    node_volts = list(pos_volt.keys())
    node_volts.sort()
    G.add_nodes_from(node_volts)
    edges_volt = []
    edges_volt_pairs = []
    for i in range(0,len(node_volts),2):
        edges_volt_pairs.append((node_volts[i],node_volts[i+1]))
        edges_volt.append((node_volts[i],node_volts[i+1],{'weight':BASE_WEIGHT}))
    G.add_edges_from(edges_volt)
    weights_volt = [float((1+abs(BASE_WEIGHT))**2) for x in range(len(edges_volt_pairs))]
    # nodes = voltage_labels()
    # G = nx.relabel_nodes(G, lambda x: nodes[x])

    positions = {**pos_par, **pos_volt}
    edge_color_par_base = plt.cm.Paired
    edge_color_volt_base = plt.cm.GnBu
    edge_color_volt_active = plt.cm.Spectral
    node_color_base = '#A2D290'
    node_color_active = '#FF8787'
    par = 0

    def update(index):
        particles = states[index][:6]
        gates = states[index][6:]
        empty = list(set(nds)-set(particles))
        label_par = {pos:particles.index(pos)+1 for pos in particles}
        label_empty = {pos:pos for pos in empty}
        index += 1
        index = index%len(states)

        ## Nanowire positions
        nx.draw_networkx_edges(G, positions, edgelist=edges_par, style='solid', width=weights_par, edge_color=weights_par, edge_cmap=edge_color_par_base)
        nx.draw_networkx_nodes(G, positions, node_color=node_color_base, nodelist=empty, node_size=500, alpha=0.8)
        nx.draw_networkx_nodes(G, positions, node_color=node_color_active, nodelist=particles, node_size=500, alpha=0.8)

        ## Nanowire Voltage gates
        edges_volt_open = []
        edges_volt_shut = []
        label_gates = dict()
        for i in range(len(gates)):
            key,lbl = get_voltage_gate_labels(i)
            if gates[i] is 'O':
                edges_volt_open.append(edges_volt_pairs[i])
            else:
                edges_volt_shut.append(edges_volt_pairs[i])
                label_gates[key] = lbl
        weights_volt_open = weights_volt[:len(edges_volt_open)]
        weights_volt_shut = weights_volt[:len(edges_volt_shut)]
        nx.draw_networkx_edges(G, positions, edgelist=edges_volt_open, style='solid', width=weights_volt_open, edge_color=weights_volt_open, edge_cmap=edge_color_volt_base)
        nx.draw_networkx_edges(G, positions, edgelist=edges_volt_shut, style='solid', width=weights_volt_shut, edge_color=weights_volt_shut, edge_cmap=edge_color_volt_active)

        labels = {**label_empty, **label_par, **label_gates}
        nx.draw_networkx_labels(G,positions, labels=labels, font_size=10, font_family='sans-serif', ax=ax)
        # nx.relabel_nodes(G, lambda x: labels[x])

        title = "TQC Braiding Nanowire - 2 Qubit CNOT"
        ax.set_title(title, fontweight="bold")

    fig, ax = plt.subplots()
    ani = anima.FuncAnimation(fig, update, frames=len(states), interval=750, fargs=(index))
    ani.save('tqc-cnot.html', writer='imagemagick')
    plt.show()

# returns voltage node labels
def get_voltage_gate_labels(flag):
    key = None
    gate = None
    if flag is 0:
        key = 'x11'
        gate = 'x11'
    elif flag is 1:
        key = 'x13'
        gate = 'x12'
    elif flag is 2:
        key = 'x21'
        gate = 'x21'
    elif flag is 3:
        key = 'x23'
        gate = 'x22'
    return key, gate

# adds voltage node labels
def voltage_labels():
    nodes = ['x11','x12','x13','x14','x21','x22','x23','x24']
    return nodes

################################################################################
def start():
    try:
        matrix = read_nanowire_matrix(sys.argv[1])
        vertices = read_nanowire_vertices(sys.argv[2])
        pos_par, pos_volt = read_nanowire_positions(sys.argv[3])

        states = read_nanowire_state(sys.argv[4])
        graph = create_network_graph(vertices,np.array(matrix))
        nanowire_network_graph(graph,pos_par,pos_volt,states)
    except IOError as err:
        print(err)

#
start()