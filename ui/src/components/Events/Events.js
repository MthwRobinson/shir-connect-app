// Renders the component for the Events screen
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import './Events.css';

class Events extends Component {
    render() {
      return (
        <div className="Events">
          <h1>Welcome to Events!</h1>
        </div>
      );
    }
}

export default withRouter(Events);
