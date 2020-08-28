import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME


circ = random_circuit(num_qubits=4,
                      depth=4,
                      seed=123)
arc = [(0, 1), (1, 3), (2, 3)]


class Level3(Game):

    def __init__(self,  **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 3", **kwargs)


if __name__ == '__main__':
    lev = Level3()
    plt.show()
