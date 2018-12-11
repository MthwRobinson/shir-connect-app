// Renders the component for the Trends screen
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import AgeGroupAttendance from './../AgeGroupAttendance/AgeGroupAttendance';

import './Trends.css';

class Trends extends Component {
  state = {
    loading: true
  }
  
  componentDidMount(){
      // Pulls the users name and redirects to the Login
      // page if authentication is required
      const token = localStorage.getItem('trsToken');
      if(!token){
        this.navigate('/login');
      } else {
        const auth = 'Bearer '.concat(token);
        axios.get('/service/test', { headers: { Authorization: auth }})
          .then(res => {
            this.setState({name: res.data.name});
          })
          .catch( err => {
            if(err.response.status===401){
              this.navigate('/login');
            }
          })
      }
    }

    render() {
      return (
        <div className="Trends">
          <div className='events-header'>
            <h2>Age Group Trends
              <i
                className="fa fa-times pull-right event-icons"
                onClick={()=>this.props.history.push('/')}
              />
            </h2><hr/>
          </div>
          <AgeGroupAttendance />
        </div>
      );
    }
}

export default withRouter(Trends);

