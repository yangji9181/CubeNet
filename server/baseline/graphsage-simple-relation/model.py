import torch
import torch.nn as nn
from torch.nn import init
from torch.autograd import Variable

import numpy as np
import time
import random
from sklearn.metrics import f1_score, accuracy_score
from collections import defaultdict

from graphsage.encoders import Encoder
from graphsage.aggregators import MeanAggregator

"""
Simple supervised GraphSAGE model as well as examples running the model
on the Cora and Pubmed datasets.
"""

class SupervisedGraphSage(nn.Module):

    def __init__(self, num_classes, enc):
        super(SupervisedGraphSage, self).__init__()
        self.enc = enc
        self.xent = nn.CrossEntropyLoss()

        self.weight = nn.Parameter(torch.FloatTensor(num_classes, enc.embed_dim))
        init.xavier_uniform(self.weight)

    def forward(self, nodes):
        embeds = self.enc(nodes)
        scores = self.weight.mm(embeds)
        return scores.t()

    def loss(self, nodes, labels):
        multi_scores = self.forward(nodes)
        h, w = multi_scores.shape
        print("scores.shape", multi_scores.shape)
        num_rels = 10
        scores = multi_scores.reshape(num_rels, h/num_rels, w).sum(0)
        # scores = Variable(torch.zeros(h/num_rels, w), requires_grad=True)
        # for i in range(num_rels):
        #     scores += multi_scores[i]
        
        # scores_sum = torch.sum(scores)
        # scores = scores.div(scores_sum)
        print(scores.shape, scores)
        return self.xent(scores, labels.squeeze())

def load_dblp():
    num_nodes = 23260-1
    num_feats = 300
    num_rels = 10
    feat_data = np.zeros((num_nodes, num_feats))
    labels = np.empty((num_nodes,1), dtype=np.int64)
    node_map = {}
    label_map = {}

    # feature
    with open("dblp/sub.node.dat") as fp:
        for i,line in enumerate(fp):
            info = line.strip().split()
            feat_data[i,:] = map(float, info[-1].split(','))
            labels[i] = float(info[-2])
            name = ' '.join(info[:-2])
            node_map[name] = i
            # print(labels[i])
            # if not info[-1] in label_map:
                # label_map[info[-1]] = len(label_map)
            # labels[i] = label_map[info[-1]]

    # adjcent matrixs for each relation
    adj_lists = [defaultdict(set) for i in range(num_rels)]
    with open("dblp/sub.link.dat") as fp:
        for i,line in enumerate(fp):
            info = map(int, line.strip().split())
            sub, obj, rel, _ = info
            adj_lists[rel][sub].add(obj)

    # for debug puepose, print the dims
    # print(feat_data.shape, labels.shape)
    # for i in range(num_rels):
    #     print(i, len(adj_lists[i]))
    #     if i != 1:
    #         continue
    #     for key in adj_lists[i]:
    #         print(key, len(adj_lists[i][key]))

    return feat_data, labels, adj_lists


def run_dblp():
    np.random.seed(1)
    random.seed(1)
    num_nodes = 23259
    num_feats = 300
    num_labels = 4
    feat_data, labels, adj_lists = load_dblp()
    features = nn.Embedding(num_nodes, num_feats)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), requires_grad=False)
   # features.cuda()

    agg1 = MeanAggregator(features, cuda=True)
    enc1 = Encoder(features, num_feats, 128, adj_lists, agg1, gcn=True, cuda=False)
    agg2 = MeanAggregator(lambda nodes : enc1(nodes).t(), cuda=False, second_cut=True) # pay attention to second_cut
    enc2 = Encoder(lambda nodes : enc1(nodes).t(), enc1.embed_dim, 128, adj_lists, agg2,
            base_model=enc1, gcn=True, cuda=False)
    enc1.num_samples = 5
    enc2.num_samples = 5

    graphsage = SupervisedGraphSage(num_labels, enc2)
