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
    submit = (values) => {
      console.log(values);
    }

    render() {
      const { handleSubmit } = this.props
      return (
        <div className="Login pullLeft">
          <h2>Login</h2>
          <form onSubmit={ handleSubmit(this.submit) }>
            <FormGroup className="pullLeft">
              <ControlLabel>User Name</ControlLabel><br/>
              <Field
                name="userName"
                type="text"
                component="input"
              />
            </FormGroup>
            <FormGroup>
              <ControlLabel>Password</ControlLabel><br/>
              <Field
                name="password"
                type="text"
                component="input"
              />
            </FormGroup>
            <Button 
              className="login-button"  
              bsStyle="primary" 
              type="submit"
            >Submit</Button>
          </form>
        </div>
      );
    }
}

export default reduxForm({form: 'login'})(Login);
