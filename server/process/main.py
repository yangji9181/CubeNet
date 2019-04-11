# from config import *
from dataset import Dataset
from analysis import analysis


if __name__ == '__main__':
	data = Dataset(Args)
	analysis(data)