#    graphsage.cuda()
    rand_indices = np.random.permutation(num_nodes)
    test = rand_indices[:num_nodes//10*3]
    # val = rand_indices[num_nodes//10*3:num_nodes//10*4]
    train = list(rand_indices[num_nodes//10*3:])

    optimizer = torch.optim.SGD(filter(lambda p : p.requires_grad, graphsage.parameters()), lr=0.1)
    times = []
    for batch in range(5):
        batch_nodes = train[:256]
        random.shuffle(train)
        start_time = time.time()
        optimizer.zero_grad()
        loss = graphsage.loss(batch_nodes, 
                Variable(torch.LongTensor(labels[np.array(batch_nodes)])))
        loss.backward()
        optimizer.step()
        end_time = time.time()
        times.append(end_time-start_time)
        print(batch, loss.data) # pytorch >=0.5

    val_output = graphsage.forward(test) # change to test
    h, w = val_output.shape
    # print("scores.shape", multi_scores.shape)
    num_rels = 10
    val_output = val_output.reshape(num_rels, h/num_rels, w).sum(0)

    np.savetxt("test_label.txt", labels[test])
    np.savetxt("test_predict.txt", val_output.data.numpy().argmax(axis=1))
    print("check: ", labels[test], val_output.data.numpy(), val_output.data.numpy().argmax(axis=1))
    print("Test Accuracy:", accuracy_score(labels[test], val_output.data.numpy().argmax(axis=1)))
    print("Test F1:", f1_score(labels[test], val_output.data.numpy().argmax(axis=1), average="micro"))
    print("Average batch time:", np.mean(times))


def run_cora():
    np.random.seed(1)
    random.seed(1)
    num_nodes = 2708
    feat_data, labels, adj_lists = load_dblp()
    features = nn.Embedding(2708, 1433)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), requires_grad=False)
   # features.cuda()

    agg1 = MeanAggregator(features, cuda=True)
    enc1 = Encoder(features, 1433, 128, adj_lists, agg1, gcn=True, cuda=False)
    agg2 = MeanAggregator(lambda nodes : enc1(nodes).t(), cuda=False)
    enc2 = Encoder(lambda nodes : enc1(nodes).t(), enc1.embed_dim, 128, adj_lists, agg2,
            base_model=enc1, gcn=True, cuda=False)
    enc1.num_samples = 5
    enc2.num_samples = 5

    graphsage = SupervisedGraphSage(7, enc2)
#    graphsage.cuda()
    rand_indices = np.random.permutation(num_nodes)
    test = rand_indices[:1000]
    val = rand_indices[1000:1500]
    train = list(rand_indices[1500:])

    optimizer = torch.optim.SGD(filter(lambda p : p.requires_grad, graphsage.parameters()), lr=0.7)
    times = []
    for batch in range(100):
        batch_nodes = train[:256]
        random.shuffle(train)
        start_time = time.time()
        optimizer.zero_grad()
        loss = graphsage.loss(batch_nodes, 
                Variable(torch.LongTensor(labels[np.array(batch_nodes)])))
        loss.backward()
        optimizer.step()
        end_time = time.time()
        times.append(end_time-start_time)
        print(batch, loss.data) # pytorch >=0.5

    val_output = graphsage.forward(val) 
    print("Validation F1:", f1_score(labels[val], val_output.data.numpy().argmax(axis=1), average="micro"))
    print("Average batch time:", np.mean(times))

def load_pubmed():
    #hardcoded for simplicity...
    num_nodes = 19717
    num_feats = 500
    feat_data = np.zeros((num_nodes, num_feats))
    labels = np.empty((num_nodes, 1), dtype=np.int64)
    node_map = {}
    with open("pubmed-data/Pubmed-Diabetes.NODE.paper.tab") as fp:
        fp.readline()
        feat_map = {entry.split(":")[1]:i-1 for i,entry in enumerate(fp.readline().split("\t"))}
        for i, line in enumerate(fp):
            info = line.split("\t")
            node_map[info[0]] = i
            labels[i] = int(info[1].split("=")[1])-1
            for word_info in info[2:-1]:
                word_info = word_info.split("=")
                feat_data[i][feat_map[word_info[0]]] = float(word_info[1])
    adj_lists = defaultdict(set)
    with open("pubmed-data/Pubmed-Diabetes.DIRECTED.cites.tab") as fp:
        fp.readline()
        fp.readline()
        for line in fp:
            info = line.strip().split("\t")
            paper1 = node_map[info[1].split(":")[1]]
            paper2 = node_map[info[-1].split(":")[1]]
            adj_lists[paper1].add(paper2)
            adj_lists[paper2].add(paper1)
    return feat_data, labels, adj_lists

def run_pubmed():
    np.random.seed(1)
    random.seed(1)
    num_nodes = 19717
    feat_data, labels, adj_lists = load_pubmed()
    features = nn.Embedding(19717, 500)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), requires_grad=False)
   # features.cuda()

    agg1 = MeanAggregator(features, cuda=True)
    enc1 = Encoder(features, 500, 128, adj_lists, agg1, gcn=True, cuda=False)
    agg2 = MeanAggregator(lambda nodes : enc1(nodes).t(), cuda=False)
    enc2 = Encoder(lambda nodes : enc1(nodes).t(), enc1.embed_dim, 128, adj_lists, agg2,
            base_model=enc1, gcn=True, cuda=False)
    enc1.num_samples = 10
    enc2.num_samples = 25

    graphsage = SupervisedGraphSage(3, enc2)
