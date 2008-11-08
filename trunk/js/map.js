function load(url) {
  if (GBrowserIsCompatible()) {
    var map = new GMap2(document.getElementById("map"));

    map.addControl(new GSmallMapControl());
    map.addControl(new GMapTypeControl());
    map.setCenter(new GLatLng(12,0), 3, G_HYBRID_MAP);

    function createMarker(location, point) {      
      var marker = new GMarker(point, {title: location.getAttribute("title")});
      
      GEvent.addListener(marker, "click", function() {
	marker.openInfoWindowHtml('<h3>'+location.getAttribute("title")+'</h3><div style="text-align: center;"><img src="'+location.getAttribute("thumbnail")+'"></div>');
      });
      return marker;
    }

    GDownloadUrl(url, function(data, responseCode) {
      var xml = GXml.parse(data);      
      var locations = xml.documentElement.getElementsByTagName("location");
      var bounds = new GLatLngBounds();

      for (var i=0; i<locations.length; i++) {
	var lat = parseFloat(locations[i].getAttribute("latitude"));
	var lng = parseFloat(locations[i].getAttribute("longitude"));

	var point = new GLatLng(lat, lng);
	bounds.extend(point);
	map.addOverlay(createMarker(locations[i], point));
      }

      map.setCenter(bounds.getCenter());
      map.setZoom(Math.min(12, map.getBoundsZoomLevel(bounds)-1));
    });
  }
}
