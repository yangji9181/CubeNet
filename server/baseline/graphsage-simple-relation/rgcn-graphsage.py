import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from collections import defaultdict
import random
import sklearn.metrics

def negative_sampling(triplets, num_nodes):
#     print(len(triplets))
    labels = np.ones((len(triplets)*(10+1),1))
    labels[len(triplets):] = 0
    # random.shuffle(labels)
    # triplets = np.array(triplets)
    neg_num = 10 * len(triplets)
    neg_triplets = np.tile(triplets, (10, 1))
    neg_nodes = np.random.randint(num_nodes, size=neg_num)
    neg_choice = np.random.uniform(size=neg_num)
    neg_sub_idx, neg_obj_idx = neg_choice>0.5, neg_choice<=0.5
    neg_triplets[neg_sub_idx,0] = neg_nodes[neg_sub_idx] 
    neg_triplets[neg_obj_idx,2] = neg_nodes[neg_obj_idx]
    return np.concatenate((triplets, neg_triplets),axis=0), labels




class Encoder(nn.Module):
    def __init__(self, features, num_feats, h_dim, num_rel, adj_lists):
        super(Encoder, self).__init__()
        self.aggregator_1 = Aggregator(adj_lists)
#         self.feat_dim = features.shape[1]
        self.features = features
        self.weight_1 = nn.Parameter(
            torch.FloatTensor(num_rel, num_feats, h_dim))
        nn.init.xavier_uniform_(self.weight_1)
        
        self.aggregator_2 = Aggregator(adj_lists, second_cut=True)
        self.weight_2 = nn.Parameter(
            torch.FloatTensor(num_rel, h_dim, h_dim))
        nn.init.xavier_uniform_(self.weight_2)
        
    def encode(self, nodes):
        return F.relu(torch.bmm(self.aggregator_1.forward(nodes, self.features)
                               , self.weight_1))
        
    def forward(self, nodes):
#         aggre_feat = self.aggregator_1.forward(nodes, self.features)
#         print(aggre_feat.type(),aggre_feat)
#         x = F.relu(torch.mm(self.aggregator_1.forward(nodes, self.features)
#                             , self.weight_1))
        x = self.aggregator_2.forward(nodes, self.encode)
        x = F.relu(torch.bmm(x, self.weight_2))
#         print('encode x.shape', x.shape)
        x = x.sum(0)
#         print('encode sum 0 x.shape', x.shape)
        return x 


class RGCN_GraphSAGE(nn.Module):
    def __init__(self, features, num_feats, h_dim, num_rel, adj_lists):
        super(RGCN_GraphSAGE, self).__init__()
        self.encoder = Encoder(features, num_feats, h_dim, num_rel, adj_lists)
        self.weight_relation = nn.Parameter(
            torch.FloatTensor(num_rel, h_dim))
        nn.init.xavier_uniform_(self.weight_relation)
        
    def forward(self, triplets):
#         print(triplets[:,0])
        sub = self.encoder.forward(triplets[:,0])
        obj = self.encoder.forward(triplets[:,2])
        rel = self.weight_relation[triplets[:,1]]
#         print('sub obj rel shape', sub.shape, obj.shape, rel.shape)
        return torch.sum(sub*obj*rel, dim=1, keepdim=True)
    
    def loss(self, triplets, labels):
        score = self.forward(triplets)
#         print('score.type {}, labels.type {}'.format(score.dtype, labels.dtype))
#         print('score.shape {}, labels.shape {}'.format(score.shape, labels.shape))
        return F.binary_cross_entropy_with_logits(score, labels)



class Aggregator(nn.Module):
    def __init__(self, adj_lists, second_cut=False):
        super(Aggregator, self).__init__()
