import os
import sys
sys.path.append(os.path.abspath('../'))
from package import measurement

if __name__ == '__main__':
    try:
        positions_initial, positions_final = measurement.read_positions(sys.argv[1])
        rules = measurement.read_fusion_rules(sys.argv[2])
        channels = measurement.read_fusion_channels(sys.argv[3], int(sys.argv[6]))
        pairs = measurement.extract_pairs(positions_final, sys.argv[4], sys.argv[5])

        chl, qb = measurement.measure_particles(pairs,rules,channels)
        measurement.save_measurements(chl, qb)
    except IOError as err:
        print(err)
