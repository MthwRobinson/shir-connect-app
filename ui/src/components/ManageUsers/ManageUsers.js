// Renders the component for the ManageUsers screen
import axios from 'axios';
import React, { Component } from 'react';
import { 
  Button,
  Row,
  Table
} from 'react-bootstrap';
import ReactToolTip from 'react-tooltip';
import { withRouter } from 'react-router-dom';

import Header from './../Header/Header';
import Loading from './../Loading/Loading';

import './ManageUsers.css';

class ManageUsers extends Component {
    constructor(props){
      super(props);
      this.state = {
        users: [],
        loading: true
      }
    }
  
    componentDidMount(){
      // Pulls the users name and redirects to the Login
      this.getUsers();
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

    renderTable = () => {
      // Renders the table of current users
      let users = [];
      for(const user of this.state.users){
        const modules = user.modules.join(', ');
        const userRow = (
          <tr className='table-row'>
            <th>{user.id}</th>
            <th>{user.role}</th>
            <th>{modules}</th>
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
                ></i>
              </h2><hr/>
              <h4>Add, delete, and modify users.</h4>
            </div>
            {table}
          </div>
          <ReactToolTip />
        </div>
      );
    }
}

export default withRouter(ManageUsers);
