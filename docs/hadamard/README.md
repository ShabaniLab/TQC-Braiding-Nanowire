# TQC Compiler - Hadamard gate

## Hadamard Braid pattern

![hadamard-braid-pattern](hadamard-braid-pattern.png)

## Inputs for Hadamard

1. Circuit configuration (`circuit-config.csv`) - specifying the gate, number of particles, number of qubits, and total voltage gates
```
gate=hadamard
particles=4
qubits=1
voltages=4
```

1. Braid sequence (`braid-sequence.csv`) (with counter-clockwise braiding direction):
```
1,2,0
1,3,0
2,3,0
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

![hadamard-braid-animation](hadamard-braid-table.gif)

![hadamard-nanowire-animation](hadamard-nanowire-table.gif)
