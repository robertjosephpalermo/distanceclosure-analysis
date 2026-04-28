from populate_data import single_use_backbone_output
import networkx as nx

# Insert the full file path to your graphml file:
path_to_graphml = ""

# Path to file output.
# If this path doesn't work replace it with your own.
path_to_output = "analyze_networks/data_output/single_use_output.csv"

G = nx.read_graphml(path_to_graphml)

single_use_backbone_output(
    graph=G, 

    # Specify the graphml edge attribute that will be interpreted as 'distance' by the backbone algorithm:
    edge_attribute="weight", 
    output_file_path=path_to_output
)
