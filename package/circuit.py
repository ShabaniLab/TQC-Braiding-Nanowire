"""
License:
    Copyright (C) 2020
    All rights reserved.
    Arahant Ashok Kumar (aak700@nyu.edu)

Module: Circuit

Objectives:
    1. This combines the atomic gate braiding into a circuit
    2. Optimizes braid sequence
    3. Optimizes the gate sequences
    4. Optimizes the particle swaps

Class: Circuit

Methods:
    1. initialize_braid_sequence
    2. initialize_particle_positions
    3. initialize_nanowire_objects
    4. optimize_braid_sequence
    5. optimize_gate_sequence
    6. optimize_particle_swaps

Functions:
"""

class Circuit():

    def __init__(self, particles, qubits):
        self.particles = particles
        self.qubits = qubits
        self.sequence  = []
        self.direction = []
        self.positions = []
        self.nanowires = []

    def initialize_braid_sequence(self, sequence, direction):
        self.sequence.append(sequence)
        self.direction.append(direction)

    def initialize_particle_positions(self, positions):
        self.positions.append(positions)

    def initialize_nanowire_objects(self, nanowire):
        self.nanowires.append(nanowire)

    def optimize_braid_sequence(self):
        pass

    def optimize_gate_sequence(self):
        pass

    def optimize_particle_swaps(self):
        pass
