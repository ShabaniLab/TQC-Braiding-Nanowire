# Topological Quantum Compiling

## About
In Topological Quantum Computing (TQC), quasiparticles (such as Majorana fermions) are braided in a specific pattern to construct single- or multi-qubit Quantum gates. Serial or concurrent combinations of braid sequences between 2 quasiparticles forms the braid pattern. Each of these braid sequence correspond to a set of movements of these particles on a Nanowire, which is the Quantum hardware.

This project is the 1st stage in building a Compiler to perform TQC. It achieves this by generating a matrix representing movements of these particles on the Nanowire, thereby forming braids resulting in Quantum gates. This compiler constructs braid patterns for the following quantum gates:

1. ![Phase S (1 Qubit)](docs/phase-s/README.md)
1. ![Pauli-X (1 Qubit)](docs/pauli-x/README.md)
1. ![Hadamard (1 Qubit)](docs/hadamard/README.md)
1. ![CNOT (2 Qubits)](docs/cnot/README.md)

## TQC Compiler structure

This documentation is structured into multiple segments:

1. ![Compiler Algorithm](docs/DOC-ALGORITHM.md)
1. ![Word Done in stages](docs/DOC-WORK.md)
1. ![Compiler architecture program](docs/DOC-ARCHITECTURE.md)

## Installation and execution

1. `git clone https://github.com/ShabaniLab/TQC-Braiding-Nanowire`
1. `pip install -r requirements`
1. `cd gate`
1. `./run.sh inputs/cnot` to construct a 2-qubit CNOT Quantum gate
1. `./run.sh inputs/hadamard` to construct a 1-qubit Hadamard Quantum gate
1. `./run.sh inputs/pauli-x` to construct a 1-qubit Pauli-X Quantum gate
1. `./run.sh inputs/phase-s` to construct a 1-qubit Phase-S Quantum gate
