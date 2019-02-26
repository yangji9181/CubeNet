import json
from collections import defaultdict
from config import *
from dataset import Dataset


def analysis(data, args):
	network = {}
	query = json.load(open(args.query_file, 'r'))
	nodes = {}

	#initialize node sets of each type
	for t in data.meta['node'].keys():
		nodes[t] = set()
		if t in query['filters'].keys():
			for label in query['filters'][t]:
				nodes[t] |= set(data.labels[t][label])
		else:
			nodes[t] = set(data.nodes[t].keys())

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
	network['links'] = []
	node_size = defaultdict(int)
	for link_t in data.meta['link'].keys():
		if data.meta['link'][link_t][0] in query['nodes'] and data.meta['link'][link_t][1] in query['nodes']:
			for n1 in nodes[data.meta['link'][link_t][0]]:
				if n1 in data.links[link_t].keys():
					n2set = set(data.links[link_t][n1].keys()) & nodes[data.meta['link'][link_t][1]]
					node_size[n1] += len(n2set)
					for n2 in n2set:
						network['links'].append({'source': n1, 'target': n2, 'weight': int(data.links[link_t][n1][n2])})

	#aggregate nodes of different types
	network['nodes'] = []
	for t in nodes.keys():
		if t in query['nodes']:
			for n in nodes[t]:
				network['nodes'].append({'id': n, 'type': data.meta['node'][t], 'name': data.nodes[t][n], 'size': node_size[n]})

	
	json.dump(
		network, 
		open(args.network_file, 'w'),
		indent=4, 
		separators=(',', ': ')
		)

	 
def test(args):
	q1 = {"nodes": ["0", "1", "2", "3"], "filters": {}}
	q2 = {"nodes": ["0", "1", "2", "3"], "filters": {"2": ["0"], "3": ["2", "3"]}}
	q3 = {"nodes": ["0", "1"], "filters": {"0": ["3"], "2": ["0"], "3": ["2", "3"]}}
	q4 = {"nodes": ["1"], "filters": {"2": ["0"], "3": ["2", "3"]}}
	q5 = {"nodes": ["1"], "filters": {"1": ["1"], "2": ["0"], "3": ["2", "3"]}}

	json.dump(q5, open(args.query_file, 'w'))
	data = Dataset(args)
	analysis(data, args)

if __name__ == '__main__':
	test(args)