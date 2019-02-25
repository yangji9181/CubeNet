import json
import sys

file_path = 'network4.json'
# file_path = sys.argv[0]
output_file_path = 'new_' + file_path

def generate_json(data):
	node_ids = set([])

	output = {}
	output_nodes = []
	for node in data['nodes']:
		n = {}
		n['id'] = node[0]
		n['type'] = node[1]
		n['name'] = node[2]
		n['size'] = 1
		output_nodes.append(n)
		# validation
		node_ids.add(node[0])

	output_links = []
	for link in data['links']:
		l = {}
		l['source'] = link[0]
		l['target'] = link[1]
		l['weight'] = link[2]
		output_links.append(l)
		# validation
		if link[0] not in node_ids or link[1] not in node_ids:
			print("node not exists")

	output['nodes'] = output_nodes
	output['links'] = output_links

	return output


output = {}
with open(file_path) as f:
    data = json.load(f)
    output = generate_json(data)

with open(output_file_path, 'w') as f:  
    json.dump(output, f)
