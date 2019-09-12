## Implementation of *CubeNet*, KDD 2019 Demo.

Please cite the following work if you find the code useful.

```
@inproceedings{yang2019cube2net,
	Author = {Yang, Carl and Teng, Dai and Liu, Siyang and Basu, Sayantani and Zhang, Jieyu and Shen, Jiaming and Zhang, Chao and Shang, Jingbo and Kaplan, Lance and Haratty, Timothy and Han, Jiawei},
	Booktitle = {KDD demo},
	Title = {CubeNet: multi-facet hierarchical heterogeneous network construction, analysis and mining},
	Year = {2019}
}
```
Contact: Carl Yang (yangji9181@gmail.com)

### To run the demo
```shell
git clone https://github.com/yangji9181/CubeNet.git
cd CubeNet/server

# install dependency
sudo pip3 install -r requirements.txt

# run server
export FLASK_APP=server
python3 -m flask run
```
