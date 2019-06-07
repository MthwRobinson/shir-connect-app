// Renders the component for the Forbidden screen
// On login, the component will retrieve a JWT
//  from the server and store it in local storage
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import Header from './../Header/Header';

import './ErrorPage.css';

class Forbidden extends Component {
    render() {
      return (
        <div>
          <Header />
          <div className="ErrorPage">
            <h1>
              <u>403: Forbidden</u>
            </h1>
            <h4>You don't have access to this page.</h4>
            <h4>Please contact your system administrator.</h4>
            <h4>Click to return to the previous page.
              <i
              className="fa fa-reply return-home-icon event-icons"
              onClick={()=>this.props.history.go(-2)}
             ></i>
            </h4>
          </div>
        </div>
      );
    }
}

export default withRouter(Forbidden);
