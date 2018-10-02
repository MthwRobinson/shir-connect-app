// Renders the component for the Loading screen
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import './Loading.css';

class Loading extends Component {
    render() {
      return (
        <div className="Loading">
          <img
            className="loading-start"
            src="./Star_of_David_Blue.svg"
            height="40px"
            alt=""
            id="loading"
          />
        </div>
      );
    }
}

export default withRouter(Loading);
