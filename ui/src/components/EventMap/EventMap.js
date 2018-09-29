// Renders the component for the EventMap screen
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import './EventMap.css';

class EventMap extends Component {
    render() {
      return (
        <div className="EventMap">
          <h1>Welcome to EventMap!</h1>
        </div>
      );
    }
}

export default withRouter(EventMap);
