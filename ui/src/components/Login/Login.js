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
        password: ''
      }

      // Bindings for the login form
      this.handleUserName = this.handleUserName.bind(this);
      this.handlePassword = this.handlePassword.bind(this);

    }

    submit = (event) => {
      // axios.post('/service/user/authenticate', {
      //   username: values.userName, 
      //   password: values.password
      // }).then(res => console.log(res.data))
      console.log(this.state);
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

    render() {
      return (
        <div className="Login pullLeft">
          <h2>Login</h2>
          <Form onSubmit={this.submit} horizontal >
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
                type="text" 
              />
            </FormGroup>
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
