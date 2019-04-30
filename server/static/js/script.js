/* Author: Siyang Liu */

// const nodeMap = {"Phrase": "0", "Author": "1", "Venue": "2", "Year": "3"};
// const labelMap = {"Han" : "1", "Non-Han": "0", "Method" : "1", "Metric": "3", "Application": "2", "2005": "1", "2010": "2", "2000": "0", "2015": "3", "Machine Learning":"1", "Data Mining":"0", "Database": "2", "Information Retrieval": "3"}
// var query = {"merges": {}, "nodes": [], "filters": {}};

// $('.node').change(function() {
//   var node = $(this).parent().text();
//   console.log("node checked " + node);

//   var index = nodeMap[node];
//   if ($(this).is(':checked')) {
//   	if (query["nodes"].indexOf(index) === -1) {
// 		query["nodes"].push(index);
//   	}
//   } else {
//   	var index = query["nodes"].indexOf(index);
//   	if (index !== -1) query["nodes"].splice(index, 1);
//   }
//   console.log(query);
// });

// $('.filter').change(function() {
//   var label = $(this).parent().text();
//   var node = $(this).parent().attr("class");
//   console.log("filter checked " + node + " " + label);


//   var nodeIdx = nodeMap[node];
//   var labelIdx = labelMap[label];
//   console.log(nodeIdx + " " + labelIdx);

//   if ($(this).is(':checked')) {
//   	if (!(nodeIdx in query["filters"])) {
// 		  query["filters"][nodeIdx] = []
//   	}
//     query["filters"][nodeIdx].push(labelIdx);
//   } else {
//   	var index = query["filters"][nodeIdx].indexOf(labelIdx);
//   	if (index !== -1) query["filters"][nodeIdx].splice(index, 1);
//   	if (query["filters"][nodeIdx].length === 0) {
//   		console.log("delete list");
//   		// delete query.filters.nodeIdx;
//       delete query['filters'][nodeIdx];

//   	}
//   }
//   console.log(query);
// });

// $('.merge').change(function() {
//   var label = $(this).parent().text();
//   var node = $(this).parent().attr("class");
//   console.log("merge checked " + node + " " + label);

//   var nodeIdx = nodeMap[node];
//   var labelIdx = labelMap[label];
//   console.log(nodeIdx + " " + labelIdx);

//   if ($(this).is(':checked')) {
//   	if (!(nodeIdx in query["merges"])) {
// 		query["merges"][nodeIdx] = []
//   	}
// 	query["merges"][nodeIdx].push(labelIdx);
//   } else {
//   	var index = query["merges"][nodeIdx].indexOf(labelIdx);
//   	if (index !== -1) query["merges"][nodeIdx].splice(index, 1);
//   	if (query["merges"][nodeIdx].length === 0) {
//   		console.log("delete list");
//   		// delete query.merges.nodeIdx;
//       delete query['merges'][nodeIdx];
//   	}
//   }
//   console.log(query);
// });

// const button = document.getElementById('query_btn');
// $("button").click(function(){
// 	$.ajax({
// 	  type: "POST",
// 	  url: "/query",
// 	  data: JSON.stringify({"query": query}),
// 	  dataType: "json",
// 	  contentType : "application/json"
// 	}).done(function(data)  {
//     console.log("success");
//   	// console.log(data);
// 		updateNetwork(data);
// 	}).fail(function()  {
// 		alert("Sorry. Server unavailable. ");
// 	});
// 	console.log("click:");

// });



// new approach
// to think: for merge, select parent, shouldn't select children (b/c all to be merged)
// contrast: add all labels of a node type if not been filtered 
// probably want to split filters for each type of nodes (looks confusing right now)
// hardcoded labels
const yelp_label_mapping = {
            '0.4':'Restaurants',
            '0.8':'Breakfast & Brunch',
            '0.5':'Italian',
            '0.6':'Asian Fusion',
            '0.7':'American (New)',
            '0.9':'Active Life',
            '0.11':'Mountain Biking',
            '0.10':'Soccer',
            '0.12': 'Bowling',
            '0.13':'Fitness & Instruction',
            '0.14':'Boxing',
              '0.15':'Yoga',
              '0.0':'Shopping',
              '0.2': 'Arts & Crafts',
              '0.1': 'Computers',
              '0.3': 'Cosmatics & Beauty Supply'
          }
