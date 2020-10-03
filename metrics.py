import copy

# Update Particle positions by generating a similar sequence for the particles.
def update_particle_movements(file,par,path,vertices,voltages):
    try:
        fw = open(file,'a')
        line = "{},{}".format(par,'-'.join(vertices[v] for v in path))
        line = "{},{}".format(line,','.join(voltages))
        fw.write(line+'\n')
        fw.close()
        print(line)
    except IOError as err:
        print(err)

# Update Nanowire state matrix
def update_nanowire_state(file,positions,path,vertices,par,voltages):
    try:
        fw = open(file,'a')
        for p in path:
            pos_temp = copy.copy(positions)
            pos = vertices[p]
            # if pos == 'x1' or pos == 'x2':
                # continue
            pos_temp[par-1] = pos
            line = "{}".format(','.join(pos_temp))
            line = "{},{}".format(line,','.join(voltages))
            fw.write(line+'\n')
        fw.close()
    except IOError as err:
        print(err)
