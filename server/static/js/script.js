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
            label: 'Non-Han'
          }, {
            id: '1.1',
            label: 'Han'
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


// current global states
var dataset_info = {nodes: dblp_node, labels: dblp_label};
var query_json = {"dataset": "dblp","query": {"dataset": "dblp", "merges": {}, "nodes": [], "filters": {}}};
var contrast_json = {"node": null};

// register the component
Vue.component('treeselect', VueTreeselect.Treeselect)

var contrast_select = new Vue({
      el: '#contrast',
      data: {
        // define default value
        value: null,
        // define options
        options: [],
      },
      watch: {
        value: function (val) {
          console.log("contrast value changes");
          contrast_json.node = val;
        }
      },
      methods: {
        updateOptions: function () {

          // var newOptions = $.extend(true, [], dataset_node);
          var currTypes = node_select.value;
          // console.log("updateOptions", currTypes);
          Vue.set(contrast_select, "value", null);

          for (var i = 0; i < this.options.length; i++) {
            // debugger
            // if ($.inArray(this.options[i].id, currTypes)) {
            if (currTypes.includes(this.options[i].id)) {

              // console.log("in", this.options[i].id);
              // newOptions[i].isDisabled = false;
              Vue.set(contrast_select.options[i], "isDisabled", false);
            } else {
              // console.log("not in", this.options[i].id);
              // newOptions[i].isDisabled = true;
              Vue.set(contrast_select.options[i], "isDisabled", true);
            }
          }
          // Vue.set(contrast_select, "options", newOptions);
          // Vue.nextTick();
        }
      }
    });

var filter_select = new Vue({
      el: '#filter',
      data: {
        // define default value
        value: [],
        valueConsistsOf: 'ALL',
        // define options
        options: [],
      },
      watch: {
        value: function (val) {
          console.log("filter value changes");

          query_json.query.filters = {}
          selected_labels_flat = []
          for (var i = 0; i < val.length; i++) {
            let node_label = val[i].split('.');
            // console.log(node_label);
            if (node_label.length === 1) continue; // node type only

            if (!(node_label[0] in query_json.query.filters)) {
              query_json.query.filters[node_label[0]] = []
            }
            query_json.query.filters[node_label[0]].push(node_label[node_label.length-1]);
          }
          console.log(query_json);
        }
      }
    })

var merge_select = new Vue({
      el: '#merge',
      data: {
        // define default value
        value: [],
        // define options
        options: [],
      },
      watch: {
        value: function (val) {
          console.log("merge value changes");
          query_json.query.merges = {}
          for (var i = 0; i < val.length; i++) {
            let node_label = val[i].split('.');
            if (node_label.length === 1) continue; // node type only

            if (!(node_label[0] in query_json.query.merges)) {
              query_json.query.merges[node_label[0]] = []
            }
            query_json.query.merges[node_label[0]].push(node_label[1]);
          }
          console.log(query_json);
        }
      }
    })

var node_select = new Vue({
      el: '#nodes',
      data: {
        // define default value
        value: [],
        // define options
        options: [],
      },
      watch: {
        value: function (val) {
          query_json.query.nodes = val;
          contrast_select.updateOptions();
        }
      }
    })


var clearValues = function () {
  contrast_select.value = null;
  filter_select.value = [];
  merge_select.value = [];
  node_select.value = [];
};

// change dataset
$(".select-dataset").dropdown({
 onChange: function(data) {
    console.log('change dataset', data)
    clearValues();
    switch (data) {
      case 'dblp':
        query_json.dataset = "dblp";
        dataset_info.nodes = dblp_node;
        dataset_info.labels = dblp_label;
        break;
      case 'yelp':
        query_json.dataset = "yelp";
        dataset_info.nodes = yelp_node;
        dataset_info.labels = yelp_label;
        break;
      case 'freebase':
        
        break;
      case 'pubmed':
        
        break;
    }
    node_select.options = dataset_info.nodes;
    contrast_select.options = $.extend(true, [], dataset_info.nodes);
    for (var i = 0; i < contrast_select.options.length; i++) {
      Vue.set(contrast_select.options[i], "isDisabled", true);
    }
    filter_select.options = dataset_info.labels;
    merge_select.options = $.extend(true, [], dataset_info.labels);
    for (var i = 0; i < merge_select.options.length; i++) {
      Vue.set(merge_select.options[i], "isDisabled", true);
    }
 }
});

var graphConstructed = false;
const query_button = document.getElementById('query_btn');
$("#query_btn").click(function(){
  graphConstructed = true;
 $.ajax({
   type: "POST",
   url: "/query",
   data: JSON.stringify(query_json),
   dataType: "json",
   contentType : "application/json"
 }).done(function(data)  {
    console.log("success");
    contrast_select.value = null; // reset contrast dropdown
    clearContrastGraph();
   // console.log(data);
   updateNetwork(data);
 }).fail(function()  {
   alert("Sorry. Server unavailable. ");
 });
 console.log("click query");

});

const contrast_button = document.getElementById('contrast_btn');
$("#contrast_btn").click(function(){
  if (!graphConstructed) {
    alert("Please construct graph first.");

  } else if (contrast_json.node == null) {
    alert("Please select node type to contrast.");
  } else {
    $.ajax({
       type: "POST",
       url: "/contrast",
       data: JSON.stringify(contrast_json),
       dataType: "json",
       contentType : "application/json"
     }).done(function(data)  {
        console.log("success");
       // console.log(data);
       // delete old contrast graphs
       // console.log("to remove", document.getElementsByClassName("chart"));
       // [...document.getElementsByClassName("chart")].map(n => n && n.remove());
       clearContrastGraph();
       // document.getElementsByClassName("chart").remove();
       drawHistogram(data);
     }).fail(function()  {
       alert("Sorry. Server unavailable. ");
     });
  }
  console.log("click contrast");

});

function clearContrastGraph() {
  [...document.getElementsByClassName("chart")].map(n => n && n.remove());
  var title = document.getElementById("histogram_title");
  if (title != null) {
    title.remove();
  }
  
}

function barChart(div_id, data, node_type){
    // var svg = foo;
    //this reefers to the bars' SVG
    var numBars = data.length;
    // var margin = {top: 40, right: 20, bottom: 30, left: 70};
    var margin = {top: 30, right: 40, bottom: 50, left: 50};
    width = 220 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

    // width = d3.max(300, numBars * 15) - margin.left - margin.right,
    // height = d3.max(250, numBars * 15) - margin.top - margin.bottom;

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10, "");

    // var tip = d3.tip()
    //   .attr('class', 'd3-tip')
    //   .offset([-10, 0])
    //   .html(function(d) {
    //     return "<strong>Value:</strong> <span style='color:red'>" + d.val + "</span>";
    //   });

    var svg = d3.select("#" + div_id).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // svg.call(tip);

    x.domain(data.labels.map(function(d) { return d.name; }));
    y.domain([0, d3.max(data.labels, function(d) { return d.val; })]);


    svg.append("g")
       .attr("class", "x axis")
       .attr("transform", "translate(0," + height + ")")
       .call(xAxis)
         .selectAll("text")  
         .style("text-anchor", "end")
         .attr("dx", "-.8em")
         .attr("dy", ".15em")
         .attr("transform", "rotate(-25)");

      // .append("text")
      //   // .attr("transform", "rotate(-90)")
      //   .attr("x", 50)
      //   .attr("dx", ".71em")
      //   .style("text-anchor", "end")
      //   .text(node_type);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -50)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(data.name);

    svg.selectAll(".bar")
        .data(data.labels)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("x", function(d) { return x(d.name); })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d.val); })
        .attr("height", function(d) { return height - y(d.val); })
        // .on('mouseover', tip.show)
        // .on('mouseout', tip.hide);

    // function type(d) {
    //   d.Salary = +d.Salary;
    //   return d;
    // }

};

