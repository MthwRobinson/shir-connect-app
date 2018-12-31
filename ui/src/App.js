// Main app component. Includes routing logic
import React, { Component } from 'react';
import { 
  BrowserRouter as Router,
  Link,
  Redirect,
  Route 
} from 'react-router-dom';
import SlidingPane from 'react-sliding-pane';
import Modal from 'react-modal';

import { clearToken } from './utilities/authentication';

import './App.css';
import '../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../node_modules/font-awesome/css/font-awesome.min.css';
import 'react-sliding-pane/dist/react-sliding-pane.css';

import Events from './components/Events/Events';
import EventMap from './components/EventMap/EventMap';
import EventPage from './components/EventPage/EventPage';
import Header from './components/Header/Header';
import Home from './components/Home/Home';
import Login from './components/Login/Login';
import Members from './components/Members/Members';
import MemberPage from './components/MemberPage/MemberPage';
import Trends from './components/Trends/Trends';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      paneOpen: false
    }
  }

  componentDidMount() {
    // The modal element is the popout menu
    Modal.setAppElement(this.el);
  }

  renderMenu = () => {
    // Builds the popout menu.
    // Menu is expanded is paneOpen is true
    return (
      <div ref={ref => this.el = ref}>
        <SlidingPane
          width='20%'
          isOpen={ this.state.paneOpen }
          from='left'
          onRequestClose={this.toggleMenu}
        >
          <div className="menu-content">
            <h3>Admin</h3><hr/>
            <Link to="/login" onClick={()=>this.logout()}>Sign Out</Link>
          </div>
        </SlidingPane>
      </div>
      );
  }

  toggleMenu = (event) => {
    // Switches the menu from open to close or close to open
    event.preventDefault();
    const currentState = this.state.paneOpen;
    this.setState({paneOpen: !currentState})
  }

  logout = () => {
    // Logs out and redirects to the sign-in page
    clearToken();
    this.setState({paneOpen: false})
  }

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

    const menu = this.renderMenu();

    return (
      <div className="App">
        <Header toggleMenu={(event)=>this.toggleMenu(event)}></Header>
        <Router>
          <div>
            {menu}
            <PrivateRoute exact path="/" component={Home} />
            <PrivateRoute path="/events" component={Events} />
            <PrivateRoute path="/event" component={EventPage} />
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
