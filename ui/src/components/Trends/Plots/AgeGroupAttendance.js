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
    loading: true,
    groupBy: 'Month',
    ageGroup: 'Young Professional'
  }

  componentDidMount(){
    this.getRevenue();
  }

  getRevenue = () => {
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    const group = this.state.groupBy.toLowerCase();
    let url = '/service/trends/age-group-attendance';
    url += '?groupBy=' + group;
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        let key = this.state.ageGroup;
        let data = [];
        let x = res.data[key]['group'];
        let y = res.data[key]['count'];
        data.push({
          x: x,
          y: y,
          type: 'bar',
          color: '#0038b8'
        })
        
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
      const group = this.state.groupBy;
      const ageGroup = this.state.ageGroup;
      return (
        <div className='plot-area' id="plot-container">
          <Plot
            data={this.state.data}
            layout={ {
              width: width,
              height: Math.max(300, width/2.6),
              title: ageGroup + ' Attendees By ' + group,
              titlefont: {family: 'Source Sans Pro'},
              yaxis: {
                title: 'Unique Attendees',
                titlefont: {family: 'Source Sans Pro'}
              },
              xaxis: {
                title: group,
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
