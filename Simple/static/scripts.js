

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
    acc[i].onmouseover = function(){
        this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("show");
    }
    acc[i].onmouseout = function(){
	this.classList.toggle("active");
        this.nextElementSibling.classList.toggle("hide");
    }

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
	converter = new showdown.Converter(),
	html = converter.makeHtml(text);
    target.innerHTML = html;
    }
}


function showSampleD3(radius=50) {
    //Set some variables
    var width = 100,
	height = 100;


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

function showNetworkD3() {


//Make a force diagram object
var force = d3.layout.force()
    .charge(-120)
    .linkDistance(30)
    .size([width, height]);
 

    //Define the color scale to use  - depends on what version of D3 you are using
    var color = d3.scale.category20();
    /* <later version of D3>  var color = d3.scaleOrdinal(d3.schemeCategory10);*/

    /**This is where we are trying to do something!**/

d3.json('/data/network.json', function(error, graph) {
  if (error) throw error;
  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();
  var link = svg.selectAll(".link")
      .data(graph.links)
      .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return Math.sqrt(d.value); });
  var node = svg.selectAll(".node")
      .data(graph.nodes)
      .enter().append("circle")
      .attr("class", "node")
      .attr("r", 5)
      .style("fill", function(d) { return color(d.group); })
      .call(force.drag);
  node.append("title")
      .text(function(d) { return d.name; });
    force.on("tick", function() {
	    link.attr("x1", function(d) { return d.source.x; })
		.attr("y1", function(d) { return d.source.y; })
		.attr("x2", function(d) { return d.target.x; })
		.attr("y2", function(d) { return d.target.y; });
	    node.attr("cx", function(d) { return d.x; })
		.attr("cy", function(d) { return d.y; });
	});
    });

}