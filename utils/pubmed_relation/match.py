import json
import copy
import re
from collections import defaultdict
import argparse

ENT_dict = {"GENE", "CHEMICAL", "DISEASE", "SPECIES"}
CHAR = ["A","B","C","D","E","F","G","H","I","J","K","L","M",\
	"N","O","P","Q","R","S","T","U","V","W","X","Y","Z","["]
ITERATED = True

def clear(name):
	for ent in ENT_dict:
		if name.find(ent) != -1:
			name = ent
			return name
	return name

def treeSearch(subdict, current, last, cand_set, matched_set):
	global reverse_index, word_bag
	if last == None:
		# discard if the entity is not a leaf node
		if current+"A" in subdict:
			return []
		#search the parent
		parent = current[:-1]
		matched_set = treeSearch(subdict, parent, current, reverse_index[current], pat_list)

	else:
		#if len(last) == len(current):
			#last and current are siblings, error
		#	print("last %s and current %s can't be siblings!",last, current)

		# do inverse index intersection
		if subdict[current] in reverse_index:
			cand_set = cand_set & set(reverse_index[subdict[current]])
		else:
			return matched_set

		#the intersection is an empty set
		if len(cand_set) == 0:
			return matched_set

		for index in cand_set:
			#check if the candidate pattern is all covered
			#word_bag.remove(subdict[current])
			'''ent_flag = False
			for ent in ENT_dict:
				if subdict[current].find(ent) != -1:
					for word in word_bag[index]:
						if word.find(ent) != -1:
							word_bag[index].remove(word)
					ent_flag = True
					break

			if ent_flag == False:'''
			if subdict[current] in word_bag[index]:
				word_bag[index].remove(subdict[current])

			#if word_bag of this pattern is empty, than the pattern is covered
			if len(word_bag[index]) == 0:
				matched_set.add(index)

		#remove matched patterns from candidate patterns
		cand_set = cand_set - matched_set

		# from parent to child
		if len(last) < len(current):			

			#move on to all children
			for ch in CHAR:
				child = current + ch
				if child in subdict:
					matched_set = treeSearch(subdict, child, current, cand_set, matched_set)
				else:
					break

			return matched_set

		#move from child to parent
		else:
			for ch in CHAR:
				child = current + ch
				if child not in subdict:
					break
				if child in subdict and child != last:
					matched_set = treeSearch(subdict, child, current, cand_set,matched_set)


			parent = current[:-1]
			if parent in subdict:
				matched_set = treeSearch(subdict, parent, current, cand_set, matched_set)

			return matched_set





def match(s):
	global reverse_index, word_bag
	#find the number of entity types in subsentence
	subSentence = s[1].split("\t")[0]
	type_set = set()
	for word in subSentence.split(" "):
		for ent in ENT_dict:
			if word.find(ent) != -1:
				type_set.add(word)
	
	# if there are more or less than one type of entity, don't group
	if len(type_set) != 1:
		return False, "", {}, []

	#get reverse index for entity
	for t in type_set:
		ENT = t
	if ENT not in reverse_index:
		return False, "", {}, []

	entity_index = reverse_index[ENT]
	root = s[0].split("\t")[0]
	if root in reverse_index:
		root_index = reverse_index[root]
	else:
		root_index = set()

	#if the intersection of root_index and entity_index is empty, don't group
	intersect = entity_index & root_index
	if len(intersect) == 0:
		return False, "", {}, []

	# create a subdict, eg.: A -> effect, AA -> of, AAA -> GENE
	subdict = {}
	subsent = s[1].split("\t")[0].split(" ")
	subencode = s[1].split("\t")[1].split(" ")
	for i in range(len(subsent)):
		subdict[subencode[i]] = subsent[i]

	# find the encode of the Entity that we want to group
	ent_encode = []
	longest_encode = 0
	for i in range(len(subsent)):
		word = subsent[i]
		if word.find(ENT) != -1:
			ent_encode.append(subencode[i])
			longest_encode = max(longest_encode, len(subencode[i]))

	merge_matched_set = set()
	merge_ent_encode = list()

	#start from the encode of Entity
	for enc in ent_encode:
		# if the entity is not a leaf node, we skip it
		if len(enc) < longest_encode:
			continue
		# if the entity is not a frequent pattern, we skip it
		if subdict[enc] not in reverse_index:
			continue
		matched_set = set()
		cand_set = set(reverse_index[subdict[enc]])
		word_bag = dict()
		# read pattern list file
		f1 = open("pattern_list.json")
		for line in f1:
			word_bag = json.loads(line)
		f1.close()
		# remove entity from word_bag
		for index in cand_set:
			if subdict[enc] in word_bag[index]:
				word_bag[index].remove(subdict[enc])

		if enc[:-1] in subdict:
			matched_set = treeSearch(subdict, enc[:-1], enc, cand_set, matched_set)
		# do union operation
		merge_matched_set |= matched_set

		if len(matched_set) != 0:
			merge_ent_encode.append(enc)

	if len(merge_matched_set) == 0:
		return False, "", subdict, []
	else:
		return True, merge_ent_encode, subdict, merge_matched_set

