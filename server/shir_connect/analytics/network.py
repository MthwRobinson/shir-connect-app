""" Performs network analysis on the social network
for the organization. """
import datetime
import itertools
import logging

import daiquiri
import networkx as nx
import networkx.algorithms.approximation as approx

from shir_connect.services.events import Events

class Network(object):
    """ Pulls in data from the events database and
    performs social network analysis. """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.events_manager = Events()

        self.metrics = {
            'node_connectivity': self.node_connectivity,
            'edge_connectivity': self.edge_connectivity,
            'weighted_density': self.weighted_density
        }

    def get_events(self, start, end):
        """ Pulls events from the event database
        within the specified date range. """
        events = self.events_manager.database.read_table(
            'event_aggregates',
            columns=['id', 'start_datetime'],
            where=[('start_datetime',{'>=': start, '<': end})],

        )
        return events

    def evaluate_network(self, metrics=None):
        """ Constructs a co-attendance network ending at
        the specified data and begging <lag> days before
        the date. """
        if not metrics:
            metrics = [x for x in self.metrics.keys()]

        biggest_subgraph = self.biggest_subgraph(self.network)
        evaluation = {}
        for metric in metrics:
            if metric in self.metrics:
                if metric.endswith('connectivity'):
                    value = self.metrics[metric](biggest_subgraph)
                else:
                    value = self.metrics[metric](self.network)
                evaluation[metric] = value
        return evaluation

    def build_network(self, start, end, max_attendees=None):
        """ Builds the congregational co-attendance network
        based on events in the specified range. """
        network = nx.Graph()
        start = "'{}'".format(start)
        end = "'{}'".format(end)
        event = self.get_events(start, end)
        for event_id in event['id']:
            attendees = self.events_manager.get_attendees(event_id)
            if max_attendees:
                if len(attendees) >  max_attendees:
                    continue
            names = [x['name'].lower() for x in attendees]
            names = list(set(names)) # Drops duplicates
            pairs = itertools.combinations(names, 2)
            for pair in pairs:
                network.add_edge(*pair)
            self.network = network

    @staticmethod
    def weighted_density(network):
        """ Finds the density of the graph and scales it by the
        number of nodes in the graph. """
        n = len(network.nodes)
        return n * nx.density(network)

    @staticmethod
    def node_connectivity(network):
        """ Computes the node connectivity for the network. """
        connectivity = approx.node_connectivity(network)
        return connectivity

    @staticmethod
    def edge_connectivity(network):
        """ Compute the edge connectivity for the network. """
        connectivity = nx.connectivity.edge_connectivity(network)
        return connectivity

    @staticmethod
    def biggest_subgraph(network):
        """ Finds the biggest fully connected subgraph of the network. """
        graphs = list(nx.connected_component_subgraphs(network))
        sizes = [len(x.nodes) for x in graphs]
        idx = sizes.index(max(sizes))
        biggest_graph = graphs[idx]
        return biggest_graph
