
# $ ?= require 'jquery' # For Node.js compatibility
root = exports ? this

Network = () ->
  # variables we want to access
  # in multiple places of Network
  width = 960
  height = 800
  # allData will store the unfiltered data
  allData = []
  curLinksData = []
  curNodesData = []
  linkedByIndex = {}
  # these will hold the svg groups for
  # accessing the nodes and links display
  nodesG = null
  linksG = null
  # these will point to the circles and lines
  # of the nodes and links
  node = null
  link = null
  # variables to refect the current settings
  # of the visualization
  layout = "force"
  filter = "all"

  # our force directed layout
  force = d3.layout.force()
  # color function used to color nodes
  nodeColors = d3.scale.category20()
  # tooltip used to display details
  tooltip = Tooltip("vis-tooltip", 230)

  # max weight of links, for link width calculation
  maxLinkWeight = 0.0
  # Starting point for network visualization
  # Initializes visualization and starts force layout
  network = (selection, data) ->
    # format our data
    allData = setupData(data)

    # create our svg and groups
    vis = d3.select(selection).append("svg")
      .attr("width", width)
      .attr("height", height)
    linksG = vis.append("g").attr("id", "links")
    nodesG = vis.append("g").attr("id", "nodes")

    # setup the size of the force environment
    force.size([width, height])

    setLayout("force")
    # setFilter("all")

    # perform rendering and start force layout
    update()

  # The update() function performs the bulk of the
  # work to setup our visualization based on the
  # current layout/sort/filter.
  #
  # update() is called everytime a parameter changes
  # and the network needs to be reset.
  update = () ->
    # filter data to show based on current filter settings.
    curNodesData = allData.nodes
    curLinksData = allData.links

    # reset nodes in force layout
    force.nodes(curNodesData)
    # enter / exit for nodes
    updateNodes()

    # always show links in force layout
    if layout == "force"
      force.links(curLinksData)
      updateLinks()

    # start me up!
    force.start()

  network.updateData = (newData) ->
    allData = setupData(newData)
    link.remove()
    node.remove()
    update()

  # called once to clean up raw data and switch links to
  # point to node instances
  # Returns modified data
  setupData = (data) ->
    console.log("setupData()")
    # initialize circle radius scale
    countExtent = d3.extent(data.nodes, (d) -> d.size)
    circleRadius = d3.scale.sqrt().range([3, 12]).domain(countExtent)

    data.nodes.forEach (n) ->
      # set initial x/y to values within the width/height
      # of the visualization
      n.x = randomnumber=Math.floor(Math.random()*width)
      n.y = randomnumber=Math.floor(Math.random()*height)
      # add radius to the node so we can use it later
      n.radius = circleRadius(n.size)

    # id's -> node objects
    nodesMap  = mapNodes(data.nodes)

    # switch links to point to node objects instead of id's
    data.links.forEach (l) ->
      l.source = nodesMap.get(l.source)
      l.target = nodesMap.get(l.target)

      # linkedByIndex is used for link sorting
      linkedByIndex["#{l.source.id},#{l.target.id}"] = 1

    # uodate the max weight of links
    weights = data.links.map (l) -> l.weight
    maxLinkWeight = weights.reduce (a,b) -> Math.max a, b
    console.log("max link weight" + maxLinkWeight)
    data

  # Helper function to map node id's to node objects.
  # Returns d3.map of ids -> nodes
  mapNodes = (nodes) ->
    nodesMap = d3.map()
    nodes.forEach (n) ->
      nodesMap.set(n.id, n)
    nodesMap

  # Given two nodes a and b, returns true if
  # there is a link between them.
  # Uses linkedByIndex initialized in setupData
  neighboring = (a, b) ->
    linkedByIndex[a.id + "," + b.id] or
      linkedByIndex[b.id + "," + a.id]

  # enter/exit display for nodes
  updateNodes = () ->
    console.log("updateNodes()")
    node = nodesG.selectAll("circle.node")
      .data(curNodesData, (d) -> d.id)

    node.enter().append("circle")
      .attr("class", "node")
      .attr("cx", (d) -> d.x)
      .attr("cy", (d) -> d.y)
      .attr("r", (d) -> d.radius)
      .style("fill", (d) -> nodeColors(d.type))
      .style("stroke", (d) -> strokeFor(d))
      .style("stroke-width", 1.0)

    node.on("mouseover", showDetails)
      .on("mouseout", hideDetails)

    node.exit().remove()

  # enter/exit display for links
  updateLinks = () ->
    console.log("updateLinks()")
    link = linksG.selectAll("line.link")
      .data(curLinksData, (d) -> "#{d.source.id}_#{d.target.id}")
    link.enter().append("line")
      .attr("class", "link")
      .attr("stroke", "#ddd")
      .attr("stroke-opacity", 0.8)
      .attr("x1", (d) -> d.source.x)
      .attr("y1", (d) -> d.source.y)
      .attr("x2", (d) -> d.target.x)
      .attr("y2", (d) -> d.target.y)
      .style("stroke-width", (d) -> d.weight / maxLinkWeight * 10.0)

    link.exit().remove()

  # switches force to new layout parameters
  setLayout = (newLayout) ->
    layout = newLayout
    if layout == "force"
      force.on("tick", forceTick)
        .charge(-200)
        .linkDistance(50)
    else if layout == "radial"
      force.on("tick", radialTick)
        .charge(charge)


  # tick function for force directed layout
  forceTick = (e) ->
    node
      .attr("cx", (d) -> d.x)
      .attr("cy", (d) -> d.y)

    link
      .attr("x1", (d) -> d.source.x)
      .attr("y1", (d) -> d.source.y)
      .attr("x2", (d) -> d.target.x)
      .attr("y2", (d) -> d.target.y)

  # Helper function that returns stroke color for
  # particular node.
  strokeFor = (d) ->
    d3.rgb(nodeColors(d.type)).darker().toString()

  # Mouseover tooltip function
  showDetails = (d,i) ->
    # for map data
    content = '<p class="main">' + d.name + '</span></p>'
    content += '<hr class="tooltip-hr">'
    content += '<p class="main">' + d.type + '</span></p>'

    tooltip.showTooltip(content,d3.event)

    # higlight connected links
    if link
      link.attr("stroke", (l) ->
        if l.source == d or l.target == d then "#555" else "#ddd"
      )
        .attr("stroke-opacity", (l) ->
          if l.source == d or l.target == d then 1.0 else 0.5
        )
          # .style("stroke-width", (l) -> 
          #   if l.source == d or l.target == d then (l) -> l.weight / maxLinkWeight * 3.0  else (l) -> l.weight / maxLinkWeight * 5.0
          # )

    # highlight neighboring nodes
    # watch out - don't mess with node if search is currently matching
    node.style("stroke", (n) ->
      if (n.searched or neighboring(d, n)) then "#555" else strokeFor(n))
      .style("stroke-width", (n) ->
        if (n.searched or neighboring(d, n)) then 2.0 else 1.0)
  
    # highlight the node being moused over
    d3.select(this).style("stroke","black")
      .style("stroke-width", 2.0)

  # Mouseout function
  hideDetails = (d,i) ->
    tooltip.hideTooltip()
    # watch out - don't mess with node if search is currently matching
    node.style("stroke", (n) -> if !n.searched then strokeFor(n) else "#555")
      .style("stroke-width", (n) -> if !n.searched then 1.0 else 2.0)
    if link
      link.attr("stroke", "#ddd")
        .attr("stroke-opacity", 0.8)
        # .style("stroke-width", (l) -> l.weight / maxLinkWeight * 3.0 )

  # Final act of Network() function is to return the inner 'network()' function.
  return network

$ ->
  myNetwork = Network()

  $("#network_select").on "change", (e) ->
    networkFile = $(this).val()
    d3.json "data/#{networkFile}", (json) ->
      myNetwork.updateData(json)

  #d3.json "data/new_network1.json", (json) ->
  #  myNetwork("#vis", json)
  d3.json "data/test_data.json", (json) ->
     myNetwork("#vis", json)
  console.log("hello")


  # create and send query
  $("#query_btn").on "click", (e) ->
    query = {"merges": {"2": ["0", "1"]}, "nodes": ["0", "1", "2", "3"], "filters": {"1": ["1"], "0": ["3"]}} 

    $.post '/query',
      query: query
      (data) -> 
        console.log("query success: ")
        console.log(data)
        networkFile = data.network_file
        d3.json "data/#{networkFile}", (json) ->
          myNetwork.updateData(json)

  # # test
  # $("#query_btn").on "click", (e) ->
  #   query = {}
  #   $.get '/sample_response.json',
  #     query: query
  #     (data) -> 
  #       console.log("query success: ")
  #       console.log(data)

  #       networkFile = data.network_file
  #       d3.json "data/#{networkFile}", (json) ->
  #         myNetwork.updateData(json)

