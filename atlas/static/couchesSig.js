// Gestionnaire de couches SIG additionnelles

L.Control.CollapsableLayerTreeControl = L.Control.LayerTreeControl.extend({
  // adapted from Leaflet's L.control.layers
  expand() {
    this._container.classList.add('layer-tree-control-expanded');
    this._treeContainer.style.height = null;
    const acceptableHeight = this._map.getSize().y - (this._container.offsetTop + 50);
    if (acceptableHeight < this._treeContainer.clientHeight) {
      this._treeContainer.classList.add('leaflet-control-layers-scrollbar');
      this._treeContainer.style.height = `${acceptableHeight}px`;
    } else {
      this._treeContainer.classList.remove('leaflet-control-layers-scrollbar');
    }
    return this;
  },

  // adapted from Leaflet's L.control.layers
  collapse(ev) {
    // On touch devices `pointerleave` is fired while clicking on a checkbox.
    // The control was collapsed instead of adding the layer to the map.
    // So we allow collapse if it is not touch and pointerleave.
    if (!ev || !(ev.type === 'pointerleave' && ev.pointerType === 'touch')) {
      this._container.classList.remove('layer-tree-control-expanded');
    }
    return this;
  },

  onAdd: function (map) {
    // TODO: call onAdd on LayerTreeControl
    L.Control.LayerTreeControl.prototype.onAdd.call(this, map);

    var container = this._container;
    var collapsed = this.options.collapsed;
    // TODO: add the class on the already created DOM elmt
    // this._treeContainer = L.DomUtil.create('div', 'layer-tree-control-list', container);
    container.childNodes[0].classList.add('layer-tree-control-list');

    if (collapsed) {
      this._map.on('click', this.collapse, this);

      if (!L.Browser.android) {
        L.DomEvent.on(container, {
          mouseenter: this.expand,
          mouseleave: this.collapse
        }, this);
      }
    }

    var link = this._link = L.DomUtil.create('a', 'layer-tree-control-toggle', container);
    link.href = '#';
    link.title = 'Layers';
    link.setAttribute('role', 'button');

    if (L.Browser.touch) {
      L.DomEvent.on(link, 'click', L.DomEvent.stop);
      L.DomEvent.on(link, 'click', this.expand, this);
    } else {
      L.DomEvent.on(link, 'focus', this.expand, this);
    }

    if (!collapsed) {
      this.expand();
    }

    return this._container;
  }
});

function createLeafletLayer(coucheSigInfo) {
  return L.tileLayer.wms(
    coucheSigInfo.url,
    coucheSigInfo.options
  );
}

function createEsriDynamicLayer(coucheSigInfo) {
  return L.esri.dynamicMapLayer(
    {
      url: coucheSigInfo.url,
      layers: []
    }
  );
}

function createLayer(coucheSigInfo) {
  if (coucheSigInfo.type === "wms") {
    return createLeafletLayer(coucheSigInfo);
  } else if (coucheSigInfo.type === "arcgisMapService") {
    return createEsriDynamicLayer(coucheSigInfo);
  }
}

function addLayerControlToMap(map) {
  var layer_types_map = {
    wms: "leaflet",
    arcgisMapService: "esriDynamic"
  };
  var sigLayers = [];
  couchesSigInfo.forEach(
    (coucheSigInfo) => {
      sigLayers.push(
        {
          layer: createLayer(coucheSigInfo),
          type: layer_types_map[coucheSigInfo.type],
          name: coucheSigInfo.name
        }
      );
    }
  );
  var layerTreeCtrl = new L.Control.CollapsableLayerTreeControl(sigLayers, {
    position: 'topright',
    collapsed: true
  });

  map.addControl(layerTreeCtrl);
}
