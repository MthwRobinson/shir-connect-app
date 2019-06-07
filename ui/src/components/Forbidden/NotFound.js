// Renders the component for the NotFound screen
// On login, the component will retrieve a JWT
//  from the server and store it in local storage
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import Header from './../Header/Header';

import './ErrorPage.css';

class NotFound extends Component {
    render() {
      return (
        <div>
          <Header />
          <div className="ErrorPage">
            <h1>
              <u>404: Not Found</u>
            </h1>
            <h4>The requested page does not exist.</h4>
            <h4>Click to return to the previous page.
              <i
              className="fa fa-home return-home-icon event-icons"
              onClick={()=>this.props.history.push('/')}
             ></i>
            </h4>
          </div>
        </div>
      );
    }
}

export default withRouter(NotFound);
