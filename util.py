"""
    Some useful functions.
"""
import matplotlib.pyplot as plt
import networkx as nx


def lattice_architecture(a, b):
    """
    returns a list of edges corresponding to a lattice architecture:
    """
    # a:  row
    # b:  column

    res = []

    curr = 0

    for i in range(a):
        for j in range(b): 
            if j != b-1:
                res.append((curr, curr+1))
            if i != a -1:
                res.append((curr, curr+b))
            curr += 1

    return res


def compose(f, g):
    def h(x):
        return f(g(x))

    return h


def get_backend_graphs(provider):
    """
    Plots the connectivity graphs of each available backend.
    """
    backend_graphs = {}
    for backend in provider.backends():
        if backend.properties() is not None:
            backend_dict = backend.properties().to_dict()
            gates = []
            for g in backend_dict['gates']:
                if len(g['qubits']) > 1:  # not a single qubit gate
                    gates.append(g['qubits'])
            graph = nx.Graph()
            graph.add_edges_from(gates)
            backend_graphs[backend_dict['backend_name']] = graph

    plt.figure(figsize=(18, 18))
    for plot_num in range(len(backend_graphs)):
        ax = plt.subplot(int(len(backend_graphs) / 2) + 1, 3, plot_num + 1)
        nx.draw(backend_graphs[list(backend_graphs.keys())[plot_num]], with_labels=True, ax=ax)
        ax.set_title(list(backend_graphs.keys())[plot_num])

    return backend_graphs


def print_backend_info(provider):
    """
    For each backend, prints the number of jobs and number of qubits.
    """
    for backend in provider.backends():
        if backend.properties() is not None:
            backend_dict = backend.properties().to_dict()
            jobs_in_queue = backend.status().pending_jobs
            print(backend_dict['backend_name'], ':    {} qubits, {} jobs in queue'.format(len(backend_dict['qubits']),jobs_in_queue))
