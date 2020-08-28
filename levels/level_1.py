import sys, os
sys.path.append(os.path.abspath('..'))
import matplotlib.pyplot as plt
from qiskit.circuit import QuantumCircuit

from game import Game, NAME


circ = QuantumCircuit(3)
circ.cx(0, 1)
circ.cx(1, 2)

arc = [(0, 1), (0, 2)]


class Level1(Game):

    def __init__(self, **kwargs):
        super().__init__(circ, arc, title=NAME + " Level 1", **kwargs)


if __name__ == '__main__':
    lev = Level1()
    plt.show()
