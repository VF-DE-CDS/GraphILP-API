import networkx as nx
import pandas as pd


def create_dataframes(G):
    """
    Creates two dataframes out of a given graph
    :param G: a `NetworkX graph <https://networkx.org/documentation/stable/reference/introduction.html#graphs>`__
    :return:  Datasets representing the nodes and edges of the graph
    """
    # EDGES: Transforming Edges to Dataframe
    edges_list = list(G.edges())
    costs = []

    # NODES: Transform Nodes to DataFrame
    nodes_list = list(G.nodes())
    prices = []

    # EDGES: Extracting the Costs from the 'Attributes' - Dictionary returned by G.edges(data=True)
    for row in G.edges(data=True):
        costs.append(row[2]['weight'])

    # NODES: Extracting the prices of the Nodes from the 'Attributes' - Dictionary returned by G.nodes(data=True)
    for row in G.nodes(data=True):
        prices.append(row[1]['prize'])

    # EDGES: Creating a list of tuples. Each element is built up the structure 'startNode, endNode, costOfEdge'
    edges = []
    for i in range(len(costs)):
        edges.append((edges_list[i][0], edges_list[i][1], costs[i]))

    # NODES: Creating a list of tuples. Each element is built in the structure 'NewNodeIndex, Node, PriceOfNode'
    nodes = []
    for i in range(len(prices)):
        nodes.append((i, nodes_list[i], prices[i]))

    # EDGES: Create DataFrame from the Edges List
    df_edges = pd.DataFrame(edges, columns=['Node 1', 'Node 2', 'Costs'])

    # NODES: Create DataFrame from the Nodes List
    df_nodes = pd.DataFrame(nodes, columns=['NewNodeIndex', 'Node', 'prize'])
    # ** END MANIPULATION

    return df_nodes, df_edges


def find_indeces(df_nodes, terminals=None, root=None, accesspoints=None):
    """
    Find the index of the artificial Root, the terminals and the accespoints in the DataFrame
    dfNodes.query is a Pandas Dataframe method
    @root is used to specify we are searching for the variable root
    iloc gets the value at the [nth] position
    'NewNodeIndex' is the value we are finally interested in
    :param df_nodes: Dataset including all the nodes
    :param terminals: List of all terminals of the input graph
    :param root: Inteer representing the root. Should be -1 if there is no root.
    :param accesspoints: List of all accesspoints of the input graph
    :return:
    """
    if root != -1:
        root_index = int(df_nodes.query('Node == @root').iloc[0]['NewNodeIndex'])
    else:
        root_index = -1

    # Find the indeces of the Terminals in the Dataframe. Same as with the root
    list_terminals_indeces = df_nodes.query('Node == @terminals').values.tolist()
    terminals_indeces = []
    for entry in list_terminals_indeces:
        terminals_indeces.append(entry[0])

    list_accesspoints_indeces = df_nodes.query('Node == @accesspoints').values.tolist()
    accesspoints_indeces = []
    for entry in list_accesspoints_indeces:
        accesspoints_indeces.append(entry[0])

    return root_index, terminals_indeces, accesspoints_indeces


def merge_dataframes(df_nodes, df_edges):
    """
    The Final Dataframe contains all information needed for the transformation both into the new Data format and
    from the new Data format.
    It is important not to change df_final!
    The label on the columns is arbitrary.
    NewNodeIndex_Node1 and NewNodeIndex_Node2 refers to the new labels of the nodes
    :param df_nodes:
    :param df_edges:
    :return:
    """

    df_final = df_edges.merge(df_nodes, left_on='Node 1', right_on='Node')
    df_final = df_final.merge(df_nodes, left_on='Node 2', right_on='Node', suffixes=('_Node1', '_Node2'))

    # Since we don't want to change the df_final, we make a copy to continue our work
    df_changed = df_final.copy()

    # First, we change the labels of the start and end nodes of the edges to the new format.
    # Since we already have the new format in the df_final and df_changed, all we have to do is to assign new values
    # to the respecte Node 1 and Node 2 Columns.
    df_changed['Node 1'] = df_changed['NewNodeIndex_Node1']
    df_changed['Node 2'] = df_changed['NewNodeIndex_Node2']

    # Then we can drop the columns containg the old labels as to have a more condensed dataFrame
    # df_changed is now built up in the following structure:
    # StartNode, EndNode, CostOfEdge, PriceStartNode, PriceEndNode
    df_changed = df_changed.drop(columns=['Node_Node1', 'Node_Node2', 'NewNodeIndex_Node1', 'NewNodeIndex_Node2'])

    return df_final, df_changed


def dataframe_to_list(df_final, df_nodes, df_changed):
    """
    All the information we need is stored in the dataframe. Now we need to exract the information and put it
    into the right format for the pcst_fast library, i.e. lists where the position in the array defines
    the attributes of nodes / edges
    :param df_final: Output 1 of merge_dataframes
    :param df_nodes: Dataframe including all nodes
    :param df_changed: Output 2 of merge_dataframes
    :return:
    """

    # First, extract the edges, i.e. StartNode and EndNode
    edges = df_changed[['Node 1', 'Node 2']].values.tolist()

    # Next, extract the Prices of the Nodes and the Costs of the Edges and also put those into a list.
    node_prices = df_nodes['prize'].values.tolist()
    edge_costs = df_final['Costs'].values.tolist()

    return edges, node_prices, edge_costs


def reformat_to_graph(result_nodes, result_edges, df_final, df_nodes):
    """
    Create a graph out of the solution found by pcst-fast
    :param result_nodes: Dataset of nodes found by pcst-fast
    :param result_edges: Dataset of edges found by pcst-fast
    :param df_final: Output 1 of merge_dataframes
    :param df_nodes: Dataframe including all nodes of the input graph
    :return:
    """
    resulting_edges = df_final.iloc[result_edges]
    resulting_edges = resulting_edges[['Node 1', 'Node 2', 'Costs']]
    # resulting_graph = nx.from_pandas_dataframe(resulting_edges, 'Node 1', 'Node 2', 'Costs')
    resulting_graph = nx.from_pandas_edgelist(resulting_edges, 'Node 1', "Node 2", edge_attr='Costs')

    resulting_nodes = df_nodes.iloc[result_nodes]
    resulting_nodes = resulting_nodes.drop(columns=['NewNodeIndex'])
    prizes_list = resulting_nodes.to_dict('split')['data']
    for i in range(len(prizes_list)):
        resulting_graph.nodes[prizes_list[i][0]]['prize'] = prizes_list[i][1]

    return resulting_nodes, resulting_edges, resulting_graph, prizes_list