const yelp_label_mapping_type = {
  "0": {'0.4':'Restaurants',
            '0.8':'Breakfast & Brunch',
            '0.5':'Italian',
            '0.6':'Asian Fusion',
            '0.7':'American (New)',
            '0.9':'Active Life',
            '0.11':'Mountain Biking',
            '0.10':'Soccer',
            '0.12': 'Bowling',
            '0.13':'Fitness & Instruction',
            '0.14':'Boxing',
              '0.15':'Yoga',
              '0.0':'Shopping',
              '0.2': 'Arts & Crafts',
              '0.1': 'Computers',
              '0.3': 'Cosmatics & Beauty Supply'}
}
const dblp_label_mapping = {
        '0.1':'Method',
        '0.2': 'Metric',
        '0.3':'Application',
        '1.0':'Han',
        '1.1':'Non-Han',
        '2.0':'Data Mining',
        '2.1':'Machine Learning',
        '2.2':'Database',
        '2.3':'Information Retrieval',
        '3.0':'2000',
        '3.1':'2005',
        '3.2':'2010',
        '3.3':'2015'
      }

const dblp_label_mapping_type = {
  "0": {'0.1':'Method',
        '0.2': 'Metric',
        '0.3':'Application',},
  "1": {
    '1.0':'Han',
        '1.1':'Non-Han',
  },
  "2": {
    '2.0':'Data Mining',
        '2.1':'Machine Learning',
        '2.2':'Database',
        '2.3':'Information Retrieval',
  },
  "3":{
    '3.0':'2000',
        '3.1':'2005',
        '3.2':'2010',
        '3.3':'2015'
  }

}


const dblp_node = [ {
          id: '0',
          label: 'Phrase'
        }, {
          id: '1',
          label: 'Author'
        }, {
          id: '2',
          label: 'Venue',
        }, {
          id: '3',
          label: 'Year',
        } ]

const dblp_contrast_labels = [ {
          id: '0',
          label: 'Phrase',
          children: [],
        }, {
          id: '1',
          label: 'Author',
          children: [],
        }, {
          id: '2',
          label: 'Venue',
          children: [],
        }, {
          id: '3',
          label: 'Year',
          children: [],
        } ];

const dblp_label = [ {
          id: '0',
          label: 'Phrase',
          children: [ {
            id: '0.1',
            label: 'Method'
          }, {
            id: '0.2',
            label: 'Metric'
          }, {
            id: '0.3',
            label: 'Application'
          }]
        }, {
          id: '1',
          label: 'Author',
          children: [ {
            id: '1.0',
            label: 'Han'
          }, {
            id: '1.1',
            label: 'Non-Han'
          }]
        }, {
          id: '2',
          label: 'Venue',
          children: [ {
            id: '2.0',
            label: 'Data Mining'
          }, {
            id: '2.1',
            label: 'Machine Learning'
          }, {
            id: '2.2',
            label: 'Database'
          }, {
            id: '2.3',
            label: 'Information Retrieval'
          }]
        }, {
          id: '3',
          label: 'Year',
          children: [ {
            id: '3.0',
            label: '2000'
          }, {
            id: '3.1',
            label: '2005'
          }, {
            id: '3.2',
            label: '2010'
          }, {
            id: '3.3',
            label: '2015'
          }]
        } ]

const yelp_node = [ {
          id: '0',
          label: 'Business'
        }, {
          id: '1',
          label: 'Location'
        }, {
          id: '2',
          label: 'Stars'
        }, {
          id: '3',
          label: 'Phrase'
        } ]

