import copy

# Update Particle positions by generating a similar sequence for the particles.
def update_particle_movements(file,par,path,vertices,v11,v12,v21,v22):
    try:
        fw = open(file,'a')
        line = "{},{}".format(par,'-'.join(vertices[v] for v in path))
        print(line)
        line = "{},{},{},{},{}".format(line,v11,v12,v21,v22)
        fw.write(line+'\n')
        fw.close()
    except IOError as err:
        print(err)

# Update Nanowire state matrix
def update_nanowire_state(file,positions,path,vertices,par,v11,v12,v21,v22):
    try:
        fw = open(file,'a')
        for p in path:
            pos_temp = copy.copy(positions)
            pos = vertices[p]
            if pos == 'x1' or pos == 'x2':
                continue
            pos_temp[par-1] = pos
            line = "{}".format(','.join(pos_temp))
            line = "{},{},{},{},{}".format(line,v11,v12,v21,v22)
            fw.write(line+'\n')
        fw.close()
    except IOError as err:
        print(err)