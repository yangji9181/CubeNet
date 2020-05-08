import json
from collections import defaultdict

import networkx as nx
from networkx.readwrite import json_graph

def exploration(query, data):
    network = {}
    nodes = {}
    supernode = {}
    #initialize node sets of each type
    for t in data.meta['node'].keys():
        nodes[t] = set()
        if 'filters' in query and t in query['filters'].keys():
            for label in query['filters'][t]:
                nodes[t] |= set(data.labels[t][label])
        else:
            nodes[t] = set(data.nodes[t].keys())
        for n in nodes[t]:
            supernode[n] = n
        if 'merges' in query and t in query['merges'].keys():
            for label in query['merges'][t]:
                for n in data.labels[t][label]:
                    supernode[n] = 's/'+t+'/'+label

    #compute filters by intersection
    for t in nodes.keys():
        for link_t in data.meta['link'].keys():
            if data.meta['link'][link_t][0] == t and data.meta['link'][link_t][1] != t:
                tmp = set()
                for n in nodes[t]:
                    if n in data.links[link_t].keys():
                        tmp |= set(data.links[link_t][n].keys())
                nodes[data.meta['link'][link_t][1]] &= tmp

    #extract links
    links = defaultdict(int)
    node_size = defaultdict(int)
    for link_t in data.meta['link'].keys():
        if data.meta['link'][link_t][0] in query['nodes'] and data.meta['link'][link_t][1] in query['nodes']:
            for n1 in nodes[data.meta['link'][link_t][0]]:
                if n1 in data.links[link_t].keys():
                    n2set = set(data.links[link_t][n1].keys()) & nodes[data.meta['link'][link_t][1]]
                    node_size[supernode[n1]] += len(n2set)
                    for n2 in n2set:
                        links[supernode[n1]+'_'+supernode[n2]] += int(data.links[link_t][n1][n2])
                        #node_size[supernode[n2]] += 1

    #collect links
    network['links'] = []
    for k in links.keys():
        n1 = k.split('_')[0]
        n2 = k.split('_')[1]
        network['links'].append({'source': n1, 'target': n2, 'weight': links[k]})

    #collect nodes
    network['nodes'] = []
    for t in nodes.keys():
        if t in query['nodes']:
            sup = set()
            for n in nodes[t]:
                if supernode[n] == n:
                    network['nodes'].append({'id': n, 'type': data.meta['node'][t]['name'], 'name': data.nodes[t][n], 'size': node_size[n]})
                else:
                    sup.add(supernode[n])
            for n in sup:
                network['nodes'].append({'id': n, 'type': data.meta['node'][t]['name'], 'name': data.meta['label'][t][n.split('/')[2]][0], 'size': node_size[n]})

    return network

def properties(dim):
    NUM_PROPERTIES = 3
    from server.process.config import args
    meta = json.load(open(args['meta_json'], 'r'))
    query = json.load(open(args['query_json'], 'r'))
    from server.process.dataset import Dataset
    data = Dataset(args)

    # add the contrasted node type to the subnetworks
    if dim not in query['nodes']:
        query['nodes'].append(dim)

    # remove the contrasted node type from filters
    if dim in query['filters']:
        query['filters'].pop(dim)

    # initialize property list
    prop = [{} for i in range(NUM_PROPERTIES)]
    prop[0]['name'] = 'size'
    prop[1]['name'] = 'radius'
    prop[2]['name'] = 'density'
    prop[0]['labels'] = []
    prop[1]['labels'] = []
    prop[2]['labels'] = []

    for i in meta['label'][dim]:
        # retrieve network connected to the contrasted node
        query['filters'][dim] = [i]
        network = exploration(query, data)
        
        sub_graph = json_graph.node_link_graph(network)
        gen = nx.connected_component_subgraphs(sub_graph)

        if len(network['nodes']) > 0:
            connected_graph = max(gen, key=len)
            prop[0]['labels'].append({'name': meta['label'][dim][i][0], 'val': len(network['nodes'])})
            prop[1]['labels'].append({'name': meta['label'][dim][i][0], 'val': nx.radius(connected_graph)})
            prop[2]['labels'].append({'name': meta['label'][dim][i][0], 'val': nx.density(connected_graph)})
        else:
            prop[0]['labels'].append({'name': meta['label'][dim][i][0], 'val': 0})
            prop[1]['labels'].append({'name': meta['label'][dim][i][0], 'val': 0})
            prop[2]['labels'].append({'name': meta['label'][dim][i][0], 'val': 0})

        query['filters'].pop(dim)

    results = {}
    results['node_type'] = meta['node'][dim]['name']
    results['properties'] = prop

    return results

