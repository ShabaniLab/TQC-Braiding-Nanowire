"""
Nanowire preprocessing
"""

import os
import sys
sys.path.append(os.path.abspath('../'))
from package import nanowire

if __name__ == '__main__':
    res = 1
    try:
        nanowire_structure = nanowire.read_nanowire_structure_as_branches(sys.argv[1])
        nanowire_vertices = nanowire.extract_nanowire_vertices(nanowire_structure)
        nanowire.print_nanowire_vertices(sys.argv[2],nanowire_vertices)
        nanowire_adj_matrix = nanowire.construct_adj_matrix(nanowire_vertices,nanowire_structure)
        nanowire.print_adj_matrix(sys.argv[3],nanowire_adj_matrix)
        res = 0
    except IOError as err:
        print(err)
    finally:
        exit(res)
