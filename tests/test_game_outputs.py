import os
import ast
from qiskit import QuantumCircuit

from check_outputs import check_equiv_under_perms, check_circuit_compatible_with_arc


def test_game_outputs(verbose=False):
    """
    This function loops over all the files in the `game_outputs` directory, and tests to see if the initial and final circuit
    of a run of the game are equivalent (using `check_equiv_under_perms` from `check_outputs.py`), and tests if the final
    circuit can be directly ran on the specified hardware (using `check_circuit_compatible_with_arc` from `check_outputs.py`).

    Output game data for testing can be generated from `generate_game_outputs.py`.
    """

    filenames = os.listdir('game_outputs')
    for filename in filenames:

        filepath = os.path.join('game_outputs', filename)
        if filename.startswith('initial_circuit'):
            if verbose:
                print(filename)
            initial_circ = QuantumCircuit.from_qasm_file(filepath)
            final_circ = QuantumCircuit.from_qasm_file(filepath.replace('initial_circuit', 'final_circuit'))
            with open(filepath.replace('initial_circuit', 'details'), 'r') as file:
                details = ast.literal_eval(file.read().replace('\n', '')) # converts to dictionary

            try:
                num_qubits = details['num_arc_qubits']
            except KeyError:
                num_qubits = details['num_qubits']


            initial_lp_map = details['initial_mapping']
            initial_pl_map = [initial_lp_map.index(i) for i in range(num_qubits)]
            final_lp_map = details['final_mapping']
            final_pl_map = [final_lp_map.index(i) for i in range(num_qubits)]
            assert(check_equiv_under_perms(initial_circ, final_circ, initial_pl_map, final_pl_map,num_qubits))

            arc = details['architecture']
            assert(check_circuit_compatible_with_arc(circuit=final_circ, arc=arc))


if __name__ == '__main__':
    test_game_outputs(verbose=True)
    print('---------------------------')
    print('All tests passed!')