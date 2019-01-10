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

import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './ManageUsers.css';

class ManageUsers extends Component {
    constructor(props){
      super(props);
      this.state = {
        users: [],
        loading: true,
        addModalOpen: true,
        username: '',
        password: '',
        role: 'standard',
        events: false,
        members: false,
        trends: false,
        map: false
      }
    }
  
    componentDidMount(){
      // Pulls the users name and redirects to the Login
      this.getUsers();

      // Bindings for the new user form
      this.handleAddSubmit = this.handleAddSubmit.bind(this);
      this.handleUsername = this.handleUsername.bind(this);
      this.handlePassword = this.handlePassword.bind(this);
      this.handleRole = this.handleRole.bind(this);
      this.handleEvents = this.handleEvents.bind(this);
      this.handleMembers = this.handleMembers.bind(this);
      this.handleTrends = this.handleTrends.bind(this);
      this.handleMap = this.handleMap.bind(this);
    }
  
    getUsers = () => {
      // Pulls a list of users from the database
      this.setState({loading: true});
      const token = localStorage.getItem('trsToken');
      if(!token){
        this.this.history.push('/login');
      } else {
        const auth = 'Bearer '.concat(token);
        axios.get('/service/users/list', { headers: { Authorization: auth }})
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
    }

    addUser = () => {
      // Posts a new user to the database
      this.setState({loading: true});
      const token = localStorage.getItem('trsToken');
      if(!token){
        this.this.history.push('/login');
      } else {
        const auth = 'Bearer '.concat(token);
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
          password: this.state.password,
          role: this.state.role,
          modules: modules
        } 

        axios.post('/service/user',
          data,
          {headers: { Authorization: auth }})
          .then(res => {
            this.getUsers();
            this.setState({
              addModalOpen: false,
              username: '',
              password: '',
              role: this.state.role,
              module: this.state.modules
            })
          })
          .catch( err => {
            if(err.response.status===401){
              this.navigate('/login');
            } else if(err.response.status===403){
              this.navigate('/forbidden');
            }
          })
      }

    }

    //------------------
    // ADD USER MODAL
    //-------------------
    handleUsername(event){
      // Updates the username in the state
      this.setState({ username: event.target.value });
    }

    handlePassword(event){
      // Updates the password in the state
      this.setState({ password: event.target.value });
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
      this.setState({ addModalOpen: false });
      console.log(this.state);
    }

    renderOpenModal = () => {
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
                <FormGroup className='pullLeft'>
                  <ControlLabel>Password</ControlLabel>
                  <FormControl
                    value={this.state.password}
                    onChange={this.handlePassword}
                    type="password"
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
                <FormGroup>
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

    renderTable = () => {
      // Renders the table of current users
      let users = [];
      for(const user of this.state.users){
        const modules = user.modules.join(', ');
        const userRow = (
          <tr className='table-rows'>
            <th>{user.id}</th>
            <th className='user-management-rows'>{user.role}</th>
            <th className='user-management-rows'>{modules}</th>
            <th><i className='fa fa-times pull-right event-icons'></i></th>
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
        </div>
      )
    }

  render() {
      const addWindow = this.renderOpenModal();
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
          <ReactToolTip />
        </div>
      );
    }
}

export default withRouter(ManageUsers);
