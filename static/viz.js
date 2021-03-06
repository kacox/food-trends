// reference: https://bl.ocks.org/alokkshukla/3d6be4be0ef9f6977ec6718b2916d168
function makeBubbleChart(data) {
  // console.log("AJAX SUCCESS");
  var diameter = 600;
  var color = d3.scaleOrdinal(d3.schemeCategory20c);

  var bubble = d3.pack(data)
      .size([diameter, diameter])
      .padding(1.5);

  var svg = d3.select("#bubble-chart")
      .append("svg")
      .attr("width", diameter)
      .attr("height", diameter)
      .attr("class", "bubble");

  var nodes = d3.hierarchy(data)
      .sum(function(d) { return d.Count; });

  var node = svg.selectAll(".node")
      .data(bubble(nodes).descendants())
      .enter()
      .filter(function(d){
          return  !d.children
      })
      .append("g")
      .attr("class", "node")
      .attr("transform", function(d) {
          return "translate(" + d.x + "," + d.y + ")";
      });

  node.append("title")
      .text(function(d) {
          return d.Name + ": " + d.Count;
      });

  node.append("circle")
      .attr("r", function(d) {
          return d.r;
      })
      .style("fill", function(d,i) {
          return color(i);
      });

  node.append("text")
      .attr("dy", ".3em")
      .style("text-anchor", "middle")
      .text(function(d) {
          return d.data.Name.substring(0, d.r / 3);
      })
      .attr("font-family", "sans-serif")
      .attr("font-size", function(d){
          return d.r/4;
      })
      .attr("fill", "black");

  d3.select(self.frameElement)
      .style("height", diameter + "px");
}


// main
d3.json('/data.json', makeBubbleChart)