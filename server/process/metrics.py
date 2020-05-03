import math
from collections import defaultdict

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
def choose_best_patterns(patterns):
	K = 3

	SIZE_WEIGHT = 0.6
	COHESIVENESS_WEIGHT = 0.3
	LOYALTY_WEIGHT = 0.1

	# For each pattern in patterns, calculate size score, cohesiveness score, and loyalty score
	ranked_patterns = []
	sizeScores = score_size(patterns)
	cohesivenessScores = score_cohesiveness(patterns)
	loyaltyScores = score_loyalty(patterns)

	# Now we have sub metrics for each pattern. Time to score each one.
	for i in range(len(patterns)):
		score = sizeScores[i] * SIZE_WEIGHT + cohesivenessScores[i] * COHESIVENESS_WEIGHT + loyaltyScores[i] * LOYALTY_WEIGHT
		ranked_patterns.append([score,patterns[i]])

	ranked_patterns.sort()
	ranked_patterns.reverse()

	return ranked_patterns[0:K]



def score_size(patterns):
	scores = []
	
	maxSize = 0
	sizes = []
	for pattern in patterns:
		nodes = set()
		for node1 in pattern:
			if node1 not in nodes:
				nodes.append(node1)

			if pattern[node1]:
				for node2 in pattern[node1]:
					if node2 not in nodes:
						nodes.append(node2)

		sizes.append(len(nodes))

	print(sizes)

	maxSize = max(sizes)
	scores = [(size**2)/(maxSize**2) for size in sizes]

	print(scores)

	return scores


def score_cohesiveness(patterns):

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
		giniIndex = giniIndex / (1.0-1.0/math.comb(patternSize,2))

		giniIndices.append(giniIndex)

	return giniIndices


def score_loyalty(patterns):

	loyaltyScores = []

	# Map nodes to their total link strength across all patterns
	totalLinkStrengths = defaultdict(int)
	for pattern in patterns:
		for node1 in pattern:
			if pattern[node1]:
				for node2 in pattern[node1]:
					totalLinkStrengths[node1] += pattern[node1][node2]
					totalLinkStrengths[node2] += pattern[node1][node2]


	# Now, to compute loyalty of each pattern, we compute the loyalty of each node and take the average
	for pattern in patterns:
		localLinkStrengths = defaultdict(int)
		nodesInThisPattern = set()
		for node1 in pattern:
			if node1 not in nodesInThisPattern:
				nodesInThisPattern.add(node1)
			if pattern[node1]:
				for node2 in pattern[node1]:
					if node2 not in nodesInThisPattern:
						nodesInThisPattern.add(node2)
					localLinkStrengths[node1] += pattern[node1][node2]
					localLinkStrengths[node2] += pattern[node1][node2]

		averageLoyalty = 0
		for node in nodesInThisPattern:
			averageLoyalty += localLinkStrengths[node] / totalLinkStrengths[node]
		averageLoyalty /= len(nodesInThisPattern)

		loyaltyScores.append(averageLoyalty)

	return loyaltyScores