def expand(subencode, entity_code, replace_code, sentence):
	subsentence = {}
	new_entity_code = replace_code[entity_code]
	for s in sentence:
		subsentence[s[0].split("\t")[1]] = s[1].split("\t")[1]
	added_sentence = subsentence[entity_code]
	origin_sentence = subencode
	if new_entity_code in origin_sentence.split(" ") or new_entity_code == entity_code:
		origin_sentence = origin_sentence
	elif origin_sentence.find(' '+entity_code+' ') != -1:
		origin_sentence = origin_sentence.replace(' '+entity_code+' ', ' {{'+added_sentence+'}} ')
	elif origin_sentence.find('{{'+entity_code+' ') != -1:
		origin_sentence = origin_sentence.replace('{{'+entity_code+' ', '{{{{'+added_sentence+'}} ')
	elif origin_sentence.find(' '+entity_code+'}}') != -1:
		origin_sentence = origin_sentence.replace(' '+entity_code+'}}', ' {{'+added_sentence+'}}}}')
	elif origin_sentence.find('{{'+entity_code+'}}') != -1:
		origin_sentence = origin_sentence.replace('{{'+entity_code+'}}', '{{{{'+added_sentence+'}}}}')
	elif origin_sentence[-len(entity_code)-1:] == ' '+entity_code :
		origin_sentence = origin_sentence[:-len(entity_code)-1]+' {{'+added_sentence+'}}'
	elif origin_sentence.find(entity_code+' ') == 0:
		origin_sentence = '{{'+added_sentence+'}} '+origin_sentence[len(entity_code)+1:]
	if new_entity_code not in replace_code or new_entity_code == entity_code:
		return new_entity_code, origin_sentence
	else:
		return expand(origin_sentence, new_entity_code, replace_code, sentence)

def encode_to_words(subdict, subencode):
	subencode = subencode.split(" ")
	regex = re.compile('[^a-zA-Z]')
	words = ' '.join([re.sub(regex.sub("",x), lambda x: subdict[x.group()], x) for x in subencode])
	return words



