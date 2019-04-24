import numpy as np
import json

with open('network.json') as json_file:
    data1 = json.load(json_file)
    links = data1['links']
    data = np.zeros((len(links),4),int)
    for i in range(0, len(data)):
        data[i][0] =int(links[i]['source'])
        data[i][1] =int(links[i]['target'])
        data[i][2] =0
        data[i][3] =int(links[i]['weight'])


class READ():
    def __init__(self):
        self.nodes=[]
        self.result={}
        self.edges = len(data)
        self.nodesnumber = 0
        self.countofnodes=[]
        self.link = []
        self.linktotal=0
    def generate_graphs(self):
        maxnode = 0
        for i in range(0,len(data)):
            if data[i][0] > maxnode:
                maxnode = data[i][0]
            if data[i][1] > maxnode:
                maxnode = data[i][1]
            self.link.append(data[i][2])
            self.nodes.append(int(data[i][0]))
            self.nodes.append(data[i][1])
            if data[i][2] not in self.result:
                self.result[data[i][2]] = {}

            if data[i][0] not in self.result[data[i][2]]:
                self.result[data[i][2]][data[i][0]] ={}
            self.result[data[i][2]][data[i][0]][data[i][1]] = data[i][3]
            #self.listoffre.append(data[i][3])
        self.nodes = list(set(self.nodes))
        self.nodesnumber = len(self.nodes)
        self.linktotal = set(self.link)
        #print(self.linktotal)
        #self.listoffre = np.zeros((self.nodesnumber ))
        self.listoffre = {}
        for i in range(0,len(data)):
            if data[i][0]-1 not in self.listoffre:
                self.listoffre[data[i][0]-1] = 0
            self.listoffre[data[i][0]-1] =self.listoffre[data[i][0]-1]+1

            if data[i][1]-1 not in self.listoffre:
                self.listoffre[data[i][1]-1] = 0
            self.listoffre[data[i][1]-1] =self.listoffre[data[i][1]-1]+1
        #print(self.listoffre.values())
        return maxnode
    def gen_edgeprob(self):
        pro = {}
        vs ={}
        ve={}
        for i in self.linktotal:
            pro[i]=[]
            vs[i]=[]
            ve[i] =[]
        i = 0
        for kk in self.result.keys():
            for k in self.result[kk].keys():
                for kj in self.result[kk][k].keys():
                    pro[kk].append(self.result[kk][k][kj])
                    vs[kk].append(k)
                    ve[kk].append(kj)
            pro[kk] = np.asarray(pro[kk], dtype=np.float64)
            pro[kk] = pro[kk] / float(sum(pro[kk]))
            i = i + 1
        nP=np.asarray(list(self.listoffre.values()), dtype=np.float64)#vertex
        nP = np.power(nP, (3.0/4.0))
        #print(nP)

        return nP, pro,vs,ve
