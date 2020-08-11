# TQC Nanowire Compiler

## About
In Topological Quantum Computing, quasiparticles such as Majorana fermions are braided in a specific pattern to obtain single- or multi-Qubit Quantum gates. Serial or concurrent combinations of braid sequences between 2 particles represent these braid patterns. Each of these braid sequences correspond to a set of movements of these particles on a Nanowire.

This project is a simulation, which ultimately constructs a matrix representing movements of these particles on a Nanowire, thereby forming braids.

## TQC Nanowire Compiler

### Preprocessing - Nanowire structure

1. Given a Nanowire structure, an **Adjacency matrix** is constructed, which is used to determine the paths that the particles take in order to form a braid. In the program, ```nanowire-graph.py``` performs this preprocessing. It takes as input ```nanowire-structure.csv``` and outputs the adjacency matrix into ```nanowire-matrix.csv``` and the nanowire vertices into ```nanowire-vertex.csv```.

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

4. One of the outputs of ```nanowire-graph.py``` is a sequence of vertices of the Nanowire, saved in ```nanowire-vertex.csv```. One of the sequence is ```m,d',a',b',a,c,b,f',e,c',f,d,x2,e',x1```.

5. The other output of ```nanowire-graph.py``` is the adjacency matrix of the Nanowire, saved in ```nanowire-matrix.csv```. The matrix for the above sequence and the given nanowire structure is
```
1,0,0,0,0,0,0,0,0,0,0,0,1,0,1
0,1,0,0,0,0,0,0,0,0,0,1,1,0,0
0,0,1,0,1,0,0,0,0,0,0,0,0,0,1
0,0,0,1,0,0,1,0,0,0,0,0,0,0,1
0,0,1,0,1,0,0,0,0,0,0,0,0,0,0
0,0,0,0,0,1,0,0,0,1,0,0,0,0,0
0,0,0,1,0,0,1,0,0,0,0,0,0,0,0
0,0,0,0,0,0,0,1,0,0,1,0,0,0,1
0,0,0,0,0,0,0,0,1,0,0,0,0,1,0
0,0,0,0,0,1,0,0,0,1,0,0,1,0,0
0,0,0,0,0,0,0,1,0,0,1,0,0,0,0
0,1,0,0,0,0,0,0,0,0,0,1,0,0,0
1,1,0,0,0,0,0,0,0,1,0,0,1,1,0
0,0,0,0,0,0,0,0,1,0,0,0,1,1,0
1,0,1,1,0,0,0,1,0,0,0,0,0,0,1
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

A file, ```particle-positions.csv```, contains the initial positions of the particles on the Nanowire. In the above example, it is ```a,a',c,c',d,d'```.

### File arguments

The files mentioned above are provided as arguments to the main file, ```tqc-compiler.py```:
1. ```nanowire-structure.csv```
2. ```nanowire-vertex.csv```
3. ```nanowire-matrix.csv```
4. ```braid-sequence.csv```
5. ```particle-positions.csv```
6. ```particle-movements.csv```
7. ```particle-states.csv```

### TQC Braiding Nanowire Algorithm

#### Algorithm Rules

1. **Braiding Concurrency limits** - there is a limit on the # concurrent braiding operations
    - There is a layer of optimisation, where more than one braiding optimisation can be performed simultaneously, depending on the nanowire structure.
2. **Intermediate positions** - Every braiding operation puts the particles back in their respective final positions.
    - There is a layer of optimisation possible here. The particles can be placed in an intermediate position, so long as it does not violate any rules, interfere with other braiding operations or is needed in subsequence braiding operations.
3. **Nanowire State validity** - Every braiding operation MUST result in a valid Nanowire state. Validity can be generic or for the next braiding operation.
    - Both 1. and 2. MUST satisfy 3. EVERY braiding operation, either optimised or not, concurrent or not, must result in a valid Nanowire state.
4. **Atomic Braiding operation** - Every braid involves 2 particles, i.e., BOTH these particles needs to be moved in a braiding operation.
    - As the state before the braiding is valid, there is no obstruction during braiding for any particle.
5. **Particle-Zero mode isolation** - No two particles from different zero modes can occupy adjacent positions on the Nanowire during the braiding operation.
    - Also, when 2 particles from different zero-modes are being braided, their **non-participating** paired particle cannot be on the same side of a cut-off branch
    - After the braiding is completed, they can only occupy the valid final positions.
6. **Fusion** - For fusion, the particles involved must be adjacent to each other.

#### Braiding Phases

##### Validation Phase

1. **Get Final Positions** - Retrieve the **expected final positions** for the participating particles.
    - **Get Empty Positions** - on adjacent empty branches (returns both nearest and farthest locations on the branch)
    - There can be **multiple** final positions, if there are more than one free branches.
    - These positions are then **ranked** based on their
        - Nanowire Validity score
        - Number of steps
        - If the positions are useful in further braiding

2. **Validate Resulting State** - **Nanowire validation algorithm** which returns a ```score (>= 0)``` for every expected final position.
    - If ```score = 0```, then the state is **invalid** and the **braiding doesn't happen**. If ```score > 0```, then the state is **valid** and it's safe to continue with the braiding.
    - Initially, ```score = 0```.
    - If the resulting states have **at least 2** empty branches in each intersection, ```score += 1```.
    - If the resulting states do not interfere in the movement of the 2nd particle involved in the braiding, ```score += 1```.
    - If the resulting states do not interfere in the further braiding operations, ```score += 1```.

##### Braiding Phase

3. Perform Braiding
    - **Get Voltage Changes** - If the particles are from the same zero-mode, then voltage regulation is unnecessary. But, if braiding involves particles from different zero modes, perform necessary voltage gate changes. This may cut-off some branches.
        - For every particle, based on given the final position, choose whether to **open or close** the gate voltages.
        - Once the voltages are updated, the resultant isolated branches can be retrieved.
    - **Retrieve Isolated branches** - Instead of actually updating the Adjacency matrix, retrieve the list of isolated branches and its positions involved in the movement of the particle.
        - The isolated branch is a subset of vertices from the original set of vertices
        - The resulting adjacency matrix, involving this subset of vertices, is a subset of the original matrix
    - **Get Shortest Path** - Dijkstra's algorithm gives the shortest path for a particle from it's current (initial) position to the given (valid) final position.
    - **Update Particle Positions** - Generate a sequence of position-voltage pair, for every step of the involved particles for every braiding operation

#### Metrics

4. **Nanowire State matrix** - Generate a Nanowire State matrix, which is a sequence of positions of all particles and the corresponding gate voltage values, capturing each movement for every particle.

5. **Calculate Metrics** - Calculate metrics such as **Number of steps** (both within and between zero modes, and total), **Braiding Concurrency**, **Effective complexity**, etc.
