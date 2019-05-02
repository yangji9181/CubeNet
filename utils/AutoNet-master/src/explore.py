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

def explore(network, keyword, type_json, output_json):
	keyword = keyword.lower()
	pmid_index = []
	pmid_global = []
	adj, edge_pmid, node_pmid = loadEdge(network)

	with open(type_json) as IN, open('./data/pmid.json') as PMID:
		tmp = {"nodes":[], "links":[], "node_types":[]}
		types = json.load(IN)
		pmid_dict = json.load(PMID)
		seeds = []
		tmp['nodes'].append({
						"index": len(seeds),
						"id": len(seeds),
						"links": [
						#5
						], 
						"score": 10, 
						"level": 3, 
						"title": keyword, 
						"type": types[keyword],
						"label": keyword,
						"pmid": encode_pmid(pmid_index, node_pmid[keyword], pmid_dict, pmid_global)
					})

		seeds.append(keyword)
		tmp['node_types'].append(types[keyword])
		
	
	#print(types)
	current_links = set()
	for idx, seed in enumerate(seeds):
		#print idx, seed
		if len(adj[seed]) > 0:
			for surface, new_seed in adj[seed]:
				#print new_seed
				if new_seed == seed:
					continue
				#new_seed = new_seed.split('_')[0]
				if new_seed not in seeds:
					tmp['nodes'].append({
						"index": len(seeds),
						"id": len(seeds),
						"links": [
						# need to be discussed
						#5
						], 
						"score": 8, 
						"level": 3, 
						"title": new_seed, 
						"type": types[surface],
						"label": surface,
						"pmid": encode_pmid(pmid_index, node_pmid[new_seed], pmid_dict, pmid_global)
					})
					seeds.append(new_seed)
				if types[surface] not in tmp['node_types']:
					tmp['node_types'].append(types[surface])
					
				#for other_node in seeds:
				for surface, other_node in adj[new_seed]:
					if other_node == new_seed or other_node not in seeds:
						continue
					if (other_node, new_seed) not in current_links and (other_node, new_seed) in edge_pmid:
						#print(surface)
						current_links.add((other_node, new_seed))
						current_links.add((new_seed, other_node))
						tmp['links'].append({
							"source": seeds.index(other_node), 
							"target": seeds.index(new_seed), 
							"weight": 100, 
							"type": types[surface],
							"pmid": encode_pmid(pmid_index, edge_pmid[other_node, new_seed], pmid_dict, pmid_global)
						})
						if seeds.index(new_seed) not in tmp['nodes'][seeds.index(other_node)]['links']:
							tmp['nodes'][seeds.index(other_node)]['links'].append(seeds.index(new_seed))
						if seeds.index(other_node) not in tmp['nodes'][seeds.index(new_seed)]['links']:
							tmp['nodes'][seeds.index(new_seed)]['links'].append(seeds.index(other_node))
				if len(seeds) > 32:
					print(len(tmp['links']))
					#print(tmp['node_types'])
					tmp['pmids'] = pmid_global
					json.dump(tmp, open(output_json, 'w'))
					return
					
	
	#print(len(tmp['nodes']))
				    
					#seeds.append(new_seed)
	#print(tmp)

if __name__ == '__main__':
	explore(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])