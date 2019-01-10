// Main app component. Includes routing logic
import React, { Component } from 'react';
import { 
  BrowserRouter as Router,
  Redirect,
  Route 
} from 'react-router-dom';

import './App.css';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../node_modules/font-awesome/css/font-awesome.min.css';
import 'react-sliding-pane/dist/react-sliding-pane.css';

import ChangePassword from './components/ChangePassword/ChangePassword';
import Events from './components/Events/Events';
import EventMap from './components/EventMap/EventMap';
import EventPage from './components/EventPage/EventPage';
import Forbidden from './components/Forbidden/Forbidden';
import Home from './components/Home/Home';
import Login from './components/Login/Login';
import ManageUsers from './components/ManageUsers/ManageUsers';
import Members from './components/Members/Members';
import MemberPage from './components/MemberPage/MemberPage';
import Trends from './components/Trends/Trends';

class App extends Component {
  render() {
    // PrivateRoute ensures that there is a token
    // present in local storage before rendering
    // a component
    const PrivateRoute = ({ component: Component, ...rest }) => (
      <Route {...rest} render={(props) => (
        localStorage.getItem('trsToken') === null
        ? <Redirect to='/login' />
        : <Component {...props} />
      )} />
    )

    return (
      <div className="App">
        <Router>
          <div>
            <PrivateRoute exact path="/" component={Home} />
            <PrivateRoute path="/change-password" component={ChangePassword} />
            <PrivateRoute path="/events" component={Events} />
            <PrivateRoute path="/event" component={EventPage} />
            <PrivateRoute path="/forbidden" component={Forbidden} />
            <PrivateRoute path="/manage-users" component={ManageUsers} />
            <PrivateRoute path="/member" component={MemberPage} />
            <PrivateRoute path="/members" component={Members} />
            <PrivateRoute path="/trends" component={Trends} />
            <PrivateRoute path="/map" component={EventMap} />
            <Route path="/login" component={Login} />
          </div>
        </Router>
      </div>
    );
  }
}

export default App;
