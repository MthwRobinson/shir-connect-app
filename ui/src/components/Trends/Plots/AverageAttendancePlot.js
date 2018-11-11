// Reners the average attendance component
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import Plot from 'react-plotly.js';

import Loading from './../../Loading/Loading';

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
        <div className='event-loading' id="plot-container">
          <Loading />
        </div>
      )
    } else {
      const width = document.getElementById('plot-container').clientWidth;
      return (
        <div className='plot-area' id="plot-container">
          <Plot
            data={[{
              x: this.state.x,
              y: this.state.y,
              type: 'bar',
              marker: {color: '#0038b8'},
            }]}
            layout={ {
              width: width,
              height: Math.max(300, width/2.6),
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

export default withRouter(AverageAttendancePlot);
