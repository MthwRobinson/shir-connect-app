import networkx as nx

from shir_connect.analytics.network import Network

def test_build_network():
    network = Network()
    network.build_network('2018-01-01', lag=30)
    assert isinstance(network.network, nx.classes.graph.Graph)

def test_evaluate_network():
    network = Network()
    network.build_network('2018-01-01', lag=30)
    metrics = network.evaluate_network()
    assert type(metrics['edge_connectivity']) == int
    assert type(metrics['node_connectivity']) == int
    assert type(metrics['weighted_density']) == float
