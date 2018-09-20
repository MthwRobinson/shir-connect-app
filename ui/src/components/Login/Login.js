import React, { Component } from 'react';
import { 
  Button, 
  ControlLabel, 
  Form, 
  FormControl, 
  FormGroup 
} from 'react-bootstrap';

import './Login.css';

class Login extends Component {
    render() {
      return (
        <div className="Login pullLeft">
          <h2>Login</h2>
          <Form horizontal>
            <FormGroup className="pullLeft">
              <ControlLabel>User Name</ControlLabel>
              <FormControl type="text"></FormControl>
            </FormGroup>
            <FormGroup>
              <ControlLabel>Password</ControlLabel>
              <FormControl type="text"></FormControl>
            </FormGroup>
            <Button className="login-button"  bsStyle="primary">Submit</Button>
          </Form>
        </div>
      );
    }
}

export default Login;
