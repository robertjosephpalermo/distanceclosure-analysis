import networkx as nx
import numpy as np

def get_edge_attribute_names(graph: nx.Graph) -> set:
    keys = set()
    for _, _, attrs in graph.edges(data=True):
        keys.update(attrs.keys())
    return keys


def rename_edge_attributes(graph: nx.Graph, old_name: str, new_name: str) -> nx.Graph:
    for _, _, d in graph.edges(data=True):
        if old_name in d:
            d[new_name] = d.pop(old_name)
    return graph


def all_edges_have_attribute(G, attribute: str) -> bool:
    return all(attribute in d for _, _, d in G.edges(data=True))


def has_edge_attribute(graph: nx.Graph, attribute: str) -> bool:
    return any(attribute in d for _, _, d in graph.edges(data=True))


def compute_distance_cv(graph: nx.Graph) -> float:
    weights = [float(data["distance"]) for _, _, data in graph.edges(data=True)]
    return np.std(weights) / np.mean(weights)