// Header component for the app
// The header is persistent in all views
import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Navbar } from 'react-bootstrap';
import ReactToolTip from 'react-tooltip';
import SlidingPane from 'react-sliding-pane';
import Toggle from 'react-bootstrap-toggle';
import Modal from 'react-modal';
import axios from 'axios';

import { logout } from './../../utilities/authentication';

import './Header.css';

const MODULES = require('./../../data/modules.json');

class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      paneOpen: false,
      userRole: 'standard',
      modules: [],
      demoMode: false,
      initialDemo: null
    }

    this.onToggle = this.onToggle.bind(this);
  }
  
  componentDidMount() {
    // The modal element is the popout menu
    Modal.setAppElement(this.el);
    this.checkAccess();
    this.checkDemoMode();
  }

  checkAccess() {
    // Checks to make sure the role of the user
    if(this.props.history.location.pathname!=='/login'){
      const url = '/service/user/authorize';
      axios.get(url)
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

  checkDemoMode(){
    // Checks to see if the app is currently in demo mode
    const demoMode = sessionStorage.getItem('demoMode');
    if(demoMode==='true'){
      this.setState({demoMode: true, initialDemo: true});
    } else {
      this.setState({demoMode: false, initialDemo: false});
    }
  }

  onToggle () {
    // Toggles demo mode on and off and writes the results
    // to session storage for use around the app
    const demoMode = !this.state.demoMode;
    sessionStorage.setItem('demoMode', demoMode);
    this.setState({ demoMode: demoMode });
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
      let toolTip = 'Click to toggle between using real data for ';
      toolTip +=    '<br/>for live use  and fake data for demos. ';
      return (
        <div ref={ref => this.el = ref}>
          <SlidingPane
            width='300px'
            isOpen={ this.state.paneOpen }
            from='left'
            onRequestClose={this.toggleMenu}
            title={
              <div>
                <Toggle
                onClick={this.onToggle}
                on={<span className='toggle-span'>Demo</span>}
                off={<span className='toggle-span'>Live</span>}
                size="xs"
                offstyle="primary"
                onstyle="danger"
                active={this.state.demoMode}
                data-tip={toolTip}
                data-html={true}
              />
              <ReactToolTip />
              </div>
            }
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

    // If the demo mode toggle has change, refresh the page
    if(this.state.paneOpen===true){
      if(this.state.initialDemo!==null){
        if(this.state.demoMode!==this.state.initialDemo){
          window.location.reload();
        }
      }
    }
  }

  logout = () => {
    // Clears browser storage and redirects to the sign-in page
    logout();
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
                  href="/"
                  className='pull-left'>
                    <img
                      className="header-star"
                      src="./shirconnect_logo_white.png"
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
