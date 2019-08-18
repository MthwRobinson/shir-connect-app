// Common utility functions for the map
import axios from 'axios';

function getMapBoxToken() {
  return 'pk.eyJ1IjoiZmlkZGxlcmFuYWx5dGljcyIsImEiOiJjano5Nnp1cjEwOXA4M2NsbzZnano1dTg2In0.g9G0rlFVKBMu9OqBvys7YA';
}
export { getMapBoxToken }

function getDefaultLocation() {
  return axios.get('/service/map/default');
}
export { getDefaultLocation }

function getBoundingBox (data) {
	// Gets a bounding box from a GeoJSON object of points
	//
	// Parameters:
  // ----------
	// data: object, the geojson object. needs a type key and a data key
	//
	// Returns:
  // --------
	// bounds: object, the bounds o fthe geojson object, with xMin, xMax,
	// 	yMin, and yMax keys
  var bounds = {}, coords, point, latitude, longitude;

  // We want to use the “features” key of the FeatureCollection (see above)
  data = data.features;

  // Loop through each “feature”
  for (var i = 0; i < data.length; i++) {

    // Pull out the coordinates of this feature
    coords = data[i].geometry.coordinates;
		longitude = coords[0];
		latitude = coords[1]

		bounds.xMin = bounds.xMin < longitude ? bounds.xMin : longitude;
		bounds.xMax = bounds.xMax > longitude ? bounds.xMax : longitude;
		bounds.yMin = bounds.yMin < latitude ? bounds.yMin : latitude;
		bounds.yMax = bounds.yMax > latitude ? bounds.yMax : latitude;

  }

  // Returns an object that contains the bounds of this GeoJSON
  // data. The keys of this object describe a box formed by the
  // northwest (xMin, yMin) and southeast (xMax, yMax) coordinates.
  return bounds;
}
export { getBoundingBox }
