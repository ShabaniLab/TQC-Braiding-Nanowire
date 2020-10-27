"""
Animation - Braiding and Nanowire movements
"""

import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as anima

labels_old = None

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

# Reading Braid particle positions
def read_braid_par_pos(file):
    sequence = []
    braid_pos = []
    try:
        fr = open(file,'r')
        line = fr.readline()
        line = line.strip()
        heading = line.split(',')
        while line:
            line = fr.readline()
            if line:
                line = line.strip()
                row = line.split(',')
                sequence.append(row[:2])
                sequence.append(row[:2])
                braid_pos.append(row[2:])
                braid_pos.append(row[2:])
        fr.close()
        return sequence,braid_pos
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
# Nanowire Graph Network animation

# Creating Nanowire network graph
def create_network_graph(attributes,matrix):
    G = nx.from_numpy_matrix(matrix)
    G = nx.relabel_nodes(G, lambda x: attributes[x])
    G.edges(data=True)
    return G

# Nanowire network animation
def nanowire_network_graph(G, pos_par, pos_volt, states, seq):
    BASE_WEIGHT = 1
    index = 0
    sequence = [seq[0]]
    for el in seq:
        if el not in sequence:
            sequence.append(el)
    n_seq = len(sequence)

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

    positions = {**pos_par, **pos_volt}
    edge_color_par_base = plt.cm.Paired
    edge_color_par_active = plt.cm.Pastel1
    edge_color_volt_base = plt.cm.GnBu
    edge_color_volt_active = plt.cm.Spectral
    node_color_base = '#A2D290'
    node_color_active = '#CC6699'
    node_color_base_volt = "#DDFFCC"
    node_color_active_volt = '#990000'
    par = 0

    def update(index):
        i1 = 2
        par_no = 4
        pair = states[index][:i1]
        particles = states[index][i1:i1+par_no]
        gates = states[index][i1+par_no:]
        empty = list(set(nds)-set(particles))
        label_par = {pos:particles.index(pos)+1 for pos in particles}
        label_empty = {pos:pos for pos in empty}
        par = None
        pos1 = None
        pos2 = None
        title = None
        if index is 0:
            title = "TQC Braiding Nanowire - 1 Qubit Pauli-X"
        index += 1
        index = index%len(states)

        ## Nanowire positions
        nx.draw_networkx_edges(G, positions, edgelist=edges_par, style='solid', width=weights_par, edge_color=weights_par, edge_cmap=edge_color_par_base)
        nx.draw_networkx_nodes(G, positions, node_color=node_color_base, nodelist=empty, node_size=500, alpha=0.8)
        nx.draw_networkx_nodes(G, positions, node_color=node_color_active, nodelist=particles, node_size=500, alpha=0.8)
        nx.draw_networkx_labels(G,positions, font_size=10, font_family='sans-serif', ax=ax)

        ## Nanowire Voltage gates
        edges_volt_open = []
        edges_volt_shut = []
        nodes_volt_open = []
        nodes_volt_shut = []
        label_gates = dict()
        for i in range(len(gates)):
            key,lbl = get_voltage_gate_labels(i)
            if gates[i] is 'O':
                edges_volt_open.append(edges_volt_pairs[i])
                label_gates[key] = ''
            else:
                edges_volt_shut.append(edges_volt_pairs[i])
                label_gates[key] = lbl
        for ed in edges_volt_open:
            nodes_volt_open.extend(list(ed))
        for ed in edges_volt_shut:
            nodes_volt_shut.extend(list(ed))
        weights_volt_open = weights_volt[:len(edges_volt_open)]
        weights_volt_shut = weights_volt[:len(edges_volt_shut)]
        nx.draw_networkx_nodes(G, positions, node_color=node_color_base_volt, nodelist=nodes_volt_open, node_size=200, alpha=0.5)
        nx.draw_networkx_nodes(G, positions, node_color=node_color_active_volt, nodelist=nodes_volt_shut, node_size=200, alpha=0.5)
        nx.draw_networkx_edges(G, positions, edgelist=edges_volt_open, style='solid', width=weights_volt_open, edge_color=weights_volt_open, edge_cmap=edge_color_volt_base)
        nx.draw_networkx_edges(G, positions, edgelist=edges_volt_shut, style='solid', width=weights_volt_shut, edge_color=weights_volt_shut, edge_cmap=edge_color_volt_active)

        # relabling nodes
        labels = {**label_empty, **label_par, **label_gates}
        mapping = dict()
        global labels_old
        if labels_old is None:
            labels_old = labels
            mapping = labels
            for n in G.nodes():
                if n in mapping.keys() and n is mapping[n]:
                    mapping.pop(n)
        else:
            for k in labels_old.keys():
                key = labels_old[k]
                val = labels[k]
                if key is '' or val is '':
                    continue
                if key is not val:
                    mapping[key] = val
            labels_old = labels
        if mapping:
            nx.relabel_nodes(G, mapping, copy=True)
            if len(mapping.keys()) is 2:
                for k in mapping.keys():
                    if isinstance(k,int):
                        par = k
                    if isinstance(k,str):
                        pos2 = k
                    if isinstance(mapping[k],str):
                        pos1 = mapping[k]

        # Updating Braid table
        if par is not None:
            row = sequence.index(pair)
            braid_table[(row+1, 0)].get_text().set_color('red')
            braid_table[(row+1, 1)].get_text().set_color('red')
            braid_table[(row+1, 0)].get_text().set_fontweight('bold')
            braid_table[(row+1, 1)].get_text().set_fontweight('bold')
            if row>0:
                braid_table[(row, 0)].get_text().set_color('black')
                braid_table[(row, 1)].get_text().set_color('black')
                braid_table[(row, 0)].get_text().set_fontweight('regular')
                braid_table[(row, 1)].get_text().set_fontweight('regular')

        # Output
        if pair is not None:
            title = "Braiding particles ({},{})".format(int(pair[0]),int(pair[1]))
            if par is not None and pos1 is not None and pos2 is not None:
                title = "{}\nMoving ({}) from {} to {}".format(title,par,pos1,pos2)
        for i in range(len(gates)):
            volt = gates[i]
            if volt is 'S':
                key,gate = get_voltage_gate_labels(i)
                gt = "Voltage Gate {} is SHUT".format(gate)
                if par is None:
                    title = "{}\n{}".format(title,gt)
                else:
                    title = "{}: {}".format(title,gt)
                break

        # display
        if pos1 is not None and pos2 is not None:
            e = [(pos1,pos2,{'weight':BASE_WEIGHT})]
            w = weights_volt[:len(e)]
            nx.draw_networkx_edges(G, positions, edgelist=e, style='solid', width=w, edge_color=w, edge_cmap=edge_color_par_active)
        if title is not None:
            print(title)
            ax.set_title(title,fontweight="bold")

    fig = plt.figure(figsize=(12, 6))
    ax2 = fig.add_subplot(122)
    ax = fig.add_subplot(121)
    heading = ("Particle 1", "Particle 2")
    braid_table = ax2.table(cellText=sequence,colLabels=heading,loc='center',cellLoc='center')
    braid_table.scale(1,2)
    # braid_table.set_fontsize(16)
    for i in range(n_seq):
        for j in range(len(sequence[i])):
            if i==0:
                braid_table[(i, j)].get_text().set_fontweight('bold')
            braid_table[(i+1, j)].get_text().set_color('gray')
    ax2.set_title("Braid table",fontweight="bold")
    ax2.axis('off')

    ani = anima.FuncAnimation(fig, update, frames=len(states), interval=500, fargs=(index))
    ani.save('pauli-x-nanowire-table.gif', writer='imagemagick')
    # plt.show()

