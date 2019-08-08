/* Author: Siyang Liu */

// CUBE
const CUBE_WIDTH = 15
const CUBE_GAP = 10
var camera, scene, renderer;
var geometry, material, mesh;
var light1;
var cubes  = []; // meshes
const BASE_COLOR = 0xffffff;
const FILTER_COLOR = 0x2ABFB8;
const MERGE_COLOR = 0xfc7b03; // to delete
const OVERLAP_COLOR = 0xfc7b03;

initScene();
function setCubeColor(i, j, k, color) {
  cubes[i][j][k].material.color.setHex(color);
}

function highlightCubes(indices, color) {
  if (indices.length == 0) {
    return; 
  }

  dim_keys = [];
  for(var j in indices[0]){
      dim_keys.push(j);
  }

  for (var i = 0; i < indices.length; i++) {
    setCubeColor(indices[i][dim_keys[0]], indices[i][dim_keys[1]], indices[i][dim_keys[2]], color);
  }
}

function resetAllCubes() {
  for (var i = 0; i < cubes.length; i++) {
    for (var j = 0; j < cubes[i].length; j++) {
      for (var k = 0; k < cubes[i][j].length; k++) {
        setCubeColor(i,j,k, BASE_COLOR);
      }
    }
  }
}

function initScene() {
  // SCENE
  scene = new THREE.Scene();

  // CAMERA
  camera = new THREE.PerspectiveCamera(70, 2, 1, 1000);
  
  scene.add(camera);
  camera.position.set( - 200,0, - 200);
  camera.lookAt(scene.position); 

  container = document.getElementById( 'canvas' );
  const {left, right, top, bottom, width, height} =
  container.getBoundingClientRect();

  renderer = new THREE.WebGLRenderer();
  renderer.setSize( 600, 600 );
  container.appendChild( renderer.domElement );

  camera.aspect = width / height;
  camera.updateProjectionMatrix();
 
  const positiveYUpBottom = renderer.domElement.clientHeight - bottom;
  renderer.setScissor(left, positiveYUpBottom, width, height);
 
  renderer.render(scene, camera);

  // LIGHTS
  light1 = new THREE.PointLight(BASE_COLOR);
  light1.position.set(0,0,0);
  camera.add(light1);

  // CONTROLS
  controls = new THREE.OrbitControls( camera, renderer.domElement );
  controls.enableZoom = false;
}

function clearScene() {
  while(scene.children.length > 0){ 
    console.log(scene.children[0]);
    scene.remove(scene.children[0]); 
  }
}

