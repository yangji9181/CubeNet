from theano import tensor as T
import theano
import numpy as np

class PTE(object):

    def __init__(self,out_dim,nodes,maxnode,lr=0.05):


        eps = np.sqrt(1.0 / float(out_dim))

        self.link = np.asarray(np.random.uniform(low=-eps, high=eps, size=(maxnode, out_dim)),
                       dtype=theano.config.floatX)
        self.W = theano.shared(self.link, name='W', borrow=True)

        self.lr = lr

    def ww_model(self):

        indm = T.iscalar()
        indc = T.iscalar()
        indr = T.ivector()
        Uj = self.W[indm, :]
        Ui = self.W[indc, :]
        Ui_Set = self.W[indr, :]
        cost_ww = T.log(T.nnet.sigmoid(T.dot(Ui, Uj)))
        cost_ww -= T.log(T.sum(T.nnet.sigmoid(T.sum(Uj * Ui_Set, axis=1))))

        cost = -cost_ww
        grad_ww = T.grad(cost, [Uj, Ui, Ui_Set])
        deltaW = T.inc_subtensor(self.W[indm, :], - (self.lr) * grad_ww[0])
        deltaW = T.inc_subtensor(deltaW[indc, :], - (self.lr) * grad_ww[1])
        deltaW = T.inc_subtensor(deltaW[indr, :], - (self.lr) * grad_ww[2])
        updateD = [(self.W, deltaW)]
        self.train_ww = theano.function(inputs=[indm, indc, indr], outputs=cost, updates=updateD)

    def pretraining_ww(self, indm, indc, indr):
        return self.train_ww(indm, indc, indr)


    def save_model(self):

        W = self.W.get_value()
        np.save('lookupW', W)
    def get(self):
        return self.W.get_value()
