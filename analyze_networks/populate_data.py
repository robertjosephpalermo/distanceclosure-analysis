from function_timer.FunctionTimer import FunctionTimer
from graphml_utilities import has_edge_attribute, all_edges_have_attribute, rename_edge_attributes, get_edge_attribute_names, compute_distance_cv
import networkx as nx
import pandas as pd
import distanceclosure.backbone as dc 
import os

def define_row(graph: pd.DataFrame | nx.Graph, domain_name: str, network_name: str) -> pd.DataFrame:
    timer = FunctionTimer()
    
    if isinstance(graph, pd.DataFrame):
        graph = nx.from_pandas_edgelist(
            graph, 
            source="source", 
            target="target", 
            edge_attr="distance"
        )

    row = {
        "type": "Directed" if graph.is_directed() == True else "Undirected",
        "domain": domain_name,
        "name": network_name,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": round(nx.density(graph), 3),
        "cv": round(compute_distance_cv(graph), 3)
    }
   
    functions = { 
        "iterative": dc.iterative_backbone,
        "flagged": dc.flagged_backbone,
        "closure": dc.backbone_from_closure
    }

    kinds = [
        "metric",
        "ultrametric"
    ]
    
    i = 0 
    for kind in kinds:
        for name, function in functions.items():
            new_backbone = timer(function)(
                graph, 
                weight="distance",
                kind=kind,
                verbose=True
            )
            new_backbone_dt = timer.json_log[i]["run_log"]["runtime_in_seconds"]
            print(f"{name} {kind} backbone complete.")
            
            row[f"{name}_{kind}_edges"] = new_backbone.number_of_edges()
            row[f"{name}_{kind}_dt"] = round(new_backbone_dt, 3)
            i += 1
    
    return pd.DataFrame([row])


def append_file(new_row: pd.DataFrame, output_file_path: str) -> None:
    new_row.to_csv(
        output_file_path, 
        mode="a", 
        header=not os.path.isfile(output_file_path), 
        index=False
    )


def log_backbone_output(graph: pd.DataFrame | nx.Graph, domain_name: str, network_name: str, output_file_path: str) -> None:    
    row = define_row(graph, domain_name, network_name)
    append_file(row, output_file_path)

    print(f"{network_name} finished.")
    print()


def single_use_backbone_output(graph: nx.Graph, edge_attribute: str, output_file_path: str) -> None:
    """
    graph: Must be a directed or undirected graphml file only.\n
    edge_attribute: This is the 'edge_attribute' of the graph you want the backbone algorithm to interpret as 'distance'.\n
    output_file_name: Example: 'output_data.csv'. Include the ending. Must be CSV
    """

    if not isinstance(graph, nx.Graph):
        raise TypeError("Graph must be a NetworkX Graph or DiGraph.")

    if isinstance(graph, (nx.MultiGraph, nx.MultiDiGraph)):
        raise ValueError("Graph cannot be a MultiGraph or MultiDiGraph.")

    if not output_file_path.endswith(".csv"):
        raise ValueError("output_file_name must end with '.csv'.")

    if not has_edge_attribute(graph, edge_attribute):
        raise ValueError(f"Graph is missing '{edge_attribute}'. Available types include {get_edge_attribute_names(graph)}.")

    if not all_edges_have_attribute(graph, edge_attribute):
        raise ValueError(f"All edges must have '{edge_attribute}'.")
    
    graph = graph.copy()
    graph = rename_edge_attributes(
        graph=graph, 
        old_name=edge_attribute, 
        new_name="distance"
    )

    log_backbone_output(
        graph=graph,
        domain_name="N/A",
        network_name="N/A",
        output_file_path=output_file_path
    )




