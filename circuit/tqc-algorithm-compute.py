"""
Circuit compute: Particle position preprocessing and Braiding algorithm
"""

import os
import sys
import yaml
sys.path.append(os.path.abspath('../'))

from package import exception, graph, nanowire, compiler, braid, validation, metrics, utility
from package.braid import BraidingCNOT, BraidingHadamard, BraidingPauliX, BraidingPhaseS
from package.nanowire import Nanowire
from package.compiler import Compiler
from package.braid import Braiding
from package.utility import Utility

def initialize_nanowire(structure):
    """
    Initializing the Nanowire object which has
    """
    try:
        nanowire_structure = nanowire.nanowire_yaml_to_structure_intersections(structure)
        vertices = nanowire.read_nanowire_vertices(sys.argv[4])
        matrix = graph.adjacency_matrix(sys.argv[5])
        graph.validate_matrix(matrix)
        nanowire_obj = Nanowire(matrix, vertices, nanowire_structure)
        return nanowire_obj
    except IOError:
        raise
    except SyntaxError:
        raise

def initiate_nanowire(nanowire_obj, positions):
    """(matrix, vertex, nanowire, cutoff_adj, cutoff_opp)"""
    nanowire_obj.initiate_nanowire(positions)
    nanowire_obj.initiate_positions_inner_outer()
    nanowire_obj.initiate_cutoff_voltage_pairs_adj()
    nanowire_obj.initiate_cutoff_voltage_pairs_opp()

def initialize_positions(nanowire_obj, groups):
    try:
        positions = compiler.read_particle_positions(sys.argv[6])
        if groups is not None:
            braid_positions = compiler.read_braid_positions(sys.argv[7])
            positions = utility.get_positions_from_braids(nanowire_obj.nanowire, braid_positions)
        return positions
    except IOError:
        raise

def initialize_compiler(gate, positions):
    """
    Initialize Compiler
    """
    try:
        sequence, direction = compiler.yaml_to_structure_sequence(gate)
        compiler_obj = Compiler(sequence, direction, positions)
        return compiler_obj
    except IOError:
        raise

def get_braid_class(nanowire_obj, compiler_obj, gate):
    braid = None
    if gate == 'cnot':
        braid = BraidingCNOT(nanowire_obj, compiler_obj)
    elif gate == 'hadamard':
        braid = BraidingHadamard(nanowire_obj, compiler_obj)
    elif gate == 'pauli-x':
        braid = BraidingPauliX(nanowire_obj, compiler_obj)
    elif gate == 'phase-s':
        braid = BraidingPhaseS(nanowire_obj, compiler_obj)
    return braid

#
def preprocess_positions(gate, nanowire_obj, nanowire_b, compiler_obj, braid_obj, positions, utility):
    """Preprocessing positions before every gate"""
    try:
        check, intersections, branches, particles = validation.validate_particle_positions\
            (nanowire_obj, nanowire_b, positions, gate.get('branch_config'), str(gate.get('groups')))
        # print("Gate: {}\nParticle orientation: {}\nNanowire state validity: {}"\
            # .format(gate.get('gate'), gate.get('branch_config'), check))
        # print(check, intersections, branches, particles)
        if check is False and len(particles) > 2 and len(set(branches)) > 1:
            final_positions,pair = braid_obj.move_particles(utility, intersections, branches, particles,
                gate.get('branch_config'), sys.argv[8], sys.argv[9], gate.get('gate'))
            metrics.update_final_particle_positions(sys.argv[6], final_positions)

            # if len(pair) > 0:
            #     n = len(compiler_obj.positions)
            #     braid_positions = Utility.get_par_braid_pos(n)
            #     braid_positions = Utility.update_par_braid_pos(braid_positions, pair)
            #     metrics.update_particle_line_positions(sys.argv[7], pair, braid_positions)
    except IOError:
        raise
    except SyntaxError:
        raise
    except exception.InvalidNanowireStateException:
        raise
    except exception.InvalidMovementException:
        raise

