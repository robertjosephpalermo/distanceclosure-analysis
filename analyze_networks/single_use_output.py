from populate_data import single_use_backbone_output
import networkx as nx

path_to_graphml = "..."
G = nx.read_graphml(path_to_graphml)

single_use_backbone_output(
    graph=G, 
    edge_attribute="weight", 
    output_file_name="output.csv"
)