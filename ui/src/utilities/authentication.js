// Implements helper functions for the user authentication workflow
import axios from 'axios';

function clearToken() {
  // Clears the JWT from local storage
  localStorage.removeItem('trsToken');
}
export { clearToken };

function setAccessToken(accessToken){
  // Sets the access token in local storage
  localStorage.setItem('trsToken', accessToken);
}
export { setAccessToken };

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
  const auth = 'Bearar '.concat(refreshToken);
  const url = '/service/user/authorize';
  axios.get(url, {headers: {Authorization: auth}})
    .then(res => {
      const accessToken = res.data.jwt;
      setAccessToken(accessToken);
    })
}
export { refreshAccessToken }
