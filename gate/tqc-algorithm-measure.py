import os
import sys
sys.path.append(os.path.abspath('../'))
from package import compiler, measurement

if __name__ == '__main__':
    res = 1
    try:
        positions_final = compiler.read_particle_positions(sys.argv[1])
        rules = measurement.read_fusion_rules(sys.argv[2])
        channels = measurement.read_fusion_channels(sys.argv[3], int(sys.argv[6]))
        pairs = measurement.extract_pairs(positions_final, sys.argv[4], sys.argv[5])

        chl, qb = measurement.measure_particles(pairs,rules,channels)
        measurement.save_measurements(chl, qb)
        res = 0
    except IOError as err:
        print(err)
    finally:
        exit(res)
