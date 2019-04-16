link.dat and node.dat is processed graph, label.dat is label of nodes, all separated by '\t'

###
in node.data:
node_name   node_type   node_embed(separated by ',')

in link.data:
node_id   node_id   link_type   link_count

in label.data:
node_id   node_name    node_type   node_label

###
node_type mapping: 
0:'business'
1:'location'
2:'stars'
3:'phrase'

link_type mapping:
0:business->location
1:location->business
2:business->phrase
3:phrase->business
4:business->stars
5:stars->business
6:phrase<->phrase

label mapping:
see meta.dat
