from graphml_utilities import all_edges_have_attribute, compute_distance_cv
from definitions import DataColumn, Algorithm, Metric
from function_timer.FunctionTimer import FunctionTimer
from pathlib import Path
import distanceclosure.backbone as dc 
import networkx as nx
import pandas as pd
import os


def load_graph(path_to_graph: str) -> nx.Graph | nx.DiGraph:
    """
    Handles errors and standardizes graph data.

    Parameters
    ----------
    ``path_to_graph`` : str
        Complete path to the graph being loaded.
    
    Returns
    -------
    nx.Graph or nx.DiGraph
        A graph representation of the file input.

    Raises
    ------
    FileNotFoundError
        If ``path_to_graph`` does not exist.

    ValueError
        If ``path_to_graph`` is not a file.

    ValueError
        If the file extension is not supported. Supported file types
        are ``.csv`` and ``.graphml``.

    TypeError
        If the loaded object is not a nx.Graph or nx.DiGraph.

    ValueError
        If the loaded graph is a nx.MultiGraph or MultiDiGraph.

    ValueError
        If one or more edges do not contain the ``distance`` attribute.

    """

    path = Path(path_to_graph)

    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist.")

    if not path.is_file():
        raise ValueError(f"{path} is not a file.")
    
    if path.suffix == ".csv":
        graph = pd.read_csv(path)
        
        graph = nx.from_pandas_edgelist(
            graph, 
            source="source", 
            target="target", 
            edge_attr="distance"
        )
    elif path.suffix == ".graphml":
        graph = nx.read_graphml(path)
    else:
        raise ValueError(f"Unsupported file type '{path.suffix}'.")

    if not isinstance(graph, (nx.Graph, nx.DiGraph)):
        raise TypeError("Graph must be a NetworkX Graph or DiGraph.")

    if isinstance(graph, (nx.MultiGraph, nx.MultiDiGraph)):
        raise ValueError("Graph cannot be a MultiGraph or MultiDiGraph.")
    
    if not all_edges_have_attribute(graph, "distance"):
        raise ValueError("All edges must have edge attribute 'distance'.")

    relative_path = path.relative_to(path.parent.parent.parent)
    graph.graph["path"] = str(relative_path)

    return graph


def define_row(graph: pd.DataFrame | nx.Graph | nx.DiGraph) -> pd.DataFrame:
    """
    Computes the metric and ultrametric backbone of a directed or undirected graph using 5 algorithms.

    Parameters
    ----------
    ``graph`` : pd.DataFrame | nx.Graph | nx.DiGraph
        Graph whos backbone will be computed.
    
    Returns
    -------
    pd.DataFrame
        A single-row DataFrame with columns:
        - type
        - relative_path
        - nodes
        - edges
        - density
        - cv
        - {algorithm}_{kind}_edges
        - {algorithm}_{kind}_dt

        where algorithm is one of {iterative, flagged, closure,
        heuristic, heuristic_approximation} and kind is one of
        {metric, ultrametric}.
    """

    timer = FunctionTimer() 

    row = {
        DataColumn.TYPE: "Directed" if graph.is_directed() == True else "Undirected",
        DataColumn.RELATIVE_PATH: graph.graph["path"],
        DataColumn.NODES: graph.number_of_nodes(),
        DataColumn.EDGES: graph.number_of_edges(),
        DataColumn.DENSITY: round(nx.density(graph), 3),
        DataColumn.CV: round(compute_distance_cv(graph), 3)
    }
   
    functions = { 
        Algorithm.ITERATIVE: dc.iterative_backbone,
        Algorithm.FLAGGED: dc.flagged_backbone,
        Algorithm.CLOSURE: dc.backbone_from_closure,
        Algorithm.HEURISTIC: dc.heuristic_backbone,
        Algorithm.HEURISTIC_APPROX: dc.heuristic_backbone
    }
    
    i = 0 
    for metric in Metric:
        for name, function in functions.items():
            if name == Algorithm.HEURISTIC_APPROX:
                new_backbone = timer(function)(
                    graph, 
                    weight="distance",
                    kind=metric,
                    approx=True
                )
            else:
                new_backbone = timer(function)(
                    graph, 
                    weight="distance",
                    kind=metric,
                )

            runtime_metadata = timer.json_log[i]["run_log"]

            new_backbone_dt = runtime_metadata["runtime_in_seconds"]
            print(f"{name} {metric} backbone complete.")
            
            new_edges_column = name + "_" + metric + "_edges"
            new_runtime_column = name + "_" + metric + "_dt"

            row[new_edges_column] = new_backbone.number_of_edges()
            row[new_runtime_column] = round(new_backbone_dt, 3)
            i += 1
    print()
    return pd.DataFrame([row])


def append_output_file(new_row: pd.DataFrame, path_to_output: str) -> None:
    """
    Appends a row of backbone statistics to an output CSV file.

    Parameters
    ----------
    ``new_row`` : pd.DataFrame
        Single-row DataFrame containing graph metadata.

    ``path_to_output`` : str
        Path to the output CSV file. If the file does not exist,
        it is created and column headers are written.

    Returns
    -------
    None
        Writes ``new_row`` to ``path_to_output`` and does not
        return a value.
    """
    file_exists = os.path.isfile(path_to_output)

    new_row.to_csv(
        path_to_output, 
        mode="a", 
        header=not file_exists, 
        index=False
    )


def compute_backbones(path_to_graph: str, path_to_output: str) -> None:
    """
    Computes backbone statistics for a graph and appends the results
    to an output CSV file.

    Parameters
    ----------
    path_to_graph : str
        Path to the input graph file. Supported file types are
        ``.csv`` and ``.graphml``.

    path_to_output : str
        Path to the CSV file where backbone statistics will be
        appended.

    Returns
    -------
    None
        Computes backbone statistics for the input graph and writes
        the resulting row to ``path_to_output``.

    Raises
    ------
    FileNotFoundError
        If ``path_to_graph`` does not exist.

    ValueError
        If ``path_to_graph`` is not a file, has an unsupported file
        extension, represents a multigraph, or contains edges
        without the ``distance`` attribute.

    TypeError
        If the loaded object is not a NetworkX ``Graph`` or
        ``DiGraph``.

    OSError
        If the output file cannot be written.
    """    
    graph = load_graph(path_to_graph)
    row = define_row(graph)

    append_output_file(row, path_to_output)

