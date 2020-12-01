"""
Nanowire preprocessing
"""

import os
import sys
import yaml
sys.path.append(os.path.abspath('../'))
from package import nanowire

if __name__ == '__main__':
    res = 1
    try:
        with open(sys.argv[1]) as stream:
            nanowire_config = yaml.safe_load(stream)

            vertices = nanowire_config.get('vertices').split(',')
            nanowire.print_nanowire_vertices(sys.argv[2],vertices)

            structure = nanowire_config.get('structure')
            x1 = structure.get('x1')
            x2 = structure.get('x2')
            x1.extend(x2)
            nanowire_structure = []
            for b in x1:
                nanowire_structure.append(b.split(','))
            nanowire_adj_matrix = nanowire.construct_adj_matrix(vertices,nanowire_structure)
            nanowire.print_adj_matrix(sys.argv[3],nanowire_adj_matrix)
        res = 0
    except IOError as err:
        print(err)
    finally:
        exit(res)
