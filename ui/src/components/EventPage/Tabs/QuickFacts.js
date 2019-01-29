// Renders the information in the Quick Facts
// section of the events view
import React, { Component } from 'react';
import { Col, Row } from 'react-bootstrap';
import Plot from 'react-plotly.js';
import { withRouter } from 'react-router-dom';

const PLOT_COLORS = [
  'rgb(0,73,131)',
  'rgb(29,154,255)',
  'rgb(0,87,156)',
  'rgb(3,143,255)',
  'rgb(0,101,182)',
  'rgb(0,115,207)'
]

class QuickFacts extends Component {
  renderAgeGroupList = () => {
    // Shows the number of people in each age group
    // who are attending the event
    const event = this.props.event;
    let ageGroups = [];
    for(let group in event.age_groups){
      const count = event.age_groups[group];
      if(group==='Young Professional'){
        ageGroups.push(<li><b>YP:</b> {count}</li>);
      } else {
        ageGroups.push(<li><b>{group}:</b> {count}</li>);
      }
    }
    return(
      <div>
        <ul className="quick-facts-bullets">
          {ageGroups}
        </ul>
      </div>
    )
  }

  renderAgeGroups = () => {
    // Creates a donut chart showing the 
    // proportions of each age group
    
    // Generate the data for the plot
    const event = this.props.event;
    let values = [];
    let labels = [];
    for(let group in event.age_groups){
      if(group==='Young Professional'){
        labels.push('YP');
      } else {
        labels.push(group);
      }
      values.push(event.age_groups[group]);
    }
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: PLOT_COLORS, color: 'white'}
    }]


    // Determine the layout and render
    const layout = {
      height: 275,
      width: 275,
      showlegend: false,
      margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
    }

    const ageGroupList = this.renderAgeGroupList();
    return(
      <Col xs={6} sm={6} md={6} lg={6}>
      <div className='quick-facts-plot-container'>
        <h4>Age Groups</h4>
        <div className='quick-facts-list'>
          {ageGroupList}
        </div>
        <div className='quick-facts-plot-area' id="plot-container">
          <Plot
          data={data}
          layout={layout}
          style={{display: 'inline-block'}}
          config={{displayModeBar: false}}
          />
        </div>
      </div>
      </Col>
    )
  }
  
  renderMembers = () => {
    // Creates a donut chart showing the 
    // proportions members at the event
    
    // Generate the data for the plot
    const event = this.props.event;
    let values = [event.member_count, event.non_member_count];
    let labels = ['Members', 'Non-Members'];
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: PLOT_COLORS, color: 'white'}
    }]


    // Determine the layout and render
    const layout = {
      height: 275,
      width: 275,
      showlegend: false,
      margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
    }

    return(
      <Col xs={6} sm={6} md={6} lg={6}>
      <div className='quick-facts-plot-container'>
        <h4>Membership</h4>
        <div className='quick-facts-list'>
          <ul className="quick-facts-bullets">
            <li><b>Members: </b> {event.member_count}</li>
            <li><b>Non-Members: </b> {event.non_member_count}</li>
          </ul>
        </div>
        <div className='quick-facts-plot-area' id="plot-container">
          <Plot
          data={data}
          layout={layout}
          style={{display: 'inline-block'}}
          config={{displayModeBar: false}}
          />
        </div>
      </div>
      </Col>
    )
  }
  
  renderCapacity = () => {
    // Creates a donut chart showing the capacity of the event
    
    // Generate the data for the plot
    const event = this.props.event;
    const remaining = event.capacity - event.attendee_count;
    let values = [event.attendee_count, remaining];
    let labels = ['Registered', 'Remaining'];
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: PLOT_COLORS, color: 'white'}
    }]


    // Determine the layout and render
    const layout = {
      height: 275,
      width: 275,
      showlegend: false,
      margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
    }
    return(
      <Col xs={6} sm={6} md={6} lg={6}>
      <div className='quick-facts-plot-container'>
        <h4>Capacity ({event.capacity})</h4>
        <div className='quick-facts-list'>
          <ul className="quick-facts-bullets">
            <li><b>Registered: </b> {event.attendee_count}</li>
            <li><b>Remaining: </b> {remaining}</li>
          </ul>
        </div>
        <div className='quick-facts-plot-area' id="plot-container">
          <Plot
          data={data}
          layout={layout}
          style={{display: 'inline-block'}}
          config={{displayModeBar: false}}
          />
        </div>
      </div>
      </Col>
    )
  }

  renderFirstEvent = () => {
    // Renders the plot that shows the number of first-timers
    
    // Generate the data for the plot
    const event = this.props.event;
    const repeatAttendees = event.attendee_count - event.first_event_count;
    let values = [event.first_event_count, repeatAttendees];
    let labels = ['First Event', 'Repeat'];
    const data = [{
      values: values,
      labels: labels,
      type: 'pie',
      hole: .4,
      textinfo: 'label',
      textfont: {color: 'white'},
      hoverinfo: 'label+percent',
      marker: {colors: PLOT_COLORS, color: 'white'}
    }]


    // Determine the layout and render
    const layout = {
      height: 275,
      width: 275,
      showlegend: false,
      margin: {l: 0, r: 0, b: 13, t: 0, pad: 0}
    }

    return(
      <Col xs={6} sm={6} md={6} lg={6}>
      <div className='quick-facts-plot-container'>
        <h4>First Event</h4>
        <div className='quick-facts-list'>
          <ul className="quick-facts-bullets">
            <li><b>First Event: </b> {event.first_event_count}</li>
            <li><b>Repeat: </b> {repeatAttendees}</li>
          </ul>
        </div>
        <div className='quick-facts-plot-area' id="plot-container">
          <Plot
          data={data}
          layout={layout}
          style={{display: 'inline-block'}}
          config={{displayModeBar: false}}
          />
        </div>
      </div>
      </Col>
    )
  }

  render(){
    const ageGroups = this.renderAgeGroups();
    const members = this.renderMembers();
    const capacity = this.renderCapacity();
    const firstEvent = this.renderFirstEvent();
    return(
      <div className='QuickFacts'>
        <h4>Quick Facts</h4><hr/>
        <Row>
          {capacity}
          {ageGroups}
        </Row><hr/>
        <Row>
          {members}
          {firstEvent}
        </Row>
      </div> 
    )
  }
};
export default withRouter(QuickFacts);
