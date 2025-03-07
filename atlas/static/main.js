$(document).ready(function() {
  $(window).keydown(function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      return false;
    }
  });
});

window.onresize = function() {
  var presentationText = document.getElementById("presentation-text");
  if (presentationText) {
    if (window.innerWidth <= 800) {
      presentationText.hidden = true;
    } else {
      presentationText.hidden = false;
    }
  }
};

var presentationText = document.getElementById("presentation-text");
if (window.innerWidth <= 800 && presentationText) {
  presentationText.hidden = true;
}

autocompleteSearch = function(inputID, urlDestination, nbProposal) {
  $(inputID).autocomplete({
    source: function(request, response) {
      var searchUrl;
      if (urlDestination == "espece") {
        searchUrl = "/api/searchTaxon";
      } else if (urlDestination == "area") {
        searchUrl = "/api/searchArea";
      }
      else {
        searchUrl = "/api/searchArea/"+urlDestination;
      }
      $(inputID)
        .attr("loading", "true")
        .css(
          "background-image",
          "url('" +
            configuration.URL_APPLICATION +
            "/static/images/loading3.gif')"
        );
      $.get(
        configuration.URL_APPLICATION + searchUrl,
        { search: request.term, limit: nbProposal },
          function(results) {
              const unique_type_name = [...new Set(results.map(item => item.type_name))];
              const items = []
              unique_type_name.forEach(u => {
                  items.push({"type": u })
                  items.push(
                      ...results.filter(item => {
                      return item.type_name === u
                  }).slice(0, nbProposal))
              })
              response(items);
          $(inputID)
            .attr("loading", "false")
            .css("background-image", "none");
        }
      );
    },
    focus: function(event, ui) {
      return false;
    },
    select: function(event, ui) {
        if (ui.item && ui.item.type) {
            return false;
        }
      $(inputID).val(ui.item.label);
      var url = ui.item.value;
      if (urlDestination == "espece") {
        location.href = configuration.URL_APPLICATION + language  + "/espece/" + url;
      } else if (urlDestination == "area") {
        location.href = configuration.URL_APPLICATION + language  + "/area/" + url;
      } else {
        location.href = configuration.URL_APPLICATION + language  + "/area/" + urlDestination +"/"+ url;
      }

      return false;
    },
      create: function(event, ui) {
          $(this).data("ui-autocomplete")._renderItem = function(ul, item) {
              if (item && item.type) {
                  return $("<div class='type_name'>")
                      .append(`<b>${item.type}</b>`)
                      .appendTo(ul);
              }
              return $("<li>")
                  .append(`<a  class="search-bar-item"> ${item.label} </a>`)
                  .appendTo(ul);
          };
      }
  });
};

// Generate the autocompletion with the list of item, the input id and the form id
$("#searchTaxons").focus(function() {
  autocompleteSearch("#searchTaxons", "espece", 20);
});
$("#searchTaxonsStat").focus(function() {
  autocompleteSearch("#searchTaxonsStat", "espece", 10);
});

$("#searchAreas").focus(function() {
  autocompleteSearch("#searchAreas", "area", 20);
});
$("#searchAreasStat").focus(function() {
  autocompleteSearch("#searchAreasStat", "area", 10);
});


// child list display
var childList = $("#childList");
$("#buttonChild").click(function() {
  $("#buttonChild")
    .find("span")
    .toggleClass("fas fa-chevron-right")
    .toggleClass("fas fa-chevron-down");
  var childList = $("#childList");
  if (childList.attr("hidden") === "hidden") {
    childList.removeAttr("hidden");
  } else {
    childList.attr("hidden", "hidden");
  }
});

// Tooltip
$(document).ready(function() {
  $('[data-toggle="tooltip"]').tooltip();
});

// Animation index.html
$(document).ready(function() {
  $("#localScroll").on("click", function() {
    var dest = $("#DernieresObservations");
    var speed = 750;
    $("html, body").animate({ scrollTop: $(dest).offset().top }, speed);
    return false;
  });
});

// Glossarizer JQUERY utilisé dans la bloc d'infos de la fiche espèce (si paramètre GLOSSAIRE activé)
if (configuration.GLOSSAIRE) {
  $(function() {
    $("#blocInfos").glossarizer({
      sourceURL:
        configuration.URL_APPLICATION + "/static/custom/glossaire.json",
      callback: function() {
        // Callback fired after glossarizer finishes its job
        new tooltip();
      }
    });
  });
}

if (configuration.OREJIME_APPS.length > 0) {
    var orejimeConfig = {
        elementID: "orejime",
        appElement: "main",
        cookieName: "orejime",
        cookieExpiresAfterDays: 365,
        privacyPolicy: "/?personal_data=true",
        default: true,
        mustConsent: false,
        mustNotice: false,
        lang: configuration.DEFAULT_LANGUAGE,
        logo: false,
        debug: configuration.modeDebug,
        apps: configuration.OREJIME_APPS,
        categories: configuration.OREJIME_CATEGORIES
    }
  if (configuration.OREJIME_TRANSLATIONS && configuration.OREJIME_TRANSLATIONS != {}) {
      orejimeConfig.translations = configuration.OREJIME_TRANSLATIONS
  }
}
