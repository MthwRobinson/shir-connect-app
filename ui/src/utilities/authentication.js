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
