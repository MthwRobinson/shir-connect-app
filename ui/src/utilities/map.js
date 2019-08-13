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