function initCube(cube_dim, dim_labels) {
  cubes = [] // initialize

  // cubes size
  half_x = cube_dim[0] * (CUBE_WIDTH + CUBE_GAP) / 2;
  half_y = cube_dim[1] * (CUBE_WIDTH + CUBE_GAP) / 2;
  half_z = cube_dim[2] * (CUBE_WIDTH + CUBE_GAP) / 2;

  camera = new THREE.PerspectiveCamera(70, 2, 1, 1000);
  
  scene.add(camera);
  camera.position.set(-half_x - 200,0,-half_z - 200);
  camera.lookAt(scene.position); 

  container = document.getElementById( 'canvas' );
  const {left, right, top, bottom, width, height} =
  container.getBoundingClientRect();

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  // LIGHTS
  light1 = new THREE.PointLight(BASE_COLOR);
  light1.position.set(0,0,0);
  camera.add(light1);

  // CONTROLS
  controls = new THREE.OrbitControls( camera, renderer.domElement );
  controls.enableZoom = false;


  // CUBES
  geometry = new THREE.CubeGeometry( CUBE_WIDTH, CUBE_WIDTH, CUBE_WIDTH);
  var material = new THREE.MeshNormalMaterial();
  
  for (var i = 0; i < cube_dim[0]; i++) {
    cubes.push([]);
    for (var j = 0; j < cube_dim[1]; j++) {
      cubes[i].push([]);
      for (var k = 0; k < cube_dim[2]; k++) {
        cubeMaterial = new THREE.MeshLambertMaterial( {color: BASE_COLOR} ); 
        mesh = new THREE.Mesh( geometry, cubeMaterial );
        scene.add( mesh );
        mesh.position.set(i * (CUBE_WIDTH + CUBE_GAP) - half_x, j * (CUBE_WIDTH + CUBE_GAP) - half_y, k * (CUBE_WIDTH + CUBE_GAP) - half_z);

        cubes[i][j].push(mesh);
      }
    }
  }

  // axes = buildAxes( 1000 );
  // scene.add(axes);

  for (var i = 0; i < cube_dim[0]; i++) {
    var spritey = makeTextSprite( dim_labels[0][i], 
      { fontsize: 32, borderColor: {r:255, g:0, b:0, a:1.0}, backgroundColor: {r:255, g:100, b:100, a:0.8} } );
    spritey.position.set(i * (CUBE_WIDTH + CUBE_GAP) - half_x,-25 - half_y,0-half_z);
    scene.add( spritey );
  }

  for (var i = 0; i < cube_dim[1]; i++) {
    var spritey = makeTextSprite( dim_labels[1][i], 
      { fontsize: 32, borderColor: {r:255, g:0, b:0, a:1.0}, backgroundColor: {r:255, g:100, b:100, a:0.8} } );
    spritey.position.set(cube_dim[0] * (CUBE_WIDTH + CUBE_GAP) + 25-half_x, i * (CUBE_WIDTH + CUBE_GAP)-half_y,0-half_z);
    scene.add( spritey );
  }

  for (var i = 0; i < cube_dim[2]; i++) {
    var spritey = makeTextSprite( dim_labels[2][i], 
      { fontsize: 32, borderColor: {r:255, g:0, b:0, a:1.0}, backgroundColor: {r:255, g:100, b:100, a:0.8} } );
    spritey.position.set(cube_dim[0] * (CUBE_WIDTH + CUBE_GAP) + 25-half_x, cube_dim[1] * (CUBE_WIDTH + CUBE_GAP) + 25-half_y, i * (CUBE_WIDTH + CUBE_GAP)-half_z);
    scene.add( spritey );
  }
}

function buildAxes( length ) {
    var axes = new THREE.Object3D();

    axes.add( buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( length, 0, 0 ), 0xFF0000, false ) ); // +X
    axes.add( buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( -length, 0, 0 ), 0xFF0000, true) ); // -X
    axes.add( buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, length, 0 ), 0x00FF00, false ) ); // +Y
    axes.add( buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, -length, 0 ), 0x00FF00, true ) ); // -Y
    axes.add( buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, 0, length ), 0x0000FF, false ) ); // +Z
    axes.add( buildAxis( new THREE.Vector3( 0, 0, 0 ), new THREE.Vector3( 0, 0, -length ), 0x0000FF, true ) ); // -Z

    return axes;

}

function buildAxis( src, dst, colorHex, dashed ) {
    var geom = new THREE.Geometry(),
        mat; 

    if(dashed) {
        mat = new THREE.LineDashedMaterial({ linewidth: 3, color: colorHex, dashSize: 3, gapSize: 3 });
    } else {
        mat = new THREE.LineBasicMaterial({ linewidth: 3, color: colorHex });
    }

    geom.vertices.push( src.clone() );
    geom.vertices.push( dst.clone() );
    geom.computeLineDistances(); // This one is SUPER important, otherwise dashed lines will appear as simple plain lines

    var axis = new THREE.Line( geom, mat, THREE.LinePieces );

    return axis;

}

