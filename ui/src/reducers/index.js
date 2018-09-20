// Combines all the reducers
// Reducers are imported into App.js
import { combineReducers } from 'redux';
import { reducer as form } from 'redux-form'

export default combineReducers({
  form
});
