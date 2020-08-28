import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME
from util import lattice_architecture


circ = random_circuit(num_qubits=10,
                      depth=3,
                      seed=12)

arc = lattice_architecture(5,2)


class Level10(Game):

    def __init__(self,  **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 10",  **kwargs)


if __name__ == '__main__':
    lev = Level10()
    plt.show()
