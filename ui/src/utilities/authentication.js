// Implements helper functions for the user authentication workflow
import axios from 'axios';

//----------------
// ACCESS TOKENS
//----------------
function setAccessToken(accessToken){
  // Sets the access token in local storage
  localStorage.setItem('trsToken', accessToken);
}
export { setAccessToken };

function getAccessToken(){
  // Pulls the access token from local storage
  return localStorage.getItem('trsToken');
}
export { getAccessToken }

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
  const refreshToken = getRefreshToken();
  const auth = 'Bearer '.concat(refreshToken);
  const url = '/service/user/refresh';
  axios.get(url, {headers: {Authorization: auth}})
    .then(res => {
      const accessToken = res.data.jwt;
      setAccessToken(accessToken);
    })
}
export { refreshAccessToken }

//------------------
// LOGOUT FUNCTIONS
//------------------

function clearStorage() {
  // Clears the JWT from local storage
  localStorage.clear();
  sessionStorage.clear();
}
export { clearStorage };
