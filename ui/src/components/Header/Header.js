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
                    <img
                      className="header-star"
                      src="./Star_of_David.svg"
                      height="40px"
                      alt=""
                    />
                    <b>TRS Dashboard</b>
                </a>
              </Navbar.Brand>
            </Navbar.Header>
          </Navbar>
        </div>
      );
    }
}

export default Header;
