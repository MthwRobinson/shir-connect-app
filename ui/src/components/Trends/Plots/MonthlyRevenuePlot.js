// Renders the monthly revenue component
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import Plot from 'react-plotly.js';

import Loading from './../../Loading/Loading';

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
              type: 'scatter',
              mode: 'lines+points',
              marker: {color: '#0038b8'},
            }]}
            layout={ {
              width: width,
              height: Math.max(300, width/2.6),
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

export default withRouter(MonthlyRevenuePlot);
