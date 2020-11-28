"""
Particle positions preprocessing
"""

import os
import sys
sys.path.append(os.path.abspath('../'))

from package import exception, graph, nanowire, compiler, braid, validation
from package.nanowire import Nanowire
from package.braid import Braiding

def initialize_nanowire(file1, file2, file3):
    """
    Initializing the Nanowire object
    """
    try:
        structure = nanowire.read_nanowire_structure_as_intersections(file1)
        vertex = nanowire.read_nanowire_vertices(file2)
        matrix = graph.adjacency_matrix(file3)
        graph.validate_matrix(matrix)
        nanowire_obj = Nanowire(matrix, vertex, structure)
        return nanowire_obj
    except IOError:
        raise
    except SyntaxError:
        raise

if __name__ == '__main__':
    res = 1
    try:
        nanowire_obj = initialize_nanowire(sys.argv[1], sys.argv[2], sys.argv[3])
        nanowire_b = nanowire.read_nanowire_structure_as_branches(sys.argv[1])
        positions = compiler.read_particle_positions(sys.argv[4])
        check, intersections, branches, particles = validation.validate_particle_positions(nanowire_obj, nanowire_b, positions, sys.argv[8], sys.argv[9])
        print("Gate: {}\nParticle orientation: {}\nNanowire state validity: {}".format(sys.argv[10], sys.argv[8], check))
        if not check:
            Braiding.move_particles(nanowire_obj, positions, intersections, branches, particles, sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
        res = 0
    except IOError as err:
        print(err)
    except SyntaxError as err:
        print(err)
    except InvalidNanowireStateException as err:
        print(err)
    finally:
        exit(res)
