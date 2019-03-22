// Common utility functions for the map
import axios from 'axios';

function getMapBoxToken() {
  return 'pk.eyJ1IjoibXRod3JvYmluc29uIiwiYSI6ImNqNXUxcXcwaTAyamcyd3J4NzBoN283b3AifQ.JIfgHM7LDVb34sWhN4L8aA';
}
export { getMapBoxToken }

function getDefaultLocation() {
  return axios.get('/service/map/default');
}
export { getDefaultLocation }
