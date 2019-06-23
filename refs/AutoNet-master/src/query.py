from collections import defaultdict
import json
import sys

def loadEdge(bg_net):
	adj = defaultdict(list)
	edge_pmid = defaultdict(set)
	node_pmid = defaultdict(set)
	with open(bg_net) as IN:
		for line in IN:
			tmp = line.strip().split('\t')
			adj[tmp[0].lower()].append((tmp[1],tmp[1].lower()))
			adj[tmp[1].lower()].append((tmp[0],tmp[0].lower()))
			edge_pmid[(tmp[0].lower(), tmp[1].lower())].add(tmp[2])
			edge_pmid[(tmp[1].lower(), tmp[0].lower())].add(tmp[2])
			node_pmid[tmp[0].lower()].add(tmp[2])
			node_pmid[tmp[1].lower()].add(tmp[2])
	return adj, edge_pmid, node_pmid

def encode_pmid(pmid_index, pmid_list, pmid_dict, pmids):
	results = []
	for pmid in pmid_list:
		if pmid not in pmid_index:
			pmid_index.append(pmid)
		pmids.append({'index':pmid_index.index(pmid), 'url':pmid, 'title':pmid_dict[pmid]})
		results.append(pmid_index.index(pmid))
	return results

def expand(network, input_json, type_json, output_json):
	pmid_index = []
	pmid_global = []
	adj, edge_pmid, node_pmid = loadEdge(network)

	with open('./data/pmid.json') as IN:
		pmid_dict = json.load(IN)
	with open(input_json) as IN, open(type_json) as IN2:
		tmp = json.load(IN)
		for i,x in enumerate(tmp['nodes']):
			tmp['nodes'][i]["pmid"] = encode_pmid(pmid_index, node_pmid[x['title']], pmid_dict, pmid_global)
		seeds = map(lambda x: x['label'], tmp['nodes'])
		types = json.load(IN2)
	#adj = loadEdge(network)
	set_size = len(seeds)
	#print(types)
	for idx, seed in enumerate(seeds):
		#print idx, seed
		if len(adj[seed]) > 0:
			for surface, new_seed in adj[seed]:
				#print new_seed
				if new_seed == seed:
					continue
				if new_seed not in seeds and new_seed.capitalize() not in seeds:
					tmp['nodes'].append({
						"index": len(seeds),
						"id": len(seeds),
						"links": [
						#5
						], 
						"score": 8, 
						"level": 3, 
						"title": new_seed, 
						"type": types[surface],
						"label": surface,
						"pmid": encode_pmid(pmid_index, node_pmid[new_seed], pmid_dict, pmid_global)
					})
				#if new_seed.capitalize() in seeds:
				#	new_seed = new_seed.capitalize()
				if new_seed not in seeds:
					#print new_seed
					seeds.append(new_seed)
				if types[surface] not in tmp['node_types']:
					tmp['node_types'].append(types[surface])
					

				tmp['links'].append({
					"source": idx, 
					"target": seeds.index(new_seed), 
					"weight": 100, 
					"type": types[surface], 
					"pmid": encode_pmid(pmid_index, edge_pmid[seed, new_seed], pmid_dict, pmid_global)
				})

				if len(seeds) > 3 * set_size:
					tmp['pmids'] = pmid_global
					json.dump(tmp, open(output_json, 'w'))
					return 

if __name__ == '__main__':
	expand(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])