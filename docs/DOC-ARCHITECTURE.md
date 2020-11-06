# TQC Compiler - Architecture

## Package

### Nanowire <sup>M</sup> <sup>C</sup>
1. **Module**: Nanowire
1. **Class**: Nanowire
1. Objectives:
    - This is the Nanowire Preprocessing stage
    - Constructs the Adjacency matrix from the given Nanowire structure
    - Constructs the list of vertices in the graph
    - Generates the Nanowire graph data structure
    - Extracts cutoff position pairs for voltage gates

### Graph <sup>M</sup>
1. **Module**: Graph
1. Objectives:
    - Adjacency matrix
    - Dijkstra's routing

### Exception <sup>M</sup> <sup>C</sup>
1. **Module**: Exception
1. **Classes**:
    - NoEmptyPositionException <sup>C</sup>
    - InvalidNanowireStateException <sup>C</sup>
    - NoEmptyBranchException <sup>C</sup>
    - MultiModalCrossingException <sup>C</sup>
    - PathBlockedException <sup>C</sup>

### Compiler <sup>M</sup> <sup>C</sup>
1. **Module**: Compiler
1. **Class**: Compiler
1. Objectives
    - Stores initial particle positions
    - Stores Braid sequence and direction for the given gate

### Braiding <sup>M</sup> <sup>C</sup>
1. **Module**: Braiding
1. **Class**: Braiding
    - Braid1Qubit <sup>C</sup>
        - BraidHadamard <sup>C</sup>
        - BraidPauliX <sup>C</sup>
        - BraidPhaseS <sup>C</sup>
    - Braid2Qubits <sup>C</sup>
        - BraidCNOT <sup>C</sup>
1. Objectives
    - Category 1 braiding - Braiding particles on same branch
    - Category 2 braiding - Braiding particles on different branches

### Utility <sup>M</sup> <sup>C</sup>
1. **Module**: Utility
1. **Class**: Utility
1. Objectives: Braiding helper functions
1. Methods:
    - Update Zero modes - a list of Zero mode pairs DURING a braiding operation
    - Refresh Zero modes - a list of Zero mode pairs AFTER a braiding operation
    - Get Isolated particles - get isolated particles which are NOT part of any zero mode (in the middle of a braiding operation)
    - Update voltages - get Voltage Gate Changes if braiding involves particles from different zero modes.
    - Check pair zmode - checks if the pair is a zero mode
    - Check particle zmode - checks if at least 1 particle in the pair is part of a zero mode
1. Functions:
    - Get Final positions - expected final (swapped) positions of the particles to be braided
    - Update nanowire - update Nanowire with new Positions
    - Get steps - returns # steps from initial to final position
    - Comparator - _Ranks_ the positions based on **Validity Score** and **# steps**
    - Get Intermediate positions - the potential intermediate positions of the particles to be braided
    - Get Empty positions - the empty positions on adjacent empty branches

### Validation <sup>M</sup>
1. **Module**: Validation
1. Objectives:
    - Validate Nanowire State - Nanowire Validation Algorithm (returns a score)
        - Validate Empty Branches
        - Validate multi modal crossing
    - Validate path particle - Checks if any other particle blocks the path
    - Validate path gates - Checks if a shut voltage gate blocks the path
    - Check unibranch validity - Checks if the pair is in the same branch

### Metrics <sup>M</sup>
1. **Module**: Metrics
1. Objective: Saves output generated into respective files
1. Functions:
    - Update Particle movements - update particle positions by generating a sequence of positions steps for the particles.
    - Update Nanowire states - update the Nanowire state matrix
    - Update Particles' Braid positions - update the particle position in the Braid sequence
    - Update Final particle positions - update the final particle positions on the Nanowire

### Measurement <sup>M</sup>
1. **Module**: Measurement
1. Objective: Measures outcomes based on the given Fusion rules and channels

### Animation <sup>M</sup> <sup>C</sup>
1. **Module**: Animation
1. **Class**: Animation
1. Objectives:
    - Braid-table animation
    - Nanowire particle movement animation

## Implementation

1. Shell script
    - `run.sh` - executes the TQC braiding algorithm, from preprocessing to measurement and animation
    - `validate.sh` - robust input validation
    - Automation - the required data is specified in `circuit-config.csv`, there is no manual modification for different gates.
    - Colour-coded log outputs based on algorithm stages
1. Preprocessing - Nanowire
    - Read Nanowire structure
    - Construct adjacency matrix
    - Extract graph vertices
1. Algorithm - Compile
    - Nanowire
    - Compile
    - Braid - The custom classes are selected based on the `gate` in `circuit-config.csv`
1. Algorithm- Measure
    - Read Fusion rules
    - Read Fusion channels
    - Measure
1. Animation
    - Gate Braid animation
    - Nanowire particles' movement animation

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