def patterns_dnm(dim):

    # How the new pattern mining works. 
    #
    # 1) Generate distinctive frequent patterns for each label
    #    - a) First, use exploration to construct graph for each label (use existing code)
    #    - b) Then, convert graphs to gSpan/CloseGraph format. Run gSpan/CloseGraph and find some frequent patterns.
    #    - c) Keep only patterns that are distinctive, aka their average weight is higher for this label than other labels.
    # 2) Figure out which patterns are best using discriminative network metric
    #    - a) Use size, cohesiveness, and strength to rank the patterns and return the top K patterns
    #    - b) For each label, construct a graph consisting of all those patterns and any nodes with the given label.
    #    - c) Return this graph

    # 1a - First, use exploration to construct graph for each label (use existing code)
    from server.process.config import args
    query = json.load(open(args['query_json'], 'r'))
    from server.process.dataset import Dataset
    data = Dataset(args)
    meta = data.meta

    # add the contrasted node type to the subnetworks
    if dim not in query['nodes']:
        query['nodes'].append(dim)

    # remove the contrasted node type from filters
    if dim in query['filters']:
        query['filters'].pop(dim)

    counts = defaultdict(dict)
    node_type = {}
    node_name = {}
    labelNetworks = {}
    for i in meta['label'][dim]:
        # retrieve network connected to the contrasted node
        query['filters'][dim] = [i]
        query['merges'][dim] = [i]
        labelNetworks[i] = exploration(query, data)

    #print (labelNetworks)

    # 1b - Convert graphs to gSpan/CloseGraph format. Run gSpan/CloseGraph and find frequent patterns.

    # Convert CubeNet graph structure to gSpan/CloseGraph format 
    filename='./process/test.txt'
    vertexID = 10
    nodeIdToVertexId = {}

    # Supernodes have a different ID structure "ex. s/1/0" so they have to be converted into numbers for gSpan to work.
    # This dictionary stores the mapping two ways
    superNodeToNodeId = {}

    # Find the maximum node ID
    nodeIDs = []
    for i in meta['label'][dim]:
        for node in labelNetworks[i]['nodes']:
            if node['id'].isdigit():
                nodeIDs.append(int(node['id']))
    maxNodeID = max(nodeIDs)

    # Start with maxNodeID + 1 for the first supernode, then +2 for the second, etc.
    maxNodeID += 1
    print(maxNodeID)
    with open(filename,'w') as f:
        f.truncate()
        for i in meta['label'][dim]:
            f.write(str("t # "+i))
            f.write('\n')
            for node in labelNetworks[i]['nodes']:
                if not node['id'].isdigit():
                    if not node['id'] in superNodeToNodeId:
                        superNodeToNodeId[str(maxNodeID)] = node['id']
                        superNodeToNodeId[node['id']] = str(maxNodeID)
                        maxNodeID += 1
                    f.write(str("v " + str(vertexID) + " " +str(superNodeToNodeId[node['id']])))
                else:
                    f.write(str("v " + str(vertexID) + " " +str(node['id'])))
                f.write('\n')
                nodeIdToVertexId[node['id']] = vertexID
                vertexID += 10
            for link in labelNetworks[i]['links']:
                source = link['source']
                target = link['target']
                if(not source == target):
                    f.write(str("e " + str(nodeIdToVertexId[source]) + " " + str(nodeIdToVertexId[target]) + " 0"))
                    f.write('\n')

        f.close()

    print(superNodeToNodeId)


    import numpy as np
    from server.process.algorithms import g_span as gSpan
    from server.process.algorithms import load_graphs



    print("STarting gspan")
    MIN_SUP = int(len(meta['label'][dim])/2 + 0.5)
    graphs = load_graphs(filename)
    n = len(graphs)
    extensions = []
    gSpan([], graphs, min_sup=MIN_SUP, extensions=extensions)
    for i, ext in enumerate(extensions):
        print('Pattern %d' % (i+1))
        for _c in ext:
            print(_c)
        print('')
    

    # 1c - For each label, only keep patterns whose average weight is higher for this label than in other labels

    # The variable 'extensions' now contains the different frequent patterns. Each frequent pattern is a list of edges of the form:
    # (v1, v2, nodeID1, nodeID2, edgeID). We need to extract those into a format that can be used by the discriminative network metric.

    # First, for each pattern, calculate weight of each pattern in each label
    # patternWeights is a list of dictionaries, where each dictionary gives the avg link weight of the pattern for each label
    # patternWeights[2][1] gives the avg link weight of pattern 2 in label 1
    patternWeights = []
    for i in range(len(extensions)):
        patternWeights.append({})
        for label in meta['label'][dim]:
            patternWeights[i][label] = 0
        for edge in extensions[i]:
            source = edge[2]
            target = edge[3]
            if(source in superNodeToNodeId):
                source = superNodeToNodeId[source]
            if(target in superNodeToNodeId):
                target = superNodeToNodeId[target]

            # Check each label graph for this edge
            for label in meta['label'][dim]:
                for link in labelNetworks[label]['links']:
                    if link['source'] == source and link['target'] == target \
                        or link['source'] == target and link['target'] == source:

                        patternWeights[i][label] += link['weight']
        print (patternWeights[i])
        for label in meta['label'][dim]:
            patternWeights[i][label] /= len(extensions[i])

    print (patternWeights)


    # Find the distinctive patterns
    THRESHOLD_DISTINCT = 1 / len(meta['label'][dim])

    # Store a list of frequent patterns for each label
    distinctiveFrequentPatterns = {}
    for label in meta['label'][dim]:
        distinctiveFrequentPatterns[label] = []

    for i in range(len(extensions)):
        patternWeightSum = 0
        for label in patternWeights[i]:
            patternWeightSum += patternWeights[i][label]
        for label in patternWeights[i]:
            if patternWeights[i][label] > (THRESHOLD_DISTINCT * patternWeightSum):
                # This pattern is found distinctly in this label's network. Add it to the list of distinctive patterns!
                # We need to convert it from the form returned by gSpan to the form used by discriminative network metric
                pattern = {}
                for edge in extensions[i]:
                    source = edge[2]
                    target = edge[3]
                    if(source in superNodeToNodeId):
                        source = superNodeToNodeId[source]
                    if(target in superNodeToNodeId):
                        target = superNodeToNodeId[target]

                    for link in labelNetworks[label]['links']:
                        if link['source'] == source and link['target'] == target:
                            if(source not in pattern):
                                pattern[source] = {}
                            pattern[source][target] = link['weight']

                distinctiveFrequentPatterns[label].append(pattern)

    #print(distinctiveFrequentPatterns)


    # 2a - For each label, use significance score to rank the patterns. Return top K patterns.
    K = 1
    from server.process.metrics import choose_best_patterns, score_size, score_cohesiveness, score_strength
    bestPatterns = {}
    for i in meta['label'][dim]:
        bestPatterns[i] = choose_best_patterns(distinctiveFrequentPatterns[i], K)
        print("i", i , "Patterns: ", bestPatterns[i])

    # 2b - For each label, construct graph with all nodes and links in patterns, plus all nodes/links of the given label, connected to this pattern

    # The easiest way to do this is to start with the labelNetwork we constructed before and only choose nodes/links that we want
    finalLabelNetworks = {}
    for i in meta['label'][dim]:
        finalLabelNetworks[meta['label'][dim][i][0]] = {'nodes':[], 'links':[]}

        nodesOfThisLabel = set()
        # Populate nodes. Only choose nodes of this label and those that appear in the best patterns
        for node in labelNetworks[i]['nodes']:
            if node['type'] == meta['node'][dim]['name']:
                finalLabelNetworks[meta['label'][dim][i][0]]['nodes'].append(node)
                nodesOfThisLabel.add(node['id'])
            else:
                # If node is in one of the best patterns, add it. Note the node could either be a source or a target
                addNode = False
                for pattern in bestPatterns[i]:
                    if node['id'] in pattern.keys():
                        addNode = True
                    else:
                        targets = set()
                        for node1 in pattern:
                            for node2 in pattern[node1]:
                                targets.add(node2)
                        if node['id'] in targets:
                            addNode = True
                if(addNode):
                    finalLabelNetworks[meta['label'][dim][i][0]]['nodes'].append(node)

        # Populate links. Only choose links in our best patterns and those connecting this label's nodes to the best patterns
        for link in labelNetworks[i]['links']:
            source = link['source']
            target = link['target']
            addLink = False


            nodesInBestPatterns = set()
            # Is this link in our best patterns?
            for pattern in bestPatterns[i]:
                for node1 in pattern:
                    for node2 in pattern[node1]:
                        nodesInBestPatterns.add(node1)
                        nodesInBestPatterns.add(node2)
                        if node1 == source and node2 == target:
                            addLink = True
            # Is this link connecting two nodes of this label?
            if source in nodesOfThisLabel and target in nodesOfThisLabel:
                addLink = True

            # Is this link connecting a node of this label to a node in the best patterns?
            if source in nodesInBestPatterns and target in nodesOfThisLabel \
                or target in nodesInBestPatterns and source in nodesOfThisLabel:
                addLink = True

            if addLink:
                finalLabelNetworks[meta['label'][dim][i][0]]['links'].append(link)

    return finalLabelNetworks




