// alti graph
if (configuration.STAT.DISPLAY_CLASSE_ALTITUDE) {
    Morris.Bar({
                element:"altiChart",
                data : dataset,
                xkey: "altitude",
                ykeys : ["value"],
                labels: ['Observation(s)'],
                xLabelAngle: 45,
                hideHover: 'auto',
                resize: true,
                axes: true,
                gridIntegers: true
                /*yLabelFormat: function(y){return y != Math.round(y)?'':y;}*/
    /*            horizontal: true
    */        });

    svgbis=d3.selectAll("svg");

            svgbis.append("g")
            .append("text")
                .attr("y", "90%")
                .attr("x", "100%")
                .attr("dy", ".71em")
                .attr("fill", "#888888")
                .attr("font-size", "10px")
                .style("text-anchor", "end")
                .text("Altitude(m)");
}

// month graph
if (configuration.STAT.DISPLAY_OBS_MENSUELLE) {
    var phenologyChart =  Morris.Bar({
                            element:"phenologyChart",
                            data : months,
                            xkey: "mois",
                            ykeys : ["value"],
                            labels: ['Observation(s)'],
                            xLabelAngle: 60,
                            hideHover: 'auto',
                            resize: true,
                            axes: true,
                        });
    svgContainer = d3.selectAll("svg");
        svgContainer.append("g")
            .append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", '0%')
                .attr('x', '-15%')
                .attr("dy", ".71em")
                .attr("fill", "#888888")
                .attr("font-size", "10px")
                .style("text-anchor", "end")
                .text("Observations");
}


rect = d3.selectAll("rect");

            rect.on("mouseover", function(d) {
             d3.select(this).classed("highlight", true);
             d3.select(this).select("text").style("visibility", "visible");

});

            rect.on("mouseout", function() {
    d3.select(this).classed("highlight", false);

});

svgContainer = d3.selectAll("svg");
    svgContainer.append("g")
        .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", '0%')
            .attr('x', '-15%')
            .attr("dy", ".71em")
            .attr("fill", "#888888")
            .attr("font-size", "10px")
            .style("text-anchor", "end")
            .text("Observations");
