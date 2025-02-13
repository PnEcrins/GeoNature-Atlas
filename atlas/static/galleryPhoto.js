var compteurJson = 0;
var clearHtml = false;

function formatPhotoAttribut(attribut) {
  if (attribut) {
    return attribut.split("'").join("&#39;");
  }
  return "";
}

// populate HTML with the selected photos
function generateHtmlPhoto(photos, redimentionnement, taxhub_url) {
  lightbox.enable();

  if (clearHtml) {
    if (photos.length == 0) {
      htmlPhoto =
        "<h3> <span style='padding:10px;'> Aucun résultat pour cette recherche </span> </h3>";
    } else {
      htmlPhoto = "";
    }
  } else {
    htmlPhoto = $("#insertPhotos").html();
  }

  if (compteurJson <= photos.length) {
    slicePhoto = photos.slice(compteurJson, compteurJson + 22);
    compteurJson = compteurJson + 22;
    slicePhoto.forEach(function (photo) {
      photo.title = formatPhotoAttribut(photo.title);
      photo.description = formatPhotoAttribut(photo.description);
      photo.author = formatPhotoAttribut(photo.author);
      photo.licence = formatPhotoAttribut(photo.licence);
      photo.source = formatPhotoAttribut(photo.source);
      photo_url = photo.path;
      if (redimentionnement) {
        photo_url =
          taxhub_url +
          "/api/tmedias/thumbnail/" +
          photo.id_media +
          "?h=500&w=500";
      }
      let subject = `${stripHtml(photo.title)}<br/>`;
      let description = photo.description
        ? `${stripHtml(photo.description)}<br/>`
        : "";
      let author = photo.author ? `&copy; ${stripHtml(photo.author)} - ` : "";
      let licence = `${stripHtml(photo.licence)} ${stripHtml(photo.source)}`;
      let datatitle = `${subject} ${description} ${author} ${licence}`;
      onePhoto = `
				<div class="col-lg-3 col-md-4 col-sm-6 col-xs-12 thumbnail-col photo-espece ">
				  <div class="zoom-wrapper" >
				 		<a
              href="${photo.path}"
              data-lightbox="imageSet"
              data-title="${datatitle}"
              data-alt="${photo.cd_ref}"
            >
						  <div
                class="img-custom-medias"
                style="background-image:url('${photo_url}')"
                alt="${photo.name}"
              ></div>
						  <div class="stat-medias-hovereffet">
					      <h2 class="overlay-obs">${photo.name}</br> </br>${photo.nb_obs} observations</h2>
						    <img src="${configuration.URL_APPLICATION}/static/images/eye.png">
              </div>
            </a>
          </div>
				</div>`;

      htmlPhoto += onePhoto;
    });
  }
  $("#insertPhotos").html(htmlPhoto);
}

function scrollEvent(photos) {
  $("#insertPhotos").on("scroll", function () {
    clearHtml = false;
    if (
      $("#insertPhotos").scrollTop() + $("#insertPhotos").height() >=
      $("#insertPhotos")[0].scrollHeight
    ) {
      generateHtmlPhoto(
        photos,
        configuration.REDIMENSIONNEMENT_IMAGE,
        configuration.TAXHUB_URL
      );
    }
  });
}

// ORDER event
function orderPhotosEvent(photos) {
  $("body").on("click", "#order-sort", function () {
    $("#searchPhotos").val("");

    span = $("#order-sort");
    $("#order-picto").toggleClass("fas fa-sort").toggleClass("fas fa-random");
    $(span).attr("id", "order-random");
    $(span).attr("data-original-title", "Trier de manière aléatoire");
    sortedPhotos = photos.slice().sort(function (a, b) {
      if (a.nb_obs >= b.nb_obs) return -1;
      if (a.nb_obs < b.nb_obs) return 1;
      return 0;
    });
    clearHtml = true;
    compteurJson = 0;

    generateHtmlPhoto(
      sortedPhotos,
      configuration.REDIMENSIONNEMENT_IMAGE,
      configuration.TAXHUB_URL
    );
    $("#insertPhotos").off("scroll");
    scrollEvent(sortedPhotos);
  });
}

function sufflePhotosEvent(photos) {
  $("body").on("click", "#order-random", function () {
    $("#searchPhotos").val("");

    span = $("#order-random");
    $("#order-picto").toggleClass("fas fa-sort").toggleClass("fas fa-random");
    $(span).attr("id", "order-sort");
    $(span).attr(
      "data-original-title",
      "Trier les photos par nombre d'observations"
    );
    clearHtml = true;
    compteurJson = 0;
    generateHtmlPhoto(
      photos,
      configuration.REDIMENSIONNEMENT_IMAGE,
      configuration.TAXHUB_URL
    );
    $("#insertPhotos").off("scroll");
    scrollEvent(photos);
  });
}