if __name__ == "__main__":

	#read inverse index file
	f1 = open("reverse_index.json")
	for line in f1:
		reverse_index = json.loads(line)
	f1.close()

	for word in reverse_index:
		reverse_index[word] = set(reverse_index[word])

	'''pattern_list = dict()
	#read pattern list file
	f1 = open("pattern_list.json")
	for line in f1:
		pattern_list = json.loads(line)
	f1.close()'''


	#read file of the original frequent patterns
	all_pattern = {}
	f1 = open("patterns.txt")
	for line in f1:
		all_pattern[line.split("\t")[0]] = line.split("\t")[1].strip()
	f1.close()

	#read file of subSentence
	f1 = open("round1.subSentence.txt")
	#read file of subEncode
	f2 = open("round1.subEncode.txt")
    #read file of subID
	f3 = open("round1.subEncode.txt")

	parser = argparse.ArgumentParser(description='main',
									 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--start', default='1')


	args = parser.parse_args()
	start = args.start
	#output file
	outputname = "train2.subSentence.group.iterated.output"+start+".txt"
	fout = open(outputname,"w")
	start_num = int(start)

	while True:
		line1 = f1.readline()
		line2 = f2.readline()
		if not line1:
			break

		# process a sentence
		if line1 == "\n":
			if int(row_num) <= start_num:
				continue
			if int(row_num) > start_num + 99:
				break

			#fout.write(str(row_num)+"\n")

			# range the subsentences from leaves to root
			sentence = sorted(sent.items(), key=lambda x: len(x[0].split("\t")[1]), reverse = True)

			#create original projection from encode to words
			orig_sub_dict = {}
			for s in subsent_complete_order:
				tmp_val = s.split("\t")[0].split(" ")
				tmp_key = s.split("\t")[1].split(" ")
				for x in range(len(tmp_key)):
					orig_sub_dict[tmp_key[x]] = tmp_val[x]
			
			#print matched subsentence
			replace_surf = {}
			replace_code = {}
			for s in sentence:
				#from previous iteration, we get grouped words
				#we than replace the root with these entities
				if len(replace_surf) != 0 and ITERATED:
					subsent = s[1].split("\t")[0].split(" ")
					subencode = s[1].split("\t")[1].split(" ")
					for i in range(len(subsent)):
						for pos in replace_surf:
							if pos == subencode[i]:
								subsent[i] = replace_surf[pos]
					s = (s[0]," ".join(subsent)+"\t"+" ".join(subencode))

				flag, ent_leaf, subdict, matched_set = match(s)
				if flag:
					subsent_result[s[0].split("\t")[1]] = "T\t"+subdict[ent_leaf[0]]+"\t"+s[1].split("\t")[0]+"\n"
					#fout.write("T\t"+subdict[ent_leaf[0]]+"\t"+s[1].split("\t")[0]+"\n")
					# replace the surface name of root with the entity name
					if ITERATED:
						replace_surf[s[0].split("\t")[1]] = subdict[ent_leaf[0]]
						replace_code[s[0].split("\t")[1]] = ent_leaf[0]
				else:
					subsent_result[s[0].split("\t")[1]] = "F\t"+s[0].split("\t")[0]+"\t"+s[1].split("\t")[0]+"\n"
					#fout.write("F\t"+s[0].split("\t")[0]+"\t"+s[1].split("\t")[0]+"\n")

			#create a dictionary of encode_sentence
			encode_sentence = {}
			for s in sentence:
				encode_sentence[s[0].split("\t")[1]] = s[1].split("\t")[1]


			for r in subsent_order:
				#fout.write(subsent_result[r])
				subsent = subsent_result[r].split("\t")[2].strip()
				#first do sequence pattern matching and find the longest matched pattern
				#for each entity type in that pattern, find whether they have replace_code
				#if no, the instance is the entity type itself
				#if yes, find the original encode of that instance, expand the subsentence during this searching
				ent_type_num = 0
				longest_match = 0
				
				matched_pattern = ""
				matched_ent_pos = {}
				for pat in all_pattern:
					ent_pos = defaultdict(list)
					for ent in ENT_dict:
						if pat.find(ent) != -1:
							ent_pos[ent]=[i for i,x in enumerate(pat.split(" ")) if x.find(ent)!=-1 ]
					if len(ent_pos) < ent_type_num:
						continue
					elif len(ent_pos) == ent_type_num and len(pat.split(" ")) <= longest_match:
						continue
					subsent1 = ' '+subsent+' '
					if subsent1.find(' '+pat+' ') != -1:
						longest_match = len(pat.split(" "))
						ent_type_num = len(ent_pos)
						matched_pattern = pat	
						matched_ent_pos = ent_pos		
				if matched_pattern == "":
					continue
				offset = len(subsent1[:subsent1.find(' '+matched_pattern+' ')].split(" ")) - 1
				instances = []
				orig_subencode = encode_sentence[r]
				words = encode_to_words(orig_sub_dict, orig_subencode)
				flag = False
				diff_length = 0
				sorted_matched_pos = []
				for ent_type in matched_ent_pos:
					for entity_offset in matched_ent_pos[ent_type]:
						sorted_matched_pos.append(offset+entity_offset)
				sorted_matched_pos = sorted(sorted_matched_pos)
				for entity_pos in sorted_matched_pos:
					regex = re.compile('[^a-zA-Z]')
					entity_code = regex.sub('',orig_subencode.split(" ")[entity_pos+diff_length])
					if entity_code in replace_code:
						flag=True
						leaf_code, extended_subencode=expand(orig_subencode, entity_code, replace_code, sentence)
						diff_length += len(extended_subencode.split(" ")) - len(orig_subencode.split(" "))
						orig_subencode = extended_subencode
						words = encode_to_words(orig_sub_dict, orig_subencode)
						instances.append(leaf_code)
					else:
						words = encode_to_words(orig_sub_dict, orig_subencode)
						instances.append(entity_code)
				if flag:
					fout.write(str(row_num)+'\t'+matched_pattern+'\t'+str([orig_sub_dict[x] for x in instances])+'\t'+words+'\n')



		# begin reading a sentence
		elif len(line1.split("\t"))==1 :
			sent = dict()
			encode = dict()
			row_num = line1.strip()
			if int(row_num) <= start_num:
				continue
			if int(row_num) > start_num + 99:
				break
			print(str(row_num))
			#if int(row_num) % 100 == 0:
			#	print(str(row_num))
			subsent_order = list()
			subsent_complete_order = list()
			subsent_result = {}

		# each line is a subsentence
		else:
			if int(row_num) <= start_num:
				continue
			if int(row_num) > start_num + 99:
				break
			sent_root = line1.split("\t")[0].strip()
			encode_root = line2.split("\t")[0].strip()

			sent_children = line1.split("\t")[1].strip()
			encode_children = line2.split("\t")[1].strip()
			sent[sent_root + "\t" + encode_root] = sent_children + "\t" + encode_children
			subsent_order.append(encode_root)
			subsent_complete_order.append(sent_children + "\t" + encode_children)

	f1.close()
	f2.close()
	fout.close()



