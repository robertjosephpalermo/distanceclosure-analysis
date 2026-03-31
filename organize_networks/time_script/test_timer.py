from FunctionTimer import FunctionTimer
import distanceclosure as dc
import networkx as nx

# Example from: https://casci-lab.github.io/distanceclosure/
edgelist = {
    ('s', 'a'): 8,
    ('s', 'c'): 6,
    ('s', 'd'): 5,
    ('a', 'd'): 2,
    ('a', 'e'): 1,
    ('b', 'e'): 6,
    ('c', 'd'): 3,
    ('c', 'f'): 9,
    ('d', 'f'): 4,
    ('e', 'g'): 4,
    ('f', 'g'): 0,
}
G = nx.from_edgelist(edgelist)
nx.set_edge_attributes(G, name='distance', values=edgelist)

timer = FunctionTimer(module=dc)
umb = timer.ultrametric_backbone(G, weight='distance', verbose=True)
timer.json_dump()


