
## Validation phase

# Retrieves the expected inal positions of the particles to be braided
def get_final_positions():
    ;

# Retrieves the empty positions on adjacent empty branches (this can either be the nearest or farthest locations on the branch)
def get_empty_positions():
    ;

# Nanowire Validation Algorithm which returns either True or False for the expected final positions.
def validate_nanowire_state():
    ;

## Braiding phase

# Get Voltage Gate Changes if braiding involves particles from different zero modes.
def get_voltage_changes():
    ;

# Update the Adjacency Matrix as Gate variations may create a disconnected graph.
def retrieve_isolated_branches():
    ;

# Dijkstra's algorithm gives the shortest path for a particle from it's current position to a valid final position.
def get_shortest_path():
    ;

# Update Particle positions by generating a similar sequence for the particles.
def update_particle_movements():
    ;

#
def braid_particles():
    for tup in sequence:
        par1 = tup[0]-1
        par2 = tup[1]-1
        pos1 = positions[pa1]
        pos2 = positions[pa2]
