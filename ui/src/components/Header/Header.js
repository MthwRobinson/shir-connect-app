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

class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      paneOpen: false,
      userRole: 'standard'
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
          const userRole = res.data.role;
          this.setState({userRole: userRole})
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login');
          } else if(err.response.status===403){
            this.props.history.push('/forbidden');
          }
        })
    }
  }

  renderMenu = () => {
    // Builds the popout menu.
    // Menu is expanded is paneOpen is true
    let adminOptions = null;
    if(this.state.userRole==='admin'){
      adminOptions = <Link to="/manage-users">Manage Users</Link>
    }
    
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
            <div className="menu-content">
              <h3>Admin</h3><hr/>
              <Link to="/">Home</Link><br/>
              <Link to="/login" onClick={()=>this.logout()}>Sign Out</Link><br/>
              <Link to="/change-password">Change Password</Link><br/>
              {adminOptions}
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