#         self.features = features
        self.second_cut = second_cut
        self.adj_lists = adj_lists
        
    def forward(self, nodes, features, num_sample=10):
        """
        nodes --- list of nodes in a batch
        to_neighs --- list of sets, each set is the set of neighbors for node in batch
        num_sample --- number of neighbors to sample. No sampling if None.
        """
        # Local pointers to functions (speed hack)
        self.features=features
        multi_to_neighs = [[single_adj_lists[int(node)] for node in nodes]\
                     for single_adj_lists in self.adj_lists]
        _set = set
        if not num_sample is None:
            _sample = random.sample
            multi_samp_neighs = [[_set(_sample(to_neigh, 
                            num_sample,
                            )) if len(to_neigh) >= num_sample else to_neigh for to_neigh in to_neighs]
                            for to_neighs in multi_to_neighs]
#         else:
#             multi_samp_neighs = to_neighs

        # print(multi_samp_neighs)

#         if self.gcn:
#             samp_neighs = [samp_neigh + set([nodes[i]]) for i, samp_neigh in enumerate(samp_neighs)]
        multi_unique_nodes_list = [set.union(*samp_neighs) for samp_neighs in multi_samp_neighs]
        unique_nodes_list = list(set.union(*multi_unique_nodes_list))
        unique_nodes = {n:i for i,n in enumerate(unique_nodes_list)}
        mask = torch.zeros(len(multi_to_neighs), len(nodes), len(unique_nodes)) # no matter what relationship between them
        column_indices = [unique_nodes[n] for samp_neighs in multi_samp_neighs for samp_neigh in samp_neighs for n in samp_neigh]   
        row_indices = [i for r,samp_neighs in enumerate(multi_samp_neighs) for i in range(len(samp_neighs)) for j in range(len(samp_neighs[i]))]
        rel_indices = [r for r,samp_neighs in enumerate(multi_samp_neighs) for i in range(len(samp_neighs)) for j in range(len(samp_neighs[i]))]
        mask[rel_indices, row_indices, column_indices] = 1
        # no stack
#         mask = mask.reshape((-1, len(unique_nodes))) # for stack adjcent matrixs for different relations
#         if self.cuda:
#             mask = mask.cuda()
        # todo: normalize
        # no stack
        num_neigh = mask.sum(2, keepdim=True)
        thre_zeros = torch.zeros_like(mask)
        # num_neigh = mask.sum()/(mask.shape[0])
        # mask = mask.div(num_neigh)
        mask = torch.where(num_neigh != 0, mask.div(num_neigh), thre_zeros)
#         if self.cuda:
#             embed_matrix = self.features(torch.LongTensor(unique_nodes_list).cuda())
#         else:
#         print('self.features type', type(self.features))
        embed_matrix = self.features(torch.LongTensor(unique_nodes_list))

        # print(mask.shape, embed_matrix.shape)
        if self.second_cut:
#             num_rels = len(multi_samp_neighs)
#             num_rels, num_multi_cur_nodes, num_next_nodes = mask.shape
#             print('mask reshape,', num_rels, num_multi_cur_nodes//num_rels, num_next_nodes)
            # no stack
#             mask = mask.reshape((num_rels, num_multi_cur_nodes//num_rels, num_next_nodes))
#             num_multi_next_nodes, num_emb_dim = embed_matrix.shape
#             embed_matrix = embed_matrix.reshape((num_rels, num_multi_next_nodes//num_rels, num_emb_dim))
            to_feats = torch.bmm(mask, embed_matrix)
#             to_feats = torch.zeros(num_rels, num_multi_cur_nodes//num_rels, num_emb_dim)
#             for i in range(num_rels):
                # print(i, "mask[i]", mask[i], "embed_matrix[i]", embed_matrix[i])
#                 to_feats[i] = mask[i].mm(embed_matrix[i])
            # print('second cut : to_feats shape', to_feats.shape)
#             import numpy as np
#             print(np.where(np.isnan(to_feats.detach().numpy())==False))
#             to_feats = to_feats.sum(0)
#             to_feats = to_feats.reshape((num_multi_cur_nodes, num_emb_dim))
        else:
            # broadcast
            # print('first cut: mask shape and embed_matrix shape', mask.shape, embed_matrix.shape)
            to_feats = torch.matmul(mask, embed_matrix)
            # print('first cut: to_feats shape', to_feats.shape)
        return to_feats