const yelp_bus_labels = [ {
          id: '0.4',
          label: 'Restaurants',
          children: [ {
            id: '0.8',
            label: 'Breakfast & Brunch',
          }, {
            id: '0.5',
            label: 'Italian',
          }, {
            id: '0.6',
            label: 'Asian Fusion',
          }, {
            id: '0.7',
            label: 'American (New)',
          } ],
        }, {
          id: '0.9',
          label: 'Active Life',
          children: [ {
            id: '0.11', // 0.9.11 -> add 9 and 11 to query
            label: 'Mountain Biking',
          }, {
            id: '0.10',
            label: 'Soccer',
          }, {
            id: '0.12',
            label: 'Bowling',
          } , {
            id: '0.13',
            label: 'Fitness & Instruction',
            children: [{
              id: '0.14',
              label: 'Boxing',
            }, {
              id: '0.15',
              label: 'Yoga',
            } ]
          }],
        }, {
          id: '0.0',
          label: 'Shopping',
          children: [ {
            id: '0.2',
            label: 'Arts & Crafts',
          }, {
            id: '0.1',
            label: 'Computers',
          }, {
            id: '0.3',
            label: 'Cosmatics & Beauty Supply',
          } ],
        } ]

const yelp_label = [{
          id: '0',
          label: 'Business',
          children: yelp_bus_labels
        }, {
          id: '1',
          label: 'Location'
        }, {
          id: '2',
          label: 'Stars',
        }, {
          id: '3',
          label: 'Phrase',
        } ]

const yelp_contrast_labels = [ {
          id: '0',
          label: 'Business',
          children: [],
        }, {
          id: '1',
          label: 'Location',
          children: [],
        }, {
          id: '2',
          label: 'Stars',
          children: [],
        }, {
          id: '3',
          label: 'Phrase',
          children: [],
        } ]

const simulateAsyncOperation = fn => {
  setTimeout(fn, 2000)
}
// current global states
var dataset = "dblp"
var query = {"dataset": "dblp", "merges": {}, "nodes": [], "filters": {}};
var contrast = [];
var selected_labels_flat = {}
var id_mapping = dblp_label_mapping;
var id_mapping_type = dblp_label_mapping_type;

// register the component
Vue.component('treeselect', VueTreeselect.Treeselect)
selected_labels_flat = {"0":["0.1", "0.2"]}

var contrast_select = new Vue({
      el: '#contrast',
      data: {
        // define default value
        value: [],
        // define options
        options: [],
      },
      watch: {
        value: function (val) {
          // add labels to contrast array
        }
      },

      methods: {
        updateOptions: function () {
          for (var i = 0; i < this.options.length; i++) {
            var parentNode = this.options[i];
            parentNode.children = [];
            // console.log(parentNode);
            if (parentNode.id in selected_labels_flat) {
              var children = selected_labels_flat[parentNode.id].map(label_id => ({
                                          id: label_id, label: id_mapping[label_id],
                                          }));
              for (var c = 0; c < children.length; c++) {
                this.options[i].children.push(children[c]);
              }
            } else { // should include all labels under the node type
              var curr_id_mapping = id_mapping_type[parentNode.id];
              var children = Object.keys(curr_id_mapping).map(label_id => ({
                                          id: label_id, label: id_mapping[label_id],
                                          }));
              for (var c = 0; c < children.length; c++) {
                this.options[i].children.push(children[c]);
              }
            }
          }
        }
      },
    })

var filter_select = new Vue({
      el: '#filter',
      data: {
        // define default value
        value: [],
        valueConsistsOf: 'ALL',
        // define options
        options: yelp_label,
      },
      watch: {
        value: function (val) {
          query["filters"] = {}
          selected_labels_flat = []
          for (var i = 0; i < val.length; i++) {
            let node_label = val[i].split('.');
            // console.log(node_label);
            if (node_label.length === 1) continue; // node type only

            if (!(node_label[0] in selected_labels_flat)) {
              selected_labels_flat[node_label[0]] = []
            }
            selected_labels_flat[node_label[0]].push(val[i]);
            
            if (!(node_label[0] in query["filters"])) {
              query["filters"][node_label[0]] = []
            }
            query["filters"][node_label[0]].push(node_label[node_label.length-1]);
          }

          contrast_select.updateOptions();
          console.log(query);
        }
      }
    })

