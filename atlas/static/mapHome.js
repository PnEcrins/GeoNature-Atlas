var zoomHomeButton = true;

var map = generateMap(zoomHomeButton);

var legend = L.control({position: 'bottomright'});

map.scrollWheelZoom.disable();

// Gestionnaire de couches SIG additionnelles
if (couchesSigInfo !== undefined) {
  addLayerControlToMap(map);
}

$('#map').click(function(){
  map.scrollWheelZoom.enable();
})



// Markers display on window ready

$(function(){

  if (configuration.AFFICHAGE_MAILLE){
    // display maille layer
    displayMailleLayerLastObs(observations);

    // interaction list - map
      $('.lastObslistItem').click(function(){
         $(this).siblings().removeClass('bg-light');
         $(this).addClass('bg-light');
        var id_observation = $(this).attr('idSynthese');
        p = (currentLayer._layers);
        var selectLayer;
        for (var key in p) {
          if (find_id_observation_in_array(p[key].feature.properties.list_id_observation, id_observation) ){
              selectLayer = p[key];
          }
        }

        selectLayer.openPopup();
        var bounds = L.latLngBounds();
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
          map.setView(selectLayer._latlng, 14);
      })
  }


// Zoom on the popup on observation click

  currentLayer.on('click', function(e){
    if (map.getZoom()<14) {
      map.setView(e.latlng, 14);
    }
  });


});

// Generate legends and check configuration to choose which to display (Maille ou Point)

htmlLegendMaille = "<i style='border: solid 1px red;'> &nbsp; &nbsp; &nbsp;</i> Maille comportant au moins une observation <br> <br>" +
						"<i style='border: solid "+configuration.MAP.BORDERS_WEIGHT+"px "+configuration.MAP.BORDERS_COLOR+";'> &nbsp; &nbsp; &nbsp;</i> Limite du "+configuration.STRUCTURE;

htmlLegendPoint = "<i style='border: solid "+configuration.MAP.BORDERS_WEIGHT+"px "+configuration.MAP.BORDERS_COLOR+";'> &nbsp; &nbsp; &nbsp;</i> Limite du "+configuration.STRUCTURE

htmlLegend = configuration.AFFICHAGE_MAILLE ? htmlLegendMaille : htmlLegendPoint;

generateLegende(htmlLegend);
