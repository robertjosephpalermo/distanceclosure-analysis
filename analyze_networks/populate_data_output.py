from function_timer.FunctionTimer import FunctionTimer
from pathlib import Path
import networkx as nx
import pandas as pd
import distanceclosure.backbone as dc 
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def define_row(g: pd.DataFrame | nx.Graph, domain: str, network_name: str) -> pd.DataFrame:
    if isinstance(g, pd.DataFrame):
        g = nx.from_pandas_edgelist(g, source="source", target="target", edge_attr="distance")
    
    timer = FunctionTimer(module=dc)
    runtime_type = "runtime_in_seconds"
    log_type = "run_log"

    # Metric Backbone
    iter_metric_backbone = timer.iterative_backbone(g, weight="distance", kind="metric", verbose=True)
    iter_metric_dt = timer.json_log[0][log_type][runtime_type]
    print(f"Iterative Metric Complete: {network_name}")

    flag_metric_backbone = timer.flagged_backbone(g, weight="distance", kind="metric", verbose=True)
    flag_metric_dt = timer.json_log[1][log_type][runtime_type]
    print(f"Flagged Metric Complete: {network_name}")

    clos_metric_backbone = timer.backbone_from_closure(g, weight="distance", kind="metric", verbose=True)
    clos_metric_dt = timer.json_log[2][log_type][runtime_type]
    print(f"Closure Metric Complete: {network_name}")

    # Ultrametric Backbone
    iter_ultrametric_backbone = timer.iterative_backbone(g, weight="distance", kind="ultrametric", verbose=True)
    iter_ultrametric_dt = timer.json_log[3][log_type][runtime_type]
    print(f"Iterative Ultrametric Complete: {network_name}")

    flag_ultrametric_backbone = timer.flagged_backbone(g, weight="distance", kind="ultrametric", verbose=True)
    flag_ultrametric_dt = timer.json_log[4][log_type][runtime_type]
    print(f"Flagged Ultrametric Complete: {network_name}")

    clos_ultrametric_backbone = timer.backbone_from_closure(g, weight="distance", kind="ultrametric", verbose=True)
    clos_ultrametric_dt = timer.json_log[5][log_type][runtime_type]
    print(f"Closure Ultrametric Complete: {network_name}")

    row = [{
        "type": "Directed" if g.is_directed() == True else "Undirected",
        "domain": domain,
        "name": network_name,
        "nodes": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "density": round(nx.density(g), 3),
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


def append_file(new_row: pd.DataFrame) -> None:
    file_path = "/data/rpalermo/2026/distanceclosure_paper_2026/distanceclosure_analysis/distanceclosure_analysis/analyze_networks/data_output/dt_output_test.csv"

    new_row.to_csv(
        file_path, 
        mode="a", 
        header=not os.path.isfile(file_path), 
        index=False
    )


def log_results(graph: pd.DataFrame | nx.Graph, domain_name: str, network_name: str) -> None:    
    row = define_row(graph, domain_name, network_name)
    append_file(row)

    print(f"{network_name} finished.")
    print()


def cohort_undirected() -> None:
    root = Path(os.environ["NETWORK_DIR"]) / "network_samples" / "Undirected_Network_Studied"

    for domain in root.iterdir():
        for network_dir in domain.iterdir():
            network_location = network_dir / "network.csv"

            if network_location.exists():
                network_df = pd.read_csv(network_location)
                log_results(network_df, domain.name, network_dir.name)


def cohort_directed() -> None:
    root = Path(os.environ["NETWORK_DIR"]) / "network_samples" / "Directed_Network_Studied"

    for network_dir in root.iterdir():
        network_location = network_dir / "network.graphml"

        if network_location.exists():
            network_df = nx.read_graphml(network_location)
            log_results(network_df, root.name, network_dir.name)


def cohort_neurodata() -> None:
    root = Path(os.environ["NETWORK_DIR"]) / "network_samples" / "NeuroData"

    for network_dir in root.iterdir():
        if network_dir.suffix.lower() == ".graphml":
            G = nx.read_graphml(network_dir)

            if all("weight" in d for _, _, d in G.edges(data=True)) and isinstance(G, nx.DiGraph) and not G.is_multigraph():
                for _, _, d in G.edges(data=True):
                    d["distance"] = d.pop("weight")
                
                log_results(G, root.name, network_dir.stem)


# cohort_undirected()
# cohort_directed()
# cohort_neurodata()
