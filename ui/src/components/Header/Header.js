import React, { Component } from 'react';
import { Navbar } from 'react-bootstrap';

import './Header.css';

class Header extends Component {
    render() {
      return (
        <div className="Header">
          <Navbar fluid>
            <Navbar.Header>
              <Navbar.Brand>
                <a 
                  href="#home"
                  className='pull-left'>
                    TRS Dashboard
                </a>
              </Navbar.Brand>
            <Navbar.Form className='pull-right menu-icon'>
              <i className="fa fa-bars" onClick={this.props.clickMenu}></i>
            </Navbar.Form>
            </Navbar.Header>
          </Navbar>
        </div>
      );
    }
}

export default Header;
