// Renders the component for the Members screen
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import './Members.css';

class Members extends Component {
    render() {
      return (
        <div className="Members">
          <h1>Welcome to Members!</h1>
        </div>
      );
    }
}

export default withRouter(Members);
