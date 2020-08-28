import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit.random import random_circuit

from game import Game, NAME
from util import lattice_architecture


circ = random_circuit(num_qubits=9,
                      depth=3,
                      seed=12345)
#circ = random_circuit(9, 5, 20, seed=0)
arc = lattice_architecture(3,3)


class Level9(Game):

    def __init__(self,  **kwargs):
        super().__init__(circ, arc,  title=NAME + " Level 9",  **kwargs)


if __name__ == '__main__':
    lev = Level9()
    plt.show()
