import networkx as nx
import ast
import operator
import re

# class graph:

def parse_stp(path):

    G = nx.Graph()
    non_edge_lines = ['END','End', 'EOF', 'Edges']
    node_attr = {}

    with open(path, 'r') as f:
        all_lines = f.readlines()
        for line in all_lines:
            line=line.strip('\n')
            line = line.replace('\t', ' ')
            line = re.sub(' +', ' ', line)
            if line.startswith('Node'):
                n_nodes = int(line.split(' ')[1])
                G.add_nodes_from(range(1,n_nodes+1))
            if line.startswith('E') and not any([line.startswith(n) for n in non_edge_lines]):
                edge = line.split(' ')
                #print(edge)
                G.add_weighted_edges_from([[int(edge[1]), int(edge[2]), float(edge[3].strip('\n'))]])
            if line.startswith('TP'):
                #print(line)
                node_number = int(line.split(' ')[1])
                #print(node_number)
                #print(line.split(' ')[3])
                node_price = float(line.split(' ')[2].strip())
                node_attr[node_number] = node_price

    #print(node_attr)
    nx.set_node_attributes(G, name='prize', values=0)
    nx.set_node_attributes(G, name='prize', values = node_attr)
    return G


def getCostPerMeter(state):
    if state == 'BW':
        cost_per_meter = 76.67
    elif state == 'BY':
        cost_per_meter = 76.67
    elif state == 'BE':
        cost_per_meter = 50.40
    elif state == 'BB':
        cost_per_meter = 50.40
    elif state == 'HB':
        cost_per_meter = 49.78
    elif state == 'HH':
        cost_per_meter = 49.78
    elif state == 'HE':
        cost_per_meter = 63.15
    elif state == 'MV':
        cost_per_meter = 50.40
    elif state == 'NI':
        cost_per_meter = 49.78
    elif state == 'NW':
        cost_per_meter = 63.15
    elif state == 'RP':
        cost_per_meter = 63.15
    elif state == 'SL':
        cost_per_meter = 63.15
    elif state == 'SN':
        cost_per_meter = 50.40
    elif state == 'ST':
        cost_per_meter = 50.40
    elif state == 'SH':
        cost_per_meter = 49.78
    elif state == 'TH':
        cost_per_meter = 50.40
    else:
        cost_per_meter = 130

    return cost_per_meter


def parse_vdf(line):
    
    graph_data = line.split("|")
    splitpos = graph_data[0].find(",(")
    id = graph_data[0][:splitpos]
    parkdata = ast.literal_eval(graph_data[0][splitpos+1:])
    state = parkdata[1]
    
    #print("optimising instance " + id, file=sys.stderr)
    
    vertices = int(graph_data[1].split(':')[1]) #number of vertices
    terminals = ast.literal_eval(graph_data[3])
    start_terminal = int(graph_data[2].split(":")[1])
     
    edges = []
    for edgelist in graph_data[4:vertices+4]:
        edges.append(ast.literal_eval(edgelist))
        
    edge_dictionary = ast.literal_eval(graph_data[vertices+4])
    terminal_dictionary = ast.literal_eval(graph_data[vertices+5])
    terminals_in_bp = ast.literal_eval(graph_data[vertices+6])
    nodes_in_bp = ast.literal_eval(graph_data[vertices+7])
    #print("\tDone parsing", file=sys.stderr)
    if len(nodes_in_bp) > 0:
        # find the building cost per meter based on the federal state
        cost_per_meter = getCostPerMeter(state)
        #print("\tGot cost per meter", file=sys.stderr)
        # Prepare graph
        G=nx.empty_graph(vertices)
        for edgelist in edges:
            edgelist_weighted = [(e[0], e[1], cost_per_meter * e[2]) for e in edgelist]
            G.add_weighted_edges_from(edgelist_weighted)
        
        # Get shortest connection to park and update terminals, start_terminal
        d,p = nx.single_source_dijkstra(G, start_terminal)
        (mn, md) = min([(x, d[x]) for x in nodes_in_bp],key=operator.itemgetter(1))
        
        start_terminal = mn
        #print(terminals)
        terminals = {x:terminals[x] for x in terminals_in_bp if terminals_in_bp[x] == int(id.split(":")[1])}
        #terminals[start_terminal] = 100000000000 #make it profitable enough to be included in any solution, TODO: proper implementation
        nx.set_node_attributes(G, name='prize', values=0)
        nx.set_node_attributes(G, name='prize', values=terminals)
    else:
        return None, 0, 0, 0
    return G, start_terminal, cost_per_meter, id

if __name__=='__main__':
    
    from visualizations import visualize as vis
    
    line_no=1
    path = '../real_world_instances/real_world_instances_20.txt'
    with open(path) as f:
        line = f.read().split('\n')[line_no]
    print(line)
    G, start_terminal, cost_per_meter, id = parse_vdf(line)
    print('ID: {0}'.format(id))
    vis.plot_graph(G, draw_costs=False)



