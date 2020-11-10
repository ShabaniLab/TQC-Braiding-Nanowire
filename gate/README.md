# TQC Compiler - Implementation design

## Execution

### Shell script
1. `run.sh` - executes the TQC braiding algorithm, from preprocessing to measurement and animation
1. `validate.sh` - robust (and decoupled) validation of inputs
1. Automation - the required data is specified in `circuit-config.csv`, there is no manual modification for different gates.
1. Colour-coded log outputs based on algorithm stages

### Preprocessing - Nanowire
1. Read Nanowire structure
1. Construct adjacency matrix
1. Extract graph vertices

### Algorithm - Compile
1. **Initialize Nanowire** - Nanowire data structure, positions, voltage cutoff pairs
1. **Initialize Compiler** - Extract braid sequences, initial particle positions
1. **Braiding operation** - The Braiding classes are selected based on the given `gate`.

### Algorithm - Measure
1. **Fusion rules** - The rules which determine the output of each fusion operation.
1. **Fusion channels** - These are different for 1-qubit and 2-qubit quantum gates
1. **Measure** - a pseudo-random generator to simulated the quantum probability.

### Animation
1. Gate Braid animation
1. Nanowire particles' movement animation

## Inputs

### Circuit configuration <sup>csv</sup>
```
gate=cnot
particles=6
qubits=2
voltages=4
```

### Nanowire structure <sup>csv</sup>
```
b,b'
a,a'
f,f'
m
x11,x12
c,c'
m
e,e'
d,d'
x21,x22
```

### Nanowire positions <sup>csv</sup>
```
Node,X,Y
b,3,6
b',3,5
a,1,4
a',2,4
f,3,2
f',3,3
m,4,4
x1,3,4
c,5,6
c',5,5
e,5,2
e',5,3
d,7,4
d',6,4
x2,5,4
x11,3.5,4.5
x12,2.5,3.5
x13,2.5,4.5
x14,3.5,3.5
x21,5.5,4.5
x22,4.5,3.5
x23,4.5,4.5
x24,5.5,3.5
```

### Initial particle positions <sup>csv</sup>

It changes for every gate.
```
a,a',c,c',d,d'
```

### Braid sequence <sup>csv</sup> (with braiding direction)

Below is the sequence for a 2-qubit CNOT gate and it changes for every gate

```
3,4,0
3,5,0
1,2,0
4,5,0
3,6,0
4,6,0
5,6,0
```

### Fusion Channel <sup>csv</sup>
This channel is for a 2-qubit gate
```
Q1,Q2,a,b,c
0,0,1,1,1
1,0,x,x,1
0,1,1,x,x
1,1,x,1,x
```


### Fusion rules <sup>csv</sup>
```
P1,P2,Res
o,o,1
o,o,x
1,o,o
o,1,o
1,1,1
1,x,x
x,1,x
x,x,1
x,o,o
```

## Outputs

1. Nanowire matrix <sup>csv</sup> - Nanowire graph adjacency matrix
1. Nanowire vertices <sup>csv</sup> - Nanowire graph vertices list
1. Nanowire state matrix <sup>csv</sup> - Sequence of Nanowire positions
1. Particle movements (Nanowire) <sup>csv</sup> - a sequence of steps for every braiding
1. Particle positions (Nanowire) <sup>csv</sup> - Initial and Final particle positions on the Nanowire
1. Particle positions (Braid) <sup>csv</sup> - Particle positions in the braid sequence
1. Measurements <sup>csv</sup> - Qubit values after Fusion
1. Braid animation <sup>gif</sup> - A `gif` of the braid sequence
1. Nanowire animation <sup>gif</sup> - A `gif` of the particle movements on Nanowire
