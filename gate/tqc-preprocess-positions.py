"""
Particle positions preprocessing
"""

import os
import sys
sys.path.append(os.path.abspath('../'))

from package import exception, graph, nanowire, compiler, braid, validation, metrics
from package.nanowire import Nanowire
from package.compiler import Compiler
from package.braid import Braiding
from package.utility import Utility

def initialize_nanowire(positions, file1, file2, file3):
    """
    Initializing the Nanowire object
    """
    try:
        structure = nanowire.read_nanowire_structure_as_intersections(file1)
        vertex = nanowire.read_nanowire_vertices(file2)
        matrix = graph.adjacency_matrix(file3)
        graph.validate_matrix(matrix)
        nanowire_obj = Nanowire(matrix, vertex, structure)

        nanowire_obj.initiate_nanowire(positions)
        nanowire_obj.initiate_positions_inner_outer()
        return nanowire_obj
    except IOError:
        raise
    except SyntaxError:
        raise

if __name__ == '__main__':
    res = 1
    try:
        positions = compiler.read_particle_positions(sys.argv[4])
        nanowire_obj = initialize_nanowire(positions, sys.argv[1], sys.argv[2], sys.argv[3])
        nanowire_b = nanowire.read_nanowire_structure_as_branches(sys.argv[1])
        check, intersections, branches, particles = validation.validate_particle_positions(nanowire_obj, nanowire_b, positions, sys.argv[8], sys.argv[9])
        # print("Gate: {}\nParticle orientation: {}\nNanowire state validity: {}".format(sys.argv[10], sys.argv[8], check))
        # print(check, intersections, branches, particles)
        if check is False and len(particles) > 2 and len(set(branches)) > 1:
            compiler_obj = Compiler(None, None, positions)
            braid = Braiding(nanowire_obj, compiler_obj)
            utility = Utility()
            final_positions, pair = braid.move_particles(utility, intersections, branches, particles, sys.argv[8], sys.argv[6], sys.argv[7], sys.argv[10])
            metrics.update_final_particle_positions(sys.argv[5], final_positions)

            # if len(pair) > 0:
            #     n = len(compiler_obj.positions)
            #     line_pos = Utility.get_par_braid_pos(n)
            #     line_pos = Utility.update_par_braid_pos(line_pos, pair)
            #     print(line_pos)
            #     metrics.update_particle_line_positions(sys.argv[11], pair, line_pos)
        res = 0
    except IOError as err:
        print(err)
    except SyntaxError as err:
        print(err)
    except exception.InvalidNanowireStateException as err:
        print(err)
    except exception.InvalidMovementException as err:
        print(err)
    finally:
        exit(res)
