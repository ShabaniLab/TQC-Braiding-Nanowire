import os
import sys
sys.path.append(os.path.abspath('../'))
from package import animation
from package.animation import Animation

if __name__ == '__main__':
    res = 1
    try:
        anima = Animation(sys.argv[6], sys.argv[7])
        anima.initiate_file_io(sys.argv)
        # print('Animating braid...')
        # anima.animate_braid()
        print('Animating nanowire...')
        anima.initialize_network_graph()
        anima.animate_nanowire()
        res = 0
    except IOError as err:
        print(err)
    finally:
        exit(res)
