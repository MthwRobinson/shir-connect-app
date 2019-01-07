// Renders the component for the ChangePassword screen
import React, { Component } from 'react';
import { 
  Button, 
  ControlLabel, 
  Form, 
  FormControl, 
  FormGroup 
} from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import Header from './../Header/Header';

import './ChangePassword.css';

class ChangePassword extends Component {
    constructor(props){
      super(props);
      this.state = {
        oldPassword: '',
        newPassword: '',
        newPassword2: '',
        attempted: false,
        mismatch: false,
        updated: false,
        tooShort: false
      }

      // Bindings for the change password form
      this.handleOldPassword = this.handleOldPassword.bind(this);
      this.handleNewPassword = this.handleNewPassword.bind(this);
      this.handleNewPassword2 = this.handleNewPassword2.bind(this);

    }
  
    componentDidMount(){
      // Pulls the users name and redirects to the Login
      // page if authentication is required
      const token = localStorage.getItem('trsToken');
      if(!token){
        this.this.history.push('/login');
      } else {
        const auth = 'Bearer '.concat(token);
        axios.get('/service/user/authorize', { headers: { Authorization: auth }})
          .then(res => {
            this.setState({
              name: res.data.id,
              loading: false
            });
          })
          .catch( err => {
            if(err.response.status===401){
              this.navigate('/login');
            }
          })
      }
    }

    handleSubmit = (event) => {
      // Authenticates with the service and stores the JWT
      // in local storage if authentication is successful
      this.setState({updated: false, mismatch: false, attempted: false});
      const token = localStorage.getItem('trsToken');
      const auth = 'Bearer '.concat(token);
      axios.post('/service/user/change-password', 
        {
          old_password: this.state.oldPassword, 
          new_password: this.state.newPassword,
          new_password2: this.state.newPassword2
        },
        {headers: { Authorization: auth }}
      )
        .then(res => {
          this.setState({
            updated: true, 
            attempted: true,
            oldPassword: '',
            newPassword: '',
            newPassword2: ''
          });
        })
        .catch(err => {
          if(err.response.status===401){
            this.props.history.push('/login')
          } else {
            this.setState({attempted: true});
            if(this.state.newPassword!==this.state.newPassword2){
              this.setState({mismatch: true});
            }
          }
        })
      // Prevents the app from refreshing on submit
      event.preventDefault();
    }

    handleOldPassword(event) {
      // Updates the old password in the state
      this.setState({oldPassword: event.target.value});
    }
  
    handleNewPassword(event) {
      // Updates the new password in the state
      this.setState({newPassword: event.target.value});
    }
  
    handleNewPassword2(event) {
      // Updates the second new password in the state
      this.setState({newPassword2: event.target.value});
    }

    renderMessage = () => {
      // Displays the outcome of the password update
      if(this.state.attempted){
        if(this.state.mismatch&&!this.state.updated){
          return(
            <div className='error-msg'>
              <p className='error-msg'>
                Updated passwords did not match.
              </p>
            </div>
          );
        } else if(this.state.updated) {
          return(
            <div className='success-msg'>
              <p className='success-msg'>
                Password updated.
              </p>
            </div>
          );
        } else {
          return(
            <div className='error-msg'>
              <p className='error-msg'>
                Password update failed. Please Ensure:
                  <ol>
                    <li>Your old password is correct.</li>
                    <li>Your new password has at least 10 characters,
                      is not all upper case,
                      is not all lswer case,
                      and has at least one special character.</li>
                  </ol>
              </p>
            </div>
          );
        }
      } else {
        return null;
      }
    }

    render() {
      let msg = this.renderMessage();
      return (
        <div>
          <Header />
          <div className="ChangePassword pullLeft">
            <h3>Change Password</h3>
            <Form onSubmit={this.handleSubmit} horizontal >
              <FormGroup className="pullLeft">
                <ControlLabel>Old Password</ControlLabel>
                <FormControl
                  value={this.state.oldPassword}
                  onChange={this.handleOldPassword}
                  type="password" 
                />
              </FormGroup>
              <FormGroup>
                <ControlLabel>New Password</ControlLabel>
                <FormControl
                  value={this.state.newPassword}
                  onChange={this.handleNewPassword}
                  type="password" 
                />
              </FormGroup>
              <FormGroup>
                <ControlLabel>Repeat New Password</ControlLabel>
                <FormControl
                  value={this.state.newPassword2}
                  onChange={this.handleNewPassword2}
                  type="password" 
                />
              </FormGroup>
              {msg}
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

export default withRouter(ChangePassword);