var merge_select = new Vue({
      el: '#merge',
      data: {
        // define default value
        value: [],
        // define options
        options: yelp_label,
      },
      watch: {
        value: function (val) {
          query["merges"] = {}
          for (var i = 0; i < val.length; i++) {
            let node_label = val[i].split('.');
            if (node_label.length === 1) continue; // node type only

            if (!(node_label[0] in query["merges"])) {
              query["merges"][node_label[0]] = []
            }
            query["merges"][node_label[0]].push(node_label[1]);
          }
          console.log(query);
        }
      }
    })

var node_select = new Vue({
      el: '#nodes',
      data: {
        // define default value
        value: [],
        // define options
        options: yelp_node,
      },
      watch: {
        value: function (val) {
          query["nodes"] = val;
        }
      }
    })


var clearValues = function () {
  contrast_select.value = [];
  filter_select.value = [];
  merge_select.value = [];
  node_select.value = [];
};

// change dataset
$(".select-dataset").dropdown({
 onChange: function(data) {
    // console.log('change dataset', data)
    clearValues();
    switch (data) {
      case 'dblp':
        console.log('change dataset', 'dblp');
        dataset = "dblp";
        query["dataset"] = "dblp";
        node_select.options = dblp_node;
        filter_select.options = dblp_label;
        merge_select.options = $.extend(true, [], dblp_label);
        for (var i = 0; i < merge_select.options.length; i++) {
          Vue.set(merge_select.options[i], "isDisabled", true);
        }
        id_mapping = dblp_label_mapping;
        id_mapping_type = dblp_label_mapping_type;

        contrast_select.options = dblp_contrast_labels;
        break;
      case 'yelp':
        console.log('change dataset', 'yelp');
        dataset = "yelp";
        query["dataset"] = "yelp";

        node_select.options = yelp_node;
        filter_select.options = yelp_label;
        merge_select.options = $.extend(true, [], yelp_label);
        for (var i = 0; i < merge_select.options.length; i++) {
          Vue.set(merge_select.options[i], "isDisabled", true);
        }
        id_mapping = yelp_label_mapping;
        id_mapping_type = yelp_label_mapping_type;
        contrast_select.options = yelp_contrast_labels;
        break;
      case 'freebase':
        console.log('change dataset', 'freebase');
        dataset = "freebase";
        query["dataset"] = "freebase";

        node_select.options = yelp_node;
        filter_select.options = yelp_label;
        merge_select.options = $.extend(true, [], yelp_label);
        for (var i = 0; i < merge_select.options.length; i++) {
          Vue.set(merge_select.options[i], "isDisabled", true);
        }
        contrast_select.id_mapping = yelp_label_mapping;
        contrast_select.id_mapping_type = yelp_label_mapping_type;
        id_mapping = yelp_label_mapping;
        id_mapping_type = yelp_label_mapping_type;
        contrast_select.options = yelp_contrast_labels;
        break;
      case 'pubmed':
        console.log('change dataset', 'pubmed');
        dataset = "pubmed";
        query["dataset"] = "pubmed";

        node_select.options = yelp_node;
        filter_select.options = yelp_label;
        merge_select.options = $.extend(true, [], yelp_label);
        for (var i = 0; i < merge_select.options.length; i++) {
          Vue.set(merge_select.options[i], "isDisabled", true);
        }
        id_mapping = yelp_label_mapping;
        id_mapping_type = yelp_label_mapping_type;

        contrast_select.options = yelp_contrast_labels;
        break;
    }
 }
});


const query_button = document.getElementById('query_btn');
$("#query_btn").click(function(){
 $.ajax({
   type: "POST",
   url: "/query",
   data: JSON.stringify({"query": query}),
   dataType: "json",
   contentType : "application/json"
 }).done(function(data)  {
    console.log("success");
   // console.log(data);
   updateNetwork(data);
 }).fail(function()  {
   alert("Sorry. Server unavailable. ");
 });
 console.log("click:");

});

const contrast_button = document.getElementById('contrast_btn');
$("#contrast_btn").click(function(){
 $.ajax({
   type: "POST",
   url: "/contrast",
   data: JSON.stringify({"labels": contrast}),
   dataType: "json",
   contentType : "application/json"
 }).done(function(data)  {
    console.log("success");
   // console.log(data);
   updateNetwork(data);
 }).fail(function()  {
   alert("Sorry. Server unavailable. ");
 });
 console.log("click:");

});


