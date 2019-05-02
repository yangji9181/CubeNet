# import argparse
# import getpass
# import sys
#
#
# class Config():
# 	def __init__(self, args):
# 		'''
# 		convert Namespace to Config object
# 		:param args:
# 		'''
# 		var = vars(args)
# 		for k, v in var.items():
# 			setattr(self, k, v)
#
# def parse_args():
# 	parser = argparse.ArgumentParser()
# 	parser.add_argument('--data_dir', type=str, default='../data/', help='Data Directory')
# 	parser.add_argument('--data_name', type=str, default='dblp', help='Dataset name')
# 	parser.add_argument('--data_sub', type=str, default='toy', help='Dataset subset name')
# 	parser.add_argument('--query_file', type=str, default='../intermediate/query.json', help='Query file name')
# 	parser.add_argument('--meta_json', type=str, default='../intermediate/meta.json', help='Meta data json file name')
# 	parser.add_argument('--network_file', type=str, default='../intermediate/network.json', help='Network file name')
# 	return parser.parse_args()
#
# def init(args):
# 	args.meta_file = args.data_dir + args.data_name + '/' + 'meta.dat'
# 	args.node_file = args.data_dir + args.data_name + '/' + args.data_sub + '.node.dat'
# 	args.link_file = args.data_dir + args.data_name + '/' + args.data_sub + '.link.dat'
# 	args.label_file = args.data_dir + args.data_name + '/' + args.data_sub + '.label.dat'
# 	args.pickle_file = args.data_dir + args.data_name + '/' + args.data_sub + '.pickle'

# args = parse_args()
# init(args)

# print (args)
# print (args)
argsDict = {}
argsDict['data_sub'] = 'toy'
argsDict['query_file'] = 'intermediate/query.json'
argsDict['meta_json'] = 'intermediate/meta.json'
argsDict['network_file'] = 'intermediate/network.json'
argsDict['data_dir'] = 'data/'
argsDict['contrast_q'] = 'intermediate/contrast_q.json'
argsDict['contrast_n'] = 'intermediate/contrast_n.json'
def make_dir(data_name):
    argsDict['data_name'] = data_name
    argsDict['meta_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + 'meta.dat'
    argsDict['node_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + argsDict['data_sub'] + '.node.dat'
    argsDict['link_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + argsDict['data_sub'] + '.link.dat'
    argsDict['label_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + argsDict['data_sub'] + '.label.dat'
    argsDict['pickle_file'] = argsDict['data_dir'] + argsDict['data_name'] + '/' + argsDict['data_sub'] + '.pickle'

args = argsDict