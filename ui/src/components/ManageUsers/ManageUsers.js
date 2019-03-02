// Renders the component for the ManageUsers screen
import axios from 'axios';
import React, { Component } from 'react';
import { 
  Button,
  Checkbox,
  ControlLabel,
  Form,
  FormControl,
  FormGroup,
  Row,
  Table
} from 'react-bootstrap';
import ReactToolTip from 'react-tooltip';
import Modal from 'react-responsive-modal';
import { withRouter } from 'react-router-dom';

import { 
  getCSRFToken,
  refreshAccessToken
} from './../../utilities/authentication';
import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './ManageUsers.css';

class ManageUsers extends Component {
    constructor(props){
      super(props);
      this.state = {
        users: [],
        loading: true,
        addModalOpen: false,
        addUserError: false,
        username: '',
        password: '',
        role: 'standard',
        events: false,
        members: false,
        trends: false,
        map: false,
        deleteModalOpen: false,
        deleteUsername: '',
        modRole: 'standard',
        modEvents: false,
        modMembers: false,
        modTrends: false,
        modMap: false,
        modUsername: '',
        resetUsername: '',
        resetPassword: '',
        resetModalOpen: false
      }
    }
  
    componentDidMount(){
      // Pulls the users name
      this.getUsers();

      // Refreshes the token to keep the session active
      refreshAccessToken();

      // Bindings for the new user form
      this.handleAddSubmit = this.handleAddSubmit.bind(this);
      this.handleUsername = this.handleUsername.bind(this);
      this.handleRole = this.handleRole.bind(this);
      this.handleEvents = this.handleEvents.bind(this);
      this.handleMembers = this.handleMembers.bind(this);
      this.handleTrends = this.handleTrends.bind(this);
      this.handleMap = this.handleMap.bind(this);

      // Bindings for the modify user form
      this.handleModSubmit = this.handleModSubmit.bind(this);
      this.handleModRole = this.handleModRole.bind(this);
      this.handleModEvents = this.handleModEvents.bind(this);
      this.handleModMembers = this.handleModMembers.bind(this);
      this.handleModTrends = this.handleModTrends.bind(this);
      this.handleModMap = this.handleModMap.bind(this);

      // Bindings for reset password form

    }
  
    //------------------
    // SERVICE CALLS
    //-------------------
  
    getUsers = () => {
      // Pulls a list of users from the database
      this.setState({loading: true});
      axios.get('/service/users/list')
        .then(res => {
          this.setState({
            users: res.data,
            loading: false
          });
        })
        .catch( err => {
          if(err.response.status===401){
            this.navigate('/login');
          } else if(err.response.status===403){
            this.navigate('/forbidden');
          }
        })
    }

    addUser = () => {
      // Posts a new user to the database
      this.setState({
        loading: true,
        addUserError: false
      });
      const csrfToken = getCSRFToken();
      // Build the post body
      let modules = [];
      if(this.state.events){
        modules.push('events');
      }
      if(this.state.members){
        modules.push('members');
      }
      if(this.state.trends){
        modules.push('trends');
      }
      if(this.state.map){
        modules.push('map');
      }
      const data = {
        username: this.state.username,
        role: this.state.role,
        modules: modules
      } 

      axios.post('/service/user', data, {headers: {'X-CSRF-TOKEN': csrfToken}})
        .then(res => {
          this.getUsers();
          this.setState({password: res.data.password})
        })
        .catch( err => {
          if(err.response.status===401){
            this.navigate('/login');
          } else if(err.response.status===400){
            this.getUsers();
            this.setState({addUserError: true})
          }
        })
    }

    deleteUser = () => {
      // Deletes the selected user
      this.setState({loading: true});
      const csrfToken = getCSRFToken();
      this.setState({deleteModalOpen: false});
      const url = '/service/user/' + this.state.deleteUsername;
      axios.delete(url, {headers:{'X-CSRF-TOKEN': csrfToken}})
        .then(res => {
          this.getUsers();
          this.setState({ deleteUsername: '' });
        })
        .catch( err => {
          if(err.response.status===401){
            this.navigate('/login');
          }
        })
    }
  
