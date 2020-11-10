# TQC Compiler - Architecture

## Package

This is the base package containing all the necessary modules, which are imported and (re)used during the implementation of Quantum gates and the circuit.

### Nanowire <sup>M</sup> <sup>C</sup>
1. **Module**: Nanowire
1. **Class**: Nanowire
1. **Objectives**:
    - This is the Nanowire Preprocessing stage
    - Constructs the Adjacency matrix from the given Nanowire structure
    - Constructs the list of vertices in the graph
    - Generates the Nanowire graph data structure
    - Extracts cutoff position pairs for voltage gates

### Graph <sup>M</sup>
1. **Module**: Graph
1. **Objectives**:
    - Adjacency matrix
    - Dijkstra's routing

### Exception <sup>M</sup> <sup>C</sup>
1. **Module**: Exception
1. **Classes**:
    - **NoEmptyPositionException** <sup>C</sup> - raised when there are no available empty positions for the braiding to commence.
    - **InvalidNanowireStateException** <sup>C</sup> - raised if the Nanowire Validation Algorithm returns a score of `0`.
    - **NoEmptyBranchException** <sup>C</sup> - raised when there are no available empty branches for the braiding to commence.
    - **MultiModalCrossingException** <sup>C</sup> - raised when the braiding is of category 2, and there is a violation of rule 3.
    - **PathBlockedException** <sup>C</sup> - raised when the path of particle to be moved is either blocked by another particle or a shut voltage gate.

### Compiler <sup>M</sup> <sup>C</sup>
1. **Module**: Compiler
1. **Class**: Compiler
1. **Objectives**:
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
1. **Objectives**:
    - Category 1 braiding - Braiding particles on same branch
    - Category 2 braiding - Braiding particles on different branches

### Utility <sup>M</sup> <sup>C</sup>
1. **Module**: Utility
1. **Class**: Utility
1. **Objectives**: Braiding helper functions
1. **Methods**:
    - **Update Zero modes** - a list of Zero mode pairs DURING a braiding operation
    - **Refresh Zero modes** - a list of Zero mode pairs AFTER a braiding operation
    - **Get Isolated particles** - get isolated particles which are NOT part of any zero mode (in the middle of a braiding operation)
    - **Update voltages** - get Voltage Gate Changes if braiding involves particles from different zero modes.
    - **Check pair zmode** - checks if the pair is a zero mode
    - **Check particle zmode** - checks if at least 1 particle in the pair is part of a zero mode
1. **Functions**:
    - **Get Final positions** - expected final (swapped) positions of the particles to be braided
    - **Update nanowire** - update Nanowire with new Positions
    - **Get steps** - returns # steps from initial to final position
    - **Comparator** - _Ranks_ the positions based on **Validity Score** and **# steps**
    - **Get Intermediate positions** - the potential intermediate positions of the particles to be braided
    - **Get Empty positions** - the empty positions on adjacent empty branches

### Validation <sup>M</sup>
1. **Module**: Validation
1. **Objectives**:
    - **Validate Nanowire State** - Nanowire Validation Algorithm (returns a score)
        - Validate Empty Branches
        - Validate multi modal crossing
    - **Validate path particle** - Checks if any other particle blocks the path
    - **Validate path gates** - Checks if a shut voltage gate blocks the path
    - **Check unibranch validity** - Checks if the pair is in the same branch

### Metrics <sup>M</sup>
1. **Module**: Metrics
1. **Objective**: Saves output generated into respective files
1. **Functions**:
    - Update Particle movements - update particle positions by generating a sequence of positions steps for the particles.
    - Update Nanowire states - update the Nanowire state matrix
    - Update Particles' Braid positions - update the particle position in the Braid sequence
    - Update Final particle positions - update the final particle positions on the Nanowire

### Measurement <sup>M</sup>
1. **Module**: Measurement
1. **Objective**: Measures outcomes based on the given Fusion rules and channels

### Animation <sup>M</sup> <sup>C</sup>
1. **Module**: Animation
1. **Class**: Animation
1. **Objectives**:
    - Braid-table animation
    - Nanowire particle movement animation