jQuery(function () {
  lightbox.option({
    albumLabel: "Image %1 sur %2",
    wrapAround: true,
  });
  $("#lightbox .lb-next").after(
    '<a class="lb-link" href="#"> Fiche espèce </a>'
  );

  $("#lightbox .lb-link").on("click", function () {
    let cdRef = $("#lightbox .lb-image").attr("alt");
    let url = `${configuration.URL_APPLICATION}/espece/${cdRef}`;
    $(this).attr("href", url);
    location.href = url;
  });

  $.ajax({
    url: configuration.URL_APPLICATION + "/api/photosGallery",
    dataType: "json",
    beforeSend: function () {
      // $('#loadingGif').attr("src", configuration.URL_APPLICATION+'/static/images/loading.svg')
    },
  }).done(function (photos) {
    generateHtmlPhoto(
      photos,
      configuration.REDIMENSIONNEMENT_IMAGE,
      configuration.TAXHUB_URL
    );
    $("#nbPhotos").html(photos.length + " photos");
    scrollEvent(photos);
    orderPhotosEvent(photos);
    sufflePhotosEvent(photos);

    $("#allGroups").on("click", function () {
      $("#searchPhotos").val("");
      $("body").off("click");
      orderPhotosEvent(photos);
      sufflePhotosEvent(photos);
      clearHtml = true;
      compteurJson = 0;
      $("#insertPhotos").off("scroll");
      generateHtmlPhoto(
        photos,
        configuration.REDIMENSIONNEMENT_IMAGE,
        configuration.TAXHUB_URL
      );
      $("#group").html("");
      $("#nbPhotos").html(photos.length + " photos");
      scrollEvent(photos);
    });

    // search a photo by the name of the species
    $("#searchPhotos").on("keyup", function () {
      $("#insertPhotos").off("scroll");
      $("body").off("click");
      $("#group").html("");
      keyString = this.value;
      filterJsonPhoto = photos.filter(function (obj) {
        if (obj.name) {
          name = obj.name.toLowerCase();
        } else {
          name = "Nom non renseigné";
        }
        if (obj.title) {
          title = obj.title.toLowerCase();
        } else {
          title = "Titre non renseigné";
        }
        if (obj.author) {
          author = obj.author.toLowerCase();
        } else {
          author = "Auteur non renseigné";
        }
        return (
          name.includes(keyString.toLowerCase()) ||
          title.includes(keyString.toLowerCase()) ||
          author.includes(keyString.toLowerCase())
        );
      });

      clearHtml = true;
      compteurJson = 0;
      generateHtmlPhoto(
        filterJsonPhoto,
        configuration.REDIMENSIONNEMENT_IMAGE,
        configuration.TAXHUB_URL
      );
      $("#nbPhotos").html(filterJsonPhoto.length + " photos");
      scrollEvent(filterJsonPhoto);
      orderPhotosEvent(photos);
      sufflePhotosEvent(photos);
    });
  });
});

$(".INPNgroup").on("click", function () {
  $("#searchPhotos").val("");
  compteurJson = 0;
  clearHtml = true;
  group = $(this).attr("alt");
  $("#insertPhotos").off("scroll");
  $("#page").off("click");
  span = $("#orderPhotos").find("span");
  $(span).attr("class", "fas fa-sort");
  $(span).attr(
    "data-original-title",
    "Trier les photos par nombre d'observations"
  );
  $(span).attr("id", "sort");

  $.ajax({
    url: configuration.URL_APPLICATION + "/api/photoGroup/" + group,
    dataType: "json",
    beforeSend: function () {
      // $('#loadingGif').attr("src", configuration.URL_APPLICATION+'/static/images/loading.svg')
    },

    // Count and display number of photos in 1 group
  }).done(function (photos) {
    generateHtmlPhoto(
      photos,
      configuration.REDIMENSIONNEMENT_IMAGE,
      configuration.TAXHUB_URL
    );
    $("#group").html("(" + group + ")");
    $("#nbPhotos").html(photos.length + " photos");
    clearHtml = false;
    scrollEvent(photos);
    orderPhotosEvent(photos);
    sufflePhotosEvent();
  });
});

function stripHtml(html) {
  let tmp = document.createElement("DIV");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
}