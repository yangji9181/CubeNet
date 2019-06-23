output_file = 'train2.subSentence.group.iterated.output.txt'
with open(output_file,'w') as fout:
  for x in range(0,31):
    start_num = x * 10000 + 1
    file_name = 'train2.subSentence.group.iterated.output'+str(start_num)+'.txt'
    with open(file_name) as f:
      for line in f:
        fout.write(line)