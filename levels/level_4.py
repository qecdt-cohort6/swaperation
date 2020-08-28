import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME

circ = random_circuit(num_qubits=5,
                      depth=3,
                      seed=123)

arc = [(0,1), (1,2), (1,3), (3,4), (4,0)]


class Level4(Game):

    def __init__(self, *args, **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 4", *args, **kwargs)


if __name__ == '__main__':
    lev = Level4()
    plt.show()
