# TQC Nanowire Compiler

## About
In Topological Quantum Computing, quasiparticles such as Majorana fermions are braided in a specific pattern to obtain single- or multi-Qubit Quantum gates. Serial or concurrent combinations of braid sequences between 2 particles represent these braid patterns. Each of these braid sequences correspond to a set of movements of these particles on a Nanowire.

This project is a simulation, which ultimately constructs a matrix representing movements of these particles on a Nanowire, thereby forming braids.

## TQC Nanowire Compiler

### Preprocessing - Nanowire structure

1. Given a Nanowire structure, an **Adjacency matrix** is constructed, which is used to determine the paths that the particles take in order to form a braid. In the program, ```nanowire-graph.py``` performs this preprocessing. It takes as input ```nanowire-structure.csv``` and outputs the adjacency matrix into ```nanowire-graph.csv``` and the nanowire vertices into ```nanowire-vertex.csv```.

2. **Representation of the Nanowire** must follow certain rules:
    - Sequence of the branches is **Anti-clockwise**
    - Sequence of the branches is **Topmost and Leftmost**
    - Naming Sequence of the positions is **Outward to inward**
    - Each intersection is followed by the **Voltage gates**

![nanowire-2x](nanowire.png)

3. This is a Double-X junction Nanowire. It would be represented in (```nanowire-structure.csv```) as:
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

4. One of the outputs of ```nanowire-graph.py``` is a sequence of vertices of the Nanowire, saved in ```nanowire-vertex.csv```. One of the sequence is ```m,a,b,c,f',d,c',e,a',e',b',d',f```.

5. The other output of ```nanowire-graph.py``` is the adjacency matrix of the Nanowire, saved in ```nanowire-graph.csv```. The matrix for the above sequence and the given nanowire structure is
```
1,0,0,0,1,0,1,0,1,1,1,1,0
0,1,0,0,0,0,0,0,1,0,0,0,0
0,0,1,0,0,0,0,0,0,0,1,0,0
0,0,0,1,0,0,1,0,0,0,0,0,0
1,0,0,0,1,0,0,0,0,0,0,0,1
0,0,0,0,0,1,0,0,0,0,0,1,0
1,0,0,1,0,0,1,0,0,0,0,0,0
0,0,0,0,0,0,0,1,0,1,0,0,0
1,1,0,0,0,0,0,0,1,0,0,0,0
1,0,0,0,0,0,0,1,0,1,0,0,0
1,0,1,0,0,0,0,0,0,0,1,0,0
1,0,0,0,0,1,0,0,0,0,0,1,0
0,0,0,0,1,0,0,0,0,0,0,0,1
```

### Preprocessing - Braid sequence

![braid-cnot](braid-pattern.png)

1. Given a Braid pattern for a Quantum gate, it needs to be processed into a sequence of braids between 2 particles. These sequences, in turn, combine to form the braid pattern. For this Braiding pattern, which is a 2-Qubit CNOT gate, the braid sequence saved in ```braid-sequence.csv``` is:
```
3,4
3,5
1,2
4,5
3,6
4,6
5,6
```

### Preprocessing - Initial Particle positions

1. A file, ```positions.csv```, contains the initial positions of the particles on the Nanowire.

### File arguments

The files mentioned above are provided as arguments to the main file, ```particle-movement.py```:
1. ```nanowire-structure.csv```
2. ```nanowire-vertex.csv```
3. ```nanowire-graph.csv```
4. ```positions.csv```
5. ```braid-sequence.csv```
