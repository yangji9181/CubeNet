# AutoNET

=========================
## Server
```
python2 -m SimpleHTTPServer
```
## Index Network
```
python3 src/parse.py ./data/CDR_TrainingSet.PubTator.txt ./data/CDR_parsed.txt ./data/ent_type.json ./data/pmid.json
```
## Expand Network

```
python src/query.py data/CDR_parsed.txt data/mock_network.json ./data/ent_type.json data/mock_network_expanded.json
```

## Explore Network
```
python src/explore.py data/CDR_parsed.txt "headache" ./data/ent_type.json data/mock_network_explored.json
```