def patterns(dim):
    THRESH_POP = 0.3
    THRESH_DIS = 0.2
    THRESH_INT = 10

    from server.process.config import args
    query = json.load(open(args['query_json'], 'r'))
    from server.process.dataset import Dataset
    data = Dataset(args)
    meta = data.meta
    # print(meta['node'])

    # add the contrasted node type to the subnetworks
    if dim not in query['nodes']:
        query['nodes'].append(dim)

    # remove the contrasted node type from filters
    if dim in query['filters']:
        query['filters'].pop(dim)

    counts = defaultdict(dict)
    node_type = {}
    node_name = {}
    networks = {}
    for i in meta['label'][dim]:
        # retrieve network connected to the contrasted node
        query['filters'][dim] = [i]
        query['merges'][dim] = [i]
        network = exploration(query, data)
        links = {}
        for link in network['links']:
            links[link['source']+'_'+link['target']] = link['weight']
        for node in network['nodes']:
            if node['type'] != meta['node'][dim]['name']:
                if node['id'] not in node_type:
                    node_type[node['id']] = node['type']
                    node_name[node['id']] = node['name']
                if (node['id']+'_s/'+dim+'/'+i) in links:
                    #print(node)
                    counts[node['id']][i] = links[node['id']+'_s/'+dim+'/'+i]
                    if 'total' in counts[node['id']]:
                        counts[node['id']]['total'] += links[node['id']+'_s/'+dim+'/'+i]
                    else:
                        counts[node['id']]['total'] = links[node['id']+'_s/'+dim+'/'+i]

    query['merges'].pop(dim)
    for i in meta['label'][dim]:
        networks[meta['label'][dim][i][0]] = {'nodes':[], 'links':[]}
        query['filters'][dim] = [i]
        network = exploration(query, data)
        # print(network['nodes'])
        links = {}
        for link in network['links']:
            links[link['source']+'_'+link['target']] = link['weight']
        for node in network['nodes']:
            if node['type'] == meta['node'][dim]['name']:
                networks[meta['label'][dim][i][0]]['nodes'].append(node)
        for node_id in counts.keys():
            if i in counts[node_id]:
                if counts[node_id]['total'] > THRESH_POP * len(meta['label'][dim]) \
                        and counts[node_id][i] > THRESH_DIS * counts[node_id]['total']:
                    networks[meta['label'][dim][i][0]]['nodes'].append({
                                                 'id': node_id,
                                                 'type': node_type[node_id],
                                                 'name': node_name[node_id],
                                                 'size': counts[node_id][i]})
        for node_1 in networks[meta['label'][dim][i][0]]['nodes']:
            for node_2 in networks[meta['label'][dim][i][0]]['nodes']:
                if node_1['id'] != node_2['id']:
                    if (node_1['id']+'_'+node_2['id']) in links:
                        networks[meta['label'][dim][i][0]]['links'].append({
                                                     'source': node_1['id'],
                                                     'target': node_2['id'],
                                                     'weight': links[node_1['id']+'_'+node_2['id']]})

    return networks


