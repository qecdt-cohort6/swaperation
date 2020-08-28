import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME
from util import lattice_architecture


circ = random_circuit(num_qubits=8,
                      depth=3,
                      seed=123)

#circ = random_circuit(8, 3, 15, seed=0)
arc = lattice_architecture(4, 2)


class Level8(Game):

    def __init__(self,  **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 8",  **kwargs)


if __name__ == '__main__':
    lev = Level8()
    plt.show()
