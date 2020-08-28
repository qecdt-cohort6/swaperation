"""
This module contains functions necessary to check the correctness of the output of the game. They are:
* Checking if the output circuit and the input circuit are equivalent (`check_equiv_under_perms`).
* Checking if the output circuit only contains gates native to the architecture (`check_circuit_compatible_with_arc`).
"""

from qiskit import Aer, execute
import numpy as np


def order_rev_perm(n):
    p = [i for i in reversed(range(n))]
    return permutation(n, p)


def bin_to_int(b):
    n = 0
    i = 0
    for a in reversed(b):
        if a == 1:
            n += 2**i
        i += 1
    return n


def int_to_bin(x, n):
    b = [int(y) for y in list("{0:b}".format(x))]
    for j in range(len(b), n):
        b.insert(0, 0)
    return b


def swap(n=2, qubits=(0, 1)):
    mat = np.zeros((2**n, 2**n))
    for i in range(2**n):
        binary = int_to_bin(i, n)
        binary_out = []
        for j in range(n):
            if j == qubits[0]:
                binary_out.append(binary[qubits[1]])
            elif j == qubits[1]:
                binary_out.append(binary[qubits[0]])
            else:
                binary_out.append(binary[j])
        out = bin_to_int(binary_out)
        mat[i, out] = 1
    return mat


def cnot(control, target, n):
    mat = np.zeros((2**n, 2**n), dtype='complex')
    for i in range(2**n):
        binary = int_to_bin(i, n)
        binary_out = binary
        if binary[control] == 1:
            binary_out[target] = (binary_out[target] + 1)%2
        out = bin_to_int(binary_out)
        mat[i, out] = 1
    return mat


def permutation(n=2, new_ordering=(0, 1)):
    """
    Find permutation matrix on the qubit basis vectors given a new ordering (permutation) of qubits
    """
    mat = np.zeros((2**n, 2**n))
    for i in range(2**n):
        binary = int_to_bin(i, n)
        binary_out = []
        for j in range(n):
            binary_out.append(binary[new_ordering[j]])
        out = bin_to_int(binary_out)
        mat[out, i] = 1
    return mat


def perm_diff(pi, po):
    pdiff = []
    for a in po:
        pdiff.append(pi.index(a))
    return pdiff


def check_equiv_under_perms(circ_1, circ_2, initial_placement, final_mapping, n):
    """
    """
    backend = Aer.get_backend('unitary_simulator')

    job = execute(circ_1, backend)
    u_1 = job.result().get_unitary(circ_1, decimals=5)
    u1 = order_rev_perm(n) @ u_1 @ order_rev_perm(n)  # rewrite the unitary in the qubit order (0, 1, 2, 3, ...)

    job = execute(circ_2, backend)
    u_2 = job.result().get_unitary(circ_2, decimals=5)
    u2 = order_rev_perm(n) @ u_2 @ order_rev_perm(n)

    return check_unitaries(u1, u2, initial_placement, final_mapping, n)


def check_unitaries(u1, u2, initial, final, n, r_to_l=False):
    p1 = permutation(n, initial)
    p2 = permutation(n, perm_diff(initial, final))
    return np.allclose(u1, np.linalg.inv(p1) @ np.linalg.inv(p2) @ u2 @ p1)


def check_circuit_compatible_with_arc(circuit, arc):
    """
    Determine if a given circuit is compatible with a given architecture, that is, the only two-qubit gates in
    the circuit are native to the architecture.

    :param circuit: a `qistkit.QuantumCircuit` object.
    :param arc: as a list of edges.
    :return:
    """
    for g in circuit.data:  # for each gate
        if len(g[1]) > 1:  # if 2 qubit gate
            k = tuple((g[1][0].index, g[1][1].index)) # get indices

            if k not in arc and k[::-1] not in arc:
                print(k)
                print(arc)
                return False

    print('passed')

    return True

