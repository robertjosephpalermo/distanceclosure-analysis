from populate_data import log_backbone_output
from pathlib import Path
import networkx as nx
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def undirected_graph_cohort() -> None:
    root = Path(os.environ["NETWORK_DIR"]) / "network_samples" / "Undirected_Network_Studied"

    for domain in root.iterdir():
        for network_dir in domain.iterdir():
            network_location = network_dir / "network.csv"

            if network_location.exists():
                network_df = pd.read_csv(network_location)
                log_backbone_output(
                    graph=network_df, 
                    domain_name=domain.name, 
                    network_name=network_dir.name,
                    output_file_name="dt_output_test.csv",
                )


def directed_graph_cohort() -> None:
    root = Path(os.environ["NETWORK_DIR"]) / "network_samples" / "Directed_Network_Studied"

    for network_dir in root.iterdir():
        network_location = network_dir / "network.graphml"

        if network_location.exists():
            network_df = nx.read_graphml(network_location)

            log_backbone_output(
                graph=network_df,
                domain_name=root.name,
                network_name=network_dir.name, 
                output_file_name="dt_output_test.csv",
            )


def neurodata_graph_cohort() -> None:
    root = Path(os.environ["NETWORK_DIR"]) / "network_samples" / "NeuroData"

    for network_dir in root.iterdir():
        if network_dir.suffix.lower() == ".graphml":
            G = nx.read_graphml(network_dir)

            if all("weight" in d for _, _, d in G.edges(data=True)) and isinstance(G, nx.DiGraph) and not G.is_multigraph():
                for _, _, d in G.edges(data=True):
                    d["distance"] = d.pop("weight")
                
                log_backbone_output(
                    graph=G, 
                    domain_name=root.name, 
                    network_name=network_dir.stem, 
                    output_file_name="dt_output_test.csv",
                )

# undirected_graph_cohort()
# directed_graph_cohort()
# neurodata_graph_cohort()
