import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME


circ = random_circuit(num_qubits=6,
                      depth=2,
                      seed=0)

arc = [(0, 1), (0, 2), (0, 3), (0, 4), (0,5)]


class Level6(Game):

    def __init__(self,  **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 6",  **kwargs)


if __name__ == '__main__':
    lev = Level6()
    plt.show()
