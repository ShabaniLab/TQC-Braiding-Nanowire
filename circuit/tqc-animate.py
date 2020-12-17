import os
import sys
import yaml
sys.path.append(os.path.abspath('../'))
from package import animation
from package.animation import Animation

def initiate_file_io(anima, nanowire_config):
    """
    Calls all the File I/O functions
    """
    try:
        anima.nanowire_yaml_to_structure_graph(nanowire_config.get('positions'))
        anima.read_nanowire_matrix(sys.argv[3])
        anima.read_nanowire_vertices(sys.argv[4])
        anima.read_nanowire_state(sys.argv[5])
        anima.read_braid_particle_pos(sys.argv[6])
    except IOError:
        raise

if __name__ == '__main__':
    res = 1
    try:
        with open(sys.argv[1]) as stream1, open(sys.argv[2]) as stream2:
            circuit_config = yaml.safe_load(stream1)
            nanowire_config = yaml.safe_load(stream2)
            anima = Animation(circuit_config.get('application'), sys.argv[7])
            initiate_file_io(anima, nanowire_config)
            if circuit_config.get('animations') is not None:
                if "braid" in circuit_config.get('animations'):
                    print('Animating braid...')
                    anima.animate_braid()
                if "nanowire" in circuit_config.get('animations'):
                    print('Animating nanowire...')
                    anima.initialize_network_graph()
                    anima.animate_nanowire()
        res = 0
    except IOError as err:
        print(err)
    except yaml.YAMLError as err:
        print(err)
    finally:
        exit(res)