    modifyUser = () => {
      // Posts updated user roles and modules
      this.setState({loading: true});
      const csrfToken = getCSRFToken();
      this.closeModWindow();
      // Build the post body
      let modules = [];
      if(this.state.modEvents){
        modules.push('events');
      }
      if(this.state.modMembers){
        modules.push('members');
      }
      if(this.state.modTrends){
        modules.push('trends');
      }
      if(this.state.modMap){
        modules.push('map');
      }
      const data = {
        username: this.state.modUsername,
        modules: modules
      } 

      // Update the access for the user
      const updateAccess = axios.post('/service/user/update-access',
        data,
        {headers: {'X-CSRF-TOKEN': csrfToken}})
        .catch( err => {
          if(err.response.status===401){
            this.navigate('/login');
          }
        })

      // Update the role for the user
      const roleData = {
        username: this.state.modUsername,
        role: this.state.modRole
      }
      const updateRole = axios.post('/service/user/update-role',
        roleData,
        {headers: {'X-CSRF-TOKEN': csrfToken}})
        .catch( err => {
          if(err.response.status===401){
            this.navigate('/login');
          }
        })

      // Update the users in the table
      Promise.all([updateAccess, updateRole])
        .then(() => {
          this.getUsers();
        })
    }
  
    resetPassword = () => {
      // Resets a user's password
      const csrfToken = getCSRFToken();
      // Build the post body
      const data = {username: this.state.resetUsername} 
      // Update the password for the user
      axios.post('/service/user/reset-password',
        data,
        {headers: {'X-CSRF-TOKEN': csrfToken}})
        .then( res => {
          this.setState({resetPassword: res.data.password})
        })
        .catch( err => {
          if(err.response.status===401){
            this.navigate('/login');
          }
        })
    }

    //------------------
    // ADD USER MODAL
    //-------------------
    handleUsername(event){
      // Updates the username in the state
      this.setState({ username: event.target.value });
    }
  
    handleRole(event){
      // Updates the role in the state
      this.setState({ role: event.target.value });
    }

    handleEvents(event){
      // Updates the events checkbox
      this.setState({ events: event.target.checked });
    }

    handleMembers(event){
      // Updates the members checkbox
      this.setState({ members: event.target.checked});
    }

    handleTrends(event){
      // Updates the trends checkbox
      this.setState({ trends: event.target.checked });
    }

    handleMap(event){
      // Updates the map checkbox
      this.setState({ map: event.target.checked });
    }

    handleAddSubmit(event){
      // Posts the new user to the database
      event.preventDefault();
      this.addUser();
    }

    openAddWindow = () => {
      // Opens the add modal window
      this.setState({ addModalOpen: true });
    }

    closeAddWindow = () => {
      // Closes the modal window
      this.setState({
        addUserError: false,
        addModalOpen: false,
        username: '',
        password: '',
        role: '',
        events: false,
        members: false,
        trends: false,
        map: false
      });
    }

    renderAddModal = () => {
      let msg = null;
      let done = null;
      if(this.state.password&&!this.state.addUserError){
        msg = (
            <p className='success-msg'>
              Success! User password is:<br/>
              {'\n'}<b>{this.state.password}</b>
            </p>
        )
        done = (
          <Button
            className='login-button'
            bsStyle='primary'
            onClick={()=>this.closeAddWindow()}
          >Done</Button>
        )
      } else if(this.state.addUserError){
        msg = (
            <p className='error-msg'>
              Error! User may already exist.
            </p>
        )
      }
      // The modal that pops up to add a new user
      return(
        <div>
          <Modal 
            open={this.state.addModalOpen}
            showCloseIcon={false}
            center
          >
            <div className="add-user-container">
              <h3><u>
                New User
                <i 
                  className='fa fa-times pull-right event-icons'
                  onClick={()=>this.closeAddWindow()}
                ></i>
              </u></h3>
              <Form onSubmit={this.handleAddSubmit} horizontal>
                <FormGroup className='pullLeft'>
                  <ControlLabel>User Name</ControlLabel>
                  <FormControl
                    value={this.state.username}
                    onChange={this.handleUsername}
                    type="text"
                  />
                </FormGroup>
                <FormGroup>
                  <ControlLabel>Role</ControlLabel>
                  <FormControl 
                    componentClass="select"
                    value={this.state.role}
                    onChange={this.handleRole}
                  >
                    <option value="standard">Standard</option>
                    <option value="admin">Admin</option>
                  </FormControl>
                </FormGroup>
                <FormGroup className='bottom-user-form'>
                  <ControlLabel>Modules</ControlLabel><br/>
                  <Checkbox
                    checked={this.state.events}
                    onChange={this.handleEvents}
                    className='form-check-box' inline>
                    {' '}Events
                  </Checkbox>
                  <Checkbox 
                    checked={this.state.members}
                    onChange={this.handleMembers}
                  className='form-check-box' inline>
                    {' '}Members
                  </Checkbox><br/>
                  <Checkbox 
                    checked={this.state.trends}
                    onChange={this.handleTrends}
                    className='form-check-box' 
                  inline>
                    {' '}Trends
                  </Checkbox>
                  <Checkbox 
                    checked={this.state.map}
                    onChange={this.handleMap}
                    className='form-check-box' 
                  inline>
                    {' '}Map
                  </Checkbox>
                </FormGroup>
                {msg}
                <Button
                  className='login-button add-user-button'
                  bsStyle='primary'
                  type='submit'
                >Submit</Button>
                {done}
              </Form>
            </div>
          </Modal>
        </div>
      )
    }

