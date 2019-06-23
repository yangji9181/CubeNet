import spacy
import sys
from collections import defaultdict
import json

SPECIAL_TOKEN = 'MY_TOKEN'

nlp = spacy.load('en', disable = ['ner'])

def transform(pubtator_filename, output_filename, ent_type_file, pmid_dict_file):
    print(pubtator_filename)
    full_text = ''
    info = []
    out = open(output_filename, 'w')
    doc_cnt = 0
    relationList = defaultdict(list)
    ent_dict = defaultdict(set)
    ent_type = dict()
    pmid_dict = dict()
    for line in open(pubtator_filename):
        '''
        if line.strip() == '':
            if full_text != '':
                doc_cnt += 1
                if doc_cnt % 1000 == 0:
                    print(doc_cnt)

                normalized_text = ''
                last = 0
                replacements = []
                for (start, end, entity_type) in info:
                    normalized_text += full_text[last : start]
                    normalized_text += ' ' + SPECIAL_TOKEN + ' '
                    replacements.append((full_text[start : end], entity_type))
                    last = end
                normalized_text += full_text[last : ]

                doc = nlp(normalized_text)
                ptr = 0
                for sentence in doc.sents:
                    out.write('<s> O None\n')
                    for token in sentence:
                        if token.text.strip() == '':
                            continue
                        if token.text == SPECIAL_TOKEN:
                            assert ptr < len(replacements)
                            surface, entity_type = replacements[ptr]
                            ptr += 1

                            surface_tokens = nlp(surface)
                            is_first = True
                            for surface_token in surface_tokens:
                                if surface_token.text.strip() == '':
                                    continue
                                sep = 'O'
                                if is_first:
                                    sep = 'I'
                                    is_first = False
                                out.write('%s %s %s\n' % (surface_token.text, sep, entity_type))
                        else:
                            out.write('%s I None\n' % token.text)
                    out.write('<eof> I None\n\n')
                assert ptr == len(replacements)

            full_text = ''
            info = []
            continue
        '''
        if line.strip() == '':
            doc_cnt += 1
            if doc_cnt % 1000 == 0:
                print(doc_cnt)
            full_text = ''
            ent_dict = defaultdict(set)
            continue
        
        parts = line.strip().split('\t')
        if len(parts) == 1:
            text = parts[0]
            assert text.find('|') != -1, 'pmid'
            pmid = text[ : text.find('|')]
            text = text[text.find('|') + 1 : ]
            assert text.find('|') != -1, 'text type'
            text_type = text[ : text.find('|')]
            text = text[text.find('|') + 1 : ]
            if text_type == 't':
                pmid_dict[pmid] = text
            full_text += text + '\n'
        elif len(parts) == 6:
            pmid = parts[0]
            start = int(parts[1])
            end = int(parts[2])
            surface = parts[3]
            entity_type = parts[4]
            entity = parts[5]

            assert full_text[start : end] == surface
            # we may consider add surface.lower()
            ent_dict[entity].add(surface)
            ent_type[surface] = entity_type
        elif len(parts) == 4:
            #print(ent_dict)
            for arg1 in ent_dict[parts[2]]:
                for arg2 in ent_dict[parts[3]]:
                    out.write(arg1+'\t'+arg2+'\t'+parts[0]+'\n')
            #out.write()
            #drelationList[(parts[2], parts[3])].append(pmid)
            #info.append((start, end, entity_type))

    json.dump(ent_type, open(ent_type_file, 'w'))
    json.dump(pmid_dict, open(pmid_dict_file, 'w'))
    out.close()


transform(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