// function type(d) {
//   d.val = +d.val;
//   return d;
// }

function drawHistogram(contrast_res) {
      // <h3 id="histogram_title" style="text-align: center"> Contrast Analysis</h3>
    var title = document.createElement("h3");
    title.id = "histogram_title";
    title.style.textAlign = "center";
    title.innerHTML = "Contrast Analysis on " + contrast_res.node_type.charAt(0).toUpperCase() + contrast_res.node_type.slice(1);
    document.getElementById("main").appendChild(title);

    for (var i = 0; i < contrast_res.properties.length; i++) {
    // var i = 0;

      var chart_div = document.getElementById("chart" + i);
      console.log(chart_div);
      if (chart_div == null) {
        chart_div = document.createElement("div");
        chart_div.style.display = "inline-block";
      }
      
      chart_div.className = "chart";
      chart_div.id = "chart" + i;

      document.getElementById("main").appendChild(chart_div);
      barChart(chart_div.id, contrast_res.properties[i], contrast_res.node_type);
    }
}

// to test
// draw histogram
var contrast_graph_fake = 
{
  "node_type": "year",
  "properties": [
    {
      "name": "density",
      "labels": [
        {
          "name": "2000",
          "val": 20
        },
        {
          "name": "2005",
          "val": 30
        }
      ]
    },
    {
      "name": "prop2",
      "labels": [
        {
          "name": "2000",
          "val": 1
        },
        {
          "name": "2005",
          "val": 2
        }
      ]
    }
  ]
}

// drawHistogram(contrast_graph_fake);