function makeTextSprite( message, parameters )
{
  if ( parameters === undefined ) parameters = {};
  
  var fontface = parameters.hasOwnProperty("fontface") ? 
    parameters["fontface"] : "Arial";
  
  var fontsize = parameters.hasOwnProperty("fontsize") ? 
    parameters["fontsize"] : 18;
  
  var borderThickness = parameters.hasOwnProperty("borderThickness") ? 
    parameters["borderThickness"] : 4;
  
  var borderColor = parameters.hasOwnProperty("borderColor") ?
    parameters["borderColor"] : { r:0, g:0, b:0, a:1.0 };
  
  var backgroundColor = parameters.hasOwnProperty("backgroundColor") ?
    parameters["backgroundColor"] : { r:255, g:255, b:255, a:1.0 };
  //var spriteAlignment = parameters.hasOwnProperty("alignment") ?
  //  parameters["alignment"] : THREE.SpriteAlignment.topLeft;
  var spriteAlignment = THREE.SpriteAlignment.topLeft;
    
  var canvas = document.createElement('canvas');
  var context = canvas.getContext('2d');
  context.font = "Bold " + fontsize + "px " + fontface;
    
  // get size data (height depends only on font size)
  var metrics = context.measureText( message );
  var textWidth = metrics.width;
  
  // background color
  context.fillStyle   = "rgba(" + backgroundColor.r + "," + backgroundColor.g + ","
                  + backgroundColor.b + "," + backgroundColor.a + ")";
  // border color
  context.strokeStyle = "rgba(" + borderColor.r + "," + borderColor.g + ","
                  + borderColor.b + "," + borderColor.a + ")";
  context.lineWidth = borderThickness;
  roundRect(context, borderThickness/2, borderThickness/2, textWidth + borderThickness, fontsize * 1.4 + borderThickness, 6);
  // 1.4 is extra height factor for text below baseline: g,j,p,q.
  
  // text color
  context.fillStyle = "rgba(0, 0, 0, 1.0)";
  context.fillText( message, borderThickness, fontsize + borderThickness);
  
  // canvas contents will be used for a texture
  var texture = new THREE.Texture(canvas) 
  texture.needsUpdate = true;
  var spriteMaterial = new THREE.SpriteMaterial( 
    { map: texture, useScreenCoordinates: false, alignment: spriteAlignment } );
  var sprite = new THREE.Sprite( spriteMaterial );
  sprite.scale.set(100,50,1.0);
  // sprite.center.set(0.5,0.5);

  return sprite;  
}


// function for drawing rounded rectangles
function roundRect(ctx, x, y, w, h, r) 
{
    ctx.beginPath();
    ctx.moveTo(x+r, y);
    ctx.lineTo(x+w-r, y);
    ctx.quadraticCurveTo(x+w, y, x+w, y+r);
    ctx.lineTo(x+w, y+h-r);
    ctx.quadraticCurveTo(x+w, y+h, x+w-r, y+h);
    ctx.lineTo(x+r, y+h);
    ctx.quadraticCurveTo(x, y+h, x, y+h-r);
    ctx.lineTo(x, y+r);
    ctx.quadraticCurveTo(x, y, x+r, y);
    ctx.closePath();
    ctx.fill();
  ctx.stroke();   
}

function animate() {
  requestAnimationFrame( animate );
  renderer.render( scene, camera );
  controls.update();
}


// current global states
// var dataset_info = {nodes: dblp_node, labels: dblp_label};
var node_info = []
var label_info = []
var query_json = {"dataset": "dblp","query": {"dataset": "dblp", "merges": {}, "nodes": [], "filters": {}}};
var contrast_json = {"node": null};
var pattern_json = {"node": null};


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

              // // console.log("in", this.options[i].id);
              // // newOptions[i].isDisabled = false;
              // Vue.set(contrast_select.options[i], "isDisabled", false);
            } else {
              // // console.log("not in", this.options[i].id);
              // // newOptions[i].isDisabled = true;
              // Vue.set(contrast_select.options[i], "isDisabled", true);
            }
          }
          // Vue.set(contrast_select, "options", newOptions);
          // Vue.nextTick();
        }
      }
    });

