from graphml_utilities import all_edges_have_attribute, compute_distance_cv
from function_timer.FunctionTimer import FunctionTimer
from pathlib import Path
import distanceclosure.backbone as dc 
import networkx as nx
import pandas as pd
import os


def handle_path(path_to_graph: str) -> nx.Graph | nx.DiGraph:
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


def define_row(graph: pd.DataFrame | nx.Graph) -> pd.DataFrame:
    timer = FunctionTimer() 

    row = {
        "type": "Directed" if graph.is_directed() == True else "Undirected",
        "relative_path": graph.graph["path"],
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "density": round(nx.density(graph), 3),
        "cv": round(compute_distance_cv(graph), 3)
    }
   
    functions = { 
        "iterative": dc.iterative_backbone,
        "flagged": dc.flagged_backbone,
        "closure": dc.backbone_from_closure,
        "heuristic": dc.heuristic_backbone,
        "heuristic_approximation": dc.heuristic_backbone
    }

    kinds = [
        "metric",
        "ultrametric"
    ]
    
    i = 0 
    for kind in kinds:
        for name, function in functions.items():

            if name == "heuristic_approximation":
                new_backbone = timer(function)(
                    graph, 
                    weight="distance",
                    kind=kind,
                    approx=True
                )
            else:
                new_backbone = timer(function)(
                    graph, 
                    weight="distance",
                    kind=kind,
                )


            new_backbone_dt = timer.json_log[i]["run_log"]["runtime_in_seconds"]
            print(f"{name} {kind} backbone complete.")
            
            row[f"{name}_{kind}_edges"] = new_backbone.number_of_edges()
            row[f"{name}_{kind}_dt"] = round(new_backbone_dt, 3)
            i += 1
    print()
    return pd.DataFrame([row])


def append_output_file(new_row: pd.DataFrame, path_to_output: str) -> None:
    file_exists = os.path.isfile(path_to_output)

    new_row.to_csv(
        path_to_output, 
        mode="a", 
        header=not file_exists, 
        index=False
    )

def compute_backbones(path_to_graph: str, path_to_output: str) -> None:    
    graph = handle_path(path_to_graph)
    row = define_row(graph)

    append_output_file(row, path_to_output)



