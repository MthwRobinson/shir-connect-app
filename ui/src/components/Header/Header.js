// Header component for the app
// The header is persistent in all views
import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Navbar } from 'react-bootstrap';
import SlidingPane from 'react-sliding-pane';
import Modal from 'react-modal';
import axios from 'axios';

import { 
  clearStorage,
  getAccessToken
} from './../../utilities/authentication';

import './Header.css';

const MODULES = require('./../../data/modules.json');

class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      paneOpen: false,
      userRole: 'standard',
      modules: []
    }
  }
  
  componentDidMount() {
    // The modal element is the popout menu
    Modal.setAppElement(this.el);
    this.checkAccess();
  }

  checkAccess() {
    // Checks to make sure the role of the user
    if(this.props.history.location.pathname!=='/login'){
      const token = getAccessToken();
      const auth = 'Bearer '.concat(token);
      const url = '/service/user/authorize';
      axios.get(url, {headers: {Authorization: auth }})
        .then(res => {
          this.setState({
            modules: res.data.modules,
            userRole: res.data.role
          });
        })
        .catch( err => {
          if(err.response.status===401){
            this.navigate('/login');
          }
        })
    }
  }

  renderMenu = () => {
    // Builds the popout menu.
    // Menu is expanded is paneOpen is true
    let adminOptions = null;
    if(this.state.userRole==='admin'){
      adminOptions = (
        <div className='menu-content panel-nav-options'>
          <h3>Admin</h3><hr/>
          <Link to="/manage-users">Manage Users</Link>
        </div>
      )
    }

    // Checks which page the user has access to
    let goodModules = [];
    for(let module of this.state.modules){
      if(module in MODULES){
        goodModules.push(module);
      }
    }

    // Creates a link for each page a user can access
    let pages = [(
      <div className='menu-content'>
        <Link to="/">Home</Link><br/>
      </div>
    )];
    for(let module of goodModules){
      pages.push(
        <div className='menu-content'>
          <Link to={MODULES[module].link}>
            {MODULES[module].title}
          </Link>
        </div>
      )
    }
    let availablePages = (
      <div className="menu-content panel-nav-options">
        <h3>Pages</h3><hr/>
        {pages}
      </div>
    )
    
    if(this.props.history.location.pathname==='/login'){
      return null
    } else {
      return (
        <div ref={ref => this.el = ref}>
          <SlidingPane
            width='300px'
            isOpen={ this.state.paneOpen }
            from='left'
            onRequestClose={this.toggleMenu}
          >
            {availablePages}
            <div className="menu-content panel-nav-options">
              <h3>Actions</h3><hr/>
              <Link to="/login" onClick={()=>this.logout()}>
                Sign Out
              </Link><br/>
              <Link to="/change-password">Change Password</Link><br/>
            </div>
            {adminOptions}
          </SlidingPane>
        </div>
      );
    }
  }

  toggleMenu = (event) => {
    // Switches the menu from open to close or close to open
    event.preventDefault();
    const currentState = this.state.paneOpen;
    this.setState({paneOpen: !currentState})
  }

  logout = () => {
    // Clears browser storage and redirects to the sign-in page
    clearStorage();
    this.setState({paneOpen: false})
  }

  navigateHome = (event) => {
    event.preventDefault();
    this.props.history.push('/');
  }
  
  render() {
    let menu = this.renderMenu();
      return (
        <div className="Header">
          {menu}
          <Navbar fluid>
            <Navbar.Header>
              <Navbar.Brand>
                <a 
                  href=""
                  className='pull-left'>
                    <img
                      className="header-star"
                      src="./shirconnect_logo_white.svg"
                      height="40px"
                      alt=""
                      onClick={this.toggleMenu}
                    />
                    <b onClick={this.navigateHome}>Shir Connect</b>
                </a>
              </Navbar.Brand>
            </Navbar.Header>
          </Navbar>
        </div>
      );
    }
}

export default withRouter(Header);