var pattern_select = new Vue({
      el: '#pattern',
      data: {
        // define default value
        value: null,
        // define options
        options: [],
      },
      watch: {
        value: function (val) {
          console.log("pattern value changes");
          pattern_json.node = val;
        }
      },
      methods: {
        updateOptions: function () {
          // var newOptions = $.extend(true, [], dataset_node);
          var currTypes = node_select.value;
          // console.log("updateOptions", currTypes);
          Vue.set(pattern_select, "value", null);

          for (var i = 0; i < this.options.length; i++) {
            if (currTypes.includes(this.options[i].id)) {
              // Vue.set(pattern_select.options[i], "isDisabled", false);
            } else {
              // Vue.set(pattern_select.options[i], "isDisabled", true);
            }
          }
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
          // contrast_select.updateOptions();
        }
      }
    })

function showCubeColorLabel() {
  document.getElementById("label_filter").style.display = "block";
  document.getElementById("label_filter_merge").style.display = "block";
}



var clearValues = function () {
  node_info = [];
  label_info = [];

  filter_select.options = [];
  merge_select.options = [];
  node_select.options = [];

  contrast_select.value = null;
  pattern_select.value = null;

  filter_select.value = [];
  merge_select.value = [];
  node_select.value = [];
};

// change dataset
init_json = {'dataset': ''}
$(".select-dataset").dropdown({
 onChange: function(data) {
    console.log('change dataset', data)
    clearValues();

    switch (data) {
      case 'dblp':
        // query_json.dataset = "dblp";
        init_json.dataset = "dblp";
        break;
      case 'yelp':
        // query_json.dataset = "yelp";
        init_json.dataset = "yelp";
        break;
      case 'freebase':
        init_json.dataset = "freebase";
        break;
      case 'pubmed':
        init_json.dataset = "pubmed";
        break;
    }
    
    // fetch meta from server
    $.ajax({
       type: "POST",
       url: "/init",
       data: JSON.stringify(init_json),
       dataType: "json",
       contentType : "application/json"
     }).done(function(data)  {
        console.log("success");
        console.log("init respond");
        console.log(data);

        contrast_select.value = null; // reset contrast dropdown
        pattern_select.value = null; // reset pattern dropdown

        clearContrastGraph();
        clearPatternGraph();

        // read meta and set all selection lists
        // meta.node
        for (var node_id in data.meta.node) {
          node_info.push({id: node_id, label: data.meta.node[node_id].name})
          label_info.push({
            id: node_id, 
            label: data.meta.node[node_id].name,
            children: []
          });
        }
        // console.log(node_info);
        for (var node_id in data.meta.label) {
          var parent_node = label_info[parseInt(node_id, 10)];
          for (var child_id in data.meta.label[node_id]) {
            parent_node.children.push({id: node_id + '.' + child_id, label: data.meta.label[node_id][child_id][0]});
          }
        }

        // console.log(label_info);
        node_select.options = node_info;
        contrast_select.options = node_info;
        pattern_select.options = node_info;
        
        filter_select.options = label_info;
        merge_select.options = label_info;
        
        // read meta to initialize the cube
        var cube_dim = []
        var dim_labels = []
        for (var node_id in data.meta.node) {
          if (data.meta.node[node_id].cube) {
            
            var labels = [];
            for (var label_id in data.meta.label[node_id]) {
              labels.push(data.meta.label[node_id][label_id][0]);
            }
            cube_dim.push(labels.length)
            dim_labels.push(labels);

          }
        }
        clearScene();
        showCubeColorLabel();
        initCube(cube_dim, dim_labels);
        animate();

        // set default query
        query_json.dataset = data.query.dataset;
        query_json.query = data.query;

        // set the default checkbox
        for (var node_id in query_json.query.filters) {
          node_labels = filter_select.options[node_id].children;
          for (var child_id in query_json.query.filters[node_id]) {
            filter_select.value.push(node_id + '.' + child_id);
          }
          
        }

        for (var node_id in query_json.query.merges) {
          node_labels = merge_select.options[node_id].children;
          for (var child_id in query_json.query.merges[node_id]) {
            merge_select.value.push(node_id + '.' + child_id);
          }
          
        }
        
        for (var node_id in query_json.query.nodes) {
          node_select.value.push(node_id);   
        }

     }).fail(function()  {
      clearScene();
       alert("Sorry. Server unavailable. ");
     });
     console.log("click init");
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
    contrast_select.value = null; // reset contrast dropdown
    pattern_select.value = null; // reset pattern dropdown

    clearContrastGraph();
    clearPatternGraph();

   console.log("cube");
   console.log(data.cube);
   updateNetwork(data.network);
   resetAllCubes();
   highlightCubes(data.cube.filters, FILTER_COLOR);
   highlightCubes(data.cube.merges, MERGE_COLOR);

 }).fail(function()  {
   alert("Sorry. Server unavailable. ");
 });
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
       clearContrastGraph();
       // document.getElementsByClassName("chart").remove();
       drawHistogram(data);
     }).fail(function()  {
       alert("Sorry. Server unavailable. ");
     });
  }
});

