import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME
from util import lattice_architecture

circ = random_circuit(num_qubits=7,
                      depth=2,
                      seed=999)

arc = lattice_architecture(3,2) + [(0, 6)]


class Level7(Game):

    def __init__(self,  **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 7",  **kwargs)


if __name__ == '__main__':
    lev = Level7()
    plt.show()
