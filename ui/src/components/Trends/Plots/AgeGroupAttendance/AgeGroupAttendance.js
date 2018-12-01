// Renders the monthly revenue component
import React, { Component } from 'react';
import { withRouter } from 'react-router-dom';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { 
  Button,
  Col,
  ControlLabel,
  Form,
  FormControl, 
  FormGroup, 
  Row 
} from 'react-bootstrap';

import Loading from './../../../Loading/Loading';

import './AgeGroupAttendance.css';

class AgeGroupAttendance extends Component {
  // Class displaying the monthly revenue plot
  state = {
    data: [],
    allData: [],
    loading: true,
    groupBy: 'Month',
    ageGroup: 'Young Professional',
    ageGroups: []
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
        const ageGroups = Object.keys(res.data);
        this.setState({
          allData: res.data,
          ageGroups: ageGroups,
          loading: false
        })
        this.renderPlot(this.state.ageGroup);
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  renderPlot = (ageGroup) => {
    // Renders the plot using the specified age group
    let data = []
    let x = this.state.allData[ageGroup]['group'];
    let y = this.state.allData[ageGroup]['count'];
    data.push({
      x: x,
      y: y,
      type: 'bar',
      color: '#0038b8'
    })
    this.setState({data:data});
  }

  renderDropDowns = () => {
    // Renders drop downs to choose the time period
    // and the age group
    return (
      <div>
        <Form inline>
          <FormGroup>
            <ControlLabel className="age-group-labels"
            >Age Group</ControlLabel>
            <FormControl
              componentClass="select"
              value="Young Professional"
            >
              {this.state.ageGroups.map((ageGroup, index) => {
                return(<option value={ageGroup}>{ageGroup}</option>)
              })}
            </FormControl>
            <ControlLabel className="age-group-labels"
            >Timeframe</ControlLabel>
            <FormControl
              componentClass="select"
              value="Month"
            >
              <option value='Month'>Month</option>
              <option value='Year'>Year</option>
            </FormControl>
            <Button 
              className="age-group-button"  
              type="submit"
            >Submit</Button>
          </FormGroup>
        </Form>

      </div>
    )

  }

  render(){
    if(this.state.loading){
      return (
        <div className='event-loading' id="plot-container">
          <Loading />
        </div>
      )
    } else {
      const dropdowns = this.renderDropDowns();
      const width = document.getElementById('plot-container').clientWidth;
      const group = this.state.groupBy;
      const ageGroup = this.state.ageGroup;
      return (
        <div className='plot-area' id="plot-container">
          <Row>
            {dropdowns}
          </Row>
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
