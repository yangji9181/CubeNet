
from collections import defaultdict

import operator as op
from functools import reduce

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer / denom

# For now, assume that "patterns" is a list [] that contains the patterns to score.
# Each pattern is simply an undirected graph in the form of a dictionary {}
# Example : patterns[0] = {'A':{'B':10, 'C':4}, 'C': {'D':1}}
#
#        A         
#     10/ \  4     
#      /   -       
#     B     C      
#          /1     
#         -       
#        D                 
def choose_best_patterns(patterns, K):

	if not patterns:
		return []

	SIZE_WEIGHT = 0.3
	COHESIVENESS_WEIGHT = 0.4
	STRENGTH_WEIGHT = 0.3

	# For each pattern in patterns, calculate size score, cohesiveness score, and strength score
	ranked_patterns = []
	sizeScores = score_size(patterns)
	cohesivenessScores = score_cohesiveness(patterns)
	strengthScores = score_strength(patterns)

	# Now we have sub metrics for each pattern. Time to score each one.
	for i in range(len(patterns)):

		score = sizeScores[i] * SIZE_WEIGHT + cohesivenessScores[i] * COHESIVENESS_WEIGHT + strengthScores[i] * STRENGTH_WEIGHT

		# Add i to prevent ties in sorting
		ranked_patterns.append([score,i,patterns[i]])

	
	ranked_patterns.sort()
	ranked_patterns.reverse()
	print("All ranked patterns: " , ranked_patterns)

	if (K > len(ranked_patterns)):
		return [ranked_patterns[i][2] for i in range(len(ranked_patterns))]
	else:
		return [ranked_patterns[i][2] for i in range(K)]



def score_size(patterns):
	scores = []
	
	maxSize = 0
	sizes = []
	for pattern in patterns:
		nodes = set()
		for node1 in pattern:
			if node1 not in nodes:
				nodes.add(node1)

			if pattern[node1]:
				for node2 in pattern[node1]:
					if node2 not in nodes:
						nodes.add(node2)

		sizes.append(len(nodes))

	#print(sizes)

	maxSize = max(sizes)
	scores = [(size**2)/(maxSize**2) for size in sizes]

	#print(scores)

	return scores


def score_cohesiveness(patterns):
	import math
	# For each pattern, compute normalized gini index
	giniIndices = []
	for pattern in patterns:

		# First compute total link size and number of nodes in pattern
		patternSize = 0
		nodes = set()
		totalLinkSize = 0
		for node1 in pattern:
			if node1 not in nodes:
				nodes.add(node1)
			if pattern[node1]:
				for node2 in pattern[node1]:
					if node2 not in nodes:
						nodes.add(node2)
					totalLinkSize += pattern[node1][node2]

		# Now, compute gini index for this pattern
		giniIndex = 0.0
		for node1 in pattern:
			if pattern[node1]:
				for node2 in pattern[node1]:
					giniIndex += (pattern[node1][node2] / totalLinkSize)**2
		giniIndex = 1.0 - giniIndex

		# convert gini into value between [0,1]
		patternSize = len(nodes)
		#print(pattern, giniIndex, patternSize)
		if(not patternSize == 2):
			giniIndex = giniIndex / (1.0-1.0/ncr(patternSize,2))
		else:
			giniIndex = 1

		giniIndices.append(giniIndex)

	return giniIndices


def score_strength(patterns):

	patternStrength = []
	for pattern in patterns:
		strength = 0
		numLinks = 0
		for node1 in pattern:
			if pattern[node1]:
				for node2 in pattern[node1]:
					strength += pattern[node1][node2]
					numLinks += 1

		patternStrength.append(strength/numLinks)

	maxPatternStrength = max(patternStrength)

	patternStrengthNormalized = [(p**2)/(maxPatternStrength**2) for p in patternStrength]

	return patternStrengthNormalized





