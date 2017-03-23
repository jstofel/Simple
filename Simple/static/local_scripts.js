

/* ACCORDIAN: Toggle between adding and removing the "active" and "show" classes when the user clicks on one of the "Section" buttons. 
 The "active" class is used to add a background color to the current button when its belonging panel is open. 
 The "show" class is used to open the specific accordion panel */

var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
    acc[i].onclick = function(){
        this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("show");
    }
    /*
    acc[i].onmouseover = function(){
        this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("show");
    }
    acc[i].onmouseout = function(){
	this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("hide");
    }
    */

}


/**Try It Editor **/

    function runCode()
{
    var content = document.getElementById('sourceCode').value;
    var iframe = document.getElementById('targetCode');
    iframe = (iframe.contentWindow) ? iframe.contentWindow : (iframe.contentDocument.document) ? iframe.contentDocument.document : iframe.contentDocument;
    iframe.document.open();
    iframe.document.write(content);
    iframe.document.close();
    return false;
}


/**  Use ShowDown to convert markdown to HTML **/
function runConverter() {
    if (typeof targetDiv != "undefined") {

    var text = document.getElementById('sourceTA').value,
	target = document.getElementById('targetDiv'),
	converter = new showdown.Converter({tables:true}),
	html = converter.makeHtml(text);

    target.innerHTML = html;
    }
}


function showSampleD3(radius=50) {
    //Set some variables
    var width = 400,
	height = 500;


    //Define the canvas as an svg in the show_network div
    if (typeof show_network != "undefined") {
    var svg = d3.select("#show_network").append("svg")
	.attr("width", width)
	.attr("height", height);


    //Add a circle to it
    svg.append("circle")
	.style("stroke", "gray")
	.style("fill", "white")
	.attr("r", radius)
	.attr("cx", 50)
	.attr("cy", 50)
	.on("mouseover", function(){d3.select(this).style("fill", "aliceblue");} )
	.on("mouseout",  function(){d3.select(this).style("fill", "pink")    ;} )
    }
}


function showNetworkD3(graph
		       ,ormtgt="#show_network"
		       ,width=$(ormtgt).width()
		       ,height=$(ormtgt).height()
		       ,radius=10
		       ,markerht=10
		       ,markerwth=10) {

    //alert("ht "+height+" wth:"+width)

  if (typeof graph != "undefined") {
      if ((width > 0) && (height == 0)) {
	  var height = width;
      } else if ((width == 0) && (height > 0)) {
	  var height = width;
      } else if ((width == 0) && (height==0))  {
	  var width =  $(ormtgt).width(),
	      height = $(ormtgt).height() ;
      }

      //alert("ht "+height+" wth:"+width)

       //Set node and marker sizes
      //var radius = 10, markerht = 10, markerwth = 10;
       //Set color scale (works only in d3 version 3)
	var color = d3.scale.category20();
       //Make an SVG object and attach it to the named ORM target
	 var svg = d3.select(ormtgt).append("svg")
	     .attr("width", width)
	     .attr("height", height);
       //Make the force diagram
	var force = d3.layout.force()
	    .gravity(.05)
	    .charge(-100)
	    .distance(radius * 10)
	    .size([width, height]);

	force
	    .nodes(graph.nodes)
	    .links(graph.links)
	    .start();


	// build directional arrow for marker end
	 svg.append("svg:defs").selectAll("marker")
	    .data(["end"])      // Different link/path types can be defined here
	    .enter().append("svg:marker")    // This section adds in the arrows
	    .attr("id", function(d) {return d; } )
	    .attr("viewBox", "0 -5 10 10")
	    .attr("refX", markerwth + radius) //Sets arrow to touch outside of node, at least approx
	    .attr("refY", 0)                    //Setting refY to 0 centers arrow tip on line
	    .attr("markerWidth", markerwth)
	    .attr("markerHeight", markerht)
	    .attr("orient", "auto")
	    .append("svg:path")
	    .attr("d", "M0,-5L10,0L0,5");

	  //Create links as shape line, with width as square-root of the weight value, and marker end defined
	   var link = svg.selectAll(".link")
	     .data(graph.links)
	     .enter().append("line")
	     .attr("class", "link")
	     .style("marker-end",  "url(#end)")
	       .style("stroke-width", function(d) { return Math.sqrt(d.value); }) ;

	   //Create the nodes : use the g ("group") object as a placeholder - this will be a group of circle and text
	     var node = svg.selectAll(".node")
	       .data(graph.nodes)
	       .enter().append("g")
	       .attr("class", "node")
	       .call(force.drag);

	    //Append to the node a circle object with specified radius and color by group
	       node.append("circle")
		    .attr("r", radius)
		    .style("fill", function (d) { return color(d.group); })

	    //Append to the node a text object, with relative x and y locations (dx dy) relative to the node center x and y.
	    // Note that the relative directions are to the right for x, and down for y
	    // Also note that the y text aligns the bottom of the text. So, if you want to align the center of the text height
	    // with the center of the node circle, you will want to push it down by, say, 0.25rem (see note below)
		  node.append("text")
			  .attr("dx", 15)
			  .attr("dy", 0 ) /*use "0.25rem" to vertical align the text with the circle center **/
			  .text(function(d) { return d.name })
			  .style("stroke", "black");


	     //Give the coordinates for the node and line objects
	     // the force layout generates the coordinates used to update the attributes of the SVG elements
		  force.on("tick", function () {
			  link.attr("x1", function (d) {        return d.source.x; })
			      .attr("y1", function (d) {        return d.source.y; })
			      .attr("x2", function (d) {        return d.target.x; })
			      .attr("y2", function (d) {        return d.target.y; });

		  d3.selectAll("circle")
			      .attr("cx", function (d) {        return d.x; })
			      .attr("cy", function (d) {        return d.y; });

		  d3.selectAll("text")
			      .attr("x", function (d) {         return d.x; })
			      .attr("y", function (d) {         return d.y; });
		      });


   } //end of if graph is not undefined
}

