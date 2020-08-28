import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME


circ = random_circuit(num_qubits=4,
                          depth=3,
                          seed=1235)

arc = [(0, 1), (1, 2), (2, 3), (3,0), (0,2)]


class Level2(Game):

    def __init__(self, **kwargs):
        super().__init__(circ, arc, title=NAME + " Level 2", **kwargs)


if __name__ == '__main__':
    lev = Level2()
    plt.show()
