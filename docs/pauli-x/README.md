# TQC Compiler - Pauli X gate

## Pauli X Braid pattern

![pauli-x-braid-pattern](pauli-x-braid-pattern.png)

## Inputs for Pauli X

1. Circuit configuration (`circuit-config.csv`) - specifying the gate, number of particles, number of qubits, and total voltage gates
```
gate=pauli-x
particles=4
qubits=1
voltages=4
```

1. Braid sequence (`braid-sequence.csv`) (with counter-clockwise braiding direction):
```
2,3,0
3,2,0
```

1. Fusion Channel (`fusion-channel.csv`) - this channel is for a 1-qubit gate
```
Q,a,b
0,1,1
1,x,x
```

1. Initial particle positions (`initial-positions.csv`):
```
b,b',f',f
```

1. The Fusion rules, Nanowire structure and Nanowire positions are the same as for CNOT.

## Outputs - Animation

![pauli-x-braid-animation](pauli-x-braid-table.gif)

![pauli-x-nanowire-animation](pauli-x-nanowire-table.gif)
