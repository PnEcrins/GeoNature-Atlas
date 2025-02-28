var zoomHomeButton = true;

var map = generateMap(zoomHomeButton);

var legend = L.control({position: 'bottomright'});

map.scrollWheelZoom.disable();
$('#map').click(function(){
    map.scrollWheelZoom.enable();
})



// Markers display on window ready

$(function(){

    if (configuration.AFFICHAGE_MAILLE){
        // display maille layer
        displayMailleLayerLastObs(observations);

        // interaction list - map
        $('.lastObslistItem').click(function(elem){
            $(this).siblings().removeClass('current');
            $(this).addClass('current');
            const idMaille = Number(elem.currentTarget.getAttribute("area-code"));
            p = (currentLayer._layers);
            let selectLayer;
            for (var key in p) {
                if (p[key].feature.properties.meshId === idMaille){
                    selectLayer = p[key];
                }
            }

            resetStyleMailles()
            selectLayer.setStyle(styleMailleClickedOrHover(selectLayer));
            selectLayer.openPopup(selectLayer._bounds.getCenter());
            var bounds = L.latLngBounds([]);
            var layerBounds = selectLayer.getBounds();
            bounds.extend(layerBounds);
            map.fitBounds(bounds, {
                maxZoom : 12
            });
        });
    }

    // Display point layer
    else{
        displayMarkerLayerPointLastObs(observations);

        // interaction list - map
        $('.lastObslistItem').click(function(){
            $(this).siblings().removeClass('current');
            $(this).addClass('current');
            var id_observation = $(this).attr('idSynthese');

            var p = (currentLayer._layers);
            var selectLayer;
            for (var key in p) {
                if (p[key].feature.properties.id_observation == id_observation){
                    selectLayer = p[key];
                }
            }
            selectLayer.openPopup();
            selectLayer.openPopup(selectLayer._latlng);
            map.setView(selectLayer._latlng, 14);
        })
    }



});

// Generate legends and check configuration to choose which to display (Maille ou Point)

htmlLegendMaille = "<i style='border: solid 1px red;'> &nbsp; &nbsp; &nbsp;</i> Maille comportant au moins une observation <br> <br>" +
    "<i style='border: solid "+configuration.MAP.BORDERS_WEIGHT+"px "+configuration.MAP.BORDERS_COLOR+";'> &nbsp; &nbsp; &nbsp;</i> Limite du "+configuration.STRUCTURE;

htmlLegendPoint = "<i style='border: solid "+configuration.MAP.BORDERS_WEIGHT+"px "+configuration.MAP.BORDERS_COLOR+";'> &nbsp; &nbsp; &nbsp;</i> Limite du "+configuration.STRUCTURE

htmlLegend = configuration.AFFICHAGE_MAILLE ? htmlLegendMaille : htmlLegendPoint;

generateLegende(htmlLegend);
