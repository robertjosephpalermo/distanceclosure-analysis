from function_timer.FunctionTimer import FunctionTimer
from graphml_utilities import has_edge_attribute, all_edges_have_attribute, rename_edge_attributes, get_edge_attribute_names
from pathlib import Path
import networkx as nx
import pandas as pd
import distanceclosure.backbone as dc 
import os


def define_row(graph: pd.DataFrame | nx.Graph, domain_name: str, network_name: str) -> pd.DataFrame:
    if isinstance(graph, pd.DataFrame):
        graph = nx.from_pandas_edgelist(graph, source="source", target="target", edge_attr="distance")
    
    timer = FunctionTimer(module=dc)
    runtime_type = "runtime_in_seconds"
    log_type = "run_log"

    # Metric Backbone
    iter_metric_backbone = timer.iterative_backbone(graph, weight="distance", kind="metric", verbose=True)
    iter_metric_dt = timer.json_log[0][log_type][runtime_type]
    print(f"Iterative Metric Complete: {network_name}")

    flag_metric_backbone = timer.flagged_backbone(graph, weight="distance", kind="metric", verbose=True)
    flag_metric_dt = timer.json_log[1][log_type][runtime_type]
    print(f"Flagged Metric Complete: {network_name}")

    clos_metric_backbone = timer.backbone_from_closure(graph, weight="distance", kind="metric", verbose=True)
    clos_metric_dt = timer.json_log[2][log_type][runtime_type]
    print(f"Closure Metric Complete: {network_name}")

    # Ultrametric Backbone
    iter_ultrametric_backbone = timer.iterative_backbone(graph, weight="distance", kind="ultrametric", verbose=True)
    iter_ultrametric_dt = timer.json_log[3][log_type][runtime_type]
    print(f"Iterative Ultrametric Complete: {network_name}")

    flag_ultrametric_backbone = timer.flagged_backbone(graph, weight="distance", kind="ultrametric", verbose=True)
    flag_ultrametric_dt = timer.json_log[4][log_type][runtime_type]
    print(f"Flagged Ultrametric Complete: {network_name}")

    clos_ultrametric_backbone = timer.backbone_from_closure(graph, weight="distance", kind="ultrametric", verbose=True)
    clos_ultrametric_dt = timer.json_log[5][log_type][runtime_type]
    print(f"Closure Ultrametric Complete: {network_name}")

    row = [{
        "type": "Directed" if graph.is_directed() == True else "Undirected",
        "domain": domain_name,
        "name": network_name,
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": round(nx.density(graph), 3),
        "iter_metric_edges": iter_metric_backbone.number_of_edges(),
        "flag_metric_edges": flag_metric_backbone.number_of_edges(),
        "clos_metric_edges": clos_metric_backbone.number_of_edges(),
        "iter_ultrametric_edges": iter_ultrametric_backbone.number_of_edges(),
        "flag_ultrametric_edges": flag_ultrametric_backbone.number_of_edges(),
        "clos_ultrametric_edges": clos_ultrametric_backbone.number_of_edges(),
        "iter_metric_dt": round(iter_metric_dt, 3),
        "flag_metric_dt": round(flag_metric_dt ,3),
        "clos_metric_dt": round(clos_metric_dt ,3),
        "iter_ultrametric_dt": round(iter_ultrametric_dt, 3),
        "flag_ultrametric_dt": round(flag_ultrametric_dt ,3),
        "clos_ultrametric_dt": round(clos_ultrametric_dt ,3)
    }]

    return pd.DataFrame(row)


def append_file(new_row: pd.DataFrame, output_file_name: str) -> None:
    file_path = Path(os.environ["OUTPUT_DIR"]) / "analyze_networks" / "data_output" / output_file_name 

    new_row.to_csv(
        file_path, 
        mode="a", 
        header=not os.path.isfile(file_path), 
        index=False
    )


def log_backbone_output(graph: pd.DataFrame | nx.Graph, domain_name: str, network_name: str, output_file_name: str) -> None:    
    row = define_row(graph, domain_name, network_name)
    append_file(row, output_file_name)

    print(f"{network_name} finished.")
    print()


def single_use_backbone_output(graph: nx.Graph, edge_attribute: str, output_file_name: str) -> None:
    """
    graph: Must be a directed or undirected graphml file only.\n
    edge_attribute: This is the 'edge_attribute' of the graph you want the backbone algorithm to interpret as 'distance'.\n
    output_file_name: Example: 'output_data.csv'. Include the ending. Must be CSV
    """

    if not isinstance(graph, nx.Graph):
        raise TypeError("Graph must be a NetworkX Graph or DiGraph.")

    if isinstance(graph, (nx.MultiGraph, nx.MultiDiGraph)):
        raise ValueError("Graph cannot be a MultiGraph or MultiDiGraph.")

    if not output_file_name.endswith(".csv"):
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
        output_file_name=output_file_name
    )




