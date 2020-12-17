"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Animation

Objectives:
    1. Braid pattern animation
    2. Nanowire particles animation

Class: Animation

Functions:
    i. __init__
    ii. initiate_file_io

    1. read_nanowire_matrix
    2. read_nanowire_vertices
    3. read_nanowire_positions
    4. read_nanowire_state
    5. read_braid_particle_pos

    A. animate_braid
    B. animate_nanowire
    6. initialize_network_graph
    7. get_voltage_gate_labels

"""

import re
import copy
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as anima

class Animation:
    """
    Animation class
        A. Braid pattern animation using Pyplot
        B. Nanowire Particle movements animation using Networkx
    """

    labels_old = None

    ################################################################################
    # Initialization
    def __init__(self, gate, output):
        """
        i. Initializes required variables
        gate - string
        """
        self.gate = gate
        self.matrix = None
        self.vertices = None
        self.pos_par = None
        self.pos_volt = None
        self.states = None
        self.sequence = None
        self.sequence_states = None
        self.positions = None
        self.par_n = 0
        self.graph = None
        self.output = output

    def initiate_file_io(self, argv):
        """
        ii. Calls all the File I/O functions
        """
        try:
            self.read_nanowire_matrix(argv[1])
            self.read_nanowire_vertices(argv[2])
            self.read_nanowire_positions(argv[3])
            self.read_nanowire_state(argv[4])
            self.read_braid_particle_pos(argv[5])
        except IOError:
            raise

    ################################################################################
    # File I/O
    def read_nanowire_matrix(self, file):
        """
        1. Reading the Nanowire graph matrix
        """
        matrix = []
        try:
            file_read = open(file, 'r')
            line = file_read.readline()
            line = line.strip()
            row = line.split(',')
            values = [int(i) for i in row]
            matrix.append(values)
            while line:
                line = file_read.readline()
                if line:
                    line = line.strip()
                    row = line.split(',')
                    values = [int(i) for i in row]
                    matrix.append(values)
            file_read.close()
            self.matrix = matrix
        except IOError:
            raise IOError

    def read_nanowire_vertices(self, file):
        """
        2. Reading the Nnaowire graph vertices
        """
        vertices = []
        try:
            file_read = open(file, 'r')
            line = file_read.readline()
            line = line.strip()
            vertices = line.split(',')
            file_read.close()
            self.vertices = vertices
        except IOError:
            raise IOError

    def read_nanowire_positions(self, file):
        """
        3. Reading Nanowire Node positions
        """
        pos_par = dict()
        pos_volt = dict()
        try:
            file_read = open(file, 'r')
            line = file_read.readline()
            line = line.strip()
            while line:
                line = file_read.readline()
                if line:
                    line = line.strip()
                    row = line.split(',')
                    node = row[0]
                    if len(node) == 3 and 'x' in node:
                        pos_x = float(row[1])
                        pos_y = float(row[2])
                        pos_volt[node] = np.array([pos_x, pos_y])
                    else:
                        pos_x = int(row[1])
                        pos_y = int(row[2])
                        pos_par[node] = np.array([pos_x, pos_y])
            file_read.close()
            self.pos_par = pos_par
            self.pos_volt = pos_volt
        except IOError:
            raise IOError

    def read_nanowire_state(self, file):
        """
        4. Reading the Nanowire states
        """
        nanowire_states = []
        sequence_states = []
        pair = None
        try:
            file_read = open(file, 'r')
            line = file_read.readline()
            line = line.strip()
            i = 0
            while line:
                line = file_read.readline()
                if line:
                    line = line.strip()
                    row = line.split(',')
                    nanowire_states.append(row)
                    if pair != row[:2]:
                        pair = row[:2]
                        sequence_states.append(pair)
            file_read.close()
            self.states = nanowire_states
            self.sequence_states = sequence_states
        except IOError:
            raise IOError

    def read_braid_particle_pos(self, file):
        """
        5. Reading Braid particle positions
        """
        sequence = []
        braid_pos = []
        try:
            file_read = open(file, 'r')
            line = file_read.readline()
            line = line.strip()
            while line:
                line = file_read.readline()
                if line:
                    line = line.strip()
                    row = line.split(',')
                    temp = [int(e) for e in row[:2]]
                    sequence.append(temp)
                    # sequence.append(row[:2])
                    # braid_pos.append(row[2:])
                    temp = [int(e) for e in row[2:]]
                    braid_pos.append(temp)
            file_read.close()
            self.sequence = sequence
            self.positions = braid_pos
            self.par_n = len(braid_pos[0])
        except IOError:
            raise IOError

    def nanowire_yaml_to_structure_graph(self, structure):
        """
        3a. Yaml to Nanowire Node positions
        """
        pos_par = dict()
        pos_volt = dict()
        for key, val in structure.items():
            pos = val.split(',')
            pos_arr = None
            if re.search('\d\.\d', pos[0]):
                pos_arr = np.array([float(pos[0]), float(pos[1])])
            elif re.search('\d', pos[0]):
                pos_arr = np.array([int(pos[0]), int(pos[1])])
            if len(key) == 3 and 'x' in key:
                pos_volt[key] = pos_arr
            else:
                pos_par[key] = pos_arr
            self.pos_par = pos_par
            self.pos_volt = pos_volt

    ################################################################################
    # A. Braiding animation using Pyplot
    def get_braid_sequence_positions(self):
        """getting the correct braid sequence and positions"""
        sequence = []
        positions1 = []
        mapping = None
        i = 0
        for i in range(len(self.sequence)):
            seq = self.sequence[i]
            sequence.append(seq)
            sequence.append(seq)

            # if seq == [0,0]:
            #     self.pos0 = self.positions[i]
            #     pos_ini = [i+1 for i in range(self.par_n)]
            #     mapping = dict(zip(self.pos0, pos_ini))
            # else:
            #     self.pos0 = [mapping[e] for e in self.positions[i]]
            #     # pair = seq
            #     # pair = [mapping[seq[0]], mapping[seq[1]]]
            #     # pos[pair[0]-1], pos[pair[1]-1] = pos[pair[1]-1], pos[pair[0]-1]
            #     # self.pos0 = pos
            pos = self.positions[i]
            positions1.append(pos)
            positions1.append(pos)

        return sequence, positions1, mapping

    def get_animation_plots(self, time, positions, pos_initial):
        """Initializing the plot variables:
        ax, ax2, braid_list, braid_table"""
        # initialising plots [ax, ax2]
        fig = plt.figure(figsize=(12, 6))
        ax2 = fig.add_subplot(122)
        ax = fig.add_subplot(121)
        ax.grid()
        ax.set_xlabel('Time')
        ax.set_ylabel('Initial Particle positions')
        ax.set_yticklabels(pos_initial)
        ax.yaxis.set_ticks(np.arange(1, self.par_n+1))

        # creating braid_list
        braid_list = []
        for i in range(self.par_n):
            braid, = ax.plot(time, positions[i])
            braid_list.append(braid)

        # creating braid_table
        heading = ("Particle 1", "Particle 2")
        seq = copy.copy(self.sequence)
        if seq[0] == seq[1] or seq[0] == [0,0]:
            seq.pop(0)
        braid_table = ax2.table(cellText=seq, colLabels=heading, loc='center', cellLoc='center')
        braid_table.scale(1, 2)
        # braid_table.set_fontsize(16)
        for i in range(len(seq)):
            for j in range(len(seq[i])):
                if i==0:
                    braid_table[(i, j)].get_text().set_fontweight('bold')
                braid_table[(i+1, j)].get_text().set_color('gray')
        ax2.set_title("{} Braid table".format(self.gate), fontweight="bold")
        ax2.axis('off')

        return fig, ax, ax2, braid_list, braid_table

    def animate_braid(self):
        """
        A. Braid pattern animation
        """
        index = 0
        sequence, positions, mapping = self.get_braid_sequence_positions()
        pos_n = len(positions)
        pos_ini = positions[0]
        pos_final = positions[pos_n-1]
        if mapping is not None and len(mapping) == self.par_n:
            pos_final = [mapping[e] for e in pos_final]
        a = np.array(positions)
        positions = a.transpose()
        time = [i for i in range(pos_n)]
        fig, ax, ax2, braid_list, braid_table = self.get_animation_plots(time, positions, pos_ini)

        def update_braid(index, ax, braid_table, positions, time, braid_list, sequence, pos_n):
            i = -1
            for braid in braid_list:
                i += 1
                braid.set_xdata(time[:index+1])
                braid.set_ydata(positions[i][:index+1])

            # plot
            if index == pos_n-1:
                ax3=ax.twinx()
                ax3.set_yticklabels(pos_final)
                ax3.set_ylabel('Final Particle positions')
                ax3.yaxis.set_ticks(np.arange(1, self.par_n+1))
                ax3.set_ylim(ax.get_ylim())

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
                title = 'TQC - {} Braid Pattern'.format(self.gate.upper())
            else:
                title = 'Braiding Particles ({}, {})'.format(
                    int(sequence[index][0]), int(sequence[index][1])
                )
            ax.set_title(title, fontweight="bold")

            index += 1
            index = index % pos_n
            return braid_list

        ani = anima.FuncAnimation(fig, update_braid, frames=pos_n, interval=1000,
                            fargs=(ax, braid_table, positions, time, braid_list, sequence, pos_n))
        fn = '{}-braid-table.gif'.format(self.gate)
        ani.save(self.output+'/'+fn, writer='imagemagick')

    ################################################################################
    # B. Particle movements animation using Networkx
    def initialize_network_graph(self):
        """
        6. Creating Nanowire network graph
        """
        G = nx.from_numpy_matrix(np.array(self.matrix))
        G = nx.relabel_nodes(G, lambda x: self.vertices[x])
        G.edges(data=True)
        self.graph = G

    def animate_nanowire(self):
        """
        B. Nanowire particles animation
        """
        G = self.graph
        BASE_WEIGHT = 1
        index = 0
        self.pair0 = None
        self.idx = 0

        # Nanowire network graph - positions
        for node1, node2, weight in list(G.edges(data=True)):
            if (weight["weight"]<BASE_WEIGHT) or (node1==node2):
                G.remove_edge(node1, node2)
        edges_par, weights_par = zip(*nx.get_edge_attributes(G, 'weight').items())
        weights_par = [float((1+abs(x))**2) for x in weights_par]
        nds = list(G.nodes())

        # Nanowire network graph - voltage gates
        node_volts = list(self.pos_volt.keys())
        node_volts.sort()
        G.add_nodes_from(node_volts)
        edges_volt = []
        edges_volt_pairs = []
        for i in range(0, len(node_volts), 2):
            edges_volt_pairs.append((node_volts[i], node_volts[i+1]))
            edges_volt.append((node_volts[i], node_volts[i+1], {'weight':BASE_WEIGHT}))
        G.add_edges_from(edges_volt)
        weights_volt = [float((1+abs(BASE_WEIGHT))**2) for x in range(len(edges_volt_pairs))]

        positions = {**self.pos_par, **self.pos_volt}
        edge_color_par_base = plt.cm.get_cmap('Paired')
        edge_color_par_active = plt.cm.get_cmap('Pastel1')
        edge_color_volt_base = plt.cm.get_cmap('GnBu')
        edge_color_volt_active = plt.cm.get_cmap('Spectral')
        node_color_base = '#A2D290'
        node_color_active = '#CC6699'
        node_color_base_volt = "#DDFFCC"
        node_color_active_volt = '#990000'
        par = 0

        def update_nanowire(index):
            i1 = 2
            pair = self.states[index][:i1]
            particles = self.states[index][i1:i1+self.par_n]
            gates = self.states[index][i1+self.par_n:]
            empty = list(set(nds)-set(particles))
            label_par = {pos:particles.index(pos)+1 for pos in particles}
            label_empty = {pos:pos for pos in empty}
            par = None
            pos1 = None
            pos2 = None
            title = None
            if index is 0:
                title = "TQC Braiding Nanowire - {}".format(self.gate.upper())
            index += 1
            index = index%len(self.states)

            ## Nanowire positions
            nx.draw_networkx_edges(G, positions, style='solid',
                                    edgelist=edges_par,
                                    width=weights_par,
                                    edge_color=weights_par,
                                    edge_cmap=edge_color_par_base)
            nx.draw_networkx_nodes(G, positions, node_size=500, alpha=0.8,
                                    node_color=node_color_base,
                                    nodelist=empty)
            nx.draw_networkx_nodes(G, positions, node_size=500, alpha=0.8,
                                    node_color=node_color_active,
                                    nodelist=particles)
            nx.draw_networkx_labels(G, positions, font_size=10, font_family='sans-serif', ax=ax)

            ## Nanowire Voltage gates
            edges_volt_open = []
            edges_volt_shut = []
            nodes_volt_open = []
            nodes_volt_shut = []
            label_gates = dict()
            for i in range(len(gates)):
                key, lbl = self.get_voltage_gate_labels(i)
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
            nx.draw_networkx_nodes(G, positions, node_size=200, alpha=0.5,
                                    node_color=node_color_base_volt,
                                    nodelist=nodes_volt_open)
            nx.draw_networkx_nodes(G, positions, node_size=200, alpha=0.5,
                                    node_color=node_color_active_volt,
                                    nodelist=nodes_volt_shut)
            nx.draw_networkx_edges(G, positions, style='solid',
                                    edgelist=edges_volt_open,
                                    width=weights_volt_open,
                                    edge_color=weights_volt_open,
                                    edge_cmap=edge_color_volt_base)
            nx.draw_networkx_edges(G, positions, style='solid',
                                    edgelist=edges_volt_shut,
                                    width=weights_volt_shut,
                                    edge_color=weights_volt_shut,
                                    edge_cmap=edge_color_volt_active)

            # relabling nodes
            labels = {**label_empty, **label_par, **label_gates}
            mapping = dict()
            if Animation.labels_old is None:
                Animation.labels_old = labels
                mapping = labels
                for n in G.nodes():
                    if n in mapping.keys() and n is mapping[n]:
                        mapping.pop(n)
            else:
                for k in Animation.labels_old.keys():
                    key = Animation.labels_old[k]
                    val = labels[k]
                    if key is '' or val is '':
                        continue
                    if key is not val:
                        mapping[key] = val
                Animation.labels_old = labels
            if mapping:
                # if len(mapping) == 2:
                #     k1 = list(mapping.keys())[0]
                #     k2 = list(mapping.keys())[1]
                #     map1 = {}
                #     map2 = {}
                #     if isinstance(k1, int):
                #         map1[k1] = mapping[k1]
                #         map2[k2] = mapping[k2]
                #     else:
                #         map1[k2] = mapping[k2]
                #         map2[k1] = mapping[k1]
                #     G = nx.relabel_nodes(G, map1)
                #     G = nx.relabel_nodes(G, map2)
                # else:
                #     G = nx.relabel_nodes(G, mapping)
                if len(mapping.keys()) == 2:
                    for k in mapping.keys():
                        if isinstance(k, int):
                            par = k
                        if isinstance(k, str):
                            pos2 = k
                        if isinstance(mapping[k], str):
                            pos1 = mapping[k]

            # Updating Braid table
            if par is not None and pair in self.sequence_states:
                if pair != self.pair0:
                    self.idx += 1
                    self.pair0 = pair
                    print('Animating Nanowire movements for particles ({}, {})'\
                        .format(self.pair0[0], self.pair0[1]))
                row = self.idx

                braid_table[(row, 0)].get_text().set_color('red')
                braid_table[(row, 1)].get_text().set_color('red')
                braid_table[(row, 0)].get_text().set_fontweight('bold')
                braid_table[(row, 1)].get_text().set_fontweight('bold')
                if row > 1:
                    braid_table[(row-1, 0)].get_text().set_color('black')
                    braid_table[(row-1, 1)].get_text().set_color('black')
                    braid_table[(row-1, 0)].get_text().set_fontweight('regular')
                    braid_table[(row-1, 1)].get_text().set_fontweight('regular')

            # Output
            if pair is not None:
                title = "Braiding particles ({}, {})".format(int(pair[0]), int(pair[1]))
                if par is not None and pos1 is not None and pos2 is not None:
                    title = "{}\nMoving ({}) from {} to {}".format(title, par, pos1, pos2)
            for i in range(len(gates)):
                volt = gates[i]
                if volt is 'S':
                    key, gate = self.get_voltage_gate_labels(i)
                    gt = "Voltage Gate {} is SHUT".format(gate)
                    if par is None:
                        title = "{}\n{}".format(title, gt)
                    else:
                        title = "{}: {}".format(title, gt)
                    break

            # display
            if pos1 is not None and pos2 is not None:
                e = [(pos1, pos2, {'weight':BASE_WEIGHT})]
                w = weights_volt[:len(e)]
                nx.draw_networkx_edges(G, positions, style='solid',
                edgelist=e,  width=w, edge_color=w, edge_cmap=edge_color_par_active)
            if title is not None:
                ax.set_title(title, fontweight="bold")

        fig = plt.figure(figsize=(12, 6))
        ax2 = fig.add_subplot(122)
        ax = fig.add_subplot(121)
        heading = ("Particle 1", "Particle 2")
        braid_table = ax2.table(loc='center', cellLoc='center',
                                cellText=self.sequence_states, colLabels=heading)
        braid_table.scale(1, 2)
        # braid_table.set_fontsize(16)
        for i in range(len(self.sequence_states)):
            for j in range(len(self.sequence_states[i])):
                if i==0:
                    braid_table[(i, j)].get_text().set_fontweight('bold')
                braid_table[(i+1, j)].get_text().set_color('gray')
        ax2.set_title("Braid table", fontweight="bold")
        ax2.axis('off')

        ani = anima.FuncAnimation(fig, update_nanowire, frames=len(self.states), interval=500)
        fn = '{}-nanowire-table.gif'.format(self.gate)
        ani.save(self.output+'/'+fn, writer='imagemagick')

    def get_voltage_gate_labels(self, flag):
        """
        7. Returns voltage node labels
        """
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
