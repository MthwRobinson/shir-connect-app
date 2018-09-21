// Action store that handles authentication and stores
// tokens in local storage
import axios from 'axios';

export const AUTHENTICATED = 'authenticated_user';
export const UNAUTHENTICATED = 'unauthenticated_user';
export const AUTHENTICATION_ERROR = 'authentication_error';

export function logInAction({ userName, password }, history) {
  return async (dispatch) => {
    try {
      const res = await axios.post(`/login`, { userName, password });

      dispatch({ type: AUTHENTICATED });
      localStorage.setItem('user', res.data.token);
      history.push('/secret');
    } catch(error) {
      dispatch({
        type: AUTHENTICATION_ERROR,
        payload: 'Invalid user name or password'
      });
    }
  };
}
