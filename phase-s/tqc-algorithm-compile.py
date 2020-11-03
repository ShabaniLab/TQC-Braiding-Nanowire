import os
import sys
sys.path.append(os.path.abspath('../'))

from package import graph
from package import exception
from package import nanowire
from package import compiler
from package import braid
from package import utility
from package import metrics
from package import validation

from package.compiler import Compiler
from package.nanowire import Nanowire
from package.braid import BraidingCNOT, BraidingHadamard, BraidingPauliX, BraidingPhaseS
from package.utility import Utility

def initialize_compiler():
    """
    Initializing the Nanowire object which has
    (matrix, vertex, nanowire, cutoff_adj, cutoff_opp)
    """
    try:
        positions = compiler.read_particle_positions(sys.argv[5])
        sequence, direction = compiler.read_braid_sequence(sys.argv[4])
        compiler_obj = Compiler(sequence, direction, positions)
        return compiler_obj
    except IOError:
        raise

def initialize_nanowire(positions):
    """
    Initializing the Nanowire object which has
    (matrix, vertex, nanowire, cutoff_adj, cutoff_opp)
    """
    try:
        structure = nanowire.read_nanowire_structure_as_intersections(sys.argv[1])
        vertex = nanowire.read_nanowire_vertices(sys.argv[2])
        matrix = graph.adjacency_matrix(sys.argv[3])
        graph.validate_matrix(matrix)
        nanowire_obj = Nanowire(matrix, vertex, structure)

        nanowire_obj.initiate_nanowire(positions)
        nanowire_obj.initiate_positions_inner_outer()
        nanowire_obj.initiate_cutoff_voltage_pairs_adj()
        nanowire_obj.initiate_cutoff_voltage_pairs_opp()
        return nanowire_obj
    except IOError:
        raise
    except SyntaxError:
        raise

def get_braid_class(nanowire_obj, compiler_obj):
    gate = sys.argv[9]
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

def braid_particles(nanowire_obj, compiler_obj):
    """
    Performing braiding on each sequence
    """
    try:
        braid = get_braid_class(nanowire_obj, compiler_obj)
        assert(braid is not None)
        utility = Utility()
        n = len(compiler_obj.positions)
        line_pos = Utility.get_par_braid_pos(n)
        metrics.update_particle_line_positions(sys.argv[8], compiler_obj.sequence[0], line_pos)
        for i in range(len(compiler_obj.sequence)):
            pair = compiler_obj.sequence[i]
            dir  = compiler_obj.direction[i]
            utility.reset_variables(compiler_obj.positions)
            utility.refresh_zero_modes()
            print("----- Braiding particles {} -----".format(pair))

            intersection = Utility.get_intersection(nanowire_obj.nanowire, compiler_obj.positions[pair[0]-1])
            condition = validation.check_unibranch_validity(pair, compiler_obj.positions, intersection)

            if condition:
                braid.braid_particles_same_branch(pair, utility, sys.argv[6], sys.argv[7])
            else:
                braid.braid_particles_diff_branch(pair, utility, sys.argv[6], sys.argv[7])

            line_pos = Utility.update_par_braid_pos(line_pos, pair)
            metrics.update_particle_line_positions(sys.argv[8], pair, line_pos)

        metrics.update_final_particle_positions(sys.argv[5], compiler_obj.positions)
        print("----- Braiding completed -----")
    except exception.NoEmptyPositionException:
        print("----- Braiding interrupted -----")
        raise
    except exception.InvalidNanowireStateException:
        print("----- Braiding interrupted -----")
        raise
    except exception.PathBlockedException:
        print("----- Braiding interrupted -----")
        raise

if __name__ == '__main__':
    try:
        compiler_obj = initialize_compiler()
        nanowire_obj = initialize_nanowire(compiler_obj.positions)
        braid_particles(nanowire_obj, compiler_obj)
    except IOError as err:
        print(err)
    except SyntaxError as err:
        print(err)
    except exception.NoEmptyPositionException as err:
        print(err)
    except exception.InvalidNanowireStateException as err:
        print(err)
    except exception.PathBlockedException as err:
        print(err)