def cell_color(query, data):
    filter_labels = defaultdict(list)
    for dim in data.meta['node']:
        if data.meta['node'][dim]['cube']:
            for label in data.meta['label'][dim]:
                filter_labels[dim].append(label)

    assert len(filter_labels) == 3

    if 'filters' in query:
        for dim in query['filters']:
            if dim in filter_labels:
                filter_labels[dim] = list(set(filter_labels[dim]) & set(query['filters'][dim]))
    keys = list(filter_labels.keys())
    filter_cells = []
    for i in filter_labels[keys[0]]:
        for j in filter_labels[keys[1]]:
            for k in filter_labels[keys[2]]:
                filter_cells.append({keys[0]: i, keys[1]: j, keys[2]: k})

    merge_cells = []
    if 'merges' in query:
        for key in keys:
            if key in query['merges']:
                for cell in filter_cells:
                    if key in cell and cell[key] in query['merges'][key]:
                        merge_cells.append(cell)

    obj = {'filters': filter_cells, 'merges': merge_cells}
    return obj


'''
def test(args):
    q0 = {"nodes": ["0", "1", "2", "3"], "filters": {"0": ["3"], "1": ["1"]}, "merges": {"2": ["0", "1"]}}
    q1 = {"nodes": ["0", "1", "2", "3"], "filters": {}, "evals": {"1": ["0", "1"]}}
    q2 = {"nodes": ["0", "1", "2", "3"], "filters": {"2": ["0"], "3": ["2", "3"]}, "evals": {"1": ["0", "1"]}}
    q3 = {"nodes": ["0", "1"], "filters": {"0": ["3"], "2": ["0"], "3": ["2", "3"]}}
    q4 = {"nodes": ["1"], "filters": {"2": ["0"], "3": ["2", "3"]}}
    q5 = {"nodes": ["1"], "filters": {"1": ["1"], "2": ["0"], "3": ["2", "3"]}}

    json.dump(q2, open(args['query_file'], 'w'))
    data = Dataset(args)
    analysis(data, args)

if __name__ == '__main__':
    test(args)
'''