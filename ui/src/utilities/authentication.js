// Implements helper functions for the user authentication workflow
import axios from 'axios';
import Cookies from 'js-cookie';

//----------------
// ACCESS TOKENS
//----------------
function setAccessToken(accessToken){
  // Sets the access token in local storage
  localStorage.setItem('accessToken', accessToken);
}
export { setAccessToken };

function getAccessToken(){
  // Pulls the access token from local storage
  return localStorage.getItem('accessToken');
}
export { getAccessToken }

function getCSRFToken(){
  // Pulls the CSRF token from cookies
  return Cookies.get('csrf_access_token');
}
export { getCSRFToken }

//----------------
// REFRESH TOKENS
//----------------

function setRefreshToken(refreshToken){
  // Sets the refresh token in local storage
  localStorage.setItem('refreshToken', refreshToken);
}
export { setRefreshToken };

function getRefreshToken(){
  // Pulls the refresh token from local storage
  return localStorage.getItem('refreshToken');
}

function refreshAccessToken(){
  // Refreshes the access token
  const url = '/service/user/refresh';
  axios.get(url)
}
export { refreshAccessToken }

//------------------
// LOGOUT FUNCTIONS
//------------------

function clearStorage() {
  // Clears the JWT and CSRF token from browser cookies
  const url = '/service/user/logout';
  axios.get(url)
}
export { clearStorage };

function logout() {
  // Clears the JWT and CSRF token from browser cookies
  const url = '/service/user/logout';
  axios.post(url)
}
export { logout };

//-------------------
// MAPBOX TOKEN 
// ------------------

function getMapBoxToken() {
  return 'pk.eyJ1IjoibXRod3JvYmluc29uIiwiYSI6ImNqNXUxcXcwaTAyamcyd3J4NzBoN283b3AifQ.JIfgHM7LDVb34sWhN4L8aA';
}
export { getMapBoxToken }
