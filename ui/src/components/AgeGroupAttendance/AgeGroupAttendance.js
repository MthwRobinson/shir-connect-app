// Renders the monthly revenue component
import axios from 'axios';
import Plot from 'react-plotly.js';
import React, { Component } from 'react';
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
import { withRouter } from 'react-router-dom';

import Loading from './../Loading/Loading';

import './AgeGroupAttendance.css';

class AgeGroupAttendance extends Component {
  // Class displaying the monthly revenue plot
  constructor(props){
    super(props);
    this.state = {
      data: [],
      allData: [],
      loading: true,
      groupBy: 'Year',
      dropDownGroupBy: 'Year',
      ageGroup: '50-60',
      dropDownAgeGroup: '50-60',
      ageGroups: [],
      topLoading: true,
      top: [],
      topCategory: 'Participants'
    }

    // Bindings for the plot settings
    this.handleAgeGroup = this.handleAgeGroup.bind(this);
    this.handleGroupBy = this.handleGroupBy.bind(this);
  }

  componentDidMount(){
    let ageGroup = sessionStorage.getItem('ageGroup');
    let groupBy = sessionStorage.getItem('groupBy');
    let topCategory = sessionStorage.getItem('topCategory');
    if(ageGroup && groupBy && topCategory){
      this.setState({
        ageGroup: ageGroup,
        dropDownAgeGroup: ageGroup,
        groupBy: groupBy,
        dropDownGroupBy: groupBy,
        topCategory: topCategory
      })
    } else {
      ageGroup = this.state.ageGroup;
      groupBy = this.state.groupBy;
      topCategory = this.state.topCategory;
    }
    this.getAttendance(ageGroup, groupBy);
    this.getTopParticipants(ageGroup, topCategory);
  }

  selectParticipant = (participantID) => {
    // Switches to the participant page
    const url = '/participant?id=' + participantID;
    this.props.history.push(url);
  }

  selectEvent = (eventId) => {
    // Switches to the event page
    const url = '/event?id='+eventId;
    this.props.history.push(url);
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
    sessionStorage.setItem('ageGroup', ageGroup)
    sessionStorage.setItem('groupBy', groupBy)
    sessionStorage.setItem('topCategory', this.state.topCategory)

    if(newServiceCall){
      this.getAttendance(ageGroup, groupBy);
    } else {
      this.renderPlot(ageGroup)
    }
    this.getTopParticipants(ageGroup, this.state.topCategory);
  }

  switchTopCategory = () => {
    // Toggles the top category between participants and events
    let topCategory = 'Events';
    if(this.state.topCategory==='Events'){
      this.setState({topCategory: 'Participants'})
      topCategory = 'Participants';
    } else {
      this.setState({topCategory: 'Events'})

    }
    this.getTopParticipants(this.state.ageGroup, topCategory);
  }

  getTopParticipants = (ageGroup, topCategory) => {
    // Gets the top participants by age group
    this.setState({topLoading: true});
    let url = '/service/trends/participation/' + ageGroup;
    if(topCategory==='Events'){
      url += '?top=event';
    } else {
      url += '?top=participant';
    }
    if(sessionStorage.getItem('demoMode')==='true'){
      url += '&fake_data=true';
    }
    axios.get(url)
      .then(res => {
        this.setState({
          top: res.data.results,
          topLoading: false
        })
        this.renderPlot(ageGroup);
      })
      .catch(err => {
        if(err.response.status===401){
          this.props.history.push('/login');
        } else {
          this.props.history.push('/server-error');
        }
      })
  }

  getAttendance = (ageGroup, groupBy) => {
    this.setState({loading: true});
    const group = groupBy.toLowerCase();
    let url = '/service/trends/age-group-attendance';
    url += '?groupBy=' + group;
    axios.get(url)
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
        } else {
          this.props.history.push('/server-error');
        }
      })
  }

  renderTable = () => {
    // Creates the table with participant information
    if(this.state.topLoading){
      return <Loading />
    } else {
      let selectItem = null
      if(this.state.topCategory==='Events'){
        selectItem = (item) => this.selectEvent(item.id);
      } else {
        selectItem = (item) => this.selectParticipant(item.id);
      }

      return(
        <div>
          <Row className='events-table'>
            <Table responsive header hover>
              <thead>
                <tr>
                  <th className='table-heading'>Name</th>
                  <th className='table-heading'>Count</th>
                </tr>
              </thead>
              <tbody>
                {this.state.top.map((item, index) => {
                  return(
                    <tr
                      className='table-row'
                      key={index}
                      onClick={()=> selectItem(item)}
                    >
                      <th>{item.name != null
                          ? item.name : '--'}</th>
                      <th>{item.total != null
                          ? item.total : 0}</th>
                    </tr>
                  )
                })}
              </tbody>
            </Table>
          </Row>
        </div>
      )
    }
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
      let width = document.getElementById('plot-container').clientWidth;
      let height = Math.max(300, width/1.7);
      if(width < 675){
        width = Math.min(width, 500);
        height = Math.min(300, width/1.5);
      }
      const group = this.state.groupBy;
      let format = null;
      if(group==='Month'){
        format = '%m/%y';
      } else{
        format = '%Y';
      }
      const ageGroup = this.state.ageGroup;
      return (
        <div className='plot-container-half'>
          <Col xs={12} sm={12} md={12} lg={7}>
            <div className='plot-area-half' id="plot-container">
              <div className='plot-dropdown'>
                {dropdowns}
              </div>
              <Plot
                data={this.state.data}
                layout={ {
                  width: width,
                  height: height,
                  title: 'Age Group: ' + ageGroup,
                  titlefont: {family: 'Source Sans Pro'},
                  yaxis: {
                    title: 'Unique Attendees',
                    titlefont: {family: 'Source Sans Pro'},
                  },
                  xaxis: {
                    title: group,
                    titlefont: {family: 'Source Sans Pro'},
                    tickangle: 45,
                    type: 'date',
                    tickformat: format,
                  }
                }
                }
                style={{display: 'inline-block'}}
              />
            </div>
          </Col>

          <div className='top-participants'>
            <h4>Top {this.state.topCategory}
              <i
                className='fa fa-reply pull-right event-icons'
                onClick={()=>this.switchTopCategory()}
              ></i>
            </h4><hr/>
            {table}
          </div>
        </div>
      )
    }
  }
}

export default withRouter(AgeGroupAttendance);
