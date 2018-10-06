// Renders the component for the Trends screen
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import './Trends.css';

class Trends extends Component {
    render() {
      return (
        <div className="Trends">
          <h1>Welcome to Trends!</h1>
        </div>
      );
    }
}

export default withRouter(Trends);
