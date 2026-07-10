import networkx as nx
import numpy as np

def get_edge_attribute_names(graph: nx.Graph | nx.DiGraph) -> set:
    keys = set()
    for _, _, attrs in graph.edges(data=True):
        keys.update(attrs.keys())
    return keys


def rename_edge_attributes(graph: nx.Graph | nx.DiGraph, old_name: str, new_name: str) -> nx.Graph:
    for _, _, d in graph.edges(data=True):
        if old_name in d:
            d[new_name] = d.pop(old_name)
    return graph


def all_edges_have_attribute(graph: nx.Graph | nx.DiGraph, attribute: str) -> bool:
    return all(attribute in d for _, _, d in graph.edges(data=True))


def compute_distance_cv(graph: nx.Graph | nx.DiGraph) -> float:
    weights = [float(data["distance"]) for _, _, data in graph.edges(data=True)]
    return np.std(weights) / np.mean(weights)

