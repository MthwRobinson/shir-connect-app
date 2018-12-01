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
  Row,
  Table
} from 'react-bootstrap';

import Loading from './../../../Loading/Loading';

import './AgeGroupAttendance.css';

class AgeGroupAttendance extends Component {
  // Class displaying the monthly revenue plot
  constructor(props){
    super(props);
    this.state = {
      data: [],
      allData: [],
      loading: true,
      groupBy: 'Month',
      dropDownGroupBy: 'Month',
      ageGroup: 'Young Professional',
      dropDownAgeGroup: 'Young Professional',
      ageGroups: [],
      topLoading: true,
      top: []
    }

    // Bindings for the plot settings
    this.handleAgeGroup = this.handleAgeGroup.bind(this);
    this.handleGroupBy = this.handleGroupBy.bind(this);
  }

  componentDidMount(){
    this.getAttendance(this.state.ageGroup, this.state.groupBy);
    this.getTopParticipants(this.state.ageGroup);
  }

  handleAgeGroup(event) {
    // Updates the state based on the age group dropdown
    this.setState({dropDownAgeGroup: event.target.value});
  }

  handleGroupBy(event) {
    // Updates the state based on the dropdown
    this.setState({dropDownGroupBy: event.target.value});
  }

  handleSubmit = (event) => {
    // Prevents the app from refreshing on submit
    event.preventDefault();
    // Handles the submit action on the dropdown
    const ageGroup = this.state.dropDownAgeGroup;
    const groupBy = this.state.dropDownGroupBy;
    let newServiceCall = true;
    if(groupBy===this.state.groupBy){
      newServiceCall = false;
    }

    this.setState({
      ageGroup: ageGroup,
      groupBy: groupBy
    })

    if(newServiceCall){
      this.getAttendance(ageGroup, groupBy);
    } else {
      this.renderPlot(ageGroup)
    }
    this.getTopParticipants(ageGroup);
  }

  getTopParticipants = (ageGroup) => {
    // Gets the top participants by age group
    this.setState({topLoading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    let url = '/service/trends/participation/' + ageGroup;
    axios.get(url, { headers: { Authorization: auth }})
      .then(res => {
        const ageGroups = Object.keys(res.data);
        this.setState({
          top: res.data.results,
          topLoading: false
        })
        this.renderPlot(ageGroup);
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  getAttendance = (ageGroup, groupBy) => {
    this.setState({loading: true});
    const token = localStorage.getItem('trsToken');
    const auth = 'Bearer '.concat(token)
    const group = groupBy.toLowerCase();
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
        this.renderPlot(ageGroup);
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        }
      })
  }

  renderTable = () => {
    // Creates the table with member information
    return(
      <div>
        <Row className='event-table'>
          <Table responsive header hover>
            <thead>
              <tr>
                <th className='table-heading'>Mem. Id</th>
                <th className='table-heading'>Name</th>
                <th className='table-heading'>Count</th>
              </tr>
            </thead>
            <tbody>
              {this.state.top.map((member, index) => {
                return(
                  <tr className='table-row' key={index}>
                    <th>{member.member_id != null
                        ? member.member_id : '--'}</th>
                    <th>{member.member_name != null
                        ? member.member_name : '--'}</th>
                    <th>{member.total != null
                        ? member.total : 0}</th>
                  </tr>
                )
              })}
            </tbody>
          </Table>
        </Row>
      </div>
    )
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
        <Form pullLeft inline onSubmit={this.handleSubmit}>
          <FormGroup>
            <ControlLabel className="age-group-labels"
            >Age Group</ControlLabel>
            <FormControl
              componentClass="select"
              value={this.state.dropDownAgeGroup}
              onChange={this.handleAgeGroup}
            >
              {this.state.ageGroups.map((ageGroup, index) => {
                return(<option value={ageGroup}>{ageGroup}</option>)
              })}
            </FormControl>
            <ControlLabel className="age-group-labels"
            >Timeframe</ControlLabel>
            <FormControl
              componentClass="select"
              value={this.state.dropDownGroupBy}
              onChange={this.handleGroupBy}
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
    const dropdowns = this.renderDropDowns();
    const table = this.renderTable();
    if(this.state.loading){
      return (
        <div className='event-loading' id="plot-container">
          <Loading />
        </div>
      )
    } else {
      const width = document.getElementById('plot-container').clientWidth;
      const group = this.state.groupBy;
      let format = null;
      if(group==='Month'){
        format = '%m/%y';
      } else{
        format = '%Y';
      }
      const ageGroup = this.state.ageGroup;
      const observations = this.state.allData[ageGroup]['group'].length
      const nticks = Math.min(observations, 10);
      return (
        <div className='plot-container-half'>
          <Col xs={7} sm={7} md={7} lg={7}>
          <div className='plot-area-half' id="plot-container">
              {dropdowns}
              <Plot
                data={this.state.data}
                layout={ {
                  width: width,
                  height: Math.max(300, width/1.5),
                  title: ageGroup + ' Attendees By ' + group,
                  titlefont: {family: 'Source Sans Pro'},
                  yaxis: {
                    title: 'Unique Attendees',
                    titlefont: {family: 'Source Sans Pro'}
                  },
                  xaxis: {
                    title: group,
                    titlefont: {family: 'Source Sans Pro'},
                    tickangle: 45,
                    type: 'date',
                    tickformat: format,
                    nticks: nticks
                  }
                }
                }
                style={{display: 'inline-block'}}
              />
            </div>
          </Col>

          <div className='top-participants'>
            {table}
          </div>
        </div>
      )
    }
  }
}

export default withRouter(AgeGroupAttendance);
