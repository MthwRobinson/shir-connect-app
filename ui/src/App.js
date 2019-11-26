// Main app component. Includes routing logic
import React, { Component } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

import ChangePassword from './components/ChangePassword/ChangePassword';
import Events from './components/Events/Events';
import EventMap from './components/EventMap/EventMap';
import EventPage from './components/EventPage/EventPage';
import Forbidden from './components/ErrorPages/Forbidden';
import Home from './components/Home/Home';
import Login from './components/Login/Login';
import ManageUsers from './components/ManageUsers/ManageUsers';
import Members from './components/Members/Members';
import MemberPage from './components/MemberPage/MemberPage';
import NotFound from './components/ErrorPages/NotFound';
import Report from './components/Report/Report';
import ResetPassword from './components/ResetPassword/ResetPassword';
import ServerError from './components/ErrorPages/ServerError';
import Trends from './components/Trends/Trends';
import { getModules } from './utilities/utils';

import './App.css';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../node_modules/font-awesome/css/font-awesome.min.css';
import 'react-sliding-pane/dist/react-sliding-pane.css';
import '../node_modules/react-bootstrap-toggle/dist/bootstrap2-toggle.css';

const MODULES = getModules();
let PATHS = [];
for(let key in MODULES){
  if(['/participant', '/event'].indexOf(key) === -1){
    PATHS.push(MODULES[key]["link"]);
  }
}

class App extends Component {
  render() {
    return (
      <div className="App">
        <Router>
          <div>
            <Switch>
                <Route exact path="/" component={Home} />
                <Route path="/change-password" component={ChangePassword} />
                <Route path="/events" component={Events} />
                <Route path="/event" component={EventPage} />
                <Route path="/participant" component={MemberPage} />
                <Route path="/participants" component={Members} />
                <Route path="/server-error" component={ServerError} />
                <Route path="/forbidden" component={Forbidden} />
                <Route path="/manage-users" component={ManageUsers} />
                <Route path="/reset-password" component={ResetPassword} />
                <Route path="/login" component={Login} />
                {PATHS.indexOf("/report") >= 0 &&
                 <Route path="/report" component={Report} /> }
                {PATHS.indexOf("/trends") >= 0 &&
                 <Route path="/trends" component={Trends} /> }
                {PATHS.indexOf("/map") >= 0 &&
                 <Route path="/map" component={EventMap} /> }
                <Route component={NotFound} />
            </Switch>
          </div>
        </Router>
      </div>
    );
  }
}

export default App;
