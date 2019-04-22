import torch
import torch.nn as nn
from torch.autograd import Variable

import random

"""
Set of modules for aggregating embeddings of neighbors.
"""

class MeanAggregator(nn.Module):
    """
    Aggregates a node's embeddings using mean of neighbors' embeddings
    """
    def __init__(self, features, cuda=False, gcn=False, second_cut=False): 
        """
        Initializes the aggregator for a specific graph.

        features -- function mapping LongTensor of node ids to FloatTensor of feature values.
        cuda -- whether to use GPU
        gcn --- whether to perform concatenation GraphSAGE-style, or add self-loops GCN-style
        """

        super(MeanAggregator, self).__init__()

        self.features = features
        self.cuda = cuda
        self.gcn = gcn
        self.second_cut = second_cut
        
    def forward(self, nodes, multi_to_neighs, num_sample=10):
        """
        nodes --- list of nodes in a batch
        multi_to_neighs --- list of list of sets, each [list of sets] is  related to one relation, each set
                            is the set of neighbors of corresponding relation for node in batch
        to_neighs --- list of sets, each set is the set of neighbors for node in batch
        num_sample --- number of neighbors to sample. No sampling if None.
        """
        # Local pointers to functions (speed hack)
        _set = set
        if not num_sample is None:
            _sample = random.sample
            multi_samp_neighs = [[_set(_sample(to_neigh, 
                            num_sample,
                            )) if len(to_neigh) >= num_sample else to_neigh for to_neigh in to_neighs]
                            for to_neighs in multi_to_neighs]
        else:
            multi_samp_neighs = to_neighs

        # print(multi_samp_neighs)

        if self.gcn:
            samp_neighs = [samp_neigh + set([nodes[i]]) for i, samp_neigh in enumerate(samp_neighs)]
        multi_unique_nodes_list = [set.union(*samp_neighs) for samp_neighs in multi_samp_neighs]
        unique_nodes_list = list(set.union(*multi_unique_nodes_list))
        unique_nodes = {n:i for i,n in enumerate(unique_nodes_list)}
        mask = Variable(torch.zeros(len(multi_to_neighs), len(nodes), len(unique_nodes))) # no matter what relationship between them
        column_indices = [unique_nodes[n] for samp_neighs in multi_samp_neighs for samp_neigh in samp_neighs for n in samp_neigh]   
        row_indices = [i for r,samp_neighs in enumerate(multi_samp_neighs) for i in range(len(samp_neighs)) for j in range(len(samp_neighs[i]))]
        rel_indices = [r for r,samp_neighs in enumerate(multi_samp_neighs) for i in range(len(samp_neighs)) for j in range(len(samp_neighs[i]))]
        mask[rel_indices, row_indices, column_indices] = 1
        mask = mask.reshape((-1, len(unique_nodes))) # for stack adjcent matrixs for different relations
        if self.cuda:
            mask = mask.cuda()
        # todo: normalize
        num_neigh = mask.sum(1, keepdim=True)
        thre_zeros = Variable(torch.zeros_like(mask))
        # num_neigh = mask.sum()/(mask.shape[0])
        # mask = mask.div(num_neigh)
        mask = torch.where(num_neigh != 0, mask.div(num_neigh), thre_zeros)
        if self.cuda:
            embed_matrix = self.features(torch.LongTensor(unique_nodes_list).cuda())
        else:
            embed_matrix = self.features(torch.LongTensor(unique_nodes_list))

        print(mask.shape, embed_matrix.shape)
        if self.second_cut:
            num_rels = len(multi_samp_neighs)
            num_multi_cur_nodes, num_next_nodes = mask.shape
            mask = mask.reshape((num_rels, num_multi_cur_nodes/num_rels, num_next_nodes))
            num_multi_next_nodes, num_emb_dim = embed_matrix.shape
            embed_matrix = embed_matrix.reshape((num_rels, num_multi_next_nodes/num_rels, num_emb_dim))

            to_feats = Variable(torch.zeros(num_rels, num_multi_cur_nodes/num_rels, num_emb_dim))
            for i in range(num_rels):
                # print(i, "mask[i]", mask[i], "embed_matrix[i]", embed_matrix[i])
                to_feats[i] = mask[i].mm(embed_matrix[i])
            import numpy as np
            print(np.where(np.isnan(to_feats.detach().numpy())==False))
            to_feats = to_feats.reshape((num_multi_cur_nodes, num_emb_dim))
        else:
            to_feats = mask.mm(embed_matrix)
        return to_feats
