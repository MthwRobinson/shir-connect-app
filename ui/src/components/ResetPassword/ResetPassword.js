// Renders the component for the ResetPassword screen
// On login, the component will retrieve a JWT
//  from the server and store it in local storage
import axios from 'axios';
import React, { Component } from 'react';
import {
  Button,
  ControlLabel,
  Form,
  FormControl,
  FormGroup
} from 'react-bootstrap';
import { Link, withRouter } from 'react-router-dom';

import { logout } from './../../utilities/authentication';
import Header from './../Header/Header';

import './ResetPassword.css';

class ResetPassword extends Component {
    constructor(props){
      super(props);
      this.state = {
        userName: '',
        email: '',
        attempted: false,
        success: false,
        loading: false
      }

      // Bindings for the login form
      this.handleUserName = this.handleUserName.bind(this);
      this.handleEmail = this.handleEmail.bind(this);

    }

    componentDidMount(){
      // Clear any information from local storage
      logout();
    }

    handleSubmit = (event) => {
      // Prevents the app from refreshing on submit
      event.preventDefault();
      this.setState({loading: true});
      axios.post('/service/user/user-reset-password', {
        username: this.state.userName,
        email: this.state.email
      })
        .then(res => {
          this.setState({success: true, attempted: true, loading: false});
        })
        .catch(err => {
          this.setState({success: false, attempted: true, loading: false});
        })
    }

    handleUserName(event) {
      // Updates the user name in the state
      this.setState({userName: event.target.value});
    }

    handleEmail(event) {
      // Updates the pasword in the state
      this.setState({email: event.target.value});
    }

    renderButton = () => {
      // Renders the reset button if it has not been pressed yet. Otherwise,
      // the loading icon or status message is displayed, as appropriate.
      if(this.state.loading){
        return <p>Attempting password reset ...</p>
      }
      if(!this.state.success && !this.state.loading){
        return (<Button
                className="login-button"
                bsStyle="primary"
                type="submit"
              >Submit</Button>)
      } else {
        return null
      }
    }

    renderError = () => {
      // Displays an error message if authentication is not successful
      if(this.state.attempted && !this.state.success){
        return(
          <div className='error-msg'>
            <p className='error-msg'>
              An error occurred. Please double check that e-mail you entered
              corresponds to the e-mail associated with the account.
            </p>
          </div>
        );
      } else if(this.state.attempted && this.state.success){
         return( <div className='success-msg'>
            <p className='success-msg'>
              We have sent a temporary password to the e-mail associated with your account.
              For security purposes, <b>please ensure you change your password as soon as
              you log in.</b> Click <Link to="/login">here</Link> to return to the
              login page.
            </p>
          </div>)
      } else {
        return null;
      }
    }

    render() {
      let errorMsg = this.renderError();
      let button = this.renderButton();
      return (
        <div>
          <Header />
          <div className="ResetPassword pullLeft">
            <h2>Reset Password</h2>
            <Form onSubmit={this.handleSubmit} horizontal >
              <FormGroup className="pullLeft">
                <ControlLabel>User Name</ControlLabel>
                <FormControl
                  value={this.state.userName}
                  onChange={this.handleUserName}
                  type="text"
                />
              </FormGroup>
              <FormGroup>
                <ControlLabel>E-mail</ControlLabel>
                <FormControl
                  value={this.state.email}
                  onChange={this.handleEmail}
                />
              </FormGroup>
              {errorMsg}
              {button}
            </Form>
          </div>
        </div>
      );
    }
}

export default withRouter(ResetPassword);
