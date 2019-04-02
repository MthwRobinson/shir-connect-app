// Renders the component for the Report screen
import axios from 'axios';
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';

import { refreshAccessToken } from './../../utilities/authentication';
import Header from './../Header/Header';

import './Report.css';

class Report extends Component {
  state = {
    loading: true
  }
  
  componentDidMount(){
    // Checks to make sure the user has access to the 
    // trends access group
    const url = '/service/trends/authorize';
    axios.get(url)
      .then(res => {
        // Refresh the token to keep the session active
        refreshAccessToken();
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        } else if(err.response.status===403){
          this.props.history.push('/forbidden');
        }
      })
  }

  render() {
    return (
      <div>
        <Header />
        <div className="Report">
          <div className='events-header'>
            <h2>Report
              <i
                className="fa fa-times pull-right event-icons"
                onClick={()=>this.props.history.push('/')}
              />
            </h2><hr/>
          </div>
          <AgeGroupAttendance />
        </div>
      </div>
    );
  }
}

export default withRouter(Report);

