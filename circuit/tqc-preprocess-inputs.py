"""
Inputs preprocessing
"""
import sys
import yaml

if __name__ == '__main__':
    res = 1
    key_pair = "Par1,Par2"
    key_const = "Particle,Path"
    key_pars = ""
    key_volts = ""
    try:
        with open(sys.argv[1]) as stream1:
            circuit_config = yaml.safe_load(stream1)
            particles = int(circuit_config.get('particles'))
            pars = ["P"+str(p+1) for p in range(particles)]
            key_pars = ",".join(pars)

        with open(sys.argv[2]) as stream2:
            nanowire_config = yaml.safe_load(stream2)
            voltages = int(nanowire_config.get('voltages'))
            volts = ["Vg"+str(int(i/2)+1)+str(i%2+1) for i in range(voltages)]
            key_volts = ",".join(volts)

        with open(sys.argv[3], 'w') as fr:
            header_file_mvmts = "{},{},{}".format(key_pair, key_const, key_volts)
            fr.write(header_file_mvmts+'\n')
            fr.close()

        with open(sys.argv[4], 'w') as fr:
            header_file_state = "{},{},{}".format(key_pair, key_pars, key_volts)
            fr.write(header_file_state+'\n')
            fr.close()

        with open(sys.argv[5], 'w') as fr:
            header_file_braid = "{},{}".format(key_pair, key_pars)
            fr.write(header_file_braid+'\n')
            fr.close()
        res = 0
    except IOError as err:
        print(err)
    except yaml.YAMLError as err:
        print(err)
    finally:
        exit(res)
