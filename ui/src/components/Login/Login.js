// Renders the component for the Login screen
// On login, the component will retrieve a JWT
//  from the server and store it in local storage
import React, { Component } from 'react';
import { 
  Button, 
  ControlLabel, 
  Form, 
  FormControl, 
  FormGroup 
} from 'react-bootstrap';
import axios from 'axios';

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

    handleSubmit = (event) => {
      // Authenticates with the service and stores the JWT
      // in local storage if authentication is successful
      axios.post('/service/user/authenticate', {
        username: this.state.userName, 
        password: this.state.password
      })
        .then(res => {
          localStorage.setItem('trsToken', res.data.jwt);
          this.setState({authenticated: true});
        })
        .catch(err => {
          this.setState({attempted: true});
        })
      // Prevents the app from refreshing on submit
      event.preventDefault();
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
      );
    }
}

export default Login;
