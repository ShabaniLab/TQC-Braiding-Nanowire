# TQC Compiler - Architecture

## Structure

### Package

1. Nanowire <sup>C</sup> <sup>M</sup>
    - This is the Nanowire Preprocessing stage
    - Constructs the Adjacency matrix from the given Nanowire structure
    - Constructs the list of vertices in the graph
    - Generates the Nanowire graph data structure
    - Extracts cutoff position pairs for voltage gates
1. Graph <sup>M</sup>
    - Adjacency matrix
    - Dijkstra's routing
1. Exception <sup>M</sup>
    - NoEmptyPositionException<sup>C</sup>
    - InvalidNanowireStateException<sup>C</sup>
    - NoEmptyBranchException<sup>C</sup>
    - MultiModalCrossingException<sup>C</sup>
    - PathBlockedException<sup>C</sup>
1. Compiler <sup>C</sup> <sup>M</sup>
    - Stores initial particle positions
    - Stores Braid sequence and direction for the given gate
1. Braiding <sup>C</sup>
    - Category 1 - Braiding particles on same branch
    - Category 2 - Braiding particles on different branches
    - Braid1Qubit<sup>C</sup>
        - BraidHadamard<sup>C</sup>
        - BraidPauliX<sup>C</sup>
        - BraidPhaseS<sup>C</sup>
    - Braid2Qubits<sup>C</sup>
        - BraidCNOT<sup>C</sup>
1. Utility <sup>M</sup>
1. Validation <sup>M</sup>
    - Validate Nanowire State - Nanowire Validation Algorithm (returns a score)
        - Validate Empty Branches
        - Validate multi modal crossing
    - Validate path particle - Checks if any other particle blocks the path
    - Validate path gates - Checks if a shut voltage gate blocks the path
    - Check unibranch validity - Checks if the pair is in the same branch
1. Metrics <sup>M</sup>
    - Saves output generated into respective files
1. Measurement <sup>M</sup>
    - Measures outcomes based on the given Fusion rules and channels
1. Animation <sup>C</sup>
    - Braid-table animation
    - Nanowire particle movement animation

### Implementation

1. Shell script
    - Automation
    - Input validation
1. Preprocessing Nanowire
    - Read Nanowire structure
    - Construct adjacency matrix
    - Extract graph vertices
1. Algorithm Compile
    - Nanowire
    - Compile
    - Braid
1. Algorithm Measure
    - Read Fusion rules
    - Read Fusion channels
    - Measure
1. Animate
    - Braid
    - Nanowire

### Inputs

1. Circuit configuration <sup>csv</sup>
```
gate=cnot
particles=6
qubits=2
voltages=4
```

1. Nanowire structure <sup>csv</sup>
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

1. Nanowire positions <sup>csv</sup>
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

1. Initial particle positions <sup>csv</sup>
```
a,a',c,c',d,d'
```

1. Braid sequence <sup>csv</sup> (with counter-clockwise braiding direction)
```
3,4,0
3,5,0
1,2,0
4,5,0
3,6,0
4,6,0
5,6,0
```

1. Fusion Channel <sup>csv</sup> - this channel is for a 2-qubit gate
```
Q1,Q2,a,b,c
0,0,1,1,1
1,0,x,x,1
0,1,1,x,x
1,1,x,1,x
```


1. Fusion rules <sup>csv</sup>
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

### Outputs

1. Nanowire matrix <sup>csv</sup>
1. Nanowire vertices <sup>csv</sup>
1. Nanowire state matrix <sup>csv</sup>
1. Particle movements - Nanowire <sup>csv</sup>
1. Particle positions - Nanowire <sup>csv</sup>
1. Particle positions - Braid <sup>csv</sup>
1. Measurements <sup>csv</sup>
1. Braid animation <sup>gif</sup>
1. Nanowire animation <sup>gif</sup>
