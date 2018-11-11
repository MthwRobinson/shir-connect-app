// Renders the component for the Trends screen
import React, { Component } from 'react';
import { Row, Table } from 'react-bootstrap';
import { withRouter } from 'react-router-dom';
import axios from 'axios';

import AgeGroupAttendance from './Plots/AgeGroupAttendance';
import AverageAttendancePlot from './Plots/AverageAttendancePlot';
import MonthlyRevenuePlot from './Plots/MonthlyRevenuePlot';

import './Trends.css';

class Trends extends Component {
  state = {
    page: 'home',
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

    renderTable = () => {
      // Creates the table that displays the analytics
      // options
      return(
        <div>
          <Row className='trends-table'>
            <Table response header hover>
              <thead>
                <tr>
                  <th>Chart Name</th>
                  <th>Chart Description</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  className='table-row'
                  onClick={()=>this.setState({page:'monthly-revenue'})}
                >
                  <td>Monthly Revenue</td>
                  <td>Shows total revenue from all events aggregated by month.</td>
                </tr>
                <tr 
                  className='table-row'
                  onClick={()=>this.setState({page:'avg-attendance'})}
                >
                  <td>Average Attendance</td>
                  <td>Finds the average attendance for events broken down by day of week, excluding events with zero attendance.</td>
                </tr>
                <tr 
                  className='table-row'
                  onClick={()=>this.setState({page:'age-group-attendance'})}
                >
                  <td>Age Group Participation</td>
                  <td>Counts the number of unique participants in each age group during each year.</td>
                </tr>
              </tbody>
            </Table>
          </Row>

        </div>
      )
    }

    onBack = () => {
      // Goes back to the main page if the table is
      // present and back to the table if a plot
      // is displayed
      if(this.state.page==='home'){
        this.props.history.push('/');
      } else {
        this.setState({page: 'home'});
      }
    }

    render() {
      let backButton = null
      if(this.state.page==='home'){
        backButton = 'fa fa-times ';
      } else {
        backButton = 'fa fa-chevron-left ';
      }
      backButton += 'pull-right event-icons'

      let body = null
      if(this.state.page==='home'){
        body = this.renderTable();
      } else if(this.state.page==='monthly-revenue'){
        body = <MonthlyRevenuePlot />
      } else if(this.state.page==='avg-attendance'){
        body = <AverageAttendancePlot />
      } else if(this.state.page==='age-group-attendance'){
        body = <AgeGroupAttendance />
      }

      return (
        <div className="Trends">
          <div className='events-header'>
            <h2>Event Trends
              <i
                className={backButton}
                onClick={()=>this.onBack()}
              />
            </h2><hr/>
          </div>
          {body}
        </div>
      );
    }
}

export default withRouter(Trends);

