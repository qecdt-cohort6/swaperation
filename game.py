"""
This is the main module in which we define the Game class.
"""

import os
import time
import networkx as nx
import matplotlib.pyplot as plt

from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit.quantumregister import Qubit
from qiskit.circuit.library.standard_gates.u1 import U1Gate
from qiskit.circuit.library.standard_gates.u2 import U2Gate
from qiskit.circuit.library.standard_gates.u3 import U3Gate
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller

from util import compose


BASE_NODE_COLOR = 'seagreen'
HIGHLIGHTED_NODE_COLOR = 'khaki'
CIRCUIT_EDGE_COLOR = 'mediumblue'
HIGHLIGHTED_CIRCUIT_EDGE_COLOR = 'mediumseagreen'
COMPLETED_CIRCUIT_EDGE_COLOR = 'k'
ARCHITECTURE_EDGE_COLOR = 'r'

NAME = "Swaperation"


class Game:
    """
        The main class representing the game.
        The `plot` function renders the current game as a graph, via an interactive `matplotlib` plot, and the
        `onClick` function handles all of the events (from clicking).
    """
    
    def __init__(self, circuit, architecture, title=None, output_filename=None, output_dir=None, best_score=None):
        """

        :param circuit:             A `qiskit.QuantumCircuit` object.
        :param architecture:        A list of edges as tuples,  e.g. [(1,2), (2,3), (1,3)].
        :param title:               Title of the plot as string, e.g. "Level 5".
        :param output_filename:     Filename of the data of game output. If none then no data saved.
        :param output_dir:          A folder to save the game output. If `None` passed and `output_filename`
                                    is not `None` then the data saves in the current directory.

        :param best_score:          This is used when replaying the game or resetting,
                                    to keep track of the best previous score.
        """

        self.title = title if title is not None else NAME
        self.output_filename = output_filename
        self.output_dir = output_dir

        # put circuit in native gate form
        pass_ = Unroller(['id', 'u1', 'u2', 'u3', 'cx'])
        pm = PassManager(pass_)
        self.initial_circ = pm.run(circuit)

        self.arc = list(architecture)  # as a list of edges

        self.num_circuit_qubits = self.initial_circ.num_qubits
        self.num_arc_qubits = max([max(x) for x in self.arc])+1
        self.num_qubits = self.num_arc_qubits

        # final circuit will be on the number of architecture qubits (if different from input circuit number of qubits).
        self.final_circ = QuantumCircuit(self.num_arc_qubits)

        self.reset_pressed = False
        self.previous_gate_indices = None
        self.best_score = best_score
        self.num_swaps = 0
        self.message = ""  # this gets displayed at the top left
        self.cnot_gates_in_initial_circ = len([g for g in self.initial_circ.data if len(g[1]) > 1])
        self.nodes_highlighted = []
        self.node_colors = [BASE_NODE_COLOR]*self.num_arc_qubits
        self.current_gate_index = 0  # this will loop over the gates

        self.stage = 1  # stage 1 is initial stage, stage 2 is looping over the gates, stage 3 is game over

        # these are the 'circuit qubits' --> 'architecture qubits' mapping
        # initial mapping is the identity, this will specify the initial layout of qubits
        self.initial_mapping = lambda t: t
        # the current mapping determines how logical CNOTs should be applied onto the current qubits.
        self.current_mapping = lambda z: z
        
        self.circuit_edges = {}  # this will be in the form {gate: [width, color]}, e.g. {(1,2) : [5, 'b']}
        self.first_cnot_index = None
        for i in range(len(self.initial_circ.data)):  # for each gate
            g = self.initial_circ.data[i]

            if len(g[1]) > 1:  # if 2 qubit gate
                if self.first_cnot_index is None:
                    self.first_cnot_index =i

                k = tuple((g[1][0].index, g[1][1].index))  # get indices
                if k in self.circuit_edges:
                    # here we use the function y = 10 - 1/x to approach a line thickness of 15,
                    # by increasing x by 0.1 for each gate on the same connection

                    x = 1/(10 - self.circuit_edges[k][0])
                    x += 0.1
                    y = 10 - 1/x
                    self.circuit_edges[k][0] = y  # if already present, make line thicker
                else:
                    self.circuit_edges[k] = [5, CIRCUIT_EDGE_COLOR]

        first_gate = self.initial_circ.data[self.first_cnot_index]
        gate_indices = (first_gate[1][0].index, first_gate[1][1].index)
        self.circuit_edges[gate_indices] = (self.circuit_edges[gate_indices][0], HIGHLIGHTED_CIRCUIT_EDGE_COLOR)
        if gate_indices[::-1] in self.circuit_edges:
            self.circuit_edges[gate_indices[::-1]] = [self.circuit_edges[gate_indices[::-1]][0], HIGHLIGHTED_CIRCUIT_EDGE_COLOR]

        self.graph = nx.complete_graph(self.num_arc_qubits)  # used as baseline graph for plots

        self.fig, self.ax = plt.subplots(num=self.title,figsize=(11, 6))
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)
        self.plot()

    def plot(self):

        # clear the canvas
        plt.clf()

        self.pos = nx.circular_layout(self.graph)
        curr_map = [self.current_mapping(i) for i in range(self.num_arc_qubits)]
        label_pos = {curr_map.index(key): item for key, item in self.pos.items()}

        # nodes
        nx.draw_networkx_nodes(self.graph, pos=self.pos, node_color=self.node_colors)
        nx.draw_networkx_labels(self.graph, pos=label_pos)

        # edges
        # architecture
        nx.draw_networkx_edges(self.graph, self.pos,
                            edgelist=self.arc,
                            width=11, alpha=0.5, edge_color=ARCHITECTURE_EDGE_COLOR)
        # circuit
        nx.draw_networkx_edges(self.graph, self.pos,
                            edgelist=list(self.circuit_edges.keys()),
                            width=[x[0] for x in list(self.circuit_edges.values())], 
                            edge_color=[x[1] for x in list(self.circuit_edges.values())],
                            alpha=0.5)

        # next gate button
        plt.text(0.99, 0.02, 'Next Gate', fontsize=18,
                 bbox=dict(facecolor=None, boxstyle='round'),
                 transform = self.ax.transAxes,
                 horizontalalignment='right',
                 verticalalignment='bottom')

        # reset button
        plt.text(0.3 if self.num_arc_qubits ==3 else 0.01, 0.01, 'Reset', fontsize=12,
                 bbox=dict(facecolor='yellow', boxstyle='round'),
                 transform = self.ax.transAxes,
                 horizontalalignment='left',
                 verticalalignment='bottom')


        # stage
        plt.text(0.98, 0.98, 'Stage: {}'.format(self.stage), fontsize=15,
                 transform=self.ax.transAxes,
                 horizontalalignment='right',
                 verticalalignment='top')

        # swap number
        plt.text(0.98, 0.92, 'Number of Swaps: {}'.format(self.num_swaps), fontsize=10, weight='bold',
                 color='m' if self.stage == 3 else 'saddlebrown',
                 transform=self.ax.transAxes,
                 horizontalalignment='right',
                 verticalalignment='top')

        if self.best_score is not None:
            plt.text(0.98, 0.86, 'Best Score: {}'.format(self.best_score), fontsize=9, weight='bold',
                     color='midnightblue',
                     transform=self.ax.transAxes,
                     horizontalalignment='right',
                     verticalalignment='top')

        # gates remaining
        plt.text(0.99, 0.11, 'Gates remaining: {}'.format(self.gates_remaining()), fontsize=10,
                 color='midnightblue',
                 transform=self.ax.transAxes,
                 horizontalalignment='right',
                 verticalalignment='bottom')

        # message
        plt.text(0.2 if self.num_arc_qubits ==3 else 0.02, 0.98, self.message, fontsize=14, color='m',
                 transform=self.ax.transAxes,
                 horizontalalignment='left',
                 verticalalignment='top')

        # legend
        plt.text(0.3 if self.num_arc_qubits ==3 else 0.01, 0.12, "Circuit gate", fontsize=8, color='b',
                 transform=self.ax.transAxes,
                 horizontalalignment='left',
                 verticalalignment='bottom')
        plt.text(0.3 if self.num_arc_qubits ==3 else 0.01, 0.15, "Architecture connection", fontsize=8, color='r',
                 transform=self.ax.transAxes,
                 horizontalalignment='left',
                 verticalalignment='bottom')
        plt.text(0.3 if self.num_arc_qubits ==3 else 0.01, 0.09, "Next gate", fontsize=8, color=HIGHLIGHTED_CIRCUIT_EDGE_COLOR,
                 transform=self.ax.transAxes,
                 horizontalalignment='left',
                 verticalalignment='bottom')

        plt.title(self.title, fontsize=16, weight='bold')

        # update canvas as opposed to replotting
        self.fig.canvas.draw()

    def relabel_circuit(self, func):
        # `func` can be any permutation of the qubits

        # the new mapping is the old mapping composed with the new swap
        self.current_mapping = compose(func, self.current_mapping)  

        if self.stage == 1: # update initial mapping only if in initial stage
            self.initial_mapping = self.current_mapping

        new_edges = {}

        # update the edges for graph representation
        for k in self.circuit_edges:
            new_edges[(func(k[0]), func(k[1]))] = self.circuit_edges[k]
        self.circuit_edges = new_edges

        return

    def swap_nodes(self, x, y):
        if (x, y) in self.arc or (y, x) in self.arc or self.stage==1:
            def f(z): # define the swap permutation
                if z == x:
                    return y
                elif z==y:
                    return x
                else:
                    return z

            if self.stage != 1:  # add a swap gate to the new circuit
                self.final_circ.cx(x, y)
                self.final_circ.cx(y, x)
                self.final_circ.cx(x, y)

                self.num_swaps += 1

            self.relabel_circuit(func=f)
        else:
            self.message = 'Qubits are not \n connected!'
            self.plot()

    def next_gate(self):
        """
        This is called when the "Next Gate" button is pressed, and the current gate lies on the architecture.
        """
        if self.stage == 1:
            while self.current_gate_index < self.first_cnot_index:
                gate = self.initial_circ.data[self.current_gate_index]

                assert(len(gate[1]) == 1)
                gate_params = gate[0].params
                gate_class = type(gate[0])
                gate_index = gate[1][0].index
                new_gate_index = self.current_mapping(gate_index)

                if gate_class == U1Gate:
                    gate_object = U1Gate(theta=gate_params[0])
                elif gate_class == U2Gate:
                    gate_object = U2Gate(phi=gate_params[0], lam=gate_params[1])
                elif gate_class == U3Gate:
                    gate_object = U3Gate(theta=gate_params[0], phi=gate_params[1], lam=gate_params[2])
                else:
                    gate_object = gate_class()

                self.final_circ.data.append(
                    (gate_object, [Qubit(QuantumRegister(self.num_arc_qubits, 'q'), new_gate_index)],
                     []))

                self.current_gate_index += 1

            self.stage = 2

        if self.stage == 2:
            gate = self.initial_circ.data[self.current_gate_index] # get gate
            gate_class = type(gate[0])
            gate_indices = (gate[1][0].index, gate[1][1].index)
            self.previous_gate_indices = gate_indices
            new_gate_indices = (self.current_mapping(gate_indices[0]), self.current_mapping(gate_indices[1]))

            # here we use the function y = 10 - 1/x to approach a thickness of 15,
            # by increasing x by 0.1 for each gate on the same connection

            x = 1 / (10 - self.circuit_edges[new_gate_indices][0])

            if x == 0.2:
                col = COMPLETED_CIRCUIT_EDGE_COLOR
                x -= 0.1  # this removes the edge, i.e. makes finished edges have 0 thickness
            else:
                x -= 0.1
                col = CIRCUIT_EDGE_COLOR
            y = 10 - 1 / x

            self.circuit_edges[new_gate_indices] = [y, col]
            if new_gate_indices[::-1] in self.circuit_edges:
                self.circuit_edges[new_gate_indices[::-1]] = [self.circuit_edges[new_gate_indices[::-1]][0], col]

            self.final_circ.data.append(
                (gate_class(), [Qubit(QuantumRegister(self.num_arc_qubits, 'q'), new_gate_indices[0]),
                                                     Qubit(QuantumRegister(self.num_arc_qubits, 'q'), new_gate_indices[1])],
                 []))

            self.current_gate_index += 1
            self.message = ""

        else: # self.stage = 3 (or anything else)
            return
        try:
            # add gates to new circuit and get next 2 qubit gate
            while len(self.initial_circ.data[self.current_gate_index][1]) < 2:  # is a 1 qubit gate
                gate = self.initial_circ.data[self.current_gate_index]
                gate_params = gate[0].params
                gate_class = type(gate[0])
                gate_index = gate[1][0].index
                new_gate_index = self.current_mapping(gate_index)

                if gate_class == U1Gate:
                    gate_object = U1Gate(theta=gate_params[0])
                elif gate_class == U2Gate:
                    gate_object = U2Gate(phi=gate_params[0], lam=gate_params[1])
                elif gate_class == U3Gate:
                    gate_object = U3Gate(theta=gate_params[0], phi=gate_params[1], lam=gate_params[2])
                else:
                    gate_object = gate_class()

                self.final_circ.data.append(
                    (gate_object, [Qubit(QuantumRegister(self.num_arc_qubits, 'q'), new_gate_index)],
                     []))

                self.current_gate_index += 1

        except IndexError:  # no more gates left -- end of game
            self.message = "Game Over!"

            for g in self.final_circ.data:
                if len(g[1]) > 1:  # if 2 qubit gate
                    k = tuple((g[1][0].index, g[1][1].index))  # get indices

            if self.output_filename is not None:

                if self.output_dir is not None:
                    if not os.path.exists(self.output_dir):
                        os.makedirs(self.output_dir)

                self.initial_circ.qasm(filename=os.path.join(self.output_dir,'initial_circuit_{}.txt'.format(self.output_filename)))
                self.final_circ.qasm(filename=os.path.join(self.output_dir,'final_circuit_{}.txt'.format(self.output_filename)))

                self.details = {
                                'num_circuit_qubits': self.num_circuit_qubits,
                                'num_arc_qubits': self.num_arc_qubits,
                                'architecture': self.arc,
                                'initial_mapping': [self.initial_mapping(x) for x in range(self.num_arc_qubits)],
                                'final_mapping': [self.current_mapping(x) for x in range(self.num_arc_qubits)],
                                'num_swaps' : self.num_swaps
                                }

                with open(os.path.join(self.output_dir, 'details_' + self.output_filename + '.txt'), 'w') as f:
                    f.write(str(self.details))

            self.stage = 3
            self.plot()
            return

        # update current gate colour
        current_gate = self.initial_circ.data[self.current_gate_index]
        gate_indices = (current_gate[1][0].index, current_gate[1][1].index)
        new_gate_indices = (self.current_mapping(gate_indices[0]), self.current_mapping(gate_indices[1])) 
        self.circuit_edges[new_gate_indices] = (self.circuit_edges[new_gate_indices][0], HIGHLIGHTED_CIRCUIT_EDGE_COLOR)
        if new_gate_indices[::-1] in self.circuit_edges:
            self.circuit_edges[new_gate_indices[::-1]] = [self.circuit_edges[new_gate_indices[::-1]][0], HIGHLIGHTED_CIRCUIT_EDGE_COLOR]

        self.reset_colors()

        if self.previous_gate_indices is not None:
            next_gate = self.initial_circ.data[self.current_gate_index]
            new_gate_indices = (next_gate[1][0].index, next_gate[1][1].index)
            if self.previous_gate_indices == new_gate_indices or self.previous_gate_indices[::-1] == new_gate_indices:
                self.next_gate()
                return

        self.plot()
        return

    def onClick(self,event):
        """
        This is called when anywhere on the plot is clicked.
        """

        x, y = event.xdata, event.ydata # the x,y coordinates of the click
        if x is None or y is None:
            self.message = "Click inside \nthe border!"
            self.plot()
            return

        if (abs(x-0.9)**2 + abs(y+1)**2) < 0.03:  # 'next gate' clicked
            if self.stage == 1:
                gate = self.initial_circ.data[self.first_cnot_index]
            elif self.stage == 2:
                gate = self.initial_circ.data[self.current_gate_index]
            else:
                return

            logicals = (gate[1][0].index, gate[1][1].index)
            physicals = (self.current_mapping(logicals[0]), self.current_mapping(logicals[1]))
            if physicals in self.arc or (physicals[1], physicals[0]) in self.arc:
                self.next_gate()
            else:
                self.message = 'Gate not on \narchitecture!'
                self.reset_pressed = False
                self.plot()

            return

        reset_x =-0.04 if self.num_arc_qubits ==3 else -1
        reset_y = -0.9 if self.num_arc_qubits==3 else -1
        if (abs(x-reset_x)**2 + abs(y-reset_y)**2) < 0.03:  # 'reset clicked'

            if not self.reset_pressed:
                self.reset_pressed = True
                self.message="Press 'Reset' again \nto start over."
                self.plot()
                return
            else:
                if self.stage == 3:
                    new_best_score = min(self.num_swaps, self.best_score) if self.best_score is not None else self.num_swaps
                else:
                    new_best_score = None
                try:
                    self.__init__(circuit=self.initial_circ,
                                  architecture=self.arc,
                                  title=self.title,
                                  output_dir=self.output_dir,
                                  output_filename=self.output_filename,
                                  best_score=new_best_score)
                    return
                except TypeError:
                    self.__init__(best_score=new_best_score)
                    return

        else: # reset not pressed
            self.reset_pressed = False


        # check if nodes clicked
        for i in range(len(self.pos)):  # for each node
                if (abs(x-self.pos[i][0])**2 + abs(y-self.pos[i][1])**2) < 0.003: # if node clicked

                    self.node_colors[i] = HIGHLIGHTED_NODE_COLOR
                    self.nodes_highlighted.append(i)

                    if len(self.nodes_highlighted)==1:
                        self.plot()
                        return
                    else: # already one node highlighted
                        assert(len(self.nodes_highlighted)==2)

                        self.plot()
                        self.fig.canvas.draw()
                        time.sleep(1)
                        
                        self.swap_nodes(*self.nodes_highlighted)
                        self.nodes_highlighted = []
                        self.node_colors = [BASE_NODE_COLOR]*self.num_arc_qubits
                        self.plot()
                        return
        
        self.reset_colors() # clicked on nothing
        self.plot()
        return

    def reset_colors(self):
            self.node_colors = [BASE_NODE_COLOR]*self.num_arc_qubits
            self.nodes_highlighted = []
            self.message = ""
            self.reset_pressed = False
            return

    def gates_remaining(self):

        cnot_gates_in_current_circ = len([g for g in self.final_circ.data if len(g[1]) > 1])

        return self.cnot_gates_in_initial_circ - cnot_gates_in_current_circ + 3*self.num_swaps