    //------------------
    // DELETE USER MODAL
    //-------------------
    
    deleteClick = (username) => {
      // Click handler for the x in the table
      this.setState({
        deleteModalOpen: true,
        deleteUsername: username
      })
    }
  
    openDeleteWindow = () => {
      // Opens the delete modal window
      this.setState({ deleteModalOpen: true });
    }

    closeDeleteWindow = () => {
      // Closes the delete modal window
      this.setState({ deleteModalOpen: false });
    }

    renderDeleteModal = () => {
      // The modal that pops up to add a new user
      return(
        <div>
          <Modal 
            open={this.state.deleteModalOpen}
            showCloseIcon={false}
            center
          >
            <div className="add-user-container">
              <h3><u>
                Delete User
                <i 
                  className='fa fa-times pull-right event-icons'
                  onClick={()=>this.closeDeleteWindow()}
                ></i>
              </u></h3>
              <h4>
                Are you sure you want to remove 
                {' '+this.state.deleteUsername}?
              </h4>
              <Button
                className='confirm-delete-button'
                bsStyle='danger'
                onClick={()=>this.deleteUser()}
              >Confirm</Button>
            </div>
          </Modal>
        </div>
      )
    }
  
    //------------------
    // MODIFY USER MODAL
    //-------------------
    handleModUsername(event){
      // Updates the username in the state
      this.setState({ modUsername: event.target.value });
    }
  
    handleModRole(event){
      // Updates the role in the state
      this.setState({ modRole: event.target.value });
    }

    handleModEvents(event){
      // Updates the events checkbox
      this.setState({ modEvents: event.target.checked });
    }

    handleModMembers(event){
      // Updates the members checkbox
      this.setState({ modMembers: event.target.checked});
    }

    handleModTrends(event){
      // Updates the trends checkbox
      this.setState({ modTrends: event.target.checked });
    }

    handleModMap(event){
      // Updates the map checkbox
      this.setState({ modMap: event.target.checked });
    }

    handleModSubmit(event){
      // Posts user updates to the database
      event.preventDefault();
      this.modifyUser();
    }

    openModWindow = (username, role, modules) => {
      // Opens the modify user modal window
      this.setState({
        modUsername: username,
        modRole: role,
        modEvents: modules.includes('events'),
        modMembers: modules.includes('members'),
        modTrends: modules.includes('trends'),
        modMap: modules.includes('map'),
        modModalOpen: true 
      });
    }

    closeModWindow = () => {
      // Closes the modal window
      this.setState({ 
        modModalOpen: false,
        modRole: 'standard',
        modEvents: false,
        modMembers: false,
        modTrends: false,
        modMap: false,
        modUsername: ''
      });
    }

    renderModModal = () => {
      // The modal that pops up to add a new user
      return(
        <div>
          <Modal 
            open={this.state.modModalOpen}
            showCloseIcon={false}
            center
          >
            <div className="add-user-container">
              <h3><u>
                Update {this.state.modUsername}
                <i 
                  className='fa fa-times pull-right event-icons'
                  onClick={()=>this.closeModWindow()}
                ></i>
              </u></h3>
              <Form onSubmit={this.handleModSubmit} horizontal>
                <FormGroup>
                  <ControlLabel>Role</ControlLabel>
                  <FormControl 
                    componentClass="select"
                    value={this.state.modRole}
                    onChange={this.handleModRole}
                  >
                    <option value="standard">Standard</option>
                    <option value="admin">Admin</option>
                  </FormControl>
                </FormGroup>
                <FormGroup>
                  <ControlLabel>Modules</ControlLabel><br/>
                  <Checkbox
                    checked={this.state.modEvents}
                    onChange={this.handleModEvents}
                    className='form-check-box' inline>
                    {' '}Events
                  </Checkbox>
                  <Checkbox 
                    checked={this.state.modMembers}
                    onChange={this.handleModMembers}
                  className='form-check-box' inline>
                    {' '}Members
                  </Checkbox><br/>
                  <Checkbox 
                    checked={this.state.modTrends}
                    onChange={this.handleModTrends}
                    className='form-check-box' 
                  inline>
                    {' '}Trends
                  </Checkbox>
                  <Checkbox 
                    checked={this.state.modMap}
                    onChange={this.handleModMap}
                    className='form-check-box' 
                  inline>
                    {' '}Map
                  </Checkbox>
                </FormGroup>
                <Button
                  className='login-button'
                  bsStyle='primary'
                  type='submit'
                >Submit</Button>
              </Form>
            </div>
          </Modal>
        </div>
      )
    }
  
