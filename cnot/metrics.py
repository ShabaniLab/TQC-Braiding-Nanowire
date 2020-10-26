"""
TQC Braiding Nanowire Algorithm - Output
"""

import copy

# 1. Update Particle positions by generating a similar sequence for the particles.
def update_particle_movements(file,pair,par,path,vertices,voltages):
    try:
        fw = open(file,'a')
        line = "{},{},{},{}".format(str(pair[0]),str(pair[1]),par,'-'.join(vertices[v] for v in path))
        line = "{},{}".format(line,','.join(voltages))
        fw.write(line+'\n')
        fw.close()
        print(line)
    except IOError as err:
        print(err)

# 2. Update Nanowire state matrix
def update_nanowire_state(file,pair,positions,path,vertices,par,voltages):
    try:
        fw = open(file,'a')
        for p in path:
            pos_temp = copy.copy(positions)
            pos = vertices[p]
            # if pos == 'x1' or pos == 'x2':
                # continue
            pos_temp[par-1] = pos
            line = "{},{},{}".format(str(pair[0]),str(pair[1]),','.join(pos_temp))
            line = "{},{}".format(line,','.join(voltages))
            fw.write(line+'\n')
        fw.close()
    except IOError as err:
        print(err)

# 3. Update Braid particles positions
def update_particle_line_positions(file,pair,positions):
    try:
        fw = open(file,'a')
        pos = copy.copy(positions)
        newpos = [str(e) for e in positions]
        line = "{},{},{}".format(str(pair[0]),str(pair[1]),','.join(newpos))
        fw.write(line+'\n')
        fw.close()
    except IOError as err:
        print(err)

# 4. Update Final particle positions
def update_final_particle_positions(file,positions):
    try:
        fw = open(file,'a')
        line = ','.join(positions)
        fw.write(line)
        fw.close()
    except IOError as err:
        print(err)