def load_dblp():
    num_nodes = 23260-1
    num_feats = 300
    num_rels = 10
    feat_data = np.zeros((num_nodes, num_feats))
#     labels = np.empty((num_nodes,1), dtype=np.int64)
    node_map = {}
    label_map = {}

    # feature
    with open("dblp/sub.node.dat") as fp:
        for i,line in enumerate(fp):
            info = line.strip().split()
            feat_data[i,:] = list(map(float, info[-1].split(',')))
#             labels[i] = float(info[-2])
            name = ' '.join(info[:-2])
            node_map[name] = i
            # print(labels[i])
            # if not info[-1] in label_map:
                # label_map[info[-1]] = len(label_map)
            # labels[i] = label_map[info[-1]]

    # adjcent matrixs for each relation
    adj_lists = [defaultdict(set) for i in range(num_rels)]
    triplets = []
#     labels = []
    with open("dblp/sub.link.dat") as fp:
        for i,line in enumerate(fp):
            info = map(int, line.strip().split())
            sub, obj, rel, _ = info
            triplets.append([sub, rel, obj])
#             labels.append(1)
            adj_lists[rel][sub].add(obj)
            

    # for debug puepose, print the dims
    # print(feat_data.shape, labels.shape)
    # for i in range(num_rels):
    #     print(i, len(adj_lists[i]))
    #     if i != 1:
    #         continue
    #     for key in adj_lists[i]:
    #         print(key, len(adj_lists[i][key]))

    return feat_data, adj_lists, np.array(triplets)


if __name__ == '__main__':
    num_nodes = 23259
    num_feats = 300
    num_labels = 4
    feat_data, ori_adj_lists, pos_triplets = load_dblp()
    features = nn.Embedding(num_nodes, num_feats)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), 
        requires_grad=False)

    triplets, labels = negative_sampling(pos_triplets, num_nodes)

    random_idx = np.random.permutation(len(triplets))
    train_idx = random_idx[:len(triplets)//10*8]
    test_idx = random_idx[len(triplets)//10*8:]

    import copy
    adj_lists = copy.deepcopy(ori_adj_lists)
    for i in test_idx:
        if labels[i]==1:
            sub, rel, obj = triplets[i]
            adj_lists[rel][sub].remove(obj)


    rgcn_graphsage = RGCN_GraphSAGE(features, num_feats, 128, 10, adj_lists)
    optimizer = torch.optim.Adam(rgcn_graphsage.parameters(), lr=0.08)
    for i in range(80):
        bacth_train_idx = np.array(train_idx[:256])
        random.shuffle(train_idx) ###pay attention!!!!
        
        batch_triplets = triplets[bacth_train_idx]
        batch_labels = torch.FloatTensor(labels[bacth_train_idx])
        
        optimizer.zero_grad()
        loss = rgcn_graphsage.loss(batch_triplets, batch_labels)
        loss.backward()
        if i == 50:
            optimizer.lr = 0.001
        # if i == 60:
        #     optimizer.lr = 0.008
        optimizer.step()
        print(i, loss)


    for i in range(50):
        batch_test_output = rgcn_graphsage.forward(triplets[test_idx[i*256:(i+1)*256]])
        bacth_test_labels = labels[test_idx[i*256:(i+1)*256]]

        random.shuffle(test_idx)
        if i == 0:
            test_output = batch_test_output
            test_labels = bacth_test_labels
        else:
            test_output = torch.cat((test_output, batch_test_output))
            test_labels = np.concatenate((test_labels, bacth_test_labels))
    test_output[test_output>0.5]=1
    test_output[test_output<=0.5]=0
    print("Test Accuracy:", sklearn.metrics.accuracy_score(test_labels
                                                              , test_output.detach().numpy()))