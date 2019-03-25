/* Author: Siyang Liu */

const button = document.getElementById('query_btn');

$("button").click(function(){
	query = {"query" : {"merges": {"2": ["0", "1"]}, "nodes": ["0", "1", "2", "3"], "filters": {"1": ["1"], "0": ["3"]}}} 
	var request = $.ajax({
	  type: "POST",
	  url: "/query",
	  data: JSON.stringify(query),
	  done: function(data){console.log("success:" + data)},
	  fail: function(data){console.log("error:" + data)},
	  always: function(data){console.log("complete")},
	  dataType: "json",
	  contentType : "application/json"
	});
});