#    graphsage.cuda()
    rand_indices = np.random.permutation(num_nodes)
    test = rand_indices[:1000]
    val = rand_indices[1000:1500]
    train = list(rand_indices[1500:])

    optimizer = torch.optim.SGD(filter(lambda p : p.requires_grad, graphsage.parameters()), lr=0.7)
    times = []
    for batch in range(200):
        batch_nodes = train[:1024]
        random.shuffle(train)
        start_time = time.time()
        optimizer.zero_grad()
        loss = graphsage.loss(batch_nodes, 
                Variable(torch.LongTensor(labels[np.array(batch_nodes)])))
        loss.backward()
        optimizer.step()
        end_time = time.time()
        times.append(end_time-start_time)
        print(batch, loss.data[0])

    val_output = graphsage.forward(val)
    print("Validation F1:", f1_score(labels[val], val_output.data.numpy().argmax(axis=1), average="micro"))
    print("Average batch time:", np.mean(times))


def test_agg():
    np.random.seed(1)
    random.seed(1)
    num_nodes = 23259
    num_feats = 300
    num_labels = 4
    feat_data, labels, adj_lists = load_dblp()
    features = nn.Embedding(num_nodes, num_feats)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), requires_grad=False)

    agg1 = MeanAggregator(features, cuda=False)
    batch_nodes = [0,1,2,3,4]
    multi_neighs = []
    print(len(adj_lists))

    for i in range(len(adj_lists)):
        multi_neighs.append([adj_lists[i][node] for node in batch_nodes])
    multi_neighs2 = [[adj_lists[i][node] for node in batch_nodes] for i in range(len(adj_lists))]
    print(multi_neighs == multi_neighs2)

    to_feats = agg1.forward(batch_nodes, [[adj_lists[i][node] for node in batch_nodes] for i in range(len(adj_lists))],3)
    print(to_feats.shape, to_feats)


def test_enc():
    np.random.seed(1)
    random.seed(1)
    num_nodes = 23259
    num_feats = 300
    num_labels = 4
    feat_data, labels, adj_lists = load_dblp()

    features = nn.Embedding(num_nodes, num_feats)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), requires_grad=False)
    
    batch_nodes = [0,1,2,3,4]
    agg1 = MeanAggregator(features, cuda=False)
    enc1 = Encoder(features, num_feats, 128, adj_lists, agg1, gcn=True, cuda=False)

    combined = enc1(batch_nodes)
    print(combined.shape, combined)


def test_double():
    np.random.seed(1)
    random.seed(1)
    num_nodes = 23259
    num_feats = 300
    num_labels = 4
    feat_data, labels, adj_lists = load_dblp()

    features = nn.Embedding(num_nodes, num_feats)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), requires_grad=False)
    
    batch_nodes = [0,1,2,3,4]
    agg1 = MeanAggregator(features, cuda=False)
    enc1 = Encoder(features, num_feats, 128, adj_lists, agg1, gcn=True, cuda=False)
    agg2 = MeanAggregator(lambda nodes : enc1(nodes).t(), cuda=False, second_cut=True)
    enc2 = Encoder(lambda nodes : enc1(nodes).t(), enc1.embed_dim, 128, adj_lists, agg2,
            base_model=enc1, gcn=True, cuda=False)

    embeds = enc2(batch_nodes)
    print(embeds.shape, embeds, np.where(np.isnan(embeds.detach().numpy())==False))



if __name__ == "__main__":
    # run_cora()
    # load_dblp()
    # test_agg()
    # test_enc()
    run_dblp()
    



