// Renders the component for the Trends screen
import React, { Component } from 'react';
import { Row, Table } from 'react-bootstrap';
import { Route, withRouter } from 'react-router-dom';
import axios from 'axios';
import Plot from 'react-plotly.js';

import Loading from './../Loading/Loading';

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

class MonthlyRevenuePlot extends Component {
  // Class displaying the monthly revenue plot
  state = {
    x: [],
    y: [],
    loading: true
  }

  componentDidMount(){
    this.getRevenue();
  }

  getRevenue = () => {
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    let url = '/service/trends/monthly-revenue';
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        let x = [];
        let y = [];

        for(var i=0; i<res.data.results.length; i++){
          let data = res.data.results[i];
          y.push(data.revenue);
          let month = data.mn + '/' 
          month += data.yr;
          x.push(month);
        }

        this.setState({
          x: x,
          y: y,
          loading: false
        })
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  render(){
    if(this.state.loading){
      return (
        <div className='event-loading'>
          <Loading />
        </div>
      )
    } else {
      return (
        <div className='plot-area'>
          <Plot
            data={[{
            x: this.state.x,
              y: this.state.y,
              type: 'scatter',
              mode: 'lines+points',
              marker: {color: '#0038b8'},
            }]}
            layout={ {
              width: 1200,
              height: 470,
              title: 'Event Revenue by Month',
              titlefont: {family: 'Source Sans Pro'},
              yaxis: {
                title: 'Revenue (in dollars)',
                titlefont: {family: 'Source Sans Pro'}
              },
              xaxis: {
                title: 'Month',
                titlefont: {family: 'Source Sans Pro'},
                tickangle: 45
              }
            }
            }
          />
        </div>
      )
    }
  }
}

class AverageAttendancePlot extends Component {
  // Class displaying the average attendance by day
  state = {
    x: [],
    y: [],
    loading: true
  }

  componentDidMount(){
    this.getAverageAttendance();
  }

  getAverageAttendance = () => {
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    let url = '/service/trends/avg-attendance';
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        let x = [];
        let y = [];

        for(var i=0; i<res.data.results.length; i++){
          let data = res.data.results[i];
          y.push(data.avg_attendance);
          x.push(data.day_of_week);
        }

        this.setState({
          x: x,
          y: y,
          loading: false
        })
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  render(){
    if(this.state.loading){
      return (
        <div className='event-loading'>
          <Loading />
        </div>
      )
    } else {
      return (
        <div className='plot-area'>
          <Plot
            data={[{
              x: this.state.x,
              y: this.state.y,
              type: 'bar',
              marker: {color: '#0038b8'},
            }]}
            layout={ {
              width: 1200,
              height: 470,
              title: 'Average Attendance by Day',
              titlefont: {family: 'Source Sans Pro'},
              yaxis: {
                title: 'Average Attendance',
                titlefont: {family: 'Source Sans Pro'}
              },
              xaxis: { tickangle: 45 }
            }
            }
          />
        </div>
      )
    }
  }
}
