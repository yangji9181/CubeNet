import pickle
import os.path
import json
from collections import defaultdict
#from server.process.config import *

class Dataset(object):
	def __init__(self, args):
		self.args = args
		if not self.load():
			self.read_meta()
			self.read_node()
			self.read_link()
			self.read_label()
			self.save()

	def read_meta(self):
		self.meta = {}
		self.meta['node'] = {}
		self.meta['link'] = {}
		self.meta['label'] = defaultdict(dict)
		f = open(self.args['meta_file'], 'r')
		for line in f:
			tokens = line.strip().split('\t')
			if tokens[0] == 'n':
				self.meta['node'][tokens[1]] = tokens[2]
			elif tokens[0] == 'l':
				self.meta['link'][tokens[1]] = (tokens[3], tokens[4])
			elif tokens[0] == 's':
				self.meta['label'][tokens[1]][tokens[2]] = (tokens[4], tokens[3])

	def read_node(self):
		self.nodes = defaultdict(dict)
		self.nodes_tmp = []
		f = open(self.args['node_file'], 'r')
		n = 0
		for line in f:
			tokens = line.strip().split('\t')
			if tokens[1] in self.meta['node']:
				self.nodes[tokens[1]][str(n)] = tokens[0]
				self.nodes_tmp.append(tokens[0])
			n += 1

	def read_link(self):
		self.links = defaultdict(dict)
		f = open(self.args['link_file'], 'r')
		for line in f:
			tokens = line.strip().split('\t')
			if tokens[2] in self.meta['link']:
				if tokens[0] not in self.links[tokens[2]]:
					self.links[tokens[2]][tokens[0]] = {}
				self.links[tokens[2]][tokens[0]][tokens[1]] = tokens[3]

	def read_label(self):
		self.labels = defaultdict(dict)
		unused = []
		unlabeled = self.nodes_tmp[:]
		f = open(self.args['label_file'], 'r')
		for line in f:
			tokens = line.strip().split('\t')
			if tokens[1] in self.meta['label'] and tokens[2] in self.meta['label'][tokens[1]]:
				if tokens[2] not in self.labels[tokens[1]]:
					self.labels[tokens[1]][tokens[2]] = []
				if tokens[0] in self.nodes_tmp:
					indices = [i for i, x in enumerate(self.nodes_tmp) if x == tokens[0]]
					for ind in indices:
						self.labels[tokens[1]][tokens[2]].append(str(ind))
						if tokens[0] in unlabeled:
							unlabeled.remove(tokens[0])
				else:
					unused.append(tokens[0])
			else:
				unused.append(tokens[0])
		print('unused labels:' + str(unused))
		print('unlabeled nodes:' + str(unlabeled))
		del self.nodes_tmp

	def load(self):
		if os.path.isfile(self.args['pickle_file']):
			file = open(self.args['pickle_file'], 'rb')
			# tmp = pickle.load(open(args['pickle_file'], 'r'))
			tmp = pickle.load(file, encoding='latin1')
			self.__dict__.update(tmp)
			return True
		else:
			return False

	def save(self):
		pickle.dump(self.__dict__, open(self.args['pickle_file'], 'wb'))


def test(args):
	data = Dataset(args)
	json.dump(
		data.meta,
		open(args['meta_json'], 'w'),
		indent=4,
		separators=(',', ': ')
		)
	print (data.meta)

if __name__ == '__main__':
	test(args)