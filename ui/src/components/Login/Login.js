// Renders the component for the Login screen
import React, { Component } from 'react';
import { 
  Button, 
  ControlLabel, 
  Form, 
  FormControl, 
  FormGroup 
} from 'react-bootstrap';
import { Field, reduxForm } from 'redux-form';

import './Login.css';


class Login extends Component {
    render() {
      const userName = () => {
        return(
          <div>
            <ControlLabel>User Name</ControlLabel>
            <FormControl type="text"></FormControl>
          </div>

        )
      }

      const password = () => {
        return(
          <div>
            <ControlLabel>Password</ControlLabel>
            <FormControl type="text"></FormControl>
          </div>
        )
      }

      return (
        <div className="Login pullLeft">
          <h2>Login</h2>
          <Form horizontal>
            <FormGroup className="pullLeft">
              <Field
                name="userName"
                type="text"
                component={userName}
              />
            </FormGroup>
            <FormGroup>
              <Field
                name="password"
                type="text"
                component={password}
              />
            </FormGroup>
            <Button className="login-button"  bsStyle="primary">Submit</Button>
          </Form>
        </div>
      );
    }
}

export default reduxForm({form: 'login'})(Login);
