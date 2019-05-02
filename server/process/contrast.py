import json
from collections import defaultdict
#from server.process.config import *
from server.process.dataset import Dataset


def analysis(data, args):
	network = {}
	query = json.load(open(args['contrast_q'], 'r'))
	nodes = {}
	supernode = {}
	#initialize node sets of each type
	for t in data.meta['node'].keys():
		nodes[t] = set()
		if t in query['filters'].keys():
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
					network['nodes'].append({'id': n, 'type': data.meta['node'][t], 'name': data.nodes[t][n], 'size': node_size[n]})
				else:
					sup.add(supernode[n])
			for n in sup:
				network['nodes'].append({'id': n, 'type': data.meta['node'][t], 'name': data.meta['label'][t][n.split('/')[2]][0], 'size': node_size[n]})

	#collect labels
	network['labels'] = defaultdict(list)
	if 'evals' in query:
		for t in query['evals'].keys():
			for label in query['evals'][t]:
				for node in data.labels[t][label]:
					network['labels'][t].append((label, node))

	json.dump(
		network,
		open(args['contrast_n'], 'w'),
		indent=4,
		separators=(',', ': ')
		)


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