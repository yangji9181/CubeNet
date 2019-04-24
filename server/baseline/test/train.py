from process import READ
from pte import PTE
import numpy as np

class train(object):
    def __init__(self,iterate):
        self.iterate = iterate
    def train(self):
        for it in range(0, self.iterate):
            for ii in pro:
                sample = np.random.choice(pro[ii].shape[0], 20, p=pro[ii])
                k=0
                while k < sample.shape[0]:
                    i = vs[ii][sample[k]]-1

                    j = ve[ii][sample[k]]-1

                    i_set = np.asarray(np.random.choice(graphs.nodesnumber, size=5, p=nnp/sum(nnp)), dtype=np.int32)
                    if i in i_set:
                        i_set = np.delete(i_set, np.where(i_set==i))
                    costww = pte.pretraining_ww(j, i, i_set)
                    k = k + 1
        return pte.get()



if __name__ == "__main__":
    graphs = READ()
    maxnode = graphs.generate_graphs()
    nnp, pro, vs, ve = graphs.gen_edgeprob()
    pte = PTE(40,graphs.nodesnumber,maxnode)
    pte.ww_model()
    tr = train(10)
    tr.train()
