/* Author: Siyang Liu */

// "1": "author",
//         "0": "phrase",
//         "3": "year",
//         "2": "venue"

// const nodeMap = {"phraseBox": "0", "authorBox": "1", "venueBox": "2", "yearBox": "3"};
const nodeMap = {"Phrase": "0", "Author": "1", "Venue": "2", "Year": "3"};
const labelMap = {"Han" : "1", "Non-Han": "0", "Method" : "1", "Metric": "3", "Application": "2", "2005": "1", "2010": "2", "2000": "0", "2015": "3", "Machine Learning":"1", "Data Mining":"0", "Database": "2", "Information Retrieval": "3"}
// var query = {"merges": {"2": ["0", "1"]}, "nodes": ["0", "1", "2", "3"], "filters": {"1": ["1"], "0": ["3"]}}
var query = {"merges": {}, "nodes": [], "filters": {}};

$('.node').change(function() {
  var node = $(this).parent().text();
  console.log("node checked " + node);

  var index = nodeMap[node];
  if ($(this).is(':checked')) {
  	if (query["nodes"].indexOf(index) === -1) {
		query["nodes"].push(index);
  	}
  } else {
  	var index = query["nodes"].indexOf(index);
  	if (index !== -1) query["nodes"].splice(index, 1);
  }
  console.log(query);
});

$('.filter').change(function() {
  var label = $(this).parent().text();
  var node = $(this).parent().attr("class");
  console.log("filter checked " + node + " " + label);


  var nodeIdx = nodeMap[node];
  var labelIdx = labelMap[label];
  console.log(nodeIdx + " " + labelIdx);

  if ($(this).is(':checked')) {
  	if (!(nodeIdx in query["filters"])) {
		query["filters"][nodeIdx] = []
  	}
	query["filters"][nodeIdx].push(labelIdx);
  } else {
  	var index = query["filters"][nodeIdx].indexOf(labelIdx);
  	if (index !== -1) query["filters"][nodeIdx].splice(index, 1);
  	if (query["filters"][nodeIdx].length === 0) {
  		console.log("delete list");
  		delete query.filters.nodeIdx;
  	}
  }
  console.log(query);
});

$('.merge').change(function() {
  var label = $(this).parent().text();
  var node = $(this).parent().attr("class");
  console.log("merge checked " + node + " " + label);

  var nodeIdx = nodeMap[node];
  var labelIdx = labelMap[label];
  console.log(nodeIdx + " " + labelIdx);

  if ($(this).is(':checked')) {
  	if (!(nodeIdx in query["merges"])) {
		query["merges"][nodeIdx] = []
  	}
	query["merges"][nodeIdx].push(labelIdx);
  } else {
  	var index = query["merges"][nodeIdx].indexOf(labelIdx);
  	if (index !== -1) query["merges"][nodeIdx].splice(index, 1);
  	if (query["merges"][nodeIdx].length === 0) {
  		console.log("delete list");
  		delete query.merges.nodeIdx;
  	}
  }
  console.log(query);
});

const button = document.getElementById('query_btn');
$("button").click(function(){
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






