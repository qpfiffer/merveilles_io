function lerp(a, b, f) {
    return a + f * (b - a);
}

function createNodes(sigInst) {
    for (var key in data) {
        var x = Math.round(Math.random() * 15.5);
        var y = Math.round(Math.random() * 15.0);
        if (data[key]["is_person"] == true) {
            var lerpval = data[key]["data"].length/top_submitter;
            sigInst.addNode(key, {
                x: x,
                y: y,
                size: lerp(1.0, 10.0, lerpval),
                color: "rgb(" + Math.round(Math.random()*256) + "," + Math.round(Math.random()*256) + ", 255)",
                label: key
            });
        } else {
            var lerpval_links = data[key]["linked_to_count"]/highest_linked_item;
            sigInst.addNode(key, {
                x: x,
                y: y,
                size: lerp(1.0, 10.5, lerpval_links),
                //color: "rgb(" + Math.round(x*256) + "," + Math.round(y*256) + ", 255)",
                color: "rgb(255, 25, 155)",
                label: key
            });
        }
    }
}

function createEdges(sigInst) {
    for (var key in data) {
        // data[key]["data"] is a list of links to data[key]
        for (var link in data[key]["data"]) {
            if (data[key]["is_person"] == true) {
                sigInst.addEdge(key + "_" + data[key]["data"][link] + "_" + link, key, data[key]["data"][link]);
            }
        }
    }
    var greyColor = '#666';
}

function init() {
    setTimeout(function() {
        $("#container").masonry({
            itemSelector: ".item",
            isAnimated: true
        });
    }, 250);

    var sigRoot = document.getElementById('sigma_graph');
    var sigInst = sigma.init(sigRoot);

    sigInst.drawingProperties({
      defaultLabelColor: '#ccc',
      font: 'Arial',
      edgeColor: 'source',
      defaultEdgeType: 'curve'
    }).graphProperties({
      minNodeSize: 2,
      maxNodeSize: 5
    });

    createNodes(sigInst);
    createEdges(sigInst);

    sigInst.startForceAtlas2();
    setTimeout(function() {
        sigInst.stopForceAtlas2();
        sigInst.bind('overnodes',function(event){
            var nodes = event.content;
            var neighbors = {};
            sigInst.iterEdges(function(e){
                if(nodes.indexOf(e.source)<0 && nodes.indexOf(e.target)<0){
                    if(!e.attr['grey']){
                        e.attr['true_color'] = e.color;
                        e.color = greyColor;
                        e.attr['grey'] = 1;
                    }
                } else {
                    e.color = e.attr['grey'] ? e.attr['true_color'] : e.color;
                    e.attr['grey'] = 0;

                    neighbors[e.source] = 1;
                    neighbors[e.target] = 1;
                }
            }).iterNodes(function(n){
                if(!neighbors[n.id]){
                    if(!n.attr['grey']){
                        n.attr['true_color'] = n.color;
                        n.color = greyColor;
                        n.attr['grey'] = 1;
                    }
                } else {
                    n.color = n.attr['grey'] ? n.attr['true_color'] : n.color;
                    n.attr['grey'] = 0;
                }
            }).draw(2,2,2);
        }).bind('outnodes',function(){
            sigInst.iterEdges(function(e){
                e.color = e.attr['grey'] ? e.attr['true_color'] : e.color;
                e.attr['grey'] = 0;
            }).iterNodes(function(n){
                n.color = n.attr['grey'] ? n.attr['true_color'] : n.color;
                n.attr['grey'] = 0;
            }).draw(2,2,2);
        });
    },
    20000);
}
