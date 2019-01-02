// Header component for the app
// The header is persistent in all views
import React, { Component } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Navbar } from 'react-bootstrap';
import SlidingPane from 'react-sliding-pane';
import Modal from 'react-modal';

import { clearToken } from './../../utilities/authentication';

import './Header.css';

class Header extends Component {
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
    if(this.props.history.location.pathname==='/login'){
      return null
    } else {
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
