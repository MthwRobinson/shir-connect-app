// Main app component. Includes routing logic
import React, { Component } from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom';

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
import Report from './components/Report/Report';
import Trends from './components/Trends/Trends';

import './App.css';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../node_modules/font-awesome/css/font-awesome.min.css';
import 'react-sliding-pane/dist/react-sliding-pane.css';
import '../node_modules/react-bootstrap-toggle/dist/bootstrap2-toggle.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <Router>
          <div>
            <Route exact path="/" component={Home} />
            <Route path="/change-password" component={ChangePassword} />
            <Route path="/events" component={Events} />
            <Route path="/event" component={EventPage} />
            <Route path="/forbidden" component={Forbidden} />
            <Route path="/manage-users" component={ManageUsers} />
            <Route path="/participant" component={MemberPage} />
            <Route path="/participants" component={Members} />
            <Route path="/report" component={Report} />
            <Route path="/trends" component={Trends} />
            <Route path="/map" component={EventMap} />
            <Route path="/login" component={Login} />
          </div>
        </Router>
      </div>
    );
  }
}

export default App;
