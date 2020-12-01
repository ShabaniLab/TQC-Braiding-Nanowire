import os
import sys
import yaml
sys.path.append(os.path.abspath('../'))
from package import compiler, measurement

if __name__ == '__main__':
    res = 1
    try:
        with open(sys.argv[1]) as stream1, open(sys.argv[2]) as stream2:
            circuit = yaml.safe_load(stream1)
            qubits = int(circuit.get('qubits'))
            fusion = yaml.safe_load(stream2)
            rules = measurement.yaml_to_structure_rules(fusion)
            channels = measurement.yaml_to_structure_channels(fusion, qubits)

            positions_final = compiler.read_particle_positions(sys.argv[3])
            pairs = measurement.extract_pairs(positions_final, sys.argv[4], sys.argv[5])

            chl, qb = measurement.measure_particles(pairs,rules,channels)
            measurement.save_measurements(chl, qb)
        res = 0
    except IOError as err:
        print(err)
    except yaml.YAMLError as err:
        print(err)
    finally:
        exit(res)
