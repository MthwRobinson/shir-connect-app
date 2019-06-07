// Renders the component for the ServerError screen
// On login, the component will retrieve a JWT
//  from the server and store it in local storage
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import Header from './../Header/Header';

import './ErrorPage.css';

class ServerError extends Component {
    render() {
      return (
        <div>
          <Header />
          <div className="ErrorPage">
            <h1>
              <u>500: ServerError</u>
            </h1>
            <h4>An error has occurred.</h4>
            <h4>Please contact your system administrator.</h4>
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

export default withRouter(ServerError);
