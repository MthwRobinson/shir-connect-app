""" Performs network analysis on the social network
for the organization. """
import datetime
import itertools
import logging

import daiquiri
import networkx as nx
import networkx.algorithms.approximation as approx

from shir_connect.services.events import Events

class Network():
    """ Pulls in data from the events database and
    performs social network analysis. """
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.events_manager = Events()
        self.network = None
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
            where=[('start_datetime', {'>=': start, '<': end})],

        )
        return events

    def evaluate_network(self, metrics=None):
        """ Constructs a co-attendance network ending at
        the specified data and begging <lag> days before
        the date. """
        if not metrics:
            metrics = list(self.metrics.keys())
        elif isinstance(metrics, str):
            metrics = [metrics]

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

    def build_network(self, date, lag, max_attendees=None):
        """ Builds the congregational co-attendance network
        ending at the specified date and ending <lag> days later

        Parameters
        ----------
            date: the start date in 'YYYY-MM-DD' format
            lag: int, the number of days to go back
            max_attendees: int, ignores events that have
                more than the max number of attendees

        Returns
        -------
            sets the network attribute to be a network x graph
        """
        network = nx.Graph()
        # Determine the start and end dates for the pull
        split_date = date.split('-')
        year = int(split_date[0])
        month = int(split_date[1])
        day = int(split_date[2])
        end_datetime = datetime.datetime(year, month, day)
        end = "'{}'".format(date)
        start_datetime = end_datetime - datetime.timedelta(days=lag)
        start = "'{}'".format(str(start_datetime)[:10])

        # Build the network G(V,E) where V is the set of participants
        # and an edge exists between two vertices if they have
        # attended the same events
        events = self.get_events(start, end)
        msg = '\nStart: {date} \nLag: {lag} days \nEvent Count: {count}'
        msg = msg.format(date=date, lag=lag, count=len(events))
        self.logger.info(msg)
        for event_id in events['id']:
            attendees = self.events_manager.get_attendees(event_id)
            if max_attendees:
                if len(attendees) > max_attendees:
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
        num_nodes = len(network.nodes)
        return num_nodes * nx.density(network)

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
        connected_components = nx.connected_components(network)
        graphs = [network.subgraph(x).copy() for x in connected_components]
        sizes = [len(x.nodes) for x in graphs]
        idx = sizes.index(max(sizes))
        biggest_graph = graphs[idx]
        return biggest_graph