# returns voltage node labels
def get_voltage_gate_labels(flag):
    key = None
    gate = None
    if flag is 0:
        key = 'x11'
        gate = 'Vg11'
    elif flag is 1:
        key = 'x13'
        gate = 'Vg12'
    elif flag is 2:
        key = 'x21'
        gate = 'Vg21'
    elif flag is 3:
        key = 'x23'
        gate = 'Vg22'
    return key, gate

################################################################################
# Braid pattern animation

def braid_particle_positions(sequence,positions):
    index = 0
    seq = [sequence[0]]
    for el in sequence:
        if el not in seq:
            seq.append(el)
    n_seq = len(seq)
    par_n = len(positions[0])
    pos_n = len(positions)
    pos_initial = positions[0]
    pos_final = positions[pos_n-1]
    a = np.array(positions)
    positions = a.transpose()
    time = [(i+1) for i in range(pos_n)]

    fig = plt.figure(figsize=(8, 4))
    ax2 = fig.add_subplot(122)
    ax = fig.add_subplot(121)
    ax.grid()
    ax.set_xlabel('Time')
    ax.set_ylabel('Initial Particle Braid positions')
    ax.set_yticklabels(pos_initial)
    braid1, = ax.plot(time,positions[0])
    braid2, = ax.plot(time,positions[1])
    braid3, = ax.plot(time,positions[2])
    braid4, = ax.plot(time,positions[3])

    heading = ("Particle 1", "Particle 2")
    braid_table = ax2.table(cellText=seq,colLabels=heading,loc='center',cellLoc='center')
    braid_table.scale(1,2)
    # braid_table.set_fontsize(16)
    for i in range(n_seq):
        for j in range(len(seq[i])):
            if i==0:
                braid_table[(i, j)].get_text().set_fontweight('bold')
            braid_table[(i+1, j)].get_text().set_color('gray')
    ax2.set_title("Braid table",fontweight="bold")
    ax2.axis('off')

    def update(index,ax,braid_table,positions,time,braid1,braid2,braid3,braid4):
        braid1.set_data(time[:index+1],positions[0][:index+1])
        braid2.set_data(time[:index+1],positions[1][:index+1])
        braid3.set_data(time[:index+1],positions[2][:index+1])
        braid4.set_data(time[:index+1],positions[3][:index+1])

        # plot
        if index==pos_n-1:
            ax2=ax.twinx()
            ax2.set_yticklabels(pos_final)
            ax2.yaxis.set_ticks(np.arange(1, 2*par_n, 2.5*2/3))
            ax2.set_ylabel('Final Particle Braid positions')
            ax2.set_ylim(ax.get_xlim())

        # Updating Braid table
        row = int(index/2)
        if row>0:
            braid_table[(row, 0)].get_text().set_color('red')
            braid_table[(row, 1)].get_text().set_color('red')
            braid_table[(row, 0)].get_text().set_fontweight('bold')
            braid_table[(row, 1)].get_text().set_fontweight('bold')
        if row>1:
            braid_table[(row-1, 0)].get_text().set_color('black')
            braid_table[(row-1, 1)].get_text().set_color('black')
            braid_table[(row-1, 0)].get_text().set_fontweight('regular')
            braid_table[(row-1, 1)].get_text().set_fontweight('regular')

        # title
        title = None
        if index <= 1:
            title = 'TQC - Pauli-X Braid Pattern'
        else:
            title = 'Braiding Particles ({},{})'.format(int(sequence[index][0]),int(sequence[index][1]))
        ax.set_title(title,fontweight="bold")

        index += 1
        index = index % pos_n
        return [braid1,braid2,braid3,braid4]

    ani = anima.FuncAnimation(fig, update, frames=pos_n, interval=1000, fargs=(ax,braid_table,positions,time,braid1,braid2,braid3,braid4))
    ani.save('pauli-x-braid-table.gif', writer='imagemagick')
    # plt.show()

################################################################################
def start():
    try:
        sequence,braid_pos = read_braid_par_pos(sys.argv[4])
        braid_particle_positions(sequence,braid_pos)

        matrix = read_nanowire_matrix(sys.argv[1])
        vertices = read_nanowire_vertices(sys.argv[2])
        pos_par, pos_volt = read_nanowire_positions(sys.argv[3])

        states = read_nanowire_state(sys.argv[5])
        graph = create_network_graph(vertices,np.array(matrix))
        nanowire_network_graph(graph,pos_par,pos_volt,states,sequence)
    except IOError as err:
        print(err)

start()