    //----------------------
    // RESET PASSWORD MODAL
    //----------------------
    
    resetClick = (username) => {
      // Click handler for the x in the table
      this.setState({
        resetModalOpen: true,
        resetUsername: username
      })
    }
  
    openResetWindow = () => {
      // Opens the delete modal window
      this.setState({ resetModalOpen: true });
    }

    closeResetWindow = () => {
      // Closes the delete modal window
      this.setState({ 
        resetModalOpen: false,
        resetUsername: '',
        resetPassword: ''
      });
    }

    renderResetModal = () => {
      // The modal that pops up to add a new user
      let msg = null;
      let done = null;
      if(this.state.resetPassword){
        msg = (
            <p className='success-msg'>
              Success! New password is:<br/>
              {'\n'}<b>{this.state.resetPassword}</b>
            </p>
        )
        done = (
          <Button
            className='confirm-delete-button login-button'
            bsStyle='primary'
            onClick={()=>this.closeResetWindow()}
          >Done</Button>
        )
      }
      return(
        <div>
          <Modal 
            open={this.state.resetModalOpen}
            showCloseIcon={false}
            center
          >
            <div className="add-user-container">
              <h3><u>
                Reset Password
                <i 
                  className='fa fa-times pull-right event-icons'
                  onClick={()=>this.closeResetWindow()}
                ></i>
              </u></h3>
              <h4>
                Reset password for 
                {' '+this.state.resetUsername}?
              </h4>
              {msg}
              <Button
                className='confirm-delete-button login-button'
                bsStyle='primary'
                onClick={()=>this.resetPassword()}
              >Confirm</Button>
              {done}
            </div>
          </Modal>
        </div>
      )
    }

    renderTable = () => {
      // Renders the table of current users
      let users = [];
      for(const user of this.state.users){
        const modules = user.modules.join(', ');
        const userRow = (
          <tr className='table-rows'>
            <th
              onClick={()=>this.openModWindow(user.id, user.role, user.modules)}
            >{user.id}</th>
            <th 
              className='user-management-rows'
              onClick={()=>this.openModWindow(user.id, user.role, user.modules)}
            >{user.role}</th>
            <th 
              className='user-management-rows'
              onClick={()=>this.openModWindow(user.id, user.role, user.modules)}
            >{modules}</th>
            <th>
              <i 
                className='fa fa-times pull-right event-icons delete-user-icon'
                onClick={()=>this.deleteClick(user.id)}
                data-tip="Delete user."
              ></i>
              <i 
                className='fa fa-key fa-flip-horizontal pull-right event-icons'
                onClick={()=>this.resetClick(user.id)}
                data-tip="Reset password."
              ></i>
            </th>
          </tr>
        )
        users.push(userRow);
      }
      
      return (
        <div>
          <Row className='event-table'>
            <Table responsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'>User</th>
                  <th className='table-heading'>Role</th>
                  <th className='table-heading'>Modules</th>
                  <th className='table-heading'></th>
                </tr>
              </thead>
              <tbody>
                {users}
              </tbody>
            </Table>
          </Row>
          <ReactToolTip />
        </div>
      )
    }

  render() {
      const addWindow = this.renderAddModal();
      const deleteWindow = this.renderDeleteModal();
      const modWindow = this.renderModModal();
      const resetWindow = this.renderResetModal();

      let table = null;
      if(this.state.loading){
        table = (
          <div className='event-loading'>
            <Loading />
          </div>
        )
      } else {
        table = this.renderTable();
      }

      return (
        <div>
          <Header />
          <div className="ManageUsers">
            <div className='home-header'>
              <h2>
                Manage Users
                <i
                  className="fa fa-home pull-right event-icons"
                  onClick={()=>this.props.history.push('/')}
                ></i>
                <i
                  className='fa fa-plus pull-right event-icons'
                  data-tip='Add a user.'
                  onClick={()=>this.openAddWindow()}
                ></i>
              </h2><hr/>
              <h4>Add, delete, and modify users.</h4>
            </div>
            {table}
          </div>
          {addWindow}
          {deleteWindow}
          {modWindow}
          {resetWindow}
          <ReactToolTip />
        </div>
      );
    }
}

export default withRouter(ManageUsers);