#
def braid_particles(nanowire_obj, compiler_obj, braid_obj, utility, groups):
    """
    Performing braiding on each sequence
    """
    try:
        # assert(braid is not None)
        n = len(compiler_obj.positions)
        braid_positions = Utility.get_par_braid_pos(n)
        braid_pos_mapping = {}
        if groups is not None:
            braid_pos_old = compiler.read_braid_positions(sys.argv[7])
            braid_pos_mapping = dict(zip(braid_positions, braid_pos_old))
            braid_positions = braid_pos_old
        metrics.update_particle_line_positions(sys.argv[7], (0,0), braid_positions)

        for i in range(len(compiler_obj.sequence)):
            pair = compiler_obj.sequence[i]
            dir  = compiler_obj.direction[i]
            utility.reset_variables(compiler_obj.positions)
            utility.refresh_zero_modes()
            pair0 = pair
            if groups is not None:
                pair0 = (braid_pos_mapping[pair[0]], braid_pos_mapping[pair[1]])
            print("\033[0;33m----- Braiding particles {} -----\033[0m".format(pair0))

            intersection = Utility.get_intersection(nanowire_obj.nanowire, compiler_obj.positions[pair[0]-1])
            condition = validation.check_unibranch_validity(pair, compiler_obj.positions, intersection)

            if condition:
                braid_obj.braid_particles_same_branch(pair, utility, sys.argv[8], sys.argv[9])
            else:
                braid_obj.braid_particles_diff_branch(pair, utility, sys.argv[8], sys.argv[9])

            braid_positions = Utility.update_par_braid_pos(braid_positions, pair0)
            metrics.update_particle_line_positions(sys.argv[7], pair0, braid_positions)

        metrics.update_final_particle_positions(sys.argv[6], compiler_obj.positions)
    except exception.NoEmptyPositionException:
        print("\033[0;31m----- Braiding interrupted -----\033[0m")
        raise
    except exception.InvalidNanowireStateException:
        print("\033[0;31m----- Braiding interrupted -----\033[0m")
        raise
    except exception.PathBlockedException:
        print("\033[0;31m----- Braiding interrupted -----\033[0m")
        raise

#
if __name__ == '__main__':
    res = 1
    gate_ext = sys.argv[3]
    input_dir = "./inputs/"
    groups = None
    try:
        with open(sys.argv[1]) as stream1, open(sys.argv[2]) as stream2:
            circuit = yaml.safe_load(stream1)
            nanowire_config = yaml.safe_load(stream2)
            structure = nanowire_config.get('structure')
            nanowire_obj = initialize_nanowire(structure)
            nanowire_b = nanowire.nanowire_yaml_to_structure_branches(structure)

            i = -1
            for gate in circuit.get('gates'):
                i += 1
                gate_file = input_dir + gate + gate_ext
                with open(gate_file) as stream:
                    gate_config = yaml.safe_load(stream)
                    positions = initialize_positions(nanowire_obj, groups)
                    if i == 0:
                        initiate_nanowire(nanowire_obj, positions)
                    compiler_obj = initialize_compiler(gate_config, positions)
                    braid_obj = get_braid_class(nanowire_obj, compiler_obj, gate)
                    utility = Utility()

                    print('\n\033[1;36mStarted {} preprocessing...\033[0m'.format(gate))
                    preprocess_positions(gate_config, nanowire_obj, nanowire_b, compiler_obj, braid_obj, positions, utility)
                    print('\n\033[1;36mStarted {} braiding...\033[0m'.format(gate))
                    braid_particles(nanowire_obj, compiler_obj, braid_obj, utility, groups)
                    print("\033[0;32m----- {} braiding completed -----\033[0m".format(gate))
                    groups = str(gate_config.get('groups'))

        res = 0
    except IOError as err:
        print(err)
    except SyntaxError as err:
        print(err)
    except yaml.YAMLError as err:
        print(err)
    except exception.InvalidNanowireStateException as err:
        print(err)
    except exception.InvalidMovementException as err:
        print(err)
    finally:
        exit(res)
