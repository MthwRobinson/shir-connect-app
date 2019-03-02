// Implements helper functions for the user authentication workflow
import axios from 'axios';
import Cookies from 'js-cookie';


function getCSRFToken(){
  // Pulls the CSRF token from cookies
  return Cookies.get('csrf_access_token');
}
export { getCSRFToken }

function refreshAccessToken(){
  // Refreshes the access token
  const url = '/service/user/refresh';
  axios.get(url)
}
export { refreshAccessToken }

function logout() {
  // Clears the JWT and CSRF token from browser cookies
  const url = '/service/user/logout';
  axios.post(url)
}
export { logout };

function getMapBoxToken() {
  return 'pk.eyJ1IjoibXRod3JvYmluc29uIiwiYSI6ImNqNXUxcXcwaTAyamcyd3J4NzBoN283b3AifQ.JIfgHM7LDVb34sWhN4L8aA';
}
export { getMapBoxToken }
