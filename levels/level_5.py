import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME
from util import lattice_architecture

circ = random_circuit(num_qubits=6,
                      depth=3,
                      seed= 123)

arc = lattice_architecture(2, 3)


class Level5(Game):

    def __init__(self, *args, **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 5", *args, **kwargs)


if __name__ == '__main__':
    lev = Level5()
    plt.show()
