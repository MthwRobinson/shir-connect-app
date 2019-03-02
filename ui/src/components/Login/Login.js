// Renders the component for the Login screen
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
import { withRouter } from 'react-router-dom';

import { logout } from './../../utilities/authentication';
import Header from './../Header/Header';

import './Login.css';

class Login extends Component {
    constructor(props){
      super(props);
      this.state = {
        userName: '',
        password: '',
        authenticated: false,
        attempted: false
      }

      // Bindings for the login form
      this.handleUserName = this.handleUserName.bind(this);
      this.handlePassword = this.handlePassword.bind(this);

    }

    componentDidMount(){
      // Clear any information from local storage
      logout();
    }

    handleSubmit = (event) => {
      // Prevents the app from refreshing on submit
      event.preventDefault();
      axios.post('/service/user/authenticate', {
        username: this.state.userName, 
        password: this.state.password
      })
        .then(res => {
          this.setState({authenticated: true});
          this.props.history.push('/')
        })
        .catch(err => {
          this.setState({attempted: true});
        })
    }

    handleUserName(event) {
      // Updates the user name in the state
      this.setState({userName: event.target.value});
    }

    handlePassword(event) {
      // Updates the pasword in the state
      this.setState({password: event.target.value});
    }

    renderError = () => {
      // Displays an error message if authentication is not successful
      if(this.state.attempted && !this.state.authenticated){
        return(
          <div className='error-msg'>
            <p className='error-msg'>
              User name or password is incorrect.
            </p>
          </div>
        );
      } else {
        return null;
      }
    }

    render() {
      let errorMsg = this.renderError();
      return (
        <div>
          <Header />
          <div className="Login pullLeft">
            <h2>Login</h2>
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
                <ControlLabel>Password</ControlLabel>
                <FormControl
                  value={this.state.password}
                  onChange={this.handlePassword}
                  type="password" 
                />
              </FormGroup>
              {errorMsg}
              <Button 
                className="login-button"  
                bsStyle="primary" 
                type="submit"
              >Submit</Button>
            </Form>
          </div>
        </div>
      );
    }
}

export default withRouter(Login);