const pattern_button = document.getElementById('pattern_btn');
$("#pattern_btn").click(function(){
  if (!graphConstructed) {
    alert("Please construct graph first.");

  } else if (pattern_json.node == null) {
    alert("Please select node type to do pattern mining.");
  } else {
    $.ajax({
       type: "POST",
       url: "/pattern",
       data: JSON.stringify(pattern_json),
       dataType: "json",
       contentType : "application/json"
     }).done(function(data)  {
      console.log("pattern button clicked success");
      console.log(data);
      clearPatternGraph();
      createPatternDivs(data);
      createPatternSubnetwork(data);
     }).fail(function()  {
       alert("Sorry. Server unavailable. ");
     });
  }
  console.log("click pattern");

});

function createPatternDivs(data) {
  for (var key in data) {
    var div = document.createElement("div");
    div.className = "subnetwork";
    div.id = key;
    document.getElementById("subnetworks").appendChild(div);

    var title = document.createElement("h3");
    title.className = "pattern_title"
    title.innerHTML = key;
    document.getElementById(key).appendChild(title);

    var network_div = document.createElement("div");
    network_div.className = "pattern_network";
    network_div.id = key + "Pattern";
    document.getElementById(key).appendChild(network_div);

  }
}

function clearPatternGraph() {
  [...document.getElementsByClassName("subnetwork")].map(n => n && n.remove());
}

function clearContrastGraph() {
  [...document.getElementsByClassName("chart")].map(n => n && n.remove());
  var title = document.getElementById("histogram_title");
  if (title != null) {
    title.remove();
  }

  var charts = document.getElementById("charts");
  if (charts != null) {
    charts.remove();
  }

  
}

function barChart(div_id, data, node_type){
    // var svg = foo;
    //this reefers to the bars' SVG
    var numBars = data.labels.length;
    // var margin = {top: 40, right: 20, bottom: 30, left: 70};
    var margin = {top: 30, right: 40, bottom: 50, left: 50};

    width = 55 * numBars - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

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
        .attr("height", height + margin.top + margin.bottom + 50)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // svg.call(tip);

    x.domain(data.labels.map(function(d) { return d.name; }));
    y.domain([0, d3.max(data.labels, function(d) { return d.val; })]);


    svg.append("g")
       .attr("class", "x axis")
       .attr("transform", "translate(0," + (height) + ")")
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
    // document.getElementById("main").appendChild(title);

    document.getElementById("main").appendChild(title);

    var charts = document.createElement("div");
    charts.id = "charts";
    document.getElementById("main").appendChild(charts);

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

      // document.getElementById("main").appendChild(chart_div);
      document.getElementById("charts").appendChild(chart_div);

      barChart(chart_div.id, contrast_res.properties[i], contrast_res.node_type);
    }
}


