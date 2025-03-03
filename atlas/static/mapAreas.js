var zoomHomeButton = false;

var map = generateMap(zoomHomeButton);

var legend = L.control({position: "bottomright"});
// Current observation Layer: leaflet layer type
var currentLayer;

// Current observation geoJson:  type object
var myGeoJson;

// Display limit of the territory
var areaLayer = L.geoJson(areaInfos.areaGeoJson, {
    style: function () {
        return {
            opacity: 1,
            weight: 2,
            color: areaBorderColor,
            // dashArray: "3",
            fillOpacity: 0.3,
            invert: true
        };
    }
}).addTo(map);


var bounds = L.latLngBounds([]);
var layerBounds = areaLayer.getBounds();
bounds.extend(layerBounds);
map.fitBounds(bounds);
map.zoom = map.getZoom();
// Display the 'x' last observations
// MAILLE
if (configuration.AFFICHAGE_MAILLE) {
    displayMailleLayerLastObs(observations);
}
// POINT
else {
    displayMarkerLayerPointLastObs(observations);
}

// Generate legends and check configuration to choose which to display (Maille ou Point)


htmlLegendMaille =
    "<i style='border: solid 1px var(--map-maille-lastobs-border-color);'> &nbsp; &nbsp; &nbsp;</i> Maille comportant au moins une observation <br> <br>" +
    "<i style='border: dashed 2px var(--map-area-border-color); background-color:var(--map-area-border-color); opacity:0.3'> &nbsp; &nbsp; &nbsp;</i> Limite de la zone <br> <br>" +
    "<i style='border: solid var(--map-area-border-width) var(--map-territory-border-color);'> &nbsp; &nbsp; &nbsp;</i> Limite du " +
    configuration.STRUCTURE;

htmlLegendPoint =
    "<i style='border-style: dotted;'> &nbsp; &nbsp; &nbsp;</i> Limite de la zone <br> <br>" +
    "<i style='border: solid " +
    configuration.MAP.BORDERS_WEIGHT +
    "px " +
    configuration.MAP.BORDERS_COLOR +
    ";'> &nbsp; &nbsp; &nbsp;</i> Limite du " +
    configuration.STRUCTURE;

htmlLegend = configuration.AFFICHAGE_MAILLE
    ? htmlLegendMaille
    : htmlLegendPoint;

// General Legend

generateLegende(htmlLegend);

function displayObsPreciseBaseUrl() {
    return configuration.URL_APPLICATION + "/api/observations/" + areaInfos.areaCode
};

// display observation on click
function displayObsPreciseBaseUrl(areaCode, cd_ref) {
    $.ajax({
        url:
            displayObsPreciseBaseUrl() +
            areaCode +
            "/" +
            cd_ref,
        dataType: "json",
        beforeSend: function () {
            $("#loaderSpinner").show();
            // $("#loadingGif").show();
            // $("#loadingGif").attr(
            //   "src",
            //   configuration.URL_APPLICATION + "/static/images/loading.svg"
            // );
        }
    }).done(function (observations) {
        $("#loaderSpinner").hide();
        // $("#loadingGif").hide();
        map.removeLayer(currentLayer);
        clearOverlays()
        if (configuration.AFFICHAGE_MAILLE) {
            displayMailleLayerLastObs(observations);
        } else {
            displayMarkerLayerPointArea(observations);
        }
    });
}

function displayObsGridBaseUrl() {
    return configuration.URL_APPLICATION + "/api/observationsMaille/"
}

// display observation on click
function displayObsTaxon(id_area, cd_ref) {
  $.ajax({
    url:
      configuration.URL_APPLICATION +
      "/api/observations/" +
      id_area +
      "/" +
      cd_ref,
    dataType: "json",
    beforeSend: function() {
      $("#loadingGif").show();
      $("#loadingGif").attr(
        "src",
        configuration.URL_APPLICATION + "/static/images/loading.svg"
      );
    }
  }).done(function(observations) {
    $("#loadingGif").hide();
    map.removeLayer(currentLayer);
        clearOverlays()
    if (configuration.AFFICHAGE_MAILLE) {
      displayMailleLayerLastObs(observations);
    } else {
      displayMarkerLayerPointArea(observations);
    }
  });
}


function displayObsTaxonMaille(areaCode, cd_ref) {
    $.ajax({
        url:
            displayObsGridBaseUrl() +
            areaCode +
            "/" +
            cd_ref,
        dataType: "json",
        beforeSend: function () {
            $("#loaderSpinner").show();
        }
    }).done(function (observations) {
        $("#loaderSpinner").hide();
        // $("#loadingGif").hide();
        map.removeLayer(currentLayer);
        clearOverlays()
        const geojsonMaille = generateGeoJsonMailleLastObs(observations);
        displayMailleLayerFicheEspece(geojsonMaille);
    });
}

function refreshObsArea(elem) {
    $(this)
        .siblings()
        .removeClass("current");
    $(this).addClass("current");
    if (configuration.AFFICHAGE_MAILLE) {
        displayObsTaxonMaille(elem.currentTarget.getAttribute("area-code"), elem.currentTarget.getAttribute("cdref"));
    } else {
        displayObsTaxon(elem.currentTarget.getAttribute("area-code"), elem.currentTarget.getAttribute("cdref"));
    }
    const name = elem.currentTarget.querySelector("#name").innerHTML;
    $("#titleMap").fadeOut(500, function () {
        $(this)
            .html("Observations du taxon&nbsp;:&nbsp;" + name)
            .fadeIn(500);
    });
}

$(document).ready(function () {
    $("#loaderSpinner").hide();
    if (configuration.INTERACTIVE_MAP_LIST) {
        $("#taxonList ul").on("click", "#taxonListItem", elem => {
            refreshObsArea(elem);
        });
    }
});
