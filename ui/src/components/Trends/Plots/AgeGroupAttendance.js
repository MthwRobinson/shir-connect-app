// Renders the monthly revenue component
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import Plot from 'react-plotly.js';

import Loading from './../../Loading/Loading';

class AgeGroupAttendance extends Component {
  // Class displaying the monthly revenue plot
  state = {
    data: [],
    loading: true
  }

  componentDidMount(){
    this.getRevenue();
  }

  getRevenue = () => {
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    let url = '/service/trends/age-group-attendance';
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        let data = [];
        for(let key in res.data){
          let x = res.data[key]['year'];
          let y = res.data[key]['count'];
          data.push({
            x: x,
            y: y,
            type: 'scatter',
            mode: 'lines+points',
            name: key
          })
        }
        
        this.setState({
          data: data,
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
            data={this.state.data}
            layout={ {
              width: width,
              height: Math.max(300, width/2.6),
              title: 'Attendees By Age Group',
              titlefont: {family: 'Source Sans Pro'},
              yaxis: {
                title: 'Unique Attendees',
                titlefont: {family: 'Source Sans Pro'}
              },
              xaxis: {
                title: 'Year',
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

export default withRouter(AgeGroupAttendance